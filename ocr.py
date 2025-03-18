import os
import fitz  # PyMuPDF

def extract_text_dynamic(pdf_path):
    """
    Extract text from a PDF file while preserving multi-column structure.
    """
    print(f"Processing PDF file: {pdf_path}")

    try:
        doc = fitz.open(pdf_path)
        print(f"PDF has {len(doc)} page(s)")
    except Exception as e:
        print(f"Error opening PDF: {e}")
        return None

    all_text = ""
    for page_num, page in enumerate(doc):
        print(f"Processing page {page_num + 1}/{len(doc)}...")

        # Extract text blocks
        blocks = page.get_text("blocks")  # Extract text with bounding boxes
        blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by Y (top to bottom), then X

        page_width = page.rect.width
        mid_x = page_width / 2  # Find middle of page

        left_column = []
        right_column = []
        full_text = []

        # Check if text spans across both columns
        multi_column = any(b[0] < mid_x and b[2] > mid_x for b in blocks)

        for b in blocks:
            text = b[4].strip()
            if not text:
                continue

            if multi_column:  # Multi-column layout
                if b[0] < mid_x:
                    left_column.append(text)
                else:
                    right_column.append(text)
            else:
                full_text.append(text)

        if multi_column:
            page_text = f"\n--- PAGE {page_num + 1} ---\n\n"
            page_text += "\n".join(left_column) + "\n\n" + "\n".join(right_column)
        else:
            page_text = f"\n--- PAGE {page_num + 1} ---\n\n" + "\n".join(full_text)

        all_text += page_text + "\n"

    doc.close()
    return all_text

def process_file(file_path):
    """
    Process a PDF file and extract structured text.
    """
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.pdf':
        return extract_text_dynamic(file_path)
    else:
        print(f"Unsupported file format: {file_ext}")
        return None

def extract_pdf_text():
    """
    Extract text from a sample resume PDF in the 'resume' folder.
    """
    resume_folder = os.path.join(os.getcwd(), "resume")
    if not os.path.exists(resume_folder):
        print(f"Error: Resume folder not found at {resume_folder}")
        return

    sample_resume = None
    for file in os.listdir(resume_folder):
        if file.startswith("sample_resume") and file.endswith(".pdf"):
            sample_resume = os.path.join(resume_folder, file)
            break

    if sample_resume is None:
        print("Error: sample_resume PDF not found in the resume folder")
        return

    extracted_text = process_file(sample_resume)
    
    if extracted_text:
        print("\nExtracted Text:")
        print("-" * 50)
        print(extracted_text)
        print("-" * 50)
        
        output_file = os.path.join(resume_folder, "extracted_text.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(extracted_text)
        print(f"Extracted text saved to: {output_file}")
