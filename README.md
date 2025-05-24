# LM Studio Chat Interface: A Mini Framework for Agentic Tool Calling

This project provides a terminal-based chat interface for interacting with a local language model (LLM) server running on LM Studio. More than just a chat interface, it serves as a **mini framework for building agentic tool calling** capabilities, enabling the LLM to execute predefined Python functions (tools) based on conversation context. This open-source project (MIT License) welcomes contributors to make it more robust and expand its potential.

## About LM Studio

[LM Studio](https://lmstudio.ai) is a powerful platform for running local language models, making AI accessible to everyone without the need for cloud dependency. Over the past year, LM Studio has made remarkable progress, evolving from a simple local LLM runner to a comprehensive environment for AI experimentation and application development. Their team, a dedicated group of innovators based in Silicon Valley, has been instrumental in pushing the boundaries of what's possible with local AI, fostering a community of developers and researchers who are building the future of agentic AI.

## Project Structure

- **llmchat.py**: Main script for the chat interface.
- **create_sales_database.py**: Script to create a sample SQLite database for sales data.
- **tools/**: Directory containing Python modules with callable functions that the LLM can use.
  - **math_operations.py**: Basic math operations.
  - **sales_data_query.py**: Functions to query sales data from the SQLite database.
- **install.sh**: Installation script to set up the environment and dependencies.
- **requirements.txt**: Lists the Python dependencies.

## Prerequisites

- **Python 3.6 or higher**: Ensure Python is installed on your system.
- **LM Studio**: Installed and running a server on `localhost:1234` with a compatible model loaded (e.g., Qwen2.5-7B-Instruct-GGUF).

## Installation

### Automated Installation (Recommended)

Run the interactive installation script to set up the environment and dependencies:

```bash
bash install.sh
```

This script will:
1. Check for Python 3.6 or higher.
2. Create and activate a virtual environment if not already done.
3. Verify if the LM Studio server is running on `localhost:1234`.
4. Install required dependencies from `requirements.txt`.
5. Create a sample sales database if it doesn't exist.

### Manual Installation

If you prefer manual setup:

1. **Clone the Repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Set Up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Create Sample Sales Database** (optional):
   ```bash
   python create_sales_database.py
   ```
5. **Ensure LM Studio Server is Running**:
   - Start LM Studio and load a model (e.g., Qwen2.5-7B-Instruct-GGUF).
   - Confirm the server is accessible at `http://localhost:1234`.

## Usage

Run the chat interface with:

```bash
venv/bin/python3 llmchat.py
```

- **Chat**: Type your message and press Enter to send it to the model.
- **Exit**: Type `exit` to close the chat interface.

The model may call predefined tools based on your input (e.g., querying sales data or performing calculations).

## System Prompt

The system prompt used to initialize the chat with the LLM is as follows:

```plaintext
You are a helpful assistant that can use tools to answer questions. If you don't know the answer, you can search for information. Always use the provided tools to assist with the queries. If a tool is not available for a specific task, inform the user and suggest an alternative approach.
```

This prompt ensures that the model leverages the available tools to provide accurate and helpful responses.

## Tool Calling: Building Agentic AI with LM Studio

Tool calling is a transformative approach to making LLMs more interactive and functional, turning them into agentic systems capable of performing tasks beyond mere text generation. However, it relies on several moving parts that must work in harmony:

1. **The LLM Model**: The language model itself is the core component. It must be capable of understanding user intent and recognizing when a tool should be called. Models like Qwen2.5-7B-Instruct-GGUF, which are fine-tuned for instruction-following, are particularly suited for tool calling, but their effectiveness depends on their training data and inherent capabilities.

2. **The System Prompt**: A well-crafted system prompt is crucial. It sets the context for the LLM, instructing it on how to behave and when to use tools. The prompt must clearly define the LLM's role as an assistant that can leverage tools, ensuring it prioritizes tool usage over speculative answers when appropriate.

3. **Defined Functions (Tools)**: These are the Python functions that the LLM can call. Each tool must be meticulously declared with a clear name, description, and parameter schema. For example, in this framework, tools like `multiply_numbers` or `get_sales_data_by_month` are defined with JSON schemas that specify their purpose and required inputs. This structured declaration helps the LLM understand what each tool does and how to invoke it correctly.

### Challenges in Tool Calling

Despite the potential of tool calling, LLMs face significant challenges in selecting the right function based on user queries. These challenges include:
- **Knowledge Limitations**: LLMs may not always have up-to-date or comprehensive knowledge about the tools available or the specific context of a user's request. This can lead to incorrect tool selection or failure to recognize when a tool should be used.
- **Awareness of Capabilities**: An LLM must be aware of what it can assist with through tool calling. If the system prompt or tool descriptions are unclear, the model might not realize a tool is relevant to a query, resulting in suboptimal responses.
- **Ambiguity in User Intent**: User queries can be vague or ambiguous, making it difficult for the LLM to decide which tool, if any, to call. Improving tool descriptions and training models to ask clarifying questions can mitigate this issue.

This mini framework aims to address these challenges by providing a clear structure for tool definition and system prompts, but it requires ongoing refinement. Contributors are encouraged to enhance tool discovery mechanisms, improve prompt engineering, and integrate more advanced models to make agentic tool calling more robust.

## Example Tools

This framework already includes several tools for demonstration:
- **Math Operations**: Simple calculations like multiplication through `multiply_numbers`.
- **Sales Data Queries**: Tools to interact with a sample SQLite database, including:
  - `get_sales_data_by_month`: Retrieve sales data for a specific month in 'YYYY-MM' format.
  - `list_all_sold_products`: Returns a list of all unique products sold, showing units sold and total revenue.
  - `get_top_expensive_products`: Retrieves the top most expensive individual sales.
  - `list_available_tools`: Allows users to see all supported functions by asking, 'What functions do you support?' or 'List available tools'.

## Extending with More Functions (Tool Calling)

You can extend this project by adding more functions that the LLM can call as tools. Here's how to add a new tool for making an HTTP request:

1. **Define the New Function**: Add a new function in `web_requests.py` to handle HTTP requests. For example:
   ```python
   import requests

   def make_http_request(url: str) -> str:
       """Make an HTTP GET request to the specified URL and return the response text."""
       try:
           response = requests.get(url)
           response.raise_for_status()
           print(f"HTTP request to {url} successful")
           return response.text[:500] + "..." if len(response.text) > 500 else response.text
       except Exception as e:
           print(f"Error making HTTP request to {url}: {str(e)}")
           return f"Error: {str(e)}"
   ```

2. **Add the Tool to the Tools List**: Update the `tools` list to include the new function:
   ```python
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
       # Add your new tool here
   ]
   ```

3. **Register the Function for Tool Calling**: Ensure the function is registered so the LLM can call it during the chat:
   ```python
   def execute_tool(tool_call):
       tool_name = tool_call.function.name
       arguments = json.loads(tool_call.function.arguments)
       
       if tool_name == "multiply_numbers":
           return multiply_numbers(arguments["a"], arguments["b"])
       elif tool_name == "make_http_request":
           return make_http_request(arguments["url"])
       # Add more elif conditions for additional tools
       else:
           return f"Tool {tool_name} not found"
   
   # Get the final response from the model after tool execution
   final_message = chat_with_model(messages)
   messages.append(final_message)
   print(f"Assistant (after HTTP request): {final_message.content}")
   ```

4. **Install Additional Dependencies**: If your new function requires additional libraries (like `requests` for HTTP requests), install them in your virtual environment:
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # OR
   venv\Scripts\activate  # On Windows
   pip install requests
   ```

5. **Update System Message**: Optionally, update the system message to inform the model about the new capability:
   ```python
   messages = [
       {"role": "system", "content": "You are a helpful assistant that can use tools to answer questions. If you don't know the answer, you can search for information. Always use the provided tools to assist with the queries. If a tool is not available for a specific task, inform the user and suggest an alternative approach."}
   ]
   ```

Now, when interacting with the model, you can ask it to fetch content from a URL, for example: "Can you get information from https://api.example.com/data?" and it will call the `make_http_request` function to retrieve the data.

Remember to handle errors appropriately in your functions and limit response sizes if necessary to avoid overwhelming the model with too much data.

## Troubleshooting

- **LM Studio Server Not Detected**:
  - Ensure LM Studio is installed and running.
  - Check if the server is accessible at `http://localhost:1234` using a browser or `curl http://localhost:1234`.
  - If using a different port, modify the `base_url` in `llmchat.py`.
- **Installation Issues**:
  - Verify Python version with `python3 --version`.
  - Ensure virtual environment is activated before running `pip install`.
- **EOF Error**:
  - Run the script in an interactive terminal session to provide input.

## Contributing

Feel free to submit issues or pull requests for improvements to the chat interface or additional tools. As an open-source project under the MIT License, we welcome contributions to enhance this mini framework for agentic tool calling with LM Studio.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
