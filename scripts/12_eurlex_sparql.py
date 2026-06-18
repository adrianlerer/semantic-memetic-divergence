"""
EUR-Lex SPARQL query for equity/equite in CJEU decisions.
Endpoint: https://publications.europa.eu/webapi/rdf/sparql
Status: included for community extension; not yet executed by author.
"""
import requests

SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

query = """
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?doc ?title ?date
WHERE {
  ?doc a cdm:judgment ;
       cdm:work_date_document ?date ;
       cdm:work_title ?title .
  FILTER(CONTAINS(LCASE(STR(?title)), "equity") ||
         CONTAINS(LCASE(STR(?title)), "equite"))
}
ORDER BY DESC(?date)
LIMIT 200
"""

headers = {"Accept": "application/sparql-results+json"}
r = requests.post(SPARQL_ENDPOINT, data={"query": query}, headers=headers, timeout=60)
print(f"Status: {r.status_code}")
if r.ok:
    data = r.json()
    results = data.get("results",{}).get("bindings",[])
    print(f"Results: {len(results)}")
    for row in results[:5]:
        print(row)
