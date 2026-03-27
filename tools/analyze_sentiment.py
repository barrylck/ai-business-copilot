import anthropic
from dotenv import load_dotenv
import json
import re

load_dotenv()
client = anthropic.Anthropic()

def analyze_sentiment(forward_guidance):

    prompt=f"""
You are going to take the forward guidance from a company's management and extract information related to the following aspects. return only in json format. no markdown.

three aspects:
- overall_outlook: is management bullish or bearish about the company's future?
- growth_confidence : how confident are they about hitting their growth targets?
- risk_acknowledgment: how much are they flagging risks vs downplaying them?

for each aspect, output the following information:
-score: rating from 1-5, 5 being the highest/most positive, as a number
-label: one of "very negative" / "cautious" / "neutral" / "positive" / "very positive",  as a string
- quote: relevant quote from the forward guidance that support your scoring and labelling, as a string

the forward guidance is as follow:
    {forward_guidance}"""

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
        "overall_outlook": None,
        "growth_confidence": None,
        "risk_acknowledgment": None,
        "parse_error": raw_text
    }

    return result