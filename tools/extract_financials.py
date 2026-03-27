import anthropic
import pypdf
from dotenv import load_dotenv
import re
import json

load_dotenv()
client = anthropic.Anthropic()

def extract_financials(document):

    with open(document,"rb") as pdf:
        reader=pypdf.PdfReader(pdf)
        text = ""
        for page in reader.pages[2:40]:
            text+=page.extract_text()

    prompt = f"""
Read the transcript and extract the following information for commercial and financial due diligence work use. Return ONLY a JSON object with exactly these fields, No markdown, no backticks.

Fields:
- asset: total asset in million USD as a number
- revenue: total revenue in million USD as a number (e.g. 30000.0 )
- revenue_growth: year over year revenue growth as a percentage (e.g. 10.0)
- net_income: net income in million USD as a number
- shareholder_equity: as a number
- forward_guidance: management discussion and guidance as a string
- key_risks: list of top 10 risks strings
- competitive_mentions: list of competitor names mentioned

If a field cannot be found, set it to null.

Transcript:
{text}"""
    
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2048,
        messages=[{"role":"user","content":prompt}]
    )

    raw_text = response.content[0].text
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    try:
        result = json.loads(raw_text)
    except json.JSONDecodeError:
        result = {
            "asset": None,
            "revenue": None,
            "revenue_growth": None,
            "net_income": None,
            "shareholder_equity": None,
            "forward_guidance": None,
            "key_risks": [],
            "competitive_mentions": [],
            "parse_error": raw_text
        }
    
    result["source_file"] = document
    return result

