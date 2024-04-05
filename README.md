# Genotype API

Genotype is a tool to validate integrity and sex for samples.

This is a rewrite of [genotype][genotype] utilising a complete REST API implemented with [FastAPI][fastapi].

## Installation

install [poetry]

```
git clone https://github.com/Clinical-Genomics/genotype-api
cd genotype-api
pip install poetry
poetry install
```

## Usage

```
uvicorn genotype_api.api.app:app --reload 
```

Go to `http://localhost:8000/docs` and test the API


## Authorization


There is currently no working demo avalible. 
To autorize you'l need to provide a valid ID-token.

## Description

After sample prep a small part of the DNA is sent to MAF where they do SNP calling with a orthogonal method for a predefined set of SNPs. MAF also to gender prediction based on their result. The result from MAF is sent back as an excel sheet and this get uploaded to genotype via the `Upload Plate`-endpoint. 
 
The same samples get sequenced and genotyped inhouse and the result of this is uploaded in the VCF format via the `Upload Sequence`-endpoint.

The two analyses for each sample are then compared to check for anomalies.



 