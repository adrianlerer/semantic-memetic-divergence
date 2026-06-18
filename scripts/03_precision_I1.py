import pandas as pd, numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import warnings; warnings.filterwarnings("ignore")

print("Loading sentence-BERT model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

df = pd.read_csv("data/openalex_philosophy.csv")

# Keep only abstracts with "equity" and minimum length
df_eq = df[df["abstract"].str.lower().str.contains(r"\bequity\b", na=False)].copy()
df_eq = df_eq[df_eq["abstract"].str.len() > 100].copy()
print(f"Abstracts with 'equity' and len>100: {len(df_eq)}")

# Sample for tractability: 400 max
sample = df_eq.sample(min(400, len(df_eq)), random_state=42)

# Extract sentences containing "equity"
import re
equity_sentences = []
for _, row in sample.iterrows():
    sents = re.split(r'(?<=[.!?])\s+', row["abstract"])
    for s in sents:
        if "equity" in s.lower() and len(s.split()) >= 5:
            equity_sentences.append({
                "sentence": s.strip(),
                "year": row["year"]
            })

print(f"Equity-containing sentences: {len(equity_sentences)}")

if len(equity_sentences) < 10:
    print("Too few sentences — using full abstracts instead")
    equity_sentences = [{"sentence": row["abstract"][:500], "year": row["year"]}
                        for _, row in sample.iterrows()]

texts = [s["sentence"] for s in equity_sentences]
print(f"Encoding {len(texts)} sentences...")
embeddings = model.encode(texts, batch_size=64, show_progress_bar=False)

# Pairwise cosine similarity
sims = cosine_similarity(embeddings)
np.fill_diagonal(sims, np.nan)
upper = sims[np.triu_indices_from(sims, k=1)]

mean_sim = np.nanmean(upper)
std_sim  = np.nanstd(upper)
P_score  = mean_sim  # Precision = mean intra-environment cosine similarity

print(f"\n=== I-1 Philosophical Precision (P) ===")
print(f"  N sentences:       {len(texts)}")
print(f"  Mean cosine sim:   {mean_sim:.4f}  <- this is P(I-1)")
print(f"  Std cosine sim:    {std_sim:.4f}")
print(f"  Interpretation:    {'HIGH precision' if mean_sim > 0.5 else 'MODERATE precision' if mean_sim > 0.35 else 'LOW precision'}")

# Year split: pre/post 2015
years = [s["year"] for s in equity_sentences]
pre_idx  = [i for i, y in enumerate(years) if y and y < 2015]
post_idx = [i for i, y in enumerate(years) if y and y >= 2015]

if len(pre_idx) > 10 and len(post_idx) > 10:
    pre_emb  = embeddings[pre_idx]
    post_emb = embeddings[post_idx]
    pre_sims  = cosine_similarity(pre_emb)
    post_sims = cosine_similarity(post_emb)
    np.fill_diagonal(pre_sims, np.nan)
    np.fill_diagonal(post_sims, np.nan)
    P_pre  = np.nanmean(pre_sims[np.triu_indices_from(pre_sims, k=1)])
    P_post = np.nanmean(post_sims[np.triu_indices_from(post_sims, k=1)])
    print(f"\n  P(I-1) pre-2015:   {P_pre:.4f}")
    print(f"  P(I-1) post-2015:  {P_post:.4f}")
    print(f"  Delta:             {P_post - P_pre:+.4f}")

# Save results
results = {
    "environment": "I-1_philosophical",
    "n_sentences": len(texts),
    "P_overall": round(mean_sim, 4),
    "P_pre2015": round(P_pre, 4) if len(pre_idx) > 10 else None,
    "P_post2015": round(P_post, 4) if len(post_idx) > 10 else None,
    "std_sim": round(std_sim, 4)
}
import json
with open("results/precision_I1.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nSaved to results/precision_I1.json")
