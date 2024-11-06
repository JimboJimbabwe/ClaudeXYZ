import re
from pathlib import Path
import sys
from typing import Dict, List, Optional, TextIO


class MarkdownSection:
    def __init__(self, title: str, level: int, content: str):
        self.title = title
        self.level = level
        self.content = content
        self.subsections: List[MarkdownSection] = []
        self.parent: Optional[MarkdownSection] = None


class MarkdownHierarchicalExtractor:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.root_sections: List[MarkdownSection] = []
        self.all_sections: List[MarkdownSection] = []
        self.section_map: Dict[str, MarkdownSection] = {}
        self.output_file = Path("Available_sections.txt")

    def read_file(self) -> Optional[str]:
        """Read the markdown file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def extract_sections(self) -> bool:
        """Extract sections and organize them hierarchically"""
        content = self.read_file()
        if not content:
            return False

        # Split content by the triple dash separator
        sections = re.split(r'\n---\n', content)
        last_section_by_level = {}

        for section in sections:
            # Find the first header in the section
            header_match = re.match(r'^(#{1,6})\s+(.+?)(?:\n|$)', section.strip())
            if header_match:
                hashes, title = header_match.groups()
                level = len(hashes)

                # Create new section
                new_section = MarkdownSection(
                    title=title,
                    level=level,
                    content=section.strip()
                )

                # Add to flat list of all sections
                self.all_sections.append(new_section)
                self.section_map[title] = new_section

                # Handle hierarchy
                if level == 1 or not last_section_by_level:
                    self.root_sections.append(new_section)
                else:
                    # Find appropriate parent
                    parent_level = max(l for l in last_section_by_level.keys() if l < level)
                    parent = last_section_by_level[parent_level]
                    parent.subsections.append(new_section)
                    new_section.parent = parent

                last_section_by_level[level] = new_section

        return True

    def write_sections_to_file(self, sections=None, indent=0, parent_num="", file: TextIO = None):
        """Write all available sections with hierarchical numbering to a file"""
        if sections is None:
            sections = self.root_sections
            file.write("Available sections:\n")
            file.write("-" * 50 + "\n")

        for i, section in enumerate(sections, 1):
            # Create section number
            section_num = f"{parent_num}{i}" if parent_num else str(i)
            indent_str = "    " * indent
            file.write(f"{indent_str}{section_num}. {section.title}\n")

            # Store reference for selection
            self.section_map[section_num] = section

            # Recursively write subsections
            if section.subsections:
                self.write_sections_to_file(section.subsections, indent + 1, f"{section_num}.", file)


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_markdown_file>")
        return

    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"Error: File '{file_path}' not found")
        return

    extractor = MarkdownHierarchicalExtractor(file_path)

    if not extractor.extract_sections():
        print("Failed to extract sections from file")
        return

    # Write sections to file
    try:
        with open(extractor.output_file, 'w', encoding='utf-8') as f:
            extractor.write_sections_to_file(file=f)
        print(f"\nSection list has been written to {extractor.output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")
        return


if __name__ == "__main__":
    main()