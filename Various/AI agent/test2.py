#!/usr/bin/env python3
import httpx
from pydantic import BaseModel, Field
from typing import Union, Literal, List

OLLAMA_BASE_URL = "http://localhost:11434"
# OLLAMA_MODEL = "openhermes2.5-mistral"
OLLAMA_MODEL = "deepseek-llm"
BUFFER_SIZE = 10
SYSTEM_MESSAGE = "Act like Hanah, a very sarcastic and humorous assistant."



# schemas
class Message(BaseModel):
    role: Union[Literal["system"], Literal["user"], Literal["assistant"]]
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    stream: bool = Field(default=False)


# message buffer
class MessageBuffer(BaseModel):
    system_message: Message
    messages: List[Message] = Field(default_factory=list)
    buffer_size: int

    def add_message(self, message: Message):
        self.messages.append(message)

    def get_buffered_history(self) -> List[Message]:
        messages = [self.system_message]
        messages.extend(self.messages[-self.buffer_size :])

        return messages
    

# generation function
def chat_completion(ollama_api_base: str, request: ChatRequest) -> Message:
    ollama_api_base.rstrip() if ollama_api_base[-1] == "/" else ...
    request_url = ollama_api_base + "/api/chat"
    request_data = request.model_dump()
    response = httpx.post(request_url, json=request_data)
    raw_message = response.json()["message"]
    message = Message(**raw_message)

    return message

if __name__ == "__main__":
    system_message = Message(
        role="system",
        content=SYSTEM_MESSAGE,
    )
    history_buffer = MessageBuffer(
        buffer_size=BUFFER_SIZE, system_message=system_message
    )

    print("Send a message, or type 'exit' to quit")
    while True:
        user_message = input("user: ")

        if user_message == "exit":
            exit()

        history_buffer.add_message(Message(role="user", content=user_message))
        messages = history_buffer.get_buffered_history()
        request = ChatRequest(model=OLLAMA_MODEL, messages=messages)

        assistant_message = chat_completion(OLLAMA_BASE_URL, request=request)
        print("assistant: ", assistant_message.content)

        history_buffer.add_message(assistant_message)
        