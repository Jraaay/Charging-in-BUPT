import json

CONFIG = {}

with open('./chargingInBupt/config.json', 'r') as f:
    CONFIG = json.load(f)