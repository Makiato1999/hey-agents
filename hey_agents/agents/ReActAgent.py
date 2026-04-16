"""
Deprecated version
"""

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

import re
from hey_agents.core.llm import HeyAgentsLLM
from hey_agents.tools import ToolExecutor, search
from typing import Dict, List, Any


class ReActAgent:
    def __init__(
        self, llm_client: HeyAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5
    ):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        """
        Run the ReAct agent to answer a question.
        """
        self.history = []  # Reset on restart
        step = 0

        while step < self.max_steps:
            step += 1
            print(f"--- The {step}th step ---")

            # 1. Format the prompt
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=tools_desc, question=question, history=history_str
            )

            # 2. Call LLM to generate thought
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("Error: The LLM failed to return a valid response.")
                break

            # 3. Parse LLM Output
            thought, action = self._parse_output(response_text)

            if thought:
                print(f"thought: {thought}")
            if not action:
                print(
                    "Warning: An invalid action was detected. The process has been terminated."
                )
                break

            # 4. Execute Action
            if action.startswith("Finish"):
                # If the command is “Finish,” extract the final answer and exit
                # 判断字符串 action 是否以 "Finish" 开头
                final_answer = self._parse_action_input(action)
                print(f"The final answer: {final_answer}")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # ... Handling invalid Action formats ...
                self.history.append("Observation: Invalid Action format. Please check.")
                continue

            print(f"Action: {tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"Error: The tool named '{tool_name}' was not found."
            else:
                observation = tool_function(tool_input)

            print(f"Observation: {observation}")

            # Add this round's Action and Observation to the history
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        # Finish loop
        print(
            "The maximum number of steps has been reached. The process has terminated."
        )
        return None

    def _parse_output(self, text: str):
        """
        Analyze the LLM's output to extract thoughts and actions.
        """
        # Thought: Matches Action: or the end of the text
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)

        # Action: Match to the end of the text
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)

        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None

        return thought, action

    def _parse_action(self, action_text: str):
        """
        Parse the Action string to extract the tool name and input.
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _parse_action_input(self, action_text: str):
        match = re.match(r"\w+\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1)
        else:
            return ""

if __name__ == '__main__':
  llm_client = HeyAgentsLLM()
  tool_executor = ToolExecutor()
  search_desc = "A web search engine. Use this tool when you need answers to questions about current events, facts, or information you can't find in your knowledge base."
  tool_executor.registerTool(name="Search", description=search_desc, func=search)
  agent = ReActAgent(llm_client=llm_client, tool_executor=tool_executor, max_steps=5)
  question = "What is Apple's latest smartphone? What are its main selling points?"
  agent.run(question)
