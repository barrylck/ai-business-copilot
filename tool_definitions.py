
tools = [
    {
        "name":"extract_financials",
        "description":"extracts financial data from company's financial report",
        "input_schema":{
            "type":"object",
            "properties":{
                "document":{
                    "type":"string",
                    "description":"this is the document that you need to read"
                }
            },
            "required":["document"]
        }
    },
    {
        "name":"analyze_sentiment",
        "description":"takes management commentary, classify tones, and rate sentiment scores",
        "input_schema":{
            "type":"object",
            "properties":{
                "commentary":{
                    "type":"string",
                    "description":"this is the management commentary"
                }
            },
            "required":["commentary"]
            
        }
    },
    {
        "name":"compare_companies",
        "description":"takes extracted data from two or more companies and produce side by side comparison",
        "input_schema":{
            "type":"object",
            "properties":{
                "extracted_data":{
                    "type":"array",
                    "description":"these are extracted financial data of the relevant companies"
                }
            },
            "required":["extracted_data"]
        }
    },
    {
        "name":"generate_executive_summary",
        "description":"takes all analysis results and write one-page summary",
        "input_schema":{
            "type":"object",
            "properties":{
                "analysis_data":{
                    "type":"object",
                    "description":"all extracted financial and sentiment analysis results"
                }
            },
            "required":["analysis_data"]
        }
    },
    {
        "name":"search_context",
        "description":"lightweight RAG retreival from uploaded documents for follow-up questions",
        "input_schema":{
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":"the user's follow-up question to search for in the documents"
                }
            },
            "required":["query"]
        }
    }
]