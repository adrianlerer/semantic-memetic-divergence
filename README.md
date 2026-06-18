# Semantic Memetic Divergence (SMD)
## Replication Repository for "Why Good Arguments Lose"

**Paper:** Why Good Arguments Lose: Semantic Speciation and Memetic Fitness in Normative Concepts  
**Author:** Ignacio Adrian Lerer | ORCID: 0009-0007-6378-9749 | adrian@lerer.com.ar  
**Zenodo community:** law-as-extended-phenotype  
**Paper DOI:** [pending Zenodo submission]

---

## What this repo contains

Replication data and scripts for the Semantic Memetic Divergence (SMD) Index
applied to the term "equity" across four institutional environments.

All numerical results in the paper derive from computations in this repository.
No values were estimated or fabricated.

Methodological caveat: the OpenAlex environment is a broad academic corpus
retrieved through the `equity` concept and contains financial, health, policy,
and philosophical uses of the term. It should be read as an academic-use
environment, not as a pure political-philosophy corpus.

---

## Computed Results

### Table 1: SMD Vectors

| Environment | F pre-2015 | P pre-2015 | F post-2015 | P post-2015 | n | Source |
|---|---|---|---|---|---|---|
| I-1 Philosophical | 1.000 | 0.2398 | 0.7285 | 0.2484 | 638 sent. | OpenAlex n=2,000 |
| I-2 Legal (common law) | 1.000 | -- | 0.7285 | -- | 87 texts | CourtListener |
| I-4 Public Policy | 1.000 | 0.4672 | 0.7285 | 0.2913 | 350 sent. | World Bank n=500 |
| I-6 Social Doctrine | 0.137 | -- | 0.191 | -- | 218 sent. | Vatican.va n=13 |
| I-3 Social Media | qualitative only | | | | | no verified corpus |

F normalized: equity frequency Google Ngrams English 2000-2014 = 1.000.  
P = mean intra-environment cosine similarity, sentence-BERT all-MiniLM-L6-v2.

### Table 2: SMD Matrix

|  | I-1 | I-2 | I-4 | I-6 |
|---|---|---|---|---|
| I-1 | -- | 0.132 | 0.043 | **0.540*** |
| I-2 | 0.132 | -- | 0.089 | **0.566*** |
| I-4 | 0.043 | 0.089 | -- | **0.545*** |
| I-6 | **0.540*** | **0.566*** | **0.545*** | -- |

*Exceeds proposed critical threshold of 0.50.

### Key Findings

**Finding 1 (I-6 terminological decoupling):**  
"equity" = 0 occurrences in Vatican corpus post-1965 (after Gaudium et Spes).  
I-6 operates on "justice" (10.15/10k words) not "equity" (0.00/10k post-1965).  
Speciation predates the DEI debate by more than 50 years.

**Finding 2 (I-4 precision collapse):**  
P drops from 0.467 to 0.291 post-2015 in World Bank documents.  
"equity" used in increasingly heterogeneous policy contexts after 2015.

**Finding 3 (Ngrams inversion):**  
equity/equality ratio in Google Ngrams English:  
2001: 1.549 | 2013: 0.959 (inversion) | 2018: 0.772  
"equality" gains in books precisely as "equity" gains in social media.

---

## How to Replicate

### Requirements

```bash
pip install requests pandas scipy sentence-transformers scikit-learn beautifulsoup4 matplotlib
```

Python 3.10+. No API keys required for any script except where noted.

### Run order

```bash
python scripts/01_ngrams.py              # Google Ngrams (no auth)
python scripts/02_openalex.py            # OpenAlex (no auth)
python scripts/03_precision_I1.py        # sentence-BERT on I-1 corpus
python scripts/04_worldbank.py           # World Bank API (no auth)
python scripts/05_precision_I4.py        # sentence-BERT on I-4 corpus
python scripts/06_vatican.py             # Vatican.va scraping (no auth)
python scripts/07b_precision_I6_full.py  # sentence-BERT on I-6 corpus
python scripts/10_legal_corpus.py        # CourtListener (no auth for search)
python scripts/11_smd_final_table.py     # Final SMD computation and matrix
```

### Data sources

| Script | Source | Auth required |
|---|---|---|
| 01_ngrams.py | books.google.com/ngrams/json | None |
| 02_openalex.py | api.openalex.org | None (rate limits) |
| 04_worldbank.py | search.worldbank.org/api/v2/wds | None |
| 06_vatican.py | vatican.va (scraping) | None |
| 10_legal_corpus.py | courtlistener.com/api/rest/v4/search/ | None for search; free token for full opinions |

**Note on I-3 (social media):** No verified corpus available without Twitter
Academic API credentials. I-3 is analyzed qualitatively in paper Section IV.D.
The pipeline for I-3 is included (scripts/13_social_media_placeholder.py) with
instructions for researchers who have API access.

**Note on I-2 (civil law / EUR-Lex):** Script included as
scripts/12_eurlex_sparql.py. Pending execution; included for community extension.

---

## Repository Structure

```
data/
  ngrams_raw.csv              -- Google Ngrams time series 1800-2019
  openalex_philosophy.csv     -- 2,000 papers from OpenAlex
  worldbank_equity.csv        -- 500 World Bank documents
  vatican_corpus.csv          -- 13 Vatican records with derived term counts
  courtlistener_texts.csv     -- 87 CourtListener texts

results/
  precision_I1.json           -- P scores for I-1
  precision_I2.json           -- P scores for I-2
  precision_I4.json           -- P scores for I-4
  precision_I6.json           -- P scores for I-6
  final_consolidated.json     -- All computed vectors and SMD matrix

scripts/
  01_ngrams.py
  02_openalex.py
  03_precision_I1.py
  04_worldbank.py
  05_precision_I4.py
  06_vatican.py
  07b_precision_I6_full.py
  08_smd_final.py
  09_final_table.py
  10_legal_corpus.py
  11_smd_final_table.py

README.md
CITATION.cff
LICENSE
```

The committed `data/vatican_corpus.csv` omits the full scraped text column to
avoid redistributing Vatican.va content. Running `scripts/06_vatican.py` locally
regenerates the full working file needed by `scripts/07b_precision_I6_full.py`.

---

## Citation

If you use this data or pipeline, please cite:

Lerer, I. A. (2026). Why Good Arguments Lose: Semantic Speciation and Memetic
Fitness in Normative Concepts. Zenodo (community: law-as-extended-phenotype).
github.com/adrianlerer/semantic-memetic-divergence

---

## License

MIT. Data from public APIs under their respective terms.  
Vatican.va content: copyright Libreria Editrice Vaticana; the repository
publishes derived counts and URLs, not the full text corpus.  
OpenAlex data: CC0. World Bank data: CC BY 4.0.
