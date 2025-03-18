import os
import time
from ocr import extract_pdf_text
from resumeExtraction import extract_resume_info
import json

def main():
    # Step 1: Run OCR extraction to extract text from resume
    print("Starting  texttraction...")
    extract_pdf_text()
    
    # Define the path to the extracted text file
    extracted_text_file = "resume/extracted_text.txt"
    
    # Wait for the OCR process to complete (ensure file is created)
    if not os.path.exists(extracted_text_file):
        print("Error: OCR extraction did not generate the expected output file.")
        return
    
    # Step 2: Read the extracted text
    print("Reading extracted resume text...")
    try:
        with open(extracted_text_file, "r", encoding="utf-8") as file:
            resume_text = file.read()
    except FileNotFoundError:
        print("Error: Extracted text file not found.")
        return
    
    # Step 3: Process the extracted text with LLM to extract structured data
    print("Extracting structured resume information...")
    extracted_data = extract_resume_info(resume_text)
    
    if extracted_data:
        print("Extracted Resume Information:")
        print(json.dumps(extracted_data, indent=4))
        
        # Save the extracted data to a JSON file
        output_file = "resume/extracted_resume_info.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=4)
        print(f"Extracted data saved to: {output_file}")
    else:
        print("Error: Could not extract structured resume information.")

if __name__ == "__main__":
    main()