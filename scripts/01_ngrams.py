import requests, json, pandas as pd, time

def fetch_ngrams(terms, start=1800, end=2019, corpus=26, smoothing=0):
    url = "https://books.google.com/ngrams/json"
    params = {
        "content": ",".join(terms),
        "year_start": start,
        "year_end": end,
        "corpus": corpus,
        "smoothing": smoothing
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

terms = ["equity", "equality", "social justice", "equidad", "justicia social"]
print(f"Fetching Ngrams for: {terms}")
data = fetch_ngrams(terms)

rows = []
for series in data:
    ngram = series["ngram"]
    for i, year in enumerate(range(1800, 2020)):
        rows.append({"ngram": ngram, "year": year, "frequency": series["timeseries"][i]})

df = pd.DataFrame(rows)
df.to_csv("data/ngrams_raw.csv", index=False)

# Summary stats for key periods
for term in ["equity", "equality", "social justice"]:
    sub = df[df["ngram"] == term]
    pre  = sub[sub["year"].between(2000, 2009)]["frequency"].mean()
    post = sub[sub["year"].between(2015, 2019)]["frequency"].mean()
    ratio = post / pre if pre > 0 else float("inf")
    print(f"{term:20s} | pre-2015 avg: {pre:.6f} | post-2015 avg: {post:.6f} | ratio: {ratio:.2f}x")

print(f"\nRows saved: {len(df)}")
print("File: data/ngrams_raw.csv")

# Decade-level view for equity
print("\n--- equity frequency by decade ---")
sub = df[df["ngram"] == "equity"]
for decade_start in range(1900, 2020, 10):
    avg = sub[sub["year"].between(decade_start, decade_start+9)]["frequency"].mean()
    print(f"  {decade_start}s: {avg:.7f}")

# equity/equality ratio by year post-2000
print("\n--- equity / equality ratio 2000-2019 ---")
eq  = df[df["ngram"] == "equity"].set_index("year")["frequency"]
eql = df[df["ngram"] == "equality"].set_index("year")["frequency"]
ratio = (eq / eql).loc[2000:2019]
for yr, val in ratio.items():
    print(f"  {yr}: {val:.3f}")
