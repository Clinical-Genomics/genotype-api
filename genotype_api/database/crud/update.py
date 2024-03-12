from sqlmodel import Session

from genotype_api.match import check_sample
from genotype_api.database.models import Sample
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True


def refresh_sample_status(sample: Sample, session: Session) -> Sample:
    if len(sample.analyses) != 2:
        sample.status = None
    else:
        results = check_sample(sample=sample)
        sample.status = "fail" if "fail" in results.dict().values() else "pass"

    session.add(sample)
    session.commit()
    session.refresh(sample)
    return sample
