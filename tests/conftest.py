"""General fixtures"""

import datetime
from pathlib import Path
from typing import AsyncGenerator

import pytest

from genotype_api.database.database import create_all_tables, drop_all_tables, get_session
from genotype_api.database.filter_models.plate_models import PlateSignOff
from genotype_api.database.filter_models.sample_models import SampleSexesUpdate
from genotype_api.database.models import SNP, Analysis, Genotype, Plate, Sample, User
from genotype_api.database.store import Store
from tests.store_helpers import StoreHelpers


@pytest.fixture
def timestamp_now() -> datetime:
    return datetime.datetime.now()


@pytest.fixture
def date_two_weeks_future() -> datetime.date:
    return datetime.date.today() + datetime.timedelta(days=14)


@pytest.fixture
def date_yesterday() -> datetime:
    return datetime.date.today() - datetime.timedelta(days=1)


@pytest.fixture
def date_tomorrow() -> datetime:
    return datetime.date.today() + datetime.timedelta(days=1)


@pytest.fixture(scope="session")
async def store() -> AsyncGenerator[Store, None]:
    """Return a CG store."""
    session = get_session()
    _store = Store(session)
    await create_all_tables()
    yield _store
    await drop_all_tables()


@pytest.fixture
def helpers(store: Store):
    return StoreHelpers()


@pytest.fixture
def test_user() -> User:
    return User(id=1, email="test@tester.com", name="Test Testorus")


@pytest.fixture
def another_test_user() -> User:
    return User(id=2, email="testya@tester.com", name="Testya Testorus")


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
def another_test_plate(another_test_user: User, timestamp_now: datetime) -> Plate:
    return Plate(
        id=2,
        plate_id="ID_2",
        signed_by=another_test_user.id,
        method_document="mdoc",
        method_version="mdoc_ver",
        created_at=timestamp_now,
        signed_at=timestamp_now,
    )


@pytest.fixture
def test_snp() -> SNP:
    return SNP(id=1, ref="A", chrom="2", pos=12341)


@pytest.fixture
def another_test_snp() -> SNP:
    return SNP(id=2, ref="T", chrom="4", pos=112341)


@pytest.fixture
def test_sample_id() -> str:
    return "test_sample"


@pytest.fixture
def another_test_sample_id() -> str:
    return "another_test_sample"


@pytest.fixture
def sex_male() -> str:
    return "male"


@pytest.fixture
def sex_female() -> str:
    return "female"


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
def another_test_sample(
    timestamp_now: datetime, another_test_sample_id: str, sex_female: str
) -> Sample:
    return Sample(
        id=another_test_sample_id,
        status="test_status",
        comment="test_comment",
        sex=sex_female,
        created_at=timestamp_now,
    )


@pytest.fixture
def test_genotype() -> Genotype:
    return Genotype(id=1, rsnumber="12315", analysis_id=1, allele_1="A", allele_2="G")


@pytest.fixture
def another_test_genotype() -> Genotype:
    return Genotype(id=2, rsnumber="123345", analysis_id=2, allele_1="C", allele_2="T")


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
def another_test_analysis(
    sex_male: str, timestamp_now: datetime, another_test_sample_id: str
) -> Analysis:
    return Analysis(
        id=2,
        type="sequence",
        source="source",
        sex=sex_male,
        created_at=timestamp_now,
        sample_id=another_test_sample_id,
        plate_id=2,
    )


@pytest.fixture
def test_users(
    test_user: User,
    another_test_user: User,
) -> list[User]:
    return [test_user, another_test_user]


@pytest.fixture
def test_plates(
    test_plate: Plate,
    another_test_plate: Plate,
) -> list[Plate]:
    return [test_plate, another_test_plate]


@pytest.fixture
def test_snps(
    test_snp: SNP,
    another_test_snp: SNP,
) -> list[SNP]:
    return [test_snp, another_test_snp]


@pytest.fixture
def test_samples(
    test_sample: Sample,
    another_test_sample: Sample,
) -> list[Sample]:
    return [test_sample, another_test_sample]


@pytest.fixture
def test_genotypes(
    test_genotype: Genotype,
    another_test_genotype: Genotype,
) -> list[Genotype]:
    return [test_genotype, another_test_genotype]


@pytest.fixture
def test_analyses(
    test_analysis: Analysis,
    another_test_analysis: Analysis,
) -> list[Analysis]:
    return [test_analysis, another_test_analysis]


@pytest.fixture
async def base_store(
    store: Store,
    helpers: StoreHelpers,
    test_snps: list[SNP],
    test_genotypes: list[Genotype],
    test_plates: list[Plate],
    test_users: list[User],
    test_samples: list[Sample],
    test_analyses: list[Analysis],
):
    for snp in test_snps:
        await helpers.ensure_snp(store=store, snp=snp)
    for genotype in test_genotypes:
        await helpers.ensure_genotype(store=store, genotype=genotype)
    for plate in test_plates:
        await helpers.ensure_plate(store=store, plate=plate)
    for user in test_users:
        await helpers.ensure_user(store=store, user=user)
    for sample in test_samples:
        await helpers.ensure_sample(store=store, sample=sample)
    for analysis in test_analyses:
        await helpers.ensure_analysis(store=store, analysis=analysis)
    return store


@pytest.fixture
def unsigned_plate() -> Plate:
    return Plate(
        id=1,
        plate_id="ID_1",
        signed_by=None,
        method_document=None,
        method_version=None,
        created_at=datetime.datetime.now(),
        signed_at=None,
    )


@pytest.fixture
def plate_sign_off() -> PlateSignOff:
    return PlateSignOff(
        user_id=1,
        signed_at=datetime.datetime.now(),
        method_document="mdoc",
        method_version="mdoc_ver",
    )


@pytest.fixture
def sample_sex_update(test_sample_id) -> SampleSexesUpdate:
    return SampleSexesUpdate(
        sample_id=test_sample_id,
        sex="female",
        genotype_sex="female",
        sequence_sex="female",
    )


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
