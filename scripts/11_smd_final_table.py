import json, numpy as np, pandas as pd

# Load all computed results
with open("results/precision_I1.json") as f: r1 = json.load(f)
with open("results/precision_I2.json") as f: r2 = json.load(f)
with open("results/precision_I4.json") as f: r4 = json.load(f)
with open("results/precision_I6.json") as f: r6 = json.load(f)

df_ng = pd.read_csv("data/ngrams_raw.csv")

def ng_mean(term, y1, y2):
    sub = df_ng[(df_ng["ngram"]==term) & (df_ng["year"].between(y1,y2))]
    return float(sub["frequency"].mean()) if len(sub) else 0.0

# Normalize F using equity pre-2015 as baseline = 1.0
F_base = ng_mean("equity", 2000, 2014)

def F_norm(term, y1, y2):
    return round(ng_mean(term, y1, y2) / F_base, 4)

print("=" * 65)
print("FINAL COMPUTED SMD TABLE — ALL VALUES FROM REAL DATA")
print("=" * 65)

table = {
    "I-1_Philosophical": {
        "F_pre":  F_norm("equity", 2000, 2014),
        "F_post": F_norm("equity", 2015, 2019),
        "P_pre":  r1["P_pre2015"],
        "P_post": r1["P_post2015"],
        "n": r1["n_sentences"],
        "source": "OpenAlex n=2000; Ngrams",
        "status": "COMPUTED"
    },
    "I-2_Legal_CommonLaw": {
        "F_pre":  F_norm("equity", 2000, 2014),
        "F_post": F_norm("equity", 2015, 2019),
        "P_pre":  None,
        "P_post": None,
        "P_overall": r2.get("P_overall"),
        "n": r2.get("n_texts", r2.get("n_snippets", 0)),
        "source": "CourtListener n=87 texts",
        "status": "COMPUTED (overall P only; pre/post split requires token for full opinions)",
        "caveat": r2.get("caveat","")
    },
    "I-4_Public_Policy": {
        "F_pre":  F_norm("equity", 2000, 2014),
        "F_post": F_norm("equity", 2015, 2019),
        "P_pre":  r4["P_pre2015"],
        "P_post": r4["P_post2015"],
        "n": r4["n"],
        "source": "World Bank Docs n=500; Ngrams",
        "status": "COMPUTED"
    },
    "I-6_Social_Doctrine": {
        "F_pre":  F_norm("social justice", 2000, 2014),
        "F_post": F_norm("social justice", 2015, 2019),
        "P_pre":  None,
        "P_post": None,
        "P_overall": r6["P_overall"],
        "n": r6["n_sentences"],
        "source": "Vatican.va n=13 encyclicals",
        "status": "COMPUTED. KEY FINDING: equity=0 post-1965",
        "key_finding": "Terminological decoupling: I-6 uses 'justice' not 'equity'"
    },
    "I-3_Social_Media": {
        "status": "NOT COMPUTED — no verified corpus",
        "treatment": "Qualitative, paper Section IV.D"
    }
}

# Print table
print(f"\n{'Env':<22} {'F_pre':>7} {'F_post':>7} {'P_pre':>7} {'P_post':>8} {'n':>6}")
print("-"*65)
for env, d in table.items():
    if d.get("status","").startswith("NOT"):
        print(f"{env:<22} {'—':>7} {'—':>7} {'—':>7} {'—':>8} {'—':>6}  [qualitative]")
        continue
    fp  = f"{d.get('F_pre',0):.4f}"
    fpo = f"{d.get('F_post',0):.4f}"
    pp  = f"{d['P_pre']:.4f}" if d.get('P_pre') else f"({d.get('P_overall',0):.4f})"
    ppo = f"{d['P_post']:.4f}" if d.get('P_post') else "—"
    n   = str(d.get("n",""))
    print(f"{env:<22} {fp:>7} {fpo:>7} {pp:>7} {ppo:>8} {n:>6}")

# SMD matrix
def smd(f1,p1,f2,p2):
    if None in [f1,p1,f2,p2]: return None
    return round(np.sqrt((f1-f2)**2 + (p1-p2)**2), 4)

print("\n" + "=" * 65)
print("SMD MATRIX (post-2015 where available, else overall P)")
print("=" * 65)

envs = ["I-1_Philosophical","I-2_Legal_CommonLaw","I-4_Public_Policy","I-6_Social_Doctrine"]

def get_fp(d):
    return d.get("F_post", d.get("F_pre"))

def get_pp(d):
    return d.get("P_post") or d.get("P_overall")

for i, e1 in enumerate(envs):
    for e2 in envs[i+1:]:
        d1, d2 = table[e1], table[e2]
        v = smd(get_fp(d1), get_pp(d1), get_fp(d2), get_pp(d2))
        flag = " [CRITICAL >0.50]" if v and v > 0.50 else ""
        print(f"  SMD({e1[:4]}, {e2[:4]}): {v}{flag}")

# Key Ngrams finding
print("\n" + "=" * 65)
print("KEY NGRAMS FINDING")
print("=" * 65)
print("\n  equity/equality ratio by year:")
eq  = df_ng[df_ng["ngram"]=="equity"].set_index("year")["frequency"]
eql = df_ng[df_ng["ngram"]=="equality"].set_index("year")["frequency"]
ratio = (eq / eql).loc[2000:2019]
for yr, val in ratio.items():
    marker = " <-- INVERSION" if yr == 2013 else ""
    print(f"    {yr}: {val:.3f}{marker}")

with open("results/final_consolidated.json","w") as f:
    # Convert None to null-compatible
    import json
    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.floating): return float(obj)
            return super().default(obj)
    json.dump(table, f, indent=2, cls=NumpyEncoder)
print("\nSaved final_consolidated.json")
