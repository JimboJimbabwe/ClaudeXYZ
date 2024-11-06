import re
from pathlib import Path
import sys
from typing import Dict, List, Optional
from datetime import datetime


class MarkdownSection:
    def __init__(self, title: str, level: int, content: str):
        self.title = title
        self.level = level
        self.content = content
        self.subsections: List[MarkdownSection] = []
        self.parent: Optional[MarkdownSection] = None


class MarkdownBatchExtractor:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.root_sections: List[MarkdownSection] = []
        self.all_sections: List[MarkdownSection] = []
        self.section_map: Dict[str, MarkdownSection] = {}
        self.output_file = "SuggestedHelp.txt"

    def read_file(self) -> Optional[str]:
        """Read the markdown file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def read_section_numbers(self, numbers_file: str = "intgOUT.txt") -> List[str]:
        """Read section numbers from file"""
        try:
            with open(numbers_file, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"Error reading section numbers file: {e}")
            return []

    def extract_sections(self) -> bool:
        """Extract sections and organize them hierarchically"""
        content = self.read_file()
        if not content:
            return False

        sections = re.split(r'\n---\n', content)
        current_section = None
        last_section_by_level = {}

        for section in sections:
            header_match = re.match(r'^(#{1,6})\s+(.+?)(?:\n|$)', section.strip())
            if header_match:
                hashes, title = header_match.groups()
                level = len(hashes)

                new_section = MarkdownSection(
                    title=title,
                    level=level,
                    content=section.strip()
                )

                self.all_sections.append(new_section)
                self.section_map[title] = new_section

                if level == 1 or not last_section_by_level:
                    self.root_sections.append(new_section)
                else:
                    parent_level = max(l for l in last_section_by_level.keys() if l < level)
                    parent = last_section_by_level[parent_level]
                    parent.subsections.append(new_section)
                    new_section.parent = parent

                last_section_by_level[level] = new_section

        return True

    def build_section_map(self, sections=None, parent_num=""):
        """Build mapping of section numbers to sections"""
        if sections is None:
            sections = self.root_sections
            self.section_map.clear()

        for i, section in enumerate(sections, 1):
            section_num = f"{parent_num}{i}" if parent_num else str(i)
            self.section_map[section_num] = section

            if section.subsections:
                self.build_section_map(section.subsections, f"{section_num}.")

    def get_section_content(self, selection: str) -> Optional[str]:
        """Get content of selected section and its subsections"""
        if selection not in self.section_map:
            return None

        selected_section = self.section_map[selection]
        content = [selected_section.content]

        if '.' not in selection and selected_section.subsections:
            for subsection in selected_section.subsections:
                content.append(subsection.content)

        return "\n\n---\n\n".join(content)

    def process_batch(self):
        """Process all sections and write to file"""
        section_numbers = self.read_section_numbers()
        if not section_numbers:
            print("No section numbers found in intgOUT.txt")
            return

        print(f"Processing {len(section_numbers)} sections...")

        # Write to output file
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write(f"Generated Help Documentation\n")
                f.write(f"Source: {self.file_path.name}\n")
                f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

                # Write each section
                for number in section_numbers:
                    content = self.get_section_content(number)
                    if content:
                        f.write(f"\nSection {number}:\n")
                        f.write("-" * 50 + "\n")
                        f.write(content)
                        f.write("\n" + "=" * 50 + "\n")

                # Write footer
                f.write(f"\nEnd of documentation - {len(section_numbers)} sections processed\n")
                f.write("=" * 80 + "\n")

            print(f"Successfully wrote output to {self.output_file}")

        except Exception as e:
            print(f"Error writing to output file: {e}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_markdown_file>")
        return

    file_path = sys.argv[1]
    if not Path(file_path).exists():
        print(f"Error: File '{file_path}' not found")
        return

    extractor = MarkdownBatchExtractor(file_path)

    if not extractor.extract_sections():
        print("Failed to extract sections from file")
        return

    # Build the section map
    extractor.build_section_map()

    # Process all sections and save to file
    extractor.process_batch()


if __name__ == "__main__":
    main()