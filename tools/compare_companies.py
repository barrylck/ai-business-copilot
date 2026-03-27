import anthropic
import json
from dotenv import load_dotenv
import re

load_dotenv()
client = anthropic.Anthropic()

def compare_companies(extract_financials_dict):

    prompt=f'''
you are given a dictionary of extracted financial data of 2 or more companies. compare them on the following aspect:

aspects:
- profitability: net income/revenue, as a number
- asset_utilization: revenue/asset, as a number
- asset_multiplier: asset/shareholder equity, as a number

for each of these aspect, also provide a commentary for the better performing company based on your knowledge and reasoning, as a string

your return format should be in json format, no markdown.

if you can't find data for relevant field, set value to null.

the relevant extracted financial data has been aranged by company name as follows:{extract_financials_dict}'''
    
    response = client.messages.create(
        model = "claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role":"user","content":prompt}])
    
    raw_text = response.content[0].text
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        return{
            "profitability": None,
            "asset_utilization":None,
            "asset_multiplier":None,
            "commentary":None
        }
    