import anthropic
from pathlib import Path

def read_file(file_path: str) -> str:
    """Read and return the contents of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def write_file(content: str, file_path: str) -> bool:
    """Write content to a file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")
        return False

def combine_files() -> str:
    """Combine contents of both files with appropriate formatting"""
    input_content = read_file("myInput.txt")
    sections_content = read_file("SuggestedHelp.txt")

    # Combine the contents with a clear separator
    combined_content = f"""Input Query:
{input_content}

Available Sections:
{sections_content}"""

    return combined_content

def main():
    # Create an instance of the Anthropic API client
    client = anthropic.Anthropic(api_key='')

    # Get combined content from both files
    combined_content = combine_files()

    # Send to Claude
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1024,
            system="You are to receive helpful data that is relevant to the goal at hand, which is based on the prompt you receive. You will receive a request, and then helpful data to enrich your response.",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": combined_content
                        }
                    ]
                }
            ]
        )

        # Extract the response content
        response_content = response.content[0].text

        # Write response to ClaudeFinal.txt instead of IntegerList.txt
        if write_file(response_content, "ClaudeFinal.txt"):
            print(f"\nResponse has been saved to ClaudeFinal.txt")

        # Also print to console
        print("\nClaude's Response:")
        print("-" * 50)
        print(response_content)

    except Exception as e:
        print(f"Error communicating with Claude: {e}")

if __name__ == "__main__":
    main()