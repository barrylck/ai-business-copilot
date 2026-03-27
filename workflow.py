from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal
import sys
import os
import json

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), "tools"))

from extract_financials import extract_financials
from analyze_sentiment import analyze_sentiment
from compare_companies import compare_companies
from generate_executive_summary import generate_executive_summary


class State(TypedDict):
    file_paths: list[str]
    extracted_data: list[dict]
    sentiment_data: list[dict]
    comparison: list[dict]
    summary: str


def extract_node(state: State):
    results = []
    for path in state["file_paths"]:
        results.append(extract_financials(path))
    return {"extracted_data": results}


def sentiment_node(state: State):
    results = []
    for data in state["extracted_data"]:
        result = analyze_sentiment(data["forward_guidance"])
        result["source_file"] = data["source_file"]
        results.append(result)
    return {"sentiment_data": results}


def compare_node(state: State):
    all_companies = {data["source_file"]: data for data in state["extracted_data"]}
    result = compare_companies(all_companies)
    return {"comparison": [result]}


def summary_node(state: State):
    result = generate_executive_summary(
        state["extracted_data"],
        state["sentiment_data"],
        state["comparison"],
    )
    return {"summary": result}


def route_comparison(state: State) -> Literal["compare_node", "summary_node"]:
    if len(state["file_paths"]) > 1:
        return "compare_node"
    return "summary_node"


builder = StateGraph(State)
builder.add_node("extract_node", extract_node)
builder.add_node("sentiment_node", sentiment_node)
builder.add_node("compare_node", compare_node)
builder.add_node("summary_node", summary_node)
builder.add_edge(START, "extract_node")
builder.add_edge("extract_node", "sentiment_node")
builder.add_conditional_edges("sentiment_node", route_comparison)
builder.add_edge("compare_node", "summary_node")
builder.add_edge("summary_node", END)

graph = builder.compile()


def run_analysis(file_paths: list[str]) -> dict:
    return graph.invoke({
        "file_paths": file_paths,
        "extracted_data": [],
        "sentiment_data": [],
        "comparison": [],
        "summary": "",
    })


if __name__ == "__main__":
    import glob
    paths = glob.glob("documents/*.pdf")
    result = run_analysis(paths)
    print(json.dumps(result, indent=2, ensure_ascii=False))