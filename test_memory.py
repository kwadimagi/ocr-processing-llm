# test_memory.py
from langchain.memory.buffer import ConversationBufferMemory

# Create a simple conversation memory
memory = ConversationBufferMemory(return_messages=True)

# Add a human-AI message pair
memory.save_context({"input": "Hello"}, {"output": "Hi there!"})

# Load memory to check contents
vars = memory.load_memory_variables({})
print("Memory history:", vars.get("history"))
