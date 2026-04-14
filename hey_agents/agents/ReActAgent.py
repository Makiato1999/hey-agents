# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

请严格按照以下格式进行回应:

Thought: 你的思考过程，用于分析问题、拆解任务和规划下一步行动。
Action: 你决定采取的行动，必须是以下格式之一:
- `{{tool_name}}[{{tool_input}}]`:调用一个可用工具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到足够的信息，能够回答用户的最终问题时，你必须在Action:字段后使用 Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""

from hey_agents.core.llm_client import HeyAgentsLLM
from hey_agents.tools import ToolExecutor
from typing import Dict, List, Any

class ReActAgent:
    def __init__(self, llm_client: HeyAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
      self.llm_client = llm_client
      self.tool_executor = tool_executor
      self.max_steps = max_steps
      self.history = []
      
    def run(self, question: str):
      """
      Run the ReAct agent to answer a question.
      """
      self.history = [] # Reset on restart
      step = 0
      
      while step < self.max_steps:
        step += 1
        print(f"--- The {step}th step ---")
        
        tools_desc = self.tool_executor.getAvailableTools()
        history_str = "\n".join(self.history)
        prompt = REACT_PROMPT_TEMPLATE.format(
          tools = tools_desc,
          question = question,
          history = history_str
        )
        
        messages = [{"role": "user", "content": prompt}]
        response_text = self.llm_client.think(messages=messages)
        
        if not response_text:
          print("Error: The LLM failed to return a valid response.")
          break
        
        # ...
        
      def _parse_output(self, text: str):
        """
        Analyze the LLM's output to extract thoughts and actions.
        """
        
        