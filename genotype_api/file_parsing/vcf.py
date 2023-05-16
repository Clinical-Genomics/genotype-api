"""Functions to work with VCF files"""

from typing import Dict, Iterable, List, TextIO

from genotype_api.models import Analysis, Genotype as DBGenotype
from pydantic import BaseModel


class Genotype(BaseModel):
    sample_id: str
    allele_1: str
    allele_2: str


class Variant(BaseModel):
    chrom: str
    pos: int
    id: str
    ref: str
    alt: str
    genotypes: List[Genotype]


class SequenceAnalysis:
    """Class for generating analyses from a VCF"""

    def __init__(self, vcf_file: TextIO, source: str):
        self.vcf = vcf_file
        self.source = source
        self.header = []
        self.set_header()
        self.sample_ids = self.header[9:]
        self.header_columns = [col.lower() for col in self.header[:8]]

    def set_header(self) -> None:
        for line in self.vcf.split("\n"):
            if line.startswith("##"):
                continue
            if not len(line) > 10:
                continue
            line = line.rstrip()
            if line.startswith("#"):
                self.header = line[1:].split("\t")
                return

    def generate_analyses(self) -> Iterable[Analysis]:
        analyses: Dict[str, Analysis] = {
            sample_id: Analysis(type="sequence", source=self.source, sample_id=sample_id)
            for sample_id in self.sample_ids
        }

        variant_object: Variant
        for variant_object in self.generate_variants():
            gt_info: Genotype
            for gt_info in variant_object.genotypes:
                db_genotype = DBGenotype(
                    rsnumber=variant_object.id,
                    allele_1=gt_info.allele_1,
                    allele_2=gt_info.allele_2,
                )
                analyses[gt_info.sample_id].genotypes.append(db_genotype)
        return [analysis for analysis in analyses.values()]

    def generate_variants(self) -> Iterable[Variant]:
        for line in self.vcf.split("\n"):
            if line.startswith("#"):
                continue
            if len(line) < 10:
                continue
            line = line.rstrip()
            variant_line = line.split("\t")
            variant_info = dict(zip(self.header_columns, variant_line))
            gt_info: List[str] = [gt_call.split(":")[0] for gt_call in variant_line[9:]]

            variant_info["genotypes"] = self.variant_genotypes(gt_info=gt_info)
            yield Variant(**variant_info)

    def variant_genotypes(self, gt_info: List[str]) -> Iterable[dict]:
        """Build Genotype objects from vcf information."""
        for sample_id, bases in zip(self.sample_ids, gt_info):
            bases = bases.replace("|", "/")
            allele_1, allele_2 = bases.split("/")
            yield {"sample_id": sample_id, "allele_1": allele_1, "allele_2": allele_2}


if __name__ == "__main__":
    from pathlib import Path

    vcf = "../tests/fixtures/vcfs/sequence.vcf"
    vcf_path = Path(vcf)
    with open(vcf, "r") as infile:
        file_obj = infile.read()
        sequence_obj = SequenceAnalysis(file_obj, source=vcf_path.name)
        for analysis in sequence_obj.generate_analyses():
            print(analysis)
