from openai import OpenAI
import json

# Connect to LM Studio
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Define the multiplication function
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers and return the result."""
    result = a * b
    print(f"Multiplying {a} * {b} = {result}")
    return result

# Define the tool for the LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "multiply_numbers",
            "description": "Multiply two numbers and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "The first number"
                    },
                    "b": {
                        "type": "number",
                        "description": "The second number"
                    }
                },
                "required": ["a", "b"]
            }
        }
    }
]

# Function to handle chat interaction
def chat_with_model(messages):
    response = client.chat.completions.create(
        model="lmstudio-community/Qwen2.5-7B-Instruct-GGUF",
        messages=messages,
        tools=tools,
        temperature=0.7
    )
    return response.choices[0].message

# Main chat loop
def main():
    messages = [
        {"role": "system", "content": "You are a patient and helpful teacher guiding the user through mathematical operations. Explain what you are doing before and after using tools like multiply_numbers. Provide clear, step-by-step explanations to help the user learn and understand the process."}
    ]
    print("Start chatting with the model (type 'exit' to stop):")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        
        messages.append({"role": "user", "content": user_input})
        assistant_message = chat_with_model(messages)
        print(f"Assistant: {assistant_message.content}")
        messages.append({"role": "assistant", "content": assistant_message.content})
        
        # Check if the assistant wants to call a tool
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_arguments = json.loads(tool_call.function.arguments)
                
                if tool_name == "multiply_numbers":
                    result = multiply_numbers(tool_arguments['a'], tool_arguments['b'])
                    tool_response = f"The result of multiplying {tool_arguments['a']} by {tool_arguments['b']} is {result}"
                    print(f"Tool Output: {tool_response}")
                    messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_response})
                    
                    # Get follow-up response from assistant
                    follow_up_response = chat_with_model(messages)
                    print(f"Assistant: {follow_up_response.content}")
                    messages.append({"role": "assistant", "content": follow_up_response.content})

if __name__ == "__main__":
    main()
