import argparse
import json

import requests

parser = argparse.ArgumentParser(description="Query a zoekt-webserver instance")
parser.add_argument("query", help="search query, for example myFunction")
parser.add_argument("--url", default="http://127.0.0.1:6070/search", help="zoekt search endpoint")
parser.add_argument("--num", default=10, type=int, help="max number of results, default 10")
parser.add_argument("--ctx", type=int, help="number of context lines")
args = parser.parse_args()

params = {"q": args.query, "format": "json"}
if args.num is not None:
    params["num"] = args.num
if args.ctx is not None:
    params["ctx"] = args.ctx

resp = requests.get(args.url, params=params)
resp.raise_for_status()
print(json.dumps(resp.json(), indent=2))
