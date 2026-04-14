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
            # Hint!
            # 
            # in -> 最标准的“检查 key”, 对应 Java 就是containsKey
            # 
            # .get -> 关心这个 key 对应的值有没有内容
            # key 不存在 → False
            # key 存在但 value 是空列表 / None / 空字符串 → False
            # key 存在且 value 有内容 → True
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
            # Hint!
            # 
            # extend -> 把一个 list 里的元素逐个加入另一个 list，而不是把整个 list 当成一个元素塞进去。
            # Python 里最常见的“扁平化列表”处理
        else:
            output.append(item)
    
    if not output:
        return "Sorry, no info was found."
    else:
        return "\n\n".join(output)
        # Hint!
        # 
        # 先用 list 收集，再 join, 这在 Python 里更常见，也更干净
    
    
class ToolExecutor:
    """
    A tool executor responsible for managing and executing tools.
    """
    def __init__(self):
      self.tools: dict[str, dict[str, Any]] = {}
      
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
            # Hint!
            # .items() -> 遍历字典时同时获取键和值
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
