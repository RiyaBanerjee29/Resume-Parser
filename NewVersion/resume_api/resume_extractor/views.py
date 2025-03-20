import os
import fitz  # PyMuPDF
import json
import re
import ollama
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        return {"error": f"Error opening PDF: {str(e)}"}

    all_text = ""
    for page in doc:
        all_text += page.get_text("text") + "\n"

    doc.close()
    return all_text.strip()

def extract_resume_info(text):
    model = "gemma3:4b"
    prompt = f"""
    Extract the following details from the given resume:
    - Name
    - Email
    - Phone Number
    - Skills
    - Work Experience (company name, job title, start date, end date)
    - Projects
    - Education (degree, institution, start_year, end_year)
    - Certifications
    - Hobbies
    - Languages

    Return output as a **valid JSON object**.

    Resume Text:
    {text}
    """

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    raw_content = ""
    for chunk in response:
        raw_content += chunk.message.content

    cleaned_json = re.sub(r"```json|```", "", raw_content).strip()
    cleaned_json = re.sub(r"(?<!\\)\n", " ", cleaned_json)  

    try:
        extracted_info = json.loads(cleaned_json)
    except json.JSONDecodeError:
        extracted_info = {"error": "Failed to parse extracted data."}

    return extracted_info

@api_view(["POST"])
def upload_resume(request):
    print("Request received")
    if "resume" not in request.FILES:
        return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES["resume"]
    file_path = default_storage.save(f"resumes/{uploaded_file.name}", ContentFile(uploaded_file.read()))

    extracted_text = extract_text_from_pdf(file_path)
    if "error" in extracted_text:
        return Response({"error": extracted_text["error"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    extracted_data = extract_resume_info(extracted_text)

    return Response(extracted_data, status=status.HTTP_200_OK)
