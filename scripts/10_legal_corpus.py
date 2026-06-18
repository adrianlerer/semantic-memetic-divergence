import requests, pandas as pd, re, json, time
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import warnings; warnings.filterwarnings("ignore")

BASE = "https://www.courtlistener.com/api/rest/v4/search/"
texts_collected = []

queries = [
    "equitable remedy",
    "equity jurisdiction",
    "equitable relief injunction",
    "trust equity fiduciary",
    "equitable estoppel doctrine",
]

for query in queries:
    time.sleep(4)
    params = {"q": query, "type": "o", "format": "json"}
    try:
        r = requests.get(BASE, params=params, timeout=30)
        if r.status_code == 429:
            time.sleep(15); continue
        r.raise_for_status()
        data = r.json()
        for result in data.get("results", []):
            # Use available text fields
            parts = []
            for field in ["posture","procedural_history","syllabus","suitNature"]:
                val = result.get(field,"")
                if val and len(str(val)) > 20:
                    parts.append(str(val))
            # Also use caseName + court as minimal context
            if not parts:
                cn = result.get("caseName","")
                court = result.get("court","")
                if cn:
                    parts.append(f"{cn} ({court})")
            combined = " ".join(parts)
            if len(combined.split()) >= 8:
                texts_collected.append({
                    "text": combined[:500],
                    "case": result.get("caseName",""),
                    "court": result.get("court",""),
                    "date": result.get("dateFiled",""),
                    "query": query
                })
        print(f"  '{query}': {len(data.get('results',[]))} results -> {len([t for t in texts_collected if t['query']==query])} with text")
    except Exception as e:
        print(f"  Error '{query}': {e}")

print(f"\nTotal texts: {len(texts_collected)}")

# Also try fetching full opinion text for a few cases via direct URL
print("\nFetching opinion HTML for 3 cases...")
sample_urls = [
    "https://www.courtlistener.com/opinion/7328472/elec-frontier-found-v-global-equity-mgmt-sa-pty-ltd/",
    "https://www.courtlistener.com/opinion/4571/",
    "https://www.courtlistener.com/opinion/111117/",
]

for url in sample_urls:
    try:
        time.sleep(2)
        r = requests.get(url, timeout=20, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text,"html.parser")
            # Find opinion text div
            opinion_div = soup.find("div", {"id":"opinion-content"}) or soup.find("article")
            if opinion_div:
                text = re.sub(r'\s+',' ', opinion_div.get_text(" ", strip=True))
                # Extract equity sentences
                sents = re.split(r'(?<=[.!?])\s+', text)
                for s in sents:
                    if re.search(r'\bequity\b|\bequitable\b', s, re.I) and len(s.split())>=8:
                        texts_collected.append({
                            "text": s.strip()[:400],
                            "case": url.split("/")[-2],
                            "court": "scraped",
                            "date": "",
                            "query": "html_scrape"
                        })
                print(f"  Scraped {url[-40:]}: {len([t for t in texts_collected if t.get('query')=='html_scrape'])} equity sentences")
    except Exception as e:
        print(f"  Scrape error {url[-30:]}: {e}")

# Deduplicate and compute P
seen, unique = set(), []
for s in texts_collected:
    k = s["text"][:80]
    if k not in seen:
        seen.add(k); unique.append(s)
print(f"\nUnique texts: {len(unique)}")

if len(unique) >= 5:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [s["text"] for s in unique]
    emb = model.encode(texts, batch_size=32, show_progress_bar=False)
    sims = cosine_similarity(emb)
    np.fill_diagonal(sims, np.nan)
    upper = sims[np.triu_indices_from(sims, k=1)]
    P = float(np.nanmean(upper))
    std = float(np.nanstd(upper))
    print(f"\nP(I-2 common law): {P:.4f}  std: {std:.4f}  n={len(texts)}")
    
    pd.DataFrame(unique).to_csv("data/courtlistener_texts.csv", index=False)
    res = {
        "environment": "I-2_legal_common_law",
        "n_texts": len(texts),
        "P_overall": round(P,4),
        "std": round(std,4),
        "source": "CourtListener search API (posture/syllabus fields) + HTML scraping, 5 queries",
        "caveat": "Mixed text fields (posture, syllabus, case names) + some scraped opinion text. N is low."
    }
    with open("results/precision_I2.json","w") as f:
        json.dump(res,f,indent=2)
    print(json.dumps(res,indent=2))
else:
    print(f"\nInsufficient data ({len(unique)} texts). I-2 will be marked PENDING in results.")
    res = {
        "environment": "I-2_legal_common_law",
        "status": "PENDING - requires CourtListener token for opinion text access",
        "note": "Free token available at courtlistener.com/register. Use scripts/10_legal_corpus.py"
    }
    with open("results/precision_I2.json","w") as f:
        json.dump(res,f,indent=2)
