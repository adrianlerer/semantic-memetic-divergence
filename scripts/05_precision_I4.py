import pandas as pd, numpy as np, json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re, warnings; warnings.filterwarnings("ignore")

model = SentenceTransformer("all-MiniLM-L6-v2")

df = pd.read_csv("data/worldbank_equity.csv")
df_eq = df[df["abstract"].str.lower().str.contains(r"\bequity\b", na=False)].copy()
df_eq = df_eq[df_eq["abstract"].str.len() > 80].copy()
print(f"WB docs with equity, len>80: {len(df_eq)}")

sentences = []
for _, row in df_eq.iterrows():
    sents = re.split(r'(?<=[.!?])\s+', str(row["abstract"]))
    for s in sents:
        if "equity" in s.lower() and len(s.split()) >= 5:
            sentences.append({"sentence": s.strip(), "year": str(row["year"])[:4]})

print(f"Equity sentences: {len(sentences)}")
if len(sentences) < 10:
    sentences = [{"sentence": str(row["abstract"])[:500], "year": str(row["year"])[:4]}
                 for _, row in df_eq.iterrows()]

texts = [s["sentence"] for s in sentences]
print(f"Encoding {len(texts)} sentences...")
emb = model.encode(texts, batch_size=64, show_progress_bar=False)

sims = cosine_similarity(emb)
np.fill_diagonal(sims, np.nan)
upper = sims[np.triu_indices_from(sims, k=1)]
P = float(np.nanmean(upper))
std = float(np.nanstd(upper))

print(f"\n=== I-4 Public Policy Precision (P) ===")
print(f"  N: {len(texts)}")
print(f"  P(I-4): {P:.4f}")
print(f"  Std:    {std:.4f}")

# Pre/post 2015
years = [s["year"] for s in sentences]
pre_idx  = [i for i, y in enumerate(years) if y.isdigit() and int(y) < 2015]
post_idx = [i for i, y in enumerate(years) if y.isdigit() and int(y) >= 2015]

P_pre = P_post = None
if len(pre_idx) > 5 and len(post_idx) > 5:
    ps = cosine_similarity(emb[pre_idx]); np.fill_diagonal(ps, np.nan)
    qs = cosine_similarity(emb[post_idx]); np.fill_diagonal(qs, np.nan)
    P_pre  = float(np.nanmean(ps[np.triu_indices_from(ps, k=1)]))
    P_post = float(np.nanmean(qs[np.triu_indices_from(qs, k=1)]))
    print(f"  P pre-2015:  {P_pre:.4f}")
    print(f"  P post-2015: {P_post:.4f}")

res = {"environment":"I-4_public_policy","n":len(texts),
       "P_overall":round(P,4),"P_pre2015":round(P_pre,4) if P_pre else None,
       "P_post2015":round(P_post,4) if P_post else None,"std":round(std,4),
       "source":"World Bank Documents API, qterm=equity, n=500 docs"}
with open("results/precision_I4.json","w") as f:
    json.dump(res,f,indent=2)
print("\nSaved precision_I4.json")
