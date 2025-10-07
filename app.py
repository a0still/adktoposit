# app.py
import os
import sys
from pathlib import Path
from typing import List
import dotenv
from shiny import App, reactive, render, ui, Inputs, Outputs, Session
from shinywidgets import output_widget, render_plotly
from google.cloud import bigquery
from markdown2 import markdown
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from crewai import Agent, Task, Crew, Process
from agents import create_data_fetcher_agent, create_financial_analyst_agent
from tools import retrieve_training_docs
from ui import app_ui

# Load environment variables
dotenv.load_dotenv()

def server(input: Inputs, output: Outputs, session: Session):
    """Define the server logic"""
    
    @output
    @render.text
    def txt():
        return "Hello from Shiny!"

# Create and run the Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)