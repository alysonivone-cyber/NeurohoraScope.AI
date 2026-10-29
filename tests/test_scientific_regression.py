"""Offline scientific regression tests; no external API or database access."""
import unittest
from decimal import Decimal

from src.analysis.molecular_comparison import compare_molecules
from src.analysis.pharmacology_comparison import extract_btk_ic50
from src.analysis.molecular_selectivity import extract_target_profile
from src.analysis.evidence_assessment import assess_evidence
from src.analysis.exact_activity_matcher import normalize_number
from src.analysis.trial_relevance import is_relevant_trial
from src.clients.clinical_trials_client import filter_trials_by_disease
from src.ai.validation import validate_gemini_records


def sample_report():
    return {
        'molecule': 'Example A', 'disease': 'Multiple Sclerosis',
        'pharmacology': {'bioactivities': {'activities': [
            {'target_name': 'Tyrosine-protein kinase BTK', 'standard_type': 'IC50',
             'standard_units': 'nM', 'standard_relation': '=', 'standard_value': '12.5',
             'assay_chembl_id': 'CHEMBL123'},
            {'target_name': 'Tyrosine-protein kinase BTK', 'standard_type': 'IC50',
             'standard_units': 'nM', 'standard_relation': '>', 'standard_value': '100',
             'assay_chembl_id': 'CHEMBL124'},
            {'target_name': 'Tyrosine-protein kinase BTK', 'standard_type': 'IC50',
             'standard_units': 'uM', 'standard_relation': '=', 'standard_value': '2',
             'assay_chembl_id': 'CHEMBL125'},
        ]}},
        'clinical_trials': {'studies': [{'has_results': True}]},
        'literature': {'publications': [{'publication_types': ['Review']}]},
    }


class ScientificRegressionTests(unittest.TestCase):
    def test_exact_btk_ic50_extraction(self):
        self.assertEqual(extract_btk_ic50(sample_report()), [
            {'ic50_nM': 12.5, 'assay_chembl_id': 'CHEMBL123'}])

    def test_missing_measurements_not_invented(self):
        self.assertEqual(extract_btk_ic50({'pharmacology': {}}), [])

    def test_target_profile_preserves_assay(self):
        profile = extract_target_profile(sample_report())
        self.assertEqual(profile['targets_identified'], 1)
        self.assertEqual(profile['target_profile']['Tyrosine-protein kinase BTK'],
                         [{'ic50_nM': 12.5, 'assay_chembl_id': 'CHEMBL123'}])
        self.assertIn('not assessed', profile['interpretation'])

    def test_molecular_comparison_does_not_claim_efficacy(self):
        comparison = compare_molecules(sample_report(), {'molecule': 'Example B'})
        self.assertEqual(comparison['molecule_a']['bioactivity_records'], 3)
        self.assertEqual(comparison['molecule_b']['bioactivity_records'], 0)
        self.assertIn('do not measure comparative efficacy', comparison['interpretation'])

    def test_evidence_inventory_not_clinical_claim(self):
        result = assess_evidence(sample_report())
        self.assertEqual(result['clinical_evidence']['trials_with_registered_results'], 1)
        self.assertFalse(result['experimental_evidence']['clinical_efficacy_established'])
        self.assertEqual(result['clinical_evidence']['efficacy_conclusion'], 'Not assessed')

    def test_number_normalization(self):
        self.assertEqual(normalize_number('1.60'), Decimal('1.60'))
        self.assertIsNone(normalize_number('unknown'))

    def test_trial_filter_is_conservative(self):
        self.assertTrue(is_relevant_trial('Multiple Sclerosis', ['Relapsing Multiple Sclerosis']))
        self.assertFalse(is_relevant_trial('Multiple Sclerosis', ['Tuberous Sclerosis']))
        filtered = filter_trials_by_disease([
            {'nct_id': 'NCT1', 'conditions': ['Multiple Sclerosis']},
            {'nct_id': 'NCT2', 'conditions': ['Tuberous Sclerosis']},
            {'nct_id': 'NCT3', 'conditions': []},
        ], 'Multiple Sclerosis')
        self.assertEqual((filtered['relevant_count'], filtered['excluded_count'],
                          filtered['missing_conditions_count']), (1, 1, 1))

    def test_gemini_rejects_modified_measurement(self):
        original = [{'molecule': 'Example A', 'target': 'BTK',
                     'assay_chembl_id': 'CHEMBL123', 'ic50_nM': 12.5}]
        response = {'records': [{'molecule': 'Example A', 'target': 'BTK',
                                 'assay_id': 'CHEMBL123', 'ic50_nm': 12.5,
                                 'interpretation': 'In vitro result'}]}
        self.assertIs(validate_gemini_records(original, response), response)
        response['records'][0]['ic50_nm'] = 0.5
        with self.assertRaises(ValueError):
            validate_gemini_records(original, response)

    def test_gemini_rejects_dropped_records(self):
        with self.assertRaises(ValueError):
            validate_gemini_records([{'molecule': 'X', 'target': 'Y',
                                     'assay_chembl_id': 'CHEMBL1', 'ic50_nM': 1}],
                                    {'records': []})


if __name__ == '__main__':
    unittest.main()
