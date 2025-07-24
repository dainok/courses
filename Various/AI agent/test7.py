#!/usr/bin/env python3
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
# from autogen.agentchat.contrib.capabilities.teachability import Teachability
import asyncio
import pprint
"""
activate the proxy
litellm --model ollama/deepseek-llm:latest --host 127.0.0.1
"""

model = "ollama/deepseek-llm:latest"
litellm_url = "http://127.0.0.1:4000"
model_client = OpenAIChatCompletionClient(
    model=model,
    api_key="unused", # Ignored but required
    base_url=litellm_url,
    model_capabilities={
        "json_output": False,
        "vision": False,
        "function_calling": True,
    },
)

# https://medium.com/@shmilysyg/getting-started-with-autogen-ai-agentic-design-patterns-1-3-766edac03758
# https://medium.com/@shmilysyg/understanding-different-types-of-agents-in-autogen-41ddb987ed54
# https://medium.com/@sadiqgpasha89/autogen-easy-way-to-build-multi-conversational-agents-part-3-0d34a77fbfe3
# https://github.com/sadiqgpasha/Autogen_experiments/blob/main/02autogen-conversable%20agent.ipynb
# https://medium.com/@sadiqgpasha89/autogen-easy-way-to-build-multi-conversational-agents-part-2-70c5adfcdfe1

single_prompt = """
    Receive a request from an user. Requests can be:

    1. The request is about a new employee who is joining the company. Use the tool "new_employee".
    2. The request is about an employee who is leaving the company. Use the tool "leaving_employee".

    If the request from the user does not match the ones listed above, just apologies and descrive the above requests. Don't add any other details but the requests described above.

    ---

    If the request is about a new employee, ask for the following questions, one at a time, in the listed order. Each question must be validated according to the provided instructions. If the answer is not valid, ask again until a valid answer is received.

    1. **Name of the employe (firstname):**
    - Question: "Which is the firstname of the employee who is joining the company?"

    2. **Surname of the employe (lastname):**
    - Question: "Which is the lastname of the employee who is joining the company?"

    2. **First working day (first_working_day):**
    - Question: "Which is the last working day of the leabing employee? It should be in the format of YYYY-MM-DD."
    - Validation: The answer must follow the YYYY-MM-DD format.

    Finally, provide me with a JSON of the information as per the example below:

    "new_employee": {
        "firstname": "Mario",
        "lastname": "Rossi",
        "first_working_day": "2024-01-31",
        "action": "EXECUTE",
    },

    ---

    If the request is about an employee leaving the company, ask for the following questions, one at a time, in the listed order. Each question must be validated according to the provided instructions. If the answer is not valid, ask again until a valid answer is received.

    1. **Email of the employe (email):**
    - Question: "Which is the email of the employee who is leaving the company?"
    - Validation: The answer must be a valid email address.

    2. **Last working day (last_working_day):**
    - Question: "Which is the last working day of the leabing employee? It should be in the format of YYYY-MM-DD."
    - Validation: The answer must follow the YYYY-MM-DD format.

    Ensure to ask the questions in the correct order and validate each answer as described. If the answer is not valid, ask again until you get an answer that meets the specified requirements.
    
    Finally, provide me with a JSON of the information as per the example below:

    "leaving_employee": {
        "email": "test@example.com",
        "last_working_day": "2024-01-31",
        "action": "EXECUTE",
    },
"""

chatbot_prompt = """
    Receive a request from an user. Valid requests are:

    - The request is about a new employee who is joining the company. Forward the request to "leaving_employee_agent".
    - The request is about an employee who is leaving the company. Forward the request to "new_employee_agent".

    If the request from the user does not match the ones listed above, apologies and return an help message describing the two request listed above.
"""
leaving_prompt = """
    Receive a JSON with information about an employee which is leaving the company. Ask the client the following questions, one at a time, in the listed order. Each question must be validated according to the provided instructions. If the answer is not valid, ask again until a valid answer is received.

    1. **Email of the employe (email):**
    - Question: "Which is the email of the employee who is leaving the company?"
    - Validation: The answer must be a valid email address.

    2. **Last working day (last_working_day):**
    - Question: "Which is the last working day of the leabing employee? It should be in the format of YYYY-MM-DD."
    - Validation: The answer must follow the YYYY-MM-DD format.

    Ensure to ask the questions in the correct order and validate each answer as described. If the answer is not valid, ask again until you get an answer that meets the specified requirements.
    
    Finally, provide me with a JSON of the information as per the example below:

    "leaving_employee": {
        "email": "test@example.com",
        "last_working_day": "2024-01-31",
        "action": "EXECUTE",
    },
"""
new_prompt = """
    Receive a JSON with information about an employee which is joining the company. Ask the client the following questions, one at a time, in the listed order. Each question must be validated according to the provided instructions. If the answer is not valid, ask again until a valid answer is received.

    1. **Name of the employe (firstname):**
    - Question: "Which is the firstname of the employee who is joining the company?"

    2. **Surname of the employe (lastname):**
    - Question: "Which is the lastname of the employee who is joining the company?"

    2. **First working day (first_working_day):**
    - Question: "Which is the last working day of the leabing employee? It should be in the format of YYYY-MM-DD."
    - Validation: The answer must follow the YYYY-MM-DD format.

    Ensure to ask the questions in the correct order and validate each answer as described. If the answer is not valid, ask again until you get an answer that meets the specified requirements.
    
    Finally, provide me with a JSON of the information as per the example below:

    "new_employee": {
        "firstname": "Mario",
        "lastname": "Rossi",
        "first_working_day": "2024-01-31",
        "action": "EXECUTE",
    },
"""



# Define a tool
async def invalid_request():
    # print(args)
    # print(kwargs)
    # print(arguments)
    return "The request is invalid"
async def new_employee():
    # print(args)
    # print(kwargs)
    # print(arguments)
    return "new"
async def leaving_employee():
    # print(args)
    # print(kwargs)
    # print(arguments)
    return "leaving"
    


chatbot_agent = AssistantAgent(
    name="chatbot_agent",
    system_message=chatbot_prompt,
    model_client=model_client,
    reflect_on_tool_use=False
)
leaving_employee_agent = AssistantAgent(
    name="leaving_employee_agent",
    system_message=leaving_prompt,
    model_client=model_client,
    reflect_on_tool_use=True,
    tools=[new_employee],
)
new_employee_agent = AssistantAgent(
    name="new_employee_agent",
    system_message=new_prompt,
    model_client=model_client,
    reflect_on_tool_use=True,
    tools=[leaving_employee],
)
user_proxy = UserProxyAgent("user_proxy", input_func=input)  # Use input() to get user input from console.

# Forwarding (handoff)
# https://microsoft.github.io/autogen/0.4.0.dev3//user-guide/core-user-guide/design-patterns/handoffs.html

async def main() -> None:
    # Define a team with a single agent and maximum auto-gen turns of 1.
    termination = TextMentionTermination("EXECUTE") | MaxMessageTermination(10)
    agent_team = RoundRobinGroupChat(
        [
            chatbot_agent,
            leaving_employee_agent,
            new_employee_agent,
            user_proxy,
        ],
        termination_condition=termination,
        max_turns=1,
    )

    while True:
        # Get user input from the console.
        user_input = input("Enter a message (type 'exit' to leave): ")
        if user_input.strip().lower() == "exit":
            break

        # Run the team and stream messages to the console.
        stream = agent_team.run_stream(task=user_input)
        await Console(stream)

asyncio.run(main())
