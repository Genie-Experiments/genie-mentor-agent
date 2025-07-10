import os
import re
import json
import logging
import pymupdf4llm
from dotenv import load_dotenv

load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, pdf_path: str, output_dir: str = "./", output_filename: str = "processed_document.json"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.final_output_path = os.path.join(output_dir, output_filename)

        os.makedirs(output_dir, exist_ok=True)

        self.temp_raw_json = os.path.join(
            output_dir, "temp_raw_pymupdf4llm.json")
        self.output_markdown_path = os.path.join(output_dir, "temp.md")

    def extract_markdown(self):
        """Extract markdown using pymupdf4llm and merge all page content."""
        print("Step 1: Extracting and merging markdown...")

        # Extract raw markdown without page chunks for viewing
        raw_markdown = pymupdf4llm.to_markdown(
            self.pdf_path, page_chunks=False, show_progress=True, ignore_images=True, ignore_graphics=True)
        markdown_output_path = f"{os.path.splitext(self.final_output_path)[0]}_markdown_raw.md"
        with open(markdown_output_path, "w", encoding="utf-8") as f:
            f.write(raw_markdown)

        # Extract page chunks with margins to remove footers
        # Note: margins is a heuristic to remove footers/headers, adjust as needed
        pages = pymupdf4llm.to_markdown(
            self.pdf_path, page_chunks=True, show_progress=True, margins=70)  # In Pts

        merged_text = ""
        page_map = []  # Track which sections came from which page(s)

        for page in pages:
            page_num = page.get("metadata", {}).get("page")
            text = page.get("text", "").replace("\f", "").strip()
            if not text:
                continue
            merged_text += text + "\n\n"
            # Record where this page ends in full text
            page_map.append((page_num, len(merged_text)))

        return merged_text, page_map

    def split_by_section_headers(self, merged_text):
        """Split the full merged markdown liberally using various header heuristics."""
        print("Step 2: Liberally splitting by section headers...")

        # Use regex to find potential headings
        header_pattern = re.compile(
            r"(?:^|\n)(?P<header>(\*{2}.*?\*{2})|(^#+\s+.+?$)|(^\d+\.\s+.+?$)|(^[A-Z][A-Z\s\-\d]{3,}$))",
            re.MULTILINE
        )

        matches = list(header_pattern.finditer(merged_text))
        sections = []

        # Iterate through all the matched headers in merged_text and split the content between them into separate sections. This will allow multi-page sections to be captured correctly.
        for i, match in enumerate(matches):
            # Iterate thorugh all matches
            raw_header = match.group("header").strip()
            # Extracts the actual matched header string (e.g., **1. Introduction**).
            start = match.end()

            if i + 1 < len(matches):
                end = matches[i + 1].start()
            else:
                end = len(merged_text)

            content = merged_text[start:end].strip()
            header_clean = re.sub(
                r"^\*{2}(.*?)\*{2}$", r"\1", raw_header).strip()

            if content:
                sections.append((header_clean, content))

        return sections

    def write_markdown_sections(self, sections):
        """Write the split sections into a single markdown file for review. Also needed as a temp file from which we can parse back to structured chunks."""
        print("Step 3: Writing markdown output...")

        with open(self.output_markdown_path, "w", encoding="utf-8") as f:
            for header, content in sections:
                f.write(f"**{header}**\n\n{content}\n\n")

        print(f"✓ Markdown output written to: {self.output_markdown_path}")

    def parse_markdown_to_chunks(self):
        """
        Parse the output markdown line-by-line, grouping consecutive `**...**` headers together
        and attaching the next block of non-header text as the chunk body.
        """
        print("Step 4: Parsing markdown into structured chunks...")

        chunks = []
        current_header_parts = []
        current_body_lines = []

        def flush_chunk():
            if current_header_parts or current_body_lines:
                header = " ".join(part.strip("*")
                                  for part in current_header_parts).strip()
                body = "\n".join(current_body_lines).strip()
                if body:
                    chunks.append({
                        "header": header,
                        "text": body,
                        "metadata": {}  # placeholder for future additions like section/page
                    })

        with open(self.output_markdown_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Check for bold header line
                if re.fullmatch(r"\*\*.*\*\*", line):
                    if current_body_lines:
                        flush_chunk()
                        current_body_lines = []
                        current_header_parts = []

                    current_header_parts.append(line)
                else:
                    if line == "":
                        continue
                    current_body_lines.append(line)

            flush_chunk()  # Final flush

        print(f"✓ Parsed {len(chunks)} chunks from markdown")
        return chunks

    def process(self):
        """Run the complete liberal PDF markdown pipeline and output structured JSON."""
        minimum_chunk_size = int(os.environ.get("MINIMUM_CHUNK_SIZE", 300))
        print(f"Processing PDF: {self.pdf_path}")
        print("=" * 60)

        # Step 1: Extract and merge markdown text
        merged_text, page_map = self.extract_markdown()

        # Step 2: Header-based split
        sections = self.split_by_section_headers(merged_text)

        # Step 3: Write markdown for inspection and further processing
        self.write_markdown_sections(sections)

        # Step 4: Parse markdown back to structured chunks
        parsed_chunks = self.parse_markdown_to_chunks()

        # Step 5: Assign page number based on location of each chunk in original merged text
        for chunk in parsed_chunks:
            body = chunk["text"]

            # Find approximate starting index of the body text in the merged markdown
            try:
                body_start = merged_text.index(body)
            except ValueError:
                body_start = -1  # fallback if text was slightly altered

            # Assign closest page number from page_map
            if body_start != -1:
                for i, (page_num, end_idx) in enumerate(page_map):
                    if body_start < end_idx:
                        chunk["metadata"]["page_number"] = page_num
                        break
                else:
                    chunk["metadata"]["page_number"] = None
            else:
                chunk["metadata"]["page_number"] = None

        # Step 5.1: Fill missing page numbers with previous valid one
        last_valid_page = None
        for chunk in parsed_chunks:
            if chunk["metadata"]["page_number"] is not None:
                last_valid_page = chunk["metadata"]["page_number"]
            else:
                chunk["metadata"]["page_number"] = last_valid_page

        # Final cleanup: replace all single newlines with space but preserve double newlines
        filtered_chunks = []
        for chunk in parsed_chunks:
            chunk["text"] = re.sub(r'(?<!\n)\n(?!\n)', ' ', chunk["text"])
            # Skip small chunks, default value is 300 which is an average of 50-60 words in a chunk, which is appropriate for a academic paper structure
            if len(chunk["text"]) < minimum_chunk_size:
                continue
            filtered_chunks.append(chunk)

        parsed_chunks = filtered_chunks

        # Step 5.2: Move 'header' into metadata and assign chunk index
        for idx, chunk in enumerate(parsed_chunks, start=1):
            chunk["metadata"]["header"] = chunk.pop("header")
            chunk["metadata"]["chunk_index"] = idx
            chunk["metadata"]["file_path"] = os.path.basename(self.pdf_path)
            chunk["metadata"]["token_count"] = len(chunk["text"])

        # Step 6: Also save as Markdown preview
        markdown_preview_path = f"{os.path.splitext(self.final_output_path)[0]}_final_preview.md"
        with open(markdown_preview_path, "w", encoding="utf-8") as md_out:
            for chunk in parsed_chunks:
                md_out.write(f"## Chunk_{chunk['metadata']['chunk_index']}\n")
                md_out.write("```\n")
                md_out.write(chunk["metadata"]["header"].strip() + "\n\n")
                md_out.write(chunk["text"].strip() + "\n")
                md_out.write("```\n\n")

        # Step 6: Save structured JSON
        with open(self.final_output_path, "w", encoding="utf-8") as f:
            json.dump(parsed_chunks, f, indent=2, ensure_ascii=False)

        token_counts = [chunk["metadata"]["token_count"]
                        for chunk in parsed_chunks]

        print("=" * 60)
        print(f"✅ Final output saved to: {self.final_output_path}")
        print(f"📦 Total structured chunks: {len(parsed_chunks)}")
        print(
            f"🔢 Token count — min: {min(token_counts)}, max: {max(token_counts)}")
        return parsed_chunks