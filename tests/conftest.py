"""General fixtures"""

import datetime
from pathlib import Path
from typing import Generator

import pytest

from genotype_api.database.database import initialise_database, create_all_tables, drop_all_tables
from genotype_api.database.models import User, Plate, SNP, Sample, Genotype, Analysis
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


@pytest.fixture
def timestamp_now() -> datetime:
    return datetime.datetime.now()


@pytest.fixture
def store() -> Generator[Store, None, None]:
    """Return a CG store."""
    initialise_database("sqlite:///")
    _store = Store()
    create_all_tables()
    yield _store
    drop_all_tables()


@pytest.fixture
def helpers(store: Store):
    return StoreHelpers(store)


@pytest.fixture
def test_user() -> User:
    return User(id=1, email="test@tester.com", name="Test Testorus")


@pytest.fixture
def test_plate(test_user: User, timestamp_now: datetime) -> Plate:
    return Plate(
        id=1,
        plate_id="ID_1",
        signed_by=test_user.id,
        method_document="mdoc",
        method_version="mdoc_ver",
        created_at=timestamp_now,
        signed_at=timestamp_now,
    )


@pytest.fixture
def test_snp() -> SNP:
    return SNP(id=1, ref="A", chrom="2", pos=12341)


@pytest.fixture
def test_sample_id() -> str:
    return "test_sample"


@pytest.fixture
def sex_male() -> str:
    return "male"


@pytest.fixture
def test_sample(timestamp_now: datetime, test_sample_id: str, sex_male: str) -> Sample:
    return Sample(
        id=test_sample_id,
        status="test_status",
        comment="test_comment",
        sex=sex_male,
        created_at=timestamp_now,
    )


@pytest.fixture
def test_genotype() -> Genotype:
    return Genotype(id=1, rsnumber="12315", analysis_id=1, allele_1="A", allele_2="G")


@pytest.fixture
def test_analysis(sex_male, timestamp_now: datetime, test_sample_id: str) -> Analysis:
    return Analysis(
        id=1,
        type="genotype",
        source="source",
        sex=sex_male,
        created_at=timestamp_now,
        sample_id=test_sample_id,
        plate_id=1,
    )


@pytest.fixture
def base_store(
    helpers: StoreHelpers,
    test_user: User,
    test_plate: Plate,
    test_snp: SNP,
    test_sample: Sample,
    test_genotype: Genotype,
    test_analysis: Analysis,
):
    helpers.ensure_snp(test_snp)
    helpers.ensure_user(test_user)
    helpers.ensure_plate(test_plate)
    helpers.ensure_sample(test_sample)
    helpers.ensure_genotype(test_genotype)
    helpers.ensure_analysis(test_analysis)
    store: Store = helpers.store
    return store


@pytest.fixture(name="fixtures_dir")
def fixture_fixtures_dir() -> Path:
    """Return the path to fixtures dir."""
    return Path("tests/fixtures")


@pytest.fixture(name="excel_file")
def fixture_excel_file(fixtures_dir: Path) -> Path:
    """Return the path to an excel file."""
    return fixtures_dir / "excel" / "genotype.xlsx"


@pytest.fixture(name="include_key")
def fixture_include_key() -> str:
    """Return the include key."""
    return "-CG-"


@pytest.fixture(name="sample_name")
def fixture_sample_name() -> str:
    """Return a sample name."""
    return "sample"
