from agentz.utils.cvss import HEADERS, NVD_API_URL
import requests
import json

cve_id = "CVE-2021-44228"
params = {"cveId": cve_id}
response = requests.get(NVD_API_URL, headers=HEADERS, params=params)
data = response.json()

print(json.dumps(data["vulnerabilities"][0], indent=2))

