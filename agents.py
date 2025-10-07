# agents.py
from crewai import Agent
from langchain_core.tools import BaseTool
from typing import List
from langchain_google_vertexai import ChatVertexAI

def create_data_fetcher_agent(llm: ChatVertexAI, tools: List[BaseTool]) -> Agent:
    """Creates the Data Fetcher Agent."""
    return Agent(
        role='Financial Data Fetcher',
        goal='Retrieve specific financial datasets for analysis.',
        backstory=(
            "You are an efficient bot specialized in checking the work of others"
        ),
        tools=tools,
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )

def create_financial_analyst_agent(llm: ChatVertexAI) -> Agent:
    """Creates the Financial Analyst Agent."""
    return Agent(
        role='Financial Data Analyst',
        goal='Analyze fetched financial data to identify key issues and insights.',
        backstory=(
            "You are an AI assistant tasked with polishing data into a nicely formatted report output."
        ),
        tools=[],
        llm=llm,
        verbose=True,
        allow_delegation=True,
    )