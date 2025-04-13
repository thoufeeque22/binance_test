import datetime
import os
from binance.client import Client
from dotenv import load_dotenv
import pandas as pd

load_dotenv()   # read file from local .env
api_key = os.environ["BINANCE_API_KEY"]
# api_secret = os.environ["BINANCE_API_SECRET_TEST"]
# client = Client(api_key,
#                 # api_secret,
#                 testnet=True)
# print(client.ping())    # Empty response means no errors
# res = client.get_server_time()
# print(res)
# ts = datetime.datetime.fromtimestamp(res["serverTime"] / 1000)
# print(ts)
# tickers = client.get_all_tickers()
# df = pd.DataFrame(tickers)
# print(df.head())

import requests
import json

url = "https://api1.binance.com"
api_call = "/api/v3/ticker/price"
headers = {"content-type": "application/json", "X-MBX-APIKEY": api_key}
response = requests.get(f"{url}{api_call}").json()
df = pd.DataFrame.from_records(response)
print(df.head())
