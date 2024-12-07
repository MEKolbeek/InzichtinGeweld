import requests
import fitz  # PyMuPDF om PDF's te lezen
import re

API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"
headers = {"Authorization": "Bearer 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"}

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def query_llama(text):
    payload = {
        "inputs": f"Geef een lijst met alleen de zinnen die een jaartal bevatten uit de volgende tekst:\n\n{text}\n\n",
        "parameters": {"max_new_tokens": 200}
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
    return response.json()

def extract_sentences_with_years(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    chunk_size = 2000
    year_sentences = []

    for i in range(0, len(pdf_text), chunk_size):
        chunk = pdf_text[i:i+chunk_size]
        response = query_llama(chunk)

        if isinstance(response, dict) and 'error' in response:
            print("Fout:", response['error'])
            continue

        if isinstance(response, list) and 'generated_text' in response[0]:
            generated_text = response[0]['generated_text']
            sentences = generated_text.splitlines()

            # Extra filtering voor zinnen met een jaartal
            for sentence in sentences:
                if re.search(r"\b(19|20)\d{2}\b", sentence):  # Controleer op jaartal zoals 1999 of 2022
                    year_sentences.append(sentence)

    print("Zinnen met jaartallen:")
    for sentence in year_sentences:
        print("-", sentence)

# Test met een voorbeeld-PDF
extract_sentences_with_years(r"C:\Users\mkolb\Documents\ECLI_NL_RBROT_2010_BN3932.pdf")
