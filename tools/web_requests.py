import requests

def make_http_request(url: str) -> str:
    """Make an HTTP GET request to the specified URL and return the response text."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
