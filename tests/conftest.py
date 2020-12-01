"""General fixtures"""

from pathlib import Path

import pytest


@pytest.fixture(name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """Return the path to fixtures dir"""
    return Path("tests/fixtures")


@pytest.fixture(name="excel_file")
def fixture_excel_file(fixtures_dir: Path) -> Path:
    """Return the path to an excel file"""
    return fixtures_dir / "excel" / "genotype.xlsx"


@pytest.fixture(name="include_key")
def fixture_include_key() -> str:
    """Return the include key"""
    return "-CG-"


@pytest.fixture(name="sample_name")
def fixture_sample_name() -> str:
    """Return a sample name"""
    return "sample"
