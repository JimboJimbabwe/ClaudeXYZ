import difflib
from pathlib import Path
import subprocess
import re


def sanitize_filename(filename):
    """Convert string to valid filename"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = filename.strip()
    return filename


def extract_keywords(text):
    """Extract main keywords from text, removing common words."""
    words = text.lower().split()
    stop_words = {'pentesting', 'i', 'am', 'looking', 'for', 'something', 'called', 'an', 'a', 'the', 'help', 'with'}
    keywords = [word for word in words if word not in stop_words]
    return keywords


def calculate_similarity(str1, str2):
    """Calculate similarity with both sequence and keyword matching"""
    # Basic sequence similarity
    sequence_ratio = difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

    # Keyword similarity
    keywords1 = set(extract_keywords(str1))
    keywords2 = set(extract_keywords(str2))

    if keywords1 and keywords2:
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        keyword_ratio = len(intersection) / len(union)
    else:
        keyword_ratio = 0

    # Weighted combination (favoring keyword matching)
    return (sequence_ratio * 0.3) + (keyword_ratio * 0.7)


def compare_strings_and_build_path(string1, string2_file, base_path):
    """Compare strings and build path from best match."""
    try:
        # Read file 2
        with open(string2_file, 'r', encoding='utf-8') as f:
            lines2 = f.readlines()

        # Process string1 to handle newlines
        lines1 = string1.split('\n')

        best_match = None
        best_ratio = 0
        best_line_num = 0

        # Extract port number if present in query
        port_match = re.search(r'port (\d+)', string1.lower())
        target_port = port_match.group(1) if port_match else None

        # Compare each line
        for i, line2 in enumerate(lines2, 1):
            line2 = line2.strip()
            if not line2:
                continue

            # Check for port match if we have a target port
            if target_port and target_port in line2:
                current_ratio = calculate_similarity(string1, line2) + 0.3  # Boost score for port match
            else:
                current_ratio = calculate_similarity(string1, line2)

            if current_ratio > best_ratio:
                best_ratio = current_ratio
                best_match = line2
                best_line_num = i

        # Print comparison results
        print("\nTop matching lines found:")
        print("-" * 80)
        print(f"Search query: {lines1[0]}")
        print(f"Best match: {best_match}")
        print(f"Similarity: {best_ratio * 100:.2f}%")

        if best_match:
            # Sanitize and build path
            folder_name = sanitize_filename(best_match)
            full_path = Path(base_path) / folder_name / f"{folder_name}.md"

            if full_path.exists():
                print(f"\nConstructed path: {full_path}")
                return str(full_path), best_ratio
            else:
                print(f"\nWarning: Constructed path does not exist: {full_path}")
                return None, best_ratio
        else:
            print("\nNo match found")
            return None, 0

    except Exception as e:
        print(f"Error in comparison: {e}")
        return None, 0


def main():
    # Configuration
    base_path = r"C:\Users\james\PycharmProjects\webDataret\Working"
    search_query_file = "myInput.txt"
    reference_file = "Ports.txt"
    next_script = "mdExtractForPrompt.py"

    # Read search query
    try:
        with open(search_query_file, 'r', encoding='utf-8') as f:
            search_query = f.read().strip()
    except Exception as e:
        print(f"Error reading search query: {e}")
        return

    # Compare and get path
    path, similarity = compare_strings_and_build_path(search_query, reference_file, base_path)

    # If we found a valid path and it's a good match (over 30% similar)
    if path and similarity > 0.2:
        try:
            # Call the next script with the path as argument
            subprocess.run(['python', next_script, path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running next script: {e}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No suitable match found or similarity too low")


if __name__ == "__main__":
    main()