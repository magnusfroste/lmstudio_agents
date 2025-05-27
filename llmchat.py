from openai import OpenAI
import json

# Initialize the OpenAI client for LM Studio
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Import tool functions from separate modules
from tools.math_operations import multiply_numbers
from tools.web_requests import make_http_request
from tools.database_operations import get_sales_by_month, list_all_sold_products, get_top_expensive_products
from tools.file_operations import read_file_content
from tools.json_operations import read_json_file

# Define the tools for the LLM
# TOOL_METADATA: This 'tools' list is critical for tool calling. Each dictionary here represents metadata that the LLM uses to decide which tool to invoke based on user queries.
# The 'name' field identifies the tool uniquely; it must match exactly what the LLM calls.
# The 'description' field is vital - it explains the tool's purpose to the LLM, guiding it to match user intent (e.g., 'multiply numbers' for math queries).
# The 'parameters' define what inputs the tool expects, helping the LLM extract correct arguments from user input.
# Clear, specific metadata ensures the LLM selects the right tool; vague or overlapping descriptions can lead to incorrect decisions.
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
    },
    {
        "type": "function",
        "function": {
            "name": "make_http_request",
            "description": "Make an HTTP GET request to a specified URL and return the response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL to make the GET request to"
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_by_month",
            "description": "Get total sales for a specific month from the database. Use YYYY-MM format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "The month in YYYY-MM format"
                    }
                },
                "required": ["month"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_all_sold_products",
            "description": "List all sold products from the database.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_expensive_products",
            "description": "Get the top most expensive sold products from the database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of top products to return, default is 5"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "Read and return content from a local text file for discussion or analysis.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the text file, relative to project directory"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_json_file",
            "description": "Read and return content from a JSON file for analysis, such as accounting data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the JSON file, relative to project directory"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_tools",
            "description": "List all available tools and their functions to the user.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

# Global variables to track the last-used files for relevant tools
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
last_file_paths = {
    "read_file_content": os.path.join(BASE_DIR, "examples", "sample_text.txt"),  # Default file for file operations
    "read_json_file": os.path.join(BASE_DIR, "examples", "sample.json")          # Default file for JSON operations
}

# ANSI escape codes for terminal formatting
BOLD = "\033[1m"
RESET = "\033[0m"
CYAN = "\033[96m"
GREEN = "\033[92m"

# Function to handle chat interaction
def chat_with_model(messages):
    response = client.chat.completions.create(
        model="lmstudio-community/Qwen2.5-7B-Instruct-GGUF",
        messages=messages,
        tools=tools,
        temperature=0.7
    )
    return response.choices[0].message

# Router to handle tool calls
# TOOL_METADATA_USAGE: This function is where the LLM's decision to call a tool is acted upon.
# The 'tool_call' object contains the tool name and arguments decided by the LLM based on the metadata in the 'tools' list.
# Observing which tool is called and with what arguments helps users understand how well the metadata matched the user's query.
# If the LLM calls the wrong tool or provides incorrect parameters, it often indicates a need to refine the tool's description or parameters in the metadata.
def handle_tool_call(tool_call):
    tool_name = tool_call.function.name
    tool_arguments = json.loads(tool_call.function.arguments)
    
    if tool_name == "multiply_numbers":
        result = multiply_numbers(tool_arguments['a'], tool_arguments['b'])
        return f"The result of multiplying {tool_arguments['a']} by {tool_arguments['b']} is {result}"
    elif tool_name == "make_http_request":
        result = make_http_request(tool_arguments['url'])
        return f"HTTP Response: {result[:200]}..." if len(result) > 200 else f"HTTP Response: {result}"
    elif tool_name == "get_sales_by_month":
        result = get_sales_by_month(tool_arguments['month'])
        return result
    elif tool_name == "list_all_sold_products":
        result = list_all_sold_products()
        return result
    elif tool_name == "get_top_expensive_products":
        limit = tool_arguments.get('limit', 5)  # Default to 5 if not specified
        result = get_top_expensive_products(limit)
        return result
    elif tool_name == "list_available_tools":
        response = f"{BOLD}{CYAN}Here are the tools and functions I can assist you with:{RESET}\n"
        for tool in tools:
            tool_name = tool['function']['name']
            tool_desc = tool['function']['description']
            response += f"{GREEN}- `{tool_name}`{RESET}: {tool_desc}\n"
        return response
    elif tool_name == "read_file_content":
        path = tool_arguments.get('path', last_file_paths.get("read_file_content", os.path.join(BASE_DIR, "examples", "sample_text.txt")))
        last_file_paths["read_file_content"] = path  # Update last-used file
        import os
        full_path = os.path.abspath(path)
        print(f"Attempting to read file from: {full_path}")
        result = read_file_content(path)
        return f"Content of file '{path}':\n{result}"
    elif tool_name == "read_json_file":
        path = tool_arguments.get('path', last_file_paths.get("read_json_file", os.path.join(BASE_DIR, "examples", "sample.json")))
        last_file_paths["read_json_file"] = path  # Update last-used file
        import os
        full_path = os.path.abspath(path)
        print(f"Attempting to read JSON file from: {full_path}")
        result = read_json_file(path)
        return f"Content of JSON file '{path}':\n{result}"
    else:
        return f"Unknown tool: {tool_name}"

# Main chat loop
def main():
    messages = [
        # TOOL_METADATA_GUIDANCE: The system prompt below is crucial metadata for tool calling decisions.
        # It instructs the LLM on its behavior regarding tool usage, explicitly guiding it to use tools when queries match tool purposes.
        # It also sets expectations for when to assume default contexts (like last-used files), influencing how the LLM interprets follow-up queries.
        # A clear system prompt ensures the LLM prioritizes tool calling appropriately; vague instructions can lead to inconsistent decisions.
        {"role": "system", "content": "You are a helpful assistant that can use tools to answer questions. If you don't know the answer, you can search for information. Always use the provided tools to assist with queries. When you decide to use a tool, clearly inform the user by stating which tool you are calling and for what purpose before invoking it. For example, say 'I will call the [tool name] tool to [purpose].' If a tool is not available for a specific task, inform the user and suggest an alternative approach. For file-related tools like 'read_file_content' and 'read_json_file', if the user does not specify a file path, assume they are referring to the last-used file or the default file for that tool (e.g., 'examples/sample_text.txt' for text files, 'examples/sample.json' for JSON files). Track and reference the last-used file for subsequent queries unless a new path is provided."}
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
        
        # TOOL_METADATA_EXECUTION: This section checks if the LLM decided to call a tool based on the metadata and user input.
        # If 'tool_calls' are present, it means the LLM matched the query to a tool's metadata (name and description) and extracted parameters as defined.
        # This is a key point to observe the outcome of the LLM's decision-making process - which tool was chosen and why (based on metadata matching).
        # Users can learn from this by seeing how query phrasing influences tool selection.
        if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
            for tool_call in assistant_message.tool_calls:
                tool_response = handle_tool_call(tool_call)
                print(f"Tool Output: {tool_response}")
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": tool_response})
                
                # Get follow-up response from assistant
                follow_up_response = chat_with_model(messages)
                print(f"Assistant: {follow_up_response.content}")
                messages.append({"role": "assistant", "content": follow_up_response.content})

if __name__ == "__main__":
    main()
