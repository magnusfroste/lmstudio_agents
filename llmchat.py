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
                        "description": "The URL to make the HTTP GET request to"
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
            "description": "Retrieve the total sales revenue and number of items sold for a specific month from the product sales database. Use this tool when a user asks about sales data, revenue, or how much was sold in a particular month or time period. The month parameter must be in 'YYYY-MM' format (e.g., '2025-01' for January 2025). If the user specifies a month by name (like 'January'), convert it to the correct 'YYYY-MM' format before calling this tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "month": {
                        "type": "string",
                        "description": "The month in 'YYYY-MM' format (e.g., '2025-01' for January 2025). Ensure the format is correct when calling this tool."
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
            "description": "Retrieve a list of all unique products sold in the database along with the total quantity sold and total revenue for each. Use this tool when a user asks to see all sold products, a list of products, or general sales inventory data.",
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
            "description": "Retrieve a list of the top most expensive individual product sales from the database, including product name, price, and sale date. Use this tool when a user asks about the most expensive products, highest priced sales, or top sales by price. The default is to return the top 5 if no specific number is mentioned, but a custom limit can be specified.",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "The number of top expensive products to retrieve. Default is 5 if not specified.",
                        "default": 5
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_available_tools",
            "description": "List all available tools and functions that I can use to assist you. Use this tool when a user asks what functions are supported, what I can do, or to show the list of available tools and capabilities.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_content",
            "description": "Read the content of a specified file and return it as a string. Use this tool when a user asks to read or retrieve content from a file on the local system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to be read."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_json_file",
            "description": "Read the content of a specified JSON file and return it as a formatted string. Use this tool when a user asks to read or analyze structured data from a JSON file, such as accounting data, on the local system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the JSON file to be read."
                    }
                },
                "required": ["path"]
            }
        }
    }
]

# Global variables to track the last-used files for relevant tools
last_file_paths = {
    "read_file_content": "examples/sample_text.txt",  # Default file for file operations
    "read_json_file": "examples/sample.json"          # Default file for JSON operations
}

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
        response = "Here are the tools and functions I can assist you with:\n"
        for tool in tools:
            tool_name = tool['function']['name']
            tool_desc = tool['function']['description']
            response += f"- `{tool_name}`: {tool_desc}\n"
        return response
    elif tool_name == "read_file_content":
        path = tool_arguments.get('path', last_file_paths.get("read_file_content", "examples/sample_text.txt"))
        last_file_paths["read_file_content"] = path  # Update last-used file
        result = read_file_content(path)
        return f"Content of file '{path}':\n{result}"
    elif tool_name == "read_json_file":
        path = tool_arguments.get('path', last_file_paths.get("read_json_file", "examples/sample.json"))
        last_file_paths["read_json_file"] = path  # Update last-used file
        result = read_json_file(path)
        return f"Content of JSON file '{path}':\n{result}"
    else:
        return f"Unknown tool: {tool_name}"

# Main chat loop
def main():
    messages = [
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
        
        # Check if the assistant wants to call a tool
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
