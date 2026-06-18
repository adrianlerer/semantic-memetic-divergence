"""
I-3 Social Media corpus pipeline.
STATUS: NOT EXECUTED -- requires Twitter Academic API access.

Instructions for researchers with API access:
1. Obtain Twitter Academic API credentials at developer.twitter.com
2. Set environment variable: export TWITTER_BEARER_TOKEN=your_token
3. Run this script to collect equity-related tweets 2014-2024
4. The pipeline will compute F and P for I-3 using the same sentence-BERT
   approach as other environments.

Alternatively: search Zenodo (zenodo.org) for "DEI equity twitter dataset"
and substitute the downloaded corpus in place of API collection.
"""

BEARER_TOKEN = None  # set via environment variable

QUERY_TERMS = [
    "equity equality boxes",
    "equity DEI inclusion",
    "equality vs equity",
    "#equity #equality",
    "kids boxes equity",
]

print("I-3 pipeline: set TWITTER_BEARER_TOKEN environment variable to run.")
print("See README.md for alternative corpus options.")
