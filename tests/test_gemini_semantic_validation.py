
import unittest

from src.ai.validation import validate_potency_descriptions


class TestGeminiSemanticValidation(unittest.TestCase):

    def test_reject_incorrect_subnanomolar(self):
        response = {
            "records": [{
                "ic50_nm": 1.6,
                "interpretation": "Sub-nanomolar inhibitory potency."
            }]
        }

        with self.assertRaises(ValueError):
            validate_potency_descriptions(response)

    def test_accept_correct_subnanomolar(self):
        response = {
            "records": [{
                "ic50_nm": 0.5,
                "interpretation": "Sub-nanomolar inhibitory potency."
            }]
        }

        result = validate_potency_descriptions(response)
        self.assertEqual(result, response)

    def test_reject_boundary_value(self):
        response = {
            "records": [{
                "ic50_nm": 1.0,
                "interpretation": "Sub-nanomolar activity."
            }]
        }

        with self.assertRaises(ValueError):
            validate_potency_descriptions(response)

    def test_accept_non_subnanomolar_description(self):
        response = {
            "records": [{
                "ic50_nm": 1.6,
                "interpretation": "Low-nanomolar inhibitory potency."
            }]
        }

        result = validate_potency_descriptions(response)
        self.assertEqual(result, response)


if __name__ == "__main__":
    unittest.main()
