import ollama
import json
import re

def extract_resume_info(text):
    """
    Extracts structured information (name, email, phone, skills, work experience) from the given resume text using an LLM.
    """
    model = "gemma:2b"  
    prompt = f"""
    Extract the following information from the given resume text:
    - Name
    - Email
    - Phone Number
    - Skills
    - Work Experiences: Extract all work experiences. Each experience should be a dictionary with the following keys: company_name, job_title, start_date, end_date, and a description of achievements/tasks. If the end date is ongoing or not explicitly mentioned, use "Present".
    - Projects
    - Educational Qualifications: Extract all educational qualifications. Each qualification should be a dictionary with the following keys: degree, institution, end_year and start_year  (if mentioned).
    - Certifications
    - Hobbies
    - Languages

    Return the output **strictly as a valid JSON object** with no extra text.

    Resume Text:
    {text}  
   
    """

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    raw_content = response.message.content  
    print("Raw LLM Response:", raw_content)  # Debugging print

    # ✅ Step 1: Remove unwanted formatting (like markdown backticks)
    cleaned_json = re.sub(r"```json|```", "", raw_content).strip()

    # ✅ Step 2: Fix invalid newline characters inside JSON strings
    cleaned_json = re.sub(r"(?<!\\)\n", " ", cleaned_json)  # Replace unescaped newlines with spaces

    # ✅ Step 3: Attempt to parse the JSON safely
    try:
        extracted_info = json.loads(cleaned_json)
    except json.JSONDecodeError as e:
        print("Error: Could not parse JSON output from LLM.", e)
        extracted_info = None

    return extracted_info

if __name__ == "__main__":
    resume_text_file = "resume/extracted_text.txt"

    try:
        with open(resume_text_file, "r", encoding="utf-8") as file:
            resume_text = file.read()
    except FileNotFoundError:
        print("Error: Extracted resume text file not found.")
        exit(1)

    extracted_data = extract_resume_info(resume_text)

    if extracted_data:
        print("Extracted Resume Information:")
        print(json.dumps(extracted_data, indent=4))

        # Save extracted data to a JSON file
        output_file = "resume/extracted_resume_info.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=4)
        print(f"Extracted data saved to: {output_file}")
    else:
        print("Error: Could not extract structured resume information.")
