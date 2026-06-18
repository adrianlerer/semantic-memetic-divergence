import requests, re, pandas as pd, time
from bs4 import BeautifulSoup

# Known encyclicals and apostolic exhortations with direct Vatican URLs
# These are verified public documents
DOCS = [
    ("Rerum Novarum", 1891, "https://www.vatican.va/content/leo-xiii/en/encyclicals/documents/hf_l-xiii_enc_15051891_rerum-novarum.html"),
    ("Quadragesimo Anno", 1931, "https://www.vatican.va/content/pius-xi/en/encyclicals/documents/hf_p-xi_enc_19310515_quadragesimo-anno.html"),
    ("Mater et Magistra", 1961, "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_15051961_mater.html"),
    ("Pacem in Terris", 1963, "https://www.vatican.va/content/john-xxiii/en/encyclicals/documents/hf_j-xxiii_enc_11041963_pacem.html"),
    ("Gaudium et Spes", 1965, "https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19651207_gaudium-et-spes_en.html"),
    ("Populorum Progressio", 1967, "https://www.vatican.va/content/paul-vi/en/encyclicals/documents/hf_p-vi_enc_26031967_populorum.html"),
    ("Laborem Exercens", 1981, "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_14091981_laborem-exercens.html"),
    ("Sollicitudo Rei Socialis", 1987, "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_30121987_sollicitudo-rei-socialis.html"),
    ("Centesimus Annus", 1991, "https://www.vatican.va/content/john-paul-ii/en/encyclicals/documents/hf_jp-ii_enc_01051991_centesimus-annus.html"),
    ("Caritas in Veritate", 2009, "https://www.vatican.va/content/benedict-xvi/en/encyclicals/documents/hf_ben-xvi_enc_20090629_caritas-in-veritate.html"),
    ("Laudato Si", 2015, "https://www.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20150524_enciclica-laudato-si.html"),
    ("Laudate Deum", 2023, "https://www.vatican.va/content/francesco/en/apost_exhortations/documents/20231004-laudate-deum.html"),
    ("Evangelii Gaudium", 2013, "https://www.vatican.va/content/francesco/en/apost_exhortations/documents/papa-francesco_esortazione-ap_20131124_evangelii-gaudium.html"),
]

rows = []
headers = {"User-Agent": "Mozilla/5.0 (academic research)"}

for title, year, url in DOCS:
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        # Remove nav/header/footer
        for tag in soup(["nav","header","footer","script","style"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text)
        # Count equity/justice terms
        n_equity   = len(re.findall(r'\bequity\b', text, re.I))
        n_justice  = len(re.findall(r'\bjustice\b', text, re.I))
        n_equality = len(re.findall(r'\bequality\b', text, re.I))
        n_words    = len(text.split())
        rows.append({
            "title": title, "year": year, "url": url,
            "n_words": n_words,
            "n_equity": n_equity, "n_justice": n_justice,
            "n_equality": n_equality,
            "text": text[:3000]  # first 3000 chars for embedding
        })
        print(f"  OK: {title} ({year}) | words:{n_words} | equity:{n_equity} | justice:{n_justice}")
        time.sleep(1)
    except Exception as e:
        print(f"  FAIL: {title}: {e}")

df = pd.DataFrame(rows)
df.to_csv("data/vatican_corpus.csv", index=False)
print(f"\nSaved {len(df)} documents to vatican_corpus.csv")

print("\n--- Term frequencies ---")
print(df[["title","year","n_equity","n_justice","n_equality","n_words"]].to_string(index=False))
