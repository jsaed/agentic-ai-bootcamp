import os
import argparse
import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ibm import WatsonxLLM
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods
from langchain_community.tools.tavily_search import TavilySearchResults

from dotenv import load_dotenv

# Load environment variables from a .env file if available
load_dotenv()

# Fetch Watsonx credentials
WATSONX_URL = os.getenv("WATSONX_URL")
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")

print(WATSONX_URL)

# Debugging: Print error if any are missing
if not WATSONX_URL or not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
    raise ValueError("Missing Watsonx credentials. Please set WATSONX_URL, WATSONX_API_KEY, and WATSONX_PROJECT_ID.")

# Initialize Tavily search with API key
#tavily_search = TavilySearchResults(max_results=5, tavily_api_key="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")
tavily_search = TavilySearchResults(max_results=5, tavily_api_key=os.getenv("TAVILY_API_KEY"))

# Define the Internet Researcher Agent
class InternetResearcherAgent:
    """Agent that researches current market trends based on shelf description."""
    
    def __init__(self):
        self.llm = WatsonxLLM(
            model_id="mistralai/mistral-large",
            url=WATSONX_URL,
            apikey=WATSONX_API_KEY,
            project_id=WATSONX_PROJECT_ID,
            params={
                GenParams.TEMPERATURE: 0.5,
                GenParams.MAX_NEW_TOKENS: 1000
            }
        )
    
    def __call__(self, state):
        search_queries = [
            f"current retail trends for {state['shelf_description']}",
            f"popular products in {state['shelf_description']} category 2025"
        ]
        research_results = []
        for query in search_queries:
            try:
                results = tavily_search.run(query)
                research_results.append({"query": query, "results": results})
            except Exception as e:
                research_results.append({"query": query, "error": str(e)})
        
        human_message = HumanMessage(
            content=f"""Shelf description: {state['shelf_description']}\n\nSearch results: {research_results}\n\nProvide detailed market trends, industry insights, and competitor analysis."""
        )
        market_trends_response = self.llm.invoke([human_message])
        
        human_message_recommendations = HumanMessage(
            content=f"""Shelf description: {state['shelf_description']}\n\nMarket trends: {market_trends_response}\n\nBased on these insights, provide clear and actionable strategic recommendations to optimize product visibility, sales, and brand positioning."""
        )
        recommendations_response = self.llm.invoke([human_message_recommendations])
        
        # Return updated state
        new_state = state.copy()
        new_state["market_trends"] = market_trends_response
        new_state["recommendations"] = recommendations_response
        
        return new_state

# Define the Market Analyst Agent
class MarketAnalystAgent:
    """Agent that creates an action plan based on recommendations."""
    
    def __init__(self):
        self.llm = WatsonxLLM(
            model_id="mistralai/mistral-large",
            url=WATSONX_URL,
            apikey=WATSONX_API_KEY,
            project_id=WATSONX_PROJECT_ID,
            params={
                GenParams.TEMPERATURE: 0.3,
                GenParams.MAX_NEW_TOKENS: 1500
            }
        )
    
    def __call__(self, state):
        human_message = HumanMessage(
            content=f"""Shelf description: {state['shelf_description']}\nMarket Trends: {state['market_trends']}\nRecommendations: {state['recommendations']}\n\nCreate a detailed and structured action plan, including key objectives, execution steps, timeline, and measurable success indicators."""
        )
        action_plan_response = self.llm.invoke([human_message])
        
        # Return updated state
        new_state = state.copy()
        new_state["action_plan"] = action_plan_response
        
        return new_state

# Define workflow graph
def create_shelf_analysis_graph():
    workflow = StateGraph(dict)
    
    # Initialize agents
    researcher = InternetResearcherAgent()
    analyst = MarketAnalystAgent()
    
    # Add nodes
    workflow.add_node("researcher", researcher)
    workflow.add_node("analyst", analyst)
    
    # Add edges
    workflow.add_edge("researcher", "analyst")
    workflow.add_edge("analyst", END)
    
    # Set entry point
    workflow.set_entry_point("researcher")
    
    return workflow.compile()

# Main function to run the analysis
def analyze_shelf(shelf_description):
    graph = create_shelf_analysis_graph()
    initial_state = {
        "shelf_description": shelf_description,
        "market_trends": None,
        "recommendations": None,
        "action_plan": None
    }
    
    # Use the run method instead of stream for simplicity
    try:
        final_state = graph.invoke(initial_state)
        return json.dumps(final_state, indent=4)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=4)

# Command-line execution
def parse_args():
    parser = argparse.ArgumentParser(description="Analyze store shelf and provide recommendations")
    parser.add_argument("--user-prompt", type=str, required=True, help="Description of the store shelf")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    shelf_description = args.user_prompt
    print(analyze_shelf(shelf_description))

