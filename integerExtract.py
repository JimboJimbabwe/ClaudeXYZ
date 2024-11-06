import re
from pathlib import Path

def extract_hierarchical_numbers(input_file: str, output_file: str) -> None:
    """
    Extract hierarchical section numbers from input file and save to output file.
    Matches patterns like 1.2, 1.2.1, etc. on their own lines
    """
    try:
        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regular expression to match hierarchical numbers
        # This pattern looks for numbers in format like 1.2 or 1.2.3 on their own lines
        pattern = r'^(?:\d+\.)+\d+$'

        # Find all matches
        numbers = []
        for line in content.split('\n'):
            line = line.strip()
            if re.match(pattern, line):
                numbers.append(line)

        # Sort numbers naturally
        def natural_sort_key(s):
            return [int(x) for x in s.split('.')]

        numbers.sort(key=natural_sort_key)

        # Remove duplicates while preserving order
        unique_numbers = list(dict.fromkeys(numbers))

        # Write to output file
        with open(output_file, 'w', encoding='utf-8') as f:
            for num in unique_numbers:
                f.write(f"{num}\n")

        print(f"Successfully processed {len(unique_numbers)} hierarchical numbers")
        print("\nExtracted numbers:")
        for num in unique_numbers:
            print(num)
        print(f"\nResults saved to {output_file}")

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e

def main():
    input_file = "IntegerList.txt"
    output_file = "intgOUT.txt"

    # Ensure input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found")
        return

    print(f"Processing {input_file}...")
    print("\nInput file contents:")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e:
        print(f"Error reading input file: {e}")

    extract_hierarchical_numbers(input_file, output_file)

if __name__ == "__main__":
    main()