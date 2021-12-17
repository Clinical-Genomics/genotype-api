"""Tests fpr the excel module"""

from pathlib import Path

from genotype_api.excel import GenotypeAnalysis

"""
def test_read_excel(excel_file: Path, include_key: str):
    # GIVEN an excel file and a include key

    # WHEN parsing an excel file
    parser = GenotypeAnalysis(excel_file=excel_file, include_key=include_key)

    # THEN assert that the sample is in the header
    assert "SAMPLE" in parser.header_row


def test_parse_analyses(excel_file: Path, include_key: str, sample_name: str):
    # GIVEN a parsed excel file
    parser = GenotypeAnalysis(excel_file=excel_file, include_key=include_key)

    # WHEN parsing the analyses
    analyses = [analysis for analysis in parser.generate_analyses()]

    # THEN assert the number of analyses is 3
    assert len(analyses) == 3
"""
