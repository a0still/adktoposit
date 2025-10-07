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

# Ensure documentation directory exists
docs_dir = Path("Shrink_Documentation")
try:
    docs_dir.mkdir(exist_ok=True)
    intro_file = docs_dir / "introduction.md"
    if not intro_file.exists():
        with open(intro_file, "w") as f:
            f.write("# ADK Documentation\n\nThis is the default documentation file.")
except Exception as e:
    print(f"Warning: Could not create documentation directory: {e}")

def server(input: Inputs, output: Outputs, session: Session):
    """Define the server logic"""
    
    # Initialize chat history
    chat_history = reactive.Value([])
    
    # Initialize Vertex AI chat
    llm = ChatVertexAI(
        project=os.getenv("GCP_PROJECT"),
        location=os.getenv("VERTEX_LOCATION"),
        model_name=os.getenv("VERTEX_MODEL"),
    )

    @reactive.Effect
    @reactive.event(input.send)
    def _():
        if not input.user_message():
            return
            
        # Add user message to chat history
        history = chat_history.get()
        history.append({"role": "user", "content": input.user_message()})
        
        try:
            # Get AI response using ADK
            response = llm.invoke([
                SystemMessage(content="You are a helpful AI assistant."),
                HumanMessage(content=input.user_message())
            ])
            
            # Add AI response to chat history
            history.append({"role": "assistant", "content": response.content})
            chat_history.set(history)
            
        except Exception as e:
            # Handle any errors
            history.append({"role": "system", "content": f"Error: {str(e)}"})
            chat_history.set(history)

    @output
    @render.ui
    def chat_history():
        history = chat_history.get()
        chat_elements = []
        
        for msg in history:
            if msg["role"] == "user":
                chat_elements.append(
                    ui.div(
                        ui.markdown(msg["content"]),
                        style="background-color: #e9ecef; padding: 10px; margin: 5px; border-radius: 5px;"
                    )
                )
            elif msg["role"] == "assistant":
                chat_elements.append(
                    ui.div(
                        ui.markdown(msg["content"]),
                        style="background-color: #d4edda; padding: 10px; margin: 5px; border-radius: 5px;"
                    )
                )
            else:  # system messages (errors)
                chat_elements.append(
                    ui.div(
                        ui.markdown(msg["content"]),
                        style="background-color: #f8d7da; padding: 10px; margin: 5px; border-radius: 5px;"
                    )
                )
        
        return ui.div(*chat_elements)

# Create and run the Shiny app
app = App(app_ui, server)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port)