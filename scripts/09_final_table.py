import json, numpy as np, pandas as pd

# Build the honest results table for the paper
# Only report what was actually measured

results = {
    "I-1_Philosophical": {
        "F_pre2015_normalized": 1.000,  # equity is baseline, normalized to 1.0
        "F_post2015_normalized": 0.729,
        "P_pre2015_sbert": 0.2398,
        "P_post2015_sbert": 0.2484,
        "n_sentences": 638,
        "source": "OpenAlex, n=2000 papers, sentence-BERT all-MiniLM-L6-v2",
        "notes": "F from Google Ngrams English 'equity' normalized. P from intra-corpus cosine similarity."
    },
    "I-4_Public_Policy": {
        "F_pre2015_normalized": 0.736,
        "F_post2015_normalized": 0.796,  # equality gaining in books, policy docs show equity dominant
        "P_pre2015_sbert": 0.4672,
        "P_post2015_sbert": 0.2913,
        "n_sentences": 350,
        "source": "World Bank Documents API, n=500 docs, sentence-BERT",
        "notes": "Strong P decline post-2015: equity used in increasingly heterogeneous contexts."
    },
    "I-6_Social_Doctrine": {
        "F_pre2015_normalized": 0.137,
        "F_post2015_normalized": 0.191,
        "P_overall_sbert": 0.2033,
        "n_sentences": 218,
        "source": "Vatican.va, 13 encyclicals 1891-2023, sentence-BERT",
        "KEY_FINDING": "EQUITY ABSENT POST-1965. 0 occurrences of 'equity' in Vatican corpus after Gaudium et Spes (1965). I-6 operates on 'justice' (avg 10.15/10k words) not 'equity' (0.15/10k). Terminological decoupling is complete."
    },
    "I-2_Legal_Positive": {
        "status": "PENDING",
        "corpus": "Harvard CAP API (requires token registration at case.law) + CourtListener",
        "pipeline": "scripts/04_legal_corpus.py in repo"
    },
    "I-3_Social_Media": {
        "status": "NOT COMPUTED",
        "reason": "No verified corpus without Twitter Academic API or Pushshift access",
        "treatment_in_paper": "Qualitative analysis, Section IV.D, with explicit methodological note"
    }
}

print("=" * 60)
print("FINAL COMPUTED RESULTS FOR PAPER")
print("=" * 60)

for env, data in results.items():
    print(f"\n{env}:")
    for k, v in data.items():
        print(f"  {k}: {v}")

# SMD between computed environments
def smd_val(f1, p1, f2, p2):
    return round(np.sqrt((f1-f2)**2 + (p1-p2)**2), 4)

print("\n" + "=" * 60)
print("SMD MATRIX — COMPUTED VALUES ONLY")
print("=" * 60)

# Post-2015
i1f = results["I-1_Philosophical"]["F_post2015_normalized"]
i1p = results["I-1_Philosophical"]["P_post2015_sbert"]
i4f = results["I-4_Public_Policy"]["F_post2015_normalized"]
i4p = results["I-4_Public_Policy"]["P_post2015_sbert"]
i6f = results["I-6_Social_Doctrine"]["F_post2015_normalized"]
i6p = results["I-6_Social_Doctrine"]["P_overall_sbert"]

print(f"\nPost-2015 vectors:")
print(f"  I-1: F={i1f:.4f}, P={i1p:.4f}")
print(f"  I-4: F={i4f:.4f}, P={i4p:.4f}")
print(f"  I-6: F={i6f:.4f}, P={i6p:.4f} [note: P from full period, pre/post not computable with n=218]")

print(f"\nSMD(I-1, I-4) post-2015: {smd_val(i1f,i1p,i4f,i4p)}")
print(f"SMD(I-1, I-6) post-2015: {smd_val(i1f,i1p,i6f,i6p)}")
print(f"SMD(I-4, I-6) post-2015: {smd_val(i4f,i4p,i6f,i6p)}")

i1f_pre = results["I-1_Philosophical"]["F_pre2015_normalized"]
i1p_pre = results["I-1_Philosophical"]["P_pre2015_sbert"]
i4f_pre = results["I-4_Public_Policy"]["F_pre2015_normalized"]
i4p_pre = results["I-4_Public_Policy"]["P_pre2015_sbert"]

print(f"\nSMD(I-1, I-4) pre-2015:  {smd_val(i1f_pre,i1p_pre,i4f_pre,i4p_pre)}")

with open("results/final_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved final_results.json")
