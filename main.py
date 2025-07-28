import fitz  # PyMuPDF
import json
import os
import time
import torch
from sentence_transformers import SentenceTransformer, util
import numpy as np

# --- Configuration ---
MODEL_NAME = 'all-MiniLM-L6-v2'
INPUT_DIR = "input"
OUTPUT_DIR = "output"
DOCUMENTS_DIR = os.path.join(INPUT_DIR, "documents")
PERSONA_FILE = os.path.join(INPUT_DIR, "persona1.json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "challenge1b_output3.json")

# --- Load SentenceTransformer model ---
def load_model(model_name):
    print(f"Loading model: {model_name}...")
    model = SentenceTransformer(model_name)
    print("Model loaded successfully.")
    return model

# --- Extract text sections from PDF ---
def extract_text_sections(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        paragraphs = text.split('\n\n')
        for para in paragraphs:
            if para.strip():
                sections.append({
                    "document": os.path.basename(pdf_path),
                    "page_number": page_num + 1,
                    "text": para.strip()
                })
    return sections

# --- Process all documents for one persona ---
def process_documents(model, persona_data):
    role = persona_data['persona'].get('role', '')
    expertise_list = persona_data['persona'].get('expertise', [])
    if expertise_list:
        expertise = ', '.join(expertise_list)
        persona_text = f"Persona: {role} (Expertise: {expertise}). Job: {persona_data['job_to_be_done']}"
    else:
        persona_text = f"Persona: {role}. Job: {persona_data['job_to_be_done']}"
    persona_embedding = model.encode(persona_text, convert_to_tensor=True)

    all_sections = []
    pdf_files = [f for f in os.listdir(DOCUMENTS_DIR) if f.lower().endswith(".pdf")]

    for filename in pdf_files:
        pdf_path = os.path.join(DOCUMENTS_DIR, filename)
        print(f"Extracting text from {filename}...")
        all_sections.extend(extract_text_sections(pdf_path))

    if not all_sections:
        return [], []

    print("Encoding document sections...")
    section_texts = [section['text'] for section in all_sections]
    section_embeddings = model.encode(section_texts, convert_to_tensor=True)

    print("Calculating similarity scores...")
    cosine_scores = util.pytorch_cos_sim(persona_embedding, section_embeddings)[0]

    for i, section in enumerate(all_sections):
        section['score'] = cosine_scores[i].item()

    all_sections.sort(key=lambda x: x['score'], reverse=True)

    extracted_sections = []
    sub_section_analysis = []

    for i, section in enumerate(all_sections[:20]):
        extracted_sections.append({
            "document": section['document'],
            "page_number": section['page_number'],
            "section_title": f"Relevant Paragraph (Score: {section['score']:.2f})",
            "importance_rank": i + 1
        })
        sub_section_analysis.append({
            "document": section['document'],
            "page_number": section['page_number'],
            "refined_text": section['text'],
            "importance_rank": i + 1
        })

    return extracted_sections, sub_section_analysis

# --- Main Logic ---
def main():
    start_time = time.time()

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if not os.path.exists(PERSONA_FILE):
        print(f"❌ persona.json not found at {PERSONA_FILE}")
        return

    with open(PERSONA_FILE, 'r') as f:
        persona_json = json.load(f)

    # Support either one persona or multiple personas
    personas = []
    if isinstance(persona_json, list):
        personas = persona_json
    elif "personas" in persona_json:
        personas = persona_json["personas"]
    elif "persona" in persona_json:
        personas = [persona_json]
    else:
        print("❌ Invalid persona format.")
        return

    model = load_model(MODEL_NAME)

    all_outputs = []

    for idx, persona in enumerate(personas):
        print(f"\n--- Processing Persona {idx + 1}: {persona['persona'].get('role', 'Unknown Role')} ---")

        extracted_sections, sub_section_analysis = process_documents(model, {
            "persona": persona["persona"],
            "job_to_be_done": persona["job_to_be_done"]
        })

        all_outputs.append({
            "metadata": {
                "input_documents": [os.path.join(DOCUMENTS_DIR, f) for f in os.listdir(DOCUMENTS_DIR)],
                "persona": persona['persona'].get('role', "Unknown Role"),
                "job_to_be_done": persona["job_to_be_done"],
                "processing_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            },
            "extracted_section": extracted_sections,
            "sub-section_analysis": sub_section_analysis
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_outputs, f, indent=4, ensure_ascii=False)

    end_time = time.time()
    print(f"\n✅ Processing complete in {end_time - start_time:.2f} seconds.")
    print(f"📄 Output saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
