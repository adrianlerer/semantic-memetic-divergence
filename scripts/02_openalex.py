import requests, pandas as pd, time, json

BASE = "https://api.openalex.org"

def get_concept_id(term):
    r = requests.get(f"{BASE}/concepts", params={"search": term}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data["results"]:
        c = data["results"][0]
        print(f"  Concept '{term}': id={c['id']} display_name={c['display_name']} level={c['level']}")
        return c["id"]
    return None

print("=== Finding concept IDs ===")
concepts = {}
for term in ["distributive justice", "equity", "egalitarianism", "political philosophy"]:
    concepts[term] = get_concept_id(term)
    time.sleep(0.5)

# Fetch works mentioning equity in philosophy 2000-2024
print("\n=== Fetching works: equity in philosophy 2000-2024 ===")
concept_id = concepts.get("equity") or concepts.get("distributive justice")

params = {
    "filter": f"concepts.id:{concept_id},from_publication_date:2000-01-01,to_publication_date:2024-12-31",
    "select": "id,title,publication_year,abstract_inverted_index,cited_by_count,concepts",
    "per-page": 200,
    "cursor": "*"
}

all_works = []
page = 0
while len(all_works) < 2000:
    r = requests.get(f"{BASE}/works", params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    batch = data.get("results", [])
    if not batch:
        break
    all_works.extend(batch)
    cursor = data.get("meta", {}).get("next_cursor")
    if not cursor:
        break
    params["cursor"] = cursor
    page += 1
    if page % 5 == 0:
        print(f"  Fetched {len(all_works)} works so far...")
    time.sleep(0.3)

print(f"Total works fetched: {len(all_works)}")

# Reconstruct abstracts from inverted index
def reconstruct_abstract(inv_index):
    if not inv_index:
        return ""
    positions = []
    for word, pos_list in inv_index.items():
        for pos in pos_list:
            positions.append((pos, word))
    positions.sort()
    return " ".join(w for _, w in positions)

rows = []
for w in all_works:
    abstract = reconstruct_abstract(w.get("abstract_inverted_index"))
    rows.append({
        "id": w["id"],
        "title": w.get("title", ""),
        "year": w.get("publication_year"),
        "abstract": abstract,
        "cited_by_count": w.get("cited_by_count", 0)
    })

df = pd.DataFrame(rows)
df.to_csv("data/openalex_philosophy.csv", index=False)
print(f"Saved {len(df)} rows to openalex_philosophy.csv")

# Year distribution
print("\n--- Works per year (sample) ---")
print(df.groupby("year").size().tail(20).to_string())

# Equity term frequency in abstracts
df["has_equity"]    = df["abstract"].str.lower().str.contains(r"\bequity\b", na=False)
df["has_equality"]  = df["abstract"].str.lower().str.contains(r"\bequality\b", na=False)
df["has_fairness"]  = df["abstract"].str.lower().str.contains(r"\bfairness\b", na=False)

print("\n--- Term frequency in abstracts ---")
for col in ["has_equity", "has_equality", "has_fairness"]:
    n = df[col].sum()
    pct = n / len(df) * 100
    print(f"  {col}: {n} ({pct:.1f}%)")
