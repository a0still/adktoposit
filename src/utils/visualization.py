"""Data handling utilities for the application."""
import pandas as pd
import plotly.express as px
from typing import Dict, Any, Optional

def create_visualization(
    data: pd.DataFrame,
    viz_type: str,
    x_column: Optional[str] = None,
    y_column: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a visualization from the provided data.
    
    Args:
        data: DataFrame containing the data to visualize
        viz_type: Type of visualization ('table', 'line', 'bar', 'scatter')
        x_column: Column to use for x-axis (optional)
        y_column: Column to use for y-axis (optional)
        title: Title for the visualization (optional)
    
    Returns:
        Dict containing the visualization HTML and metadata
    """
    try:
        if viz_type == "table":
            return {
                "type": "table",
                "html": data.to_html(classes="table table-striped", index=False),
                "success": True
            }
        
        if not x_column or not y_column:
            return {
                "type": viz_type,
                "error": "X and Y columns are required for this visualization type",
                "success": False
            }
        
        if viz_type in ["line", "bar", "scatter"]:
            fig = getattr(px, viz_type)(
                data,
                x=x_column,
                y=y_column,
                title=title
            )
            return {
                "type": viz_type,
                "html": fig.to_html(full_html=False),
                "success": True
            }
        
        return {
            "type": "error",
            "error": f"Unsupported visualization type: {viz_type}",
            "success": False
        }
        
    except Exception as e:
        return {
            "type": "error",
            "error": str(e),
            "success": False
        }