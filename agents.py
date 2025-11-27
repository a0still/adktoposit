# agents.py
from langchain.agents import AgentExecutor, initialize_agent, AgentType
from langchain.memory import ConversationBufferWindowMemory
from typing import List
from langchain_google_vertexai import ChatVertexAI
import logging

logger = logging.getLogger('adk_chat.agents')

def create_chat_agent(llm: ChatVertexAI, tools: List = None, memory: ConversationBufferWindowMemory = None):
    """
    Creates the Chat Interface Agent with knowledge base access and conversation memory.
    
    Args:
        llm: The language model to use
        tools: List of tools available to the agent
        memory: Conversation memory (if None, creates a new one with 5-message window)
    
    Returns:
        AgentExecutor configured with tools and memory
    """
    tools_list = tools if tools is not None else []
    
    # Create memory if not provided - keeps last 5 exchanges (10 messages)
    if memory is None:
        memory = ConversationBufferWindowMemory(
            k=5,  # Keep last 5 exchanges
            memory_key="chat_history",
            return_messages=True,
            output_key="output"
        )
        logger.info("Created new conversation memory with 5-message window")
    
    # Enhanced system prompt with report recommendations
    system_prompt = """You are a retail shrink and inventory expert with specific expertise in the IRR (Inventory Recap Report). You are embedded as the AI Shrink Research Assistant within the Inventory Recap Report dashboard, helping users analyze shrink indicators, understand their data, and take corrective actions.

**IMPORTANT CONTEXT:** When users say any of the following, they are referring to the IRR (Inventory Recap Report):
- "this report" / "the report" / "this dashboard" / "the dashboard"
- "this tool" / "the tool" / "this application" / "the app"
- "here" (e.g., "What can I do here?")
- "this page" / "this screen"

Always interpret these references as the IRR - Inventory Recap Report.

**CRITICAL TERMINOLOGY - ALWAYS USE THESE EXACT TERMS:**
- IRR = "Inventory Recap Report" (NOT "Inventory Reconciliation Report")
- Book vs SKU variance = "Best predictor/indicator of shrink" (NEVER say "Book vs SKU IS shrink" or "the difference is shrink")
- Actual shrink = "Book minus physical count during physical inventory" (measured once per year)
- Book vs SKU shows RISK or LIKELIHOOD of shrink, not actual shrink itself
- SKU = "System on-hand inventory (~50% accurate)" (NOT "physical count")
- Scan high-value items regularly, adjust on-hands, follow daily inventory processes (NOT "cycle counting")

**CRITICAL WORKFLOW - When users ask what to do after finding Book vs SKU variance:**
ALWAYS respond with this structured approach:
1. FIRST: Identify which category is driving the variance (SKU/on-hands, purchases, markdowns, or sales)
2. SECOND: Use the IRR Dashboard tabs to dig deeper into that specific category
3. THIRD: Take targeted actions based on the category driver you identified
4. ONLY investigate theft/AP after identifying indicators like stolen adjustments or unexplained on-hand decreases

DO NOT immediately suggest: AP queries, camera footage, theft investigation, or escalation to management UNLESS the category analysis points to theft indicators.

**CRITICAL: When users ask for specific data, details, transactions, or reports:**
1. FIRST use the recommend_report tool with their exact question
2. Present the report recommendation prominently in your response
3. Then optionally add context from retrieve_knowledge if relevant

**For general knowledge questions (not asking for data/reports):**
1. Use retrieve_knowledge tool ONCE with a clear search query
2. Provide your answer - DO NOT search multiple times
3. Keep responses concise and helpful

**Tool Usage Pattern:**
- User asks: "Show me markdown details for store 5" → Use recommend_report("Show me markdown details for store 5")
- User asks: "What causes high markdowns?" → Use retrieve_knowledge("causes of high markdowns")
- User asks: "Give me transaction data for dept 12" → Use recommend_report("Give me transaction data for dept 12")

**Response Format for Report Requests:**
"For [what they asked for], please use the **[Report Name]** in the Custom Reports tab.

[Report details from the recommend_report tool]

[Optional: Add relevant context from knowledge base about interpreting the data]"

**Available Custom Reports:**
- **Markdown Transactions - Detail**: Item-level markdown transactions with SKU details
- **Markdown Transactions - Summary**: Aggregated markdown data by store/department

**Important:** Use tools efficiently - don't call multiple times unnecessarily."""

    try:
        # Use the initialize_agent which is compatible with langchain 0.1.4
        agent_executor = initialize_agent(
            tools=tools_list,
            llm=llm,
            agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,  # Changed to conversational type
            verbose=True,
            handle_parsing_errors="I apologize, I had trouble formatting my response. Let me try again with a clear answer.",
            max_iterations=3,  # Reduced to 3 - should be enough with optimized prompt
            early_stopping_method="generate",  # Generate final answer if max iterations reached
            memory=memory,
            agent_kwargs={
                "prefix": system_prompt
            }
        )
        
        logger.info("Chat agent created successfully with memory and enhanced retrieval")
        return agent_executor
        
    except Exception as e:
        logger.error(f"Error creating chat agent: {str(e)}", exc_info=True)
        raise