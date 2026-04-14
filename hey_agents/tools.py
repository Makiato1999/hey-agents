import os
import serpapi
from typing import List, Dict, Callable, Any
from dotenv import load_dotenv

load_dotenv()

def search(query: str) -> str:
    """
    A practical web search engine tool based on SerpApi.
    It intelligently parses search results, prioritizing direct answers or knowledge graph information.
    """
    try:
        print(f"Running [SerpApi] web search: {query}")
        
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "Error: SERPAPI_API_KEY is not configured in the .env file."
        
        client = serpapi.Client(api_key=api_key)
        results = client.search({
            "engine": "google",
            "q": query,
            # "location": "Toronto, Ontario, Canada",
            "google_domain": "google.com",
            "hl": "en",
            "gl": "ca"
        })
        outputs = []
        if "ai_overview" in results and "snippet" in results["ai_overview"]:
            outputs.append(results["ai_overview"]["snippet"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            outputs.append(results["answer_box"]["answer"])
        if "news_results" in results and results["news_results"]:
            snippets = []
            for i, res in enumerate(results["news_results"][:3]):
                snippets.append(f"{i+1} {res['title']}\n{res['source']}\n{res['link']}\n{res['snippet']}")
            outputs.append(snippets)
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            outputs.append(results["knowledge_graph"]["description"])
        if "organic_results" in results and results["organic_results"]:
            snippets = []
            for i, res in enumerate(results["organic_results"][:3]):
                snippets.append(f"{i+1} {res['title']}\n{res['snippet']}")
            outputs.append(snippets)
        
        return format_output(outputs)
    except Exception as e:
        return f"An error occurred during the search: {e}."
    
def format_output(outputs) -> str:
    output = []
    for item in outputs:
        if isinstance(item, list):
            output.extend(item)
        else:
            output.append(item)
    
    if not output:
        return "Sorry, no info was found."
    else:
        return "\n\n".join(output)
    
    
class ToolExecutor:
    """
    A tool executor responsible for managing and executing tools.
    """
    def __init__(self):
      self.tools: Dict[str, Dict[str, Any]] = {}
      
    def registerTool(self, name: str, description: str, func: Callable):
        """
        Register a new tool in the toolbox.
        """
        if name in self.tools:
            print(f"Warning: The tool ‘{name}’ already exists and will be overwritten.")
        self.tools[name] = {
            "description": description,
            "func": func
        }
        print(f"Tool '{name}' has already been registered.'")
    
    def getTool(self, name: str) -> Callable:
        """
        Retrieve a tool's execution function by name.
        """
        return self.tools.get(name, {}).get("func")
    
    def getAvailableTools(self) -> str:
        """
        Retrieve formatted description strings for all available tools.
        """
        res = []
        for name, details in self.tools.items():
            res.append("\n".join([f"- {name}: {details['description']}"]))
        return "\n".join(res)    
    
    
if __name__ == '__main__':
    toolExecutor = ToolExecutor()
    
    search_tool_description = "A web search engine. Use this tool when you need answers to questions about current events, facts, or information you can't find in your knowledge base."
    
    toolExecutor.registerTool(name="Search", description=search_tool_description, func=search)
    
    print("\n--- Available tools ---")
    print(toolExecutor.getAvailableTools())
    
    print("\n--- Execute Action: Search[‘What is NVIDIA's latest GPU model?’] ---")
    tool_name = "Search"
    tool_input = "What is NVIDIA's latest GPU model?"
    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- Observation ---")
        print(observation)
    else:
        print(f"Error: The tool named '{tool_name}' was not found.")
