"""Deterministic validation of AI-transcribed experimental ChEMBL records."""

from collections import Counter
from decimal import Decimal, InvalidOperation


def _value(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError('Invalid IC50 measurement') from exc
    if not result.is_finite() or result <= 0:
        raise ValueError('IC50 must be finite and positive')
    return result


def validate_gemini_records(original_records, response):
    """Reject missing, added or altered observations, regardless of AI prose.

    This checks experimental identity and IC50 only. It cannot verify the
    scientific accuracy of generated natural-language interpretations.
    """
    if not isinstance(original_records, list) or not isinstance(response, dict):
        raise ValueError('Unexpected input or response type')
    interpreted = response.get('records')
    if not isinstance(interpreted, list):
        raise ValueError('Gemini response has no records list')

    def original_key(row):
        if not isinstance(row, dict):
            raise ValueError('Invalid source record')
        return (row.get('molecule'), row.get('target'),
                row.get('assay_chembl_id'), _value(row.get('ic50_nM')))

    def interpreted_key(row):
        if not isinstance(row, dict):
            raise ValueError('Invalid interpreted record')
        return (row.get('molecule'), row.get('target'),
                row.get('assay_id'), _value(row.get('ic50_nm')))

    if Counter(map(original_key, original_records)) != Counter(map(interpreted_key, interpreted)):
        raise ValueError('Gemini altered, added, duplicated or omitted source measurements')
    return response


import re


def validate_potency_descriptions(response):
    """
    Detect incorrect sub-nanomolar descriptions.

    This is a targeted semantic consistency check,
    not a complete scientific interpretation validator.
    """
    records = response.get("records", [])

    if not isinstance(records, list):
        raise ValueError("Invalid Gemini records.")

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid Gemini record.")

        interpretation = record.get("interpretation", "")
        if not isinstance(interpretation, str):
            raise ValueError("Invalid interpretation.")

        ic50 = _value(record.get("ic50_nm"))

        subnanomolar = re.search(
            r"\bsub[\s-]?nanomolar\b",
            interpretation,
            flags=re.IGNORECASE,
        )

        if subnanomolar and ic50 >= Decimal("1"):
            raise ValueError(
                "Scientific inconsistency: "
                f"IC50 = {ic50} nM cannot be "
                "described as sub-nanomolar."
            )

    return response
