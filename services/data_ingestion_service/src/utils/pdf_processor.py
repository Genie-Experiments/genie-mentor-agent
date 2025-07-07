import re
import os
import json
import logging
import fitz
import pymupdf4llm
from dotenv import load_dotenv


load_dotenv(override=True)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFProcessor:
    def __init__(self, pdf_path: str, output_dir: str = "./", output_filename: str = "processed_document.json"):
        """
        Initialize the PDF processor.

        Args:
            pdf_path: Path to the input PDF file
            output_dir: Directory where output file will be saved
            output_filename: Name of the final output JSON file
        """
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.output_filename = output_filename
        self.final_output_path = os.path.join(output_dir, output_filename)

        # Create output directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)

        # Temporary file paths
        self.temp_raw_json = os.path.join(
            output_dir, "temp_raw_pymupdf4llm.json")
        self.temp_cleaned_json = os.path.join(output_dir, "temp_cleaned.json")
        self.temp_docling_json = os.path.join(output_dir, "temp_docling.json")

    def make_json_serializable(self, obj):
        """Convert PyMuPDF objects to JSON-serializable format."""
        if isinstance(obj, fitz.Rect):
            return [obj.x0, obj.y0, obj.x1, obj.y1]
        elif isinstance(obj, (list, tuple)):
            return [self.make_json_serializable(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: self.make_json_serializable(v) for k, v in obj.items()}
        else:
            return obj

    def extract_with_pymupdf4llm(self):
        """Step 1: Extract structured data using pymupdf4llm."""
        print("Step 1: Extracting data with pymupdf4llm...")

        # Get structured data with metadata
        llm_data = pymupdf4llm.to_markdown(
            self.pdf_path, page_chunks=True, show_progress=True
        )

        # Make data JSON serializable
        serializable_llm_data = self.make_json_serializable(llm_data)

        # Save raw data
        with open(self.temp_raw_json, "w", encoding="utf-8") as f:
            json.dump(serializable_llm_data, f, ensure_ascii=False, indent=2)

        print("✓ pymupdf4llm extraction complete")
        return serializable_llm_data

    def postprocess_pages(self, raw_data):
        """Step 2: Clean and structure the extracted data."""
        print("Step 2: Post-processing pages...")

        processed_pages = []
        for page in raw_data:
            meta = page.get("metadata", {})
            trimmed_metadata = {
                "file_path": meta.get("file_path"),
                "page_count": meta.get("page_count"),
                "page": meta.get("page")
            }

            toc_items = [item[1]
                         for item in page.get("toc_items", []) if len(item) >= 2]

            cleaned = {
                "metadata": trimmed_metadata,
                "toc_items": toc_items,
                "text": page.get("text", "")
            }

            processed_pages.append(cleaned)

        with open(self.temp_cleaned_json, 'w', encoding='utf-8') as f:
            json.dump(processed_pages, f, indent=2, ensure_ascii=False)

        print("✓ Post-processing complete")
        return processed_pages

    def add_section_titles(self, data):
        """Step 4: Extract section titles from TOC and assign to pages."""
        print("Step 4: Adding section titles...")

        # Find the Table of Contents page
        toc_entry = None
        for entry in data:
            if "table of contents" in entry["text"].lower():
                toc_entry = entry
                break

        if not toc_entry:
            print(
                "⚠ Warning: Table of contents page not found. Skipping section title assignment.")
            return data

        toc_text = toc_entry["text"]

        # Extract section titles and page numbers using regex
        toc_pattern = re.compile(
            r"\n(?!\*\*)([A-Z][^\n*]+?)\s+\*{2}(\d+)\*{2}")
        matches = toc_pattern.findall(toc_text)

        sections = []
        for title, page_str in matches:
            sections.append((title.strip(), int(page_str)))

        # Sort by page number ascending
        sections.sort(key=lambda x: x[1])

        # Assign parent_title to each page
        for entry in data:
            current_page = entry["metadata"]["page"]
            parent_title = None

            for i, (title, page_num) in enumerate(sections):
                if current_page >= page_num:
                    if i + 1 < len(sections):
                        if current_page < sections[i + 1][1]:
                            parent_title = title
                            break
                    else:
                        parent_title = title

            entry["metadata"]["parent_title"] = parent_title

        print("✓ Section titles added")
        return data

    def final_cleanup(self, data):
        """Step 5: Remove unnecessary fields and reorganize structure."""
        print("Step 5: Final cleanup and restructuring...")

        cleaned_data = []
        for entry in data:
            metadata = entry.get("metadata", {})

            # Merge all non-essential fields into metadata
            for key in list(entry.keys()):
                if key not in ["metadata", "text"]:
                    metadata[key] = entry[key]

            cleaned_entry = {
                "metadata": metadata,
                "text": entry.get("text", "")
            }
            cleaned_data.append(cleaned_entry)

        print("✓ Final cleanup complete")
        return cleaned_data

    def final_processing(self, data):
        """Step 6: Final text processing."""
        print("Step 6: Final text processing...")

        # Process each page
        for entry in data:
            metadata = entry["metadata"]
            page_num = metadata.get("page")

            # Rename metadata keys for consistency
            if "toc_items" in metadata:
                metadata["section_header"] = metadata.pop("toc_items")
            if "parent_title" in metadata:
                metadata["main_section_header"] = metadata.pop("parent_title")

        print("✓ Final text processing complete")
        return data

    def cleanup_temp_files(self):
        """Remove temporary files."""
        temp_files = [self.temp_raw_json,
                      self.temp_cleaned_json, self.temp_docling_json]
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        print("✓ Temporary files cleaned up")

    def process(self, cleanup_temp=True, extract_images=True):
        """Run the complete PDF processing pipeline."""
        try:
            print(f"Processing PDF: {self.pdf_path}")
            print(f"Output will be saved to: {self.final_output_path}")
            print("=" * 60)

            # Step 1: Extract with pymupdf4llm
            raw_data = self.extract_with_pymupdf4llm()

            # Step 2: Post-process and clean data
            cleaned_data = self.postprocess_pages(raw_data)

            # Step 4: Add section titles from TOC
            titled_data = self.add_section_titles(cleaned_data)

            # Step 5: Final cleanup and restructuring
            cleaned_data = self.final_cleanup(titled_data)

            # Step 6: Perform final text processing
            final_data = self.final_processing(cleaned_data)

            # Save final output
            with open(self.final_output_path, "w", encoding="utf-8") as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2)

            # Cleanup temporary files
            if cleanup_temp:
                self.cleanup_temp_files()

            print("=" * 60)
            print(
                f"✅ Processing complete! Final output saved to: {self.final_output_path}")

            # Print summary statistics
            total_pages = len(final_data)
            pages_with_sections = sum(1 for page in final_data if page.get(
                "metadata", {}).get("main_section_header"))

            print(f"📊 Summary:")
            print(f"   • Total pages: {total_pages}")
            print(f"   • Pages with section titles: {pages_with_sections}")

            return final_data

        except Exception as e:
            print(f"❌ Error during processing: {str(e)}")
            raise
