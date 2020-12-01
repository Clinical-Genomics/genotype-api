# Genotype API

Genotype is a tool to validate integrity and sex for samples.

This is a rewrite of [genotype][genotype] utilising a complete REST API implemented with [FastAPI][fastapi].

## Installation

install [poetry]

```
git clone https://github.com/Clinical-Genomics/genotype-api
poetry install
```

## Usage

```
uvicorn genotype_api.__main__:app --reload 
```

Go to `127.0.0.1:8000/docs` and test the API

## Description

After sample prep a small part of the DNA is sent to MAF where they do SNP calling with a orthogonal method for a predefined set of SNPs. MAF also to gender prediction based on their result. The result from MAF is sent back as an excel sheet and this get uploaded to genotype via the `Upload Plate`-endpoint. 
 
The same samples get sequenced and genotyped inhouse and the result of this is uploaded in the VCF format via the `Upload Sequence`-endpoint.

The two analyses for each sample are then compared to check for anomalies.

## Test usage

Start the server as described above. Go to the docs and upload the excel example in `tests/fixtures/excel/genotype.xlsx` to the upload plate endpoint. Then upload the `tests/fixtures/vcf/sequence.vcf` to the upload sequence endpoint.



 