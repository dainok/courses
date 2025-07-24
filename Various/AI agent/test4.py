#!/usr/bin/env python3
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
import asyncio

"""
activate the proxy
litellm --model ollama/llama3.2:1b
"""


prompt = """
    'Receive a JSON with information about a proposer and ask the client the following questions, one at a time, in the listed order. Each question must be validated according to the provided instructions. If the answer is not valid, ask again until a valid answer is received.

    1. **Type of Proposer:**
    - Question: "What is the type of proposer? It should be 'F' for an individual or 'J' for a legal entity."
    - Validation: The answer must be 'F' or 'J'.

    2. **Document:**
    - Question: "What is the proposer's document number? It should be in the format of CPF (xxx.xxx.xxx-xx) for individuals or CNPJ (xx.xxx.xxx/xxxx-xx) for legal entities."
    - Validation: The answer must follow the CPF or CNPJ format depending on the type of proposer.

    3. **Email:**
    - Question: "What is the proposer's email?"
    - Validation: The answer must be a valid email address.

    4. **Name:**
    - Question: "What is the proposer's full name?"
    - Validation: The answer must be a valid full name.

Ensure to ask the questions in the correct order and validate each answer as described. If the answer is not valid, ask again until you get an answer that meets the specified requirements.
    
    Finally, provide me with a JSON of the information as per the example below:

    "proponent": {
            "type": "F",
            "document": "123.456.789-10",
            "email": "teste@teste.com.br",
            "name": "Roberto Braga",
        },
"""



emails = {
    "mario.rossi@example.com": {
        "name": "Mario",
        "surname": "Rossi",
        "username": "mrossi",
    }
}

# Define a tool
async def person_leaving(email: str) -> str:
    if email not in emails:
        return f"I'm sorry but I cannot found any active employee associated to {email} email address."
    
    account = emails[email]
    return f"{account['name']} {account['surname']} is leaving the compamy. His email is {email}. Please confirm so I can deactivate all accounts."


async def main() -> None:
    # Define an agent
    person_leaving_agent = AssistantAgent(
        name="person_leaving_agent",
        model_client=OpenAIChatCompletionClient(
            model="llama3.2:1b",
            api_key="NotRequiredSinceWeAreLocal", # Ignored
            base_url="http://0.0.0.0:4000",
            # api_key="YOUR_API_KEY",
            model_capabilities={
                "json_output": False,
                "vision": False,
                "function_calling": True,
            },
        ),
        tools=[person_leaving],
    )

    # Define a team with a single agent and maximum auto-gen turns of 1.
    agent_team = RoundRobinGroupChat([person_leaving_agent], max_turns=1)

    while True:
        # Get user input from the console.
        user_input = input("Enter a message (type 'exit' to leave): ")
        if user_input.strip().lower() == "exit":
            break
        # Run the team and stream messages to the console.
        stream = agent_team.run_stream(task=user_input)
        await Console(stream)


# NOTE: if running this inside a Python script you'll need to use asyncio.run(main()).
# await main()
asyncio.run(main())
