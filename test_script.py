import os
from PDFProcessor import PDFProcessor

# Folder containing PDFs
input_folder = "GMA-KB-Index-Docuements"
output_folder = "./test_output"

# Make sure output directory exists
os.makedirs(output_folder, exist_ok=True)

# Loop over all PDF files in the folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(input_folder, filename)
        output_filename = f"{os.path.splitext(filename)[0]}.json"

        print(f"\n🔄 Processing: {filename}")

        processor = PDFProcessor(
            pdf_path=pdf_path,
            output_dir=output_folder,
            output_filename=output_filename
        )

        processor.process()  # This already saves output to file

print(f"\n✅ Batch processing complete. Outputs saved in: {output_folder}")
