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

## Selection of the max_mismatch cutoff

In order to choose the cutoff for max_mismatch (see genotype_api.constants::CUTOFFS), the following analysis was performed:

To figure out a reasonable cutoff to differentiate between concordant and discordant results, results from 5 MAF plates (ID7-11) were loaded into a new database. Correspondingly, results from sequencing were also imported from both exome and whole genome sequencing.

The results were plotted as a histogram based on number of mismatches per comparison.

<img width="397" height="281" alt="comparison_of_mismatches (1)" src="https://github.com/user-attachments/assets/f6bbdf01-1fdd-4352-ac09-a90e45baa917" />

Clustering to the left are the 200 true hits. Clustering around 26 mismatches are the random hits. The gap between true and random hits is very obvious. This lets us set the cutoff rather liberally since we have confirmed that random hits have at least 14 mismatches.

Chosen cutoff: **3 mismatches**. Anything above that will set the status to fail.

