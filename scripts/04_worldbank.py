import requests, pandas as pd, time, json

print("=== World Bank Documents API ===")
url = "https://search.worldbank.org/api/v2/wds"
params = {
    "format": "json",
    "qterm": "equity",
    "rows": 100,
    "os": 0,
    "fl": "id,docdt,repnb,docty,abstracts,title,lang"
}

all_docs = []
for offset in range(0, 500, 100):
    params["os"] = offset
    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()
        docs = data.get("documents", {})
        # The API returns a dict keyed by doc ID
        if isinstance(docs, dict):
            batch = list(docs.values())
        else:
            batch = docs
        # Filter out metadata keys
        batch = [d for d in batch if isinstance(d, dict) and "id" in d]
        all_docs.extend(batch)
        print(f"  Offset {offset}: got {len(batch)} docs (total {len(all_docs)})")
        time.sleep(0.5)
        if len(batch) < 100:
            break
    except Exception as e:
        print(f"  Error at offset {offset}: {e}")
        break

print(f"\nTotal documents retrieved: {len(all_docs)}")

rows = []
for d in all_docs:
    abstract_raw = d.get("abstracts", {})
    if isinstance(abstract_raw, dict):
        abstract = abstract_raw.get("cdata!", "") or abstract_raw.get("#text", "") or str(abstract_raw)
    else:
        abstract = str(abstract_raw) if abstract_raw else ""
    rows.append({
        "id": d.get("id",""),
        "title": d.get("title",""),
        "year": str(d.get("docdt",""))[:4],
        "doctype": d.get("docty",""),
        "abstract": abstract[:1000],
        "lang": d.get("lang","")
    })

df = pd.DataFrame(rows)
df.to_csv("data/worldbank_equity.csv", index=False)

print(f"\nSaved {len(df)} rows")
print("\n--- Doc types ---")
print(df["doctype"].value_counts().head(10).to_string())
print("\n--- Year distribution (post-2000) ---")
year_df = df[df["year"].str.match(r'^\d{4}$', na=False)]
year_df = year_df[year_df["year"].astype(int) >= 2000]
print(year_df.groupby("year").size().tail(20).to_string())

# Term frequency check
df["has_equity"]   = df["abstract"].str.lower().str.contains(r"\bequity\b", na=False)
df["has_equality"] = df["abstract"].str.lower().str.contains(r"\bequality\b", na=False)
print(f"\nAbstracts with 'equity':   {df['has_equity'].sum()}")
print(f"Abstracts with 'equality': {df['has_equality'].sum()}")
