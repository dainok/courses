#!/usr/bin/env python3
import ollama

response = ollama.chat(model="deepseek-llm", messages=[
    {
        "role": "system",
        "content": "You are an expert at creating brief poems about animals"
    },
    {
        "role": "user",
        "content": "Write a poem about a dog"
    },
])
print(response["message"]["content"])
