
import json
import plotly.express as px
import pandas as pd
from langchain.tools import tool

@tool
def create_chart(data_json: str, chart_type: str = "line", x_col: str = "x", y_col: str = "y", title: str = "Chart") -> str:
    """
    Creates a dynamic chart from data.
    Args:
        data_json: A JSON string representing a list of records (e.g. '[{"Date": "2023-01", "Price": 100}, ...]')
        chart_type: Type of chart: "line", "bar", "scatter", "pie".
        x_col: Name of the column for X axis.
        y_col: Name of the column for Y axis (or value for pie).
        title: Title of the chart.
    Returns:
        A formatted string containing a hidden JSON payload that the frontend will render as a chart.
    """
    try:
        # Validate JSON
        data = json.loads(data_json)
        
        # Support Columnar Dict Input (e.g. {"cities": ["A", "B"], "vals": [10, 20]})
        if isinstance(data, dict):
            # Convert to List of Records
            keys = list(data.keys())
            if not keys:
                 return "Error: Empty data dictionary."
            
            length = len(data[keys[0]])
            new_data = []
            for i in range(length):
                record = {}
                for k in keys:
                    # Robustness: ensure lists are equal length, else truncate/pad
                    if i < len(data[k]):
                        record[k] = data[k][i]
                new_data.append(record)
            data = new_data

        if not isinstance(data, list):
            return "Error: data_json must be a list of dictionaries or a columnar dictionary."
        
        # We construct a payload for the frontend
        payload = {
            "type": chart_type,
            "data": data,
            "x": x_col,
            "y": y_col,
            "title": title
        }
        
        # We return this as a special comment block that `streamlit_app.py` detects.
        # This is consistent with our Stock Chart implementation.
        # Format: <!-- CHART_TOOL_JSON: {...} -->
        return f"Chart Created: {title}\n<!-- CHART_TOOL_JSON: {json.dumps(payload)} -->"

    except Exception as e:
        return f"Failed to create chart: {str(e)}"
