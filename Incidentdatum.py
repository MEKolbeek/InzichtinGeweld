import requests
import fitz  # PyMuPDF om PDF's te lezen
import re
import json

API_URL = "http://localhost:11434/api/generate"  # Zorg dat deze klopt
MODEL_NAME = "llama3.2"

# Functie om tekst uit een PDF te halen
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Functie om een LLaMA-model op te slaan
def save_llama_model(api_url, model_name, save_path):
    payload = {"model": model_name, "action": "save", "path": save_path}
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        print("Model succesvol opgeslagen.")
    except requests.exceptions.RequestException as e:
        print(f"Fout bij opslaan van model: {e}")

# Functie om een LLaMA-model te laden
def load_llama_model(api_url, model_name, load_path):
    payload = {"model": model_name, "action": "load", "path": load_path}
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        print("Model succesvol geladen.")
    except requests.exceptions.RequestException as e:
        print(f"Fout bij laden van model: {e}")

# Functie om een prompt naar LLaMA te sturen en streaming resultaten te verwerken
def query_llama_streaming(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 200,
    }
    try:
        response = requests.post(API_URL, json=payload, stream=True, timeout=120)
        response.raise_for_status()
        return response.iter_lines()  # Streaming respons
    except requests.exceptions.RequestException as e:
        raise Exception(f"Fout bij API-aanroep: {e}")

# Functie om streaming response te verwerken
def process_streaming_response(lines):
    full_text = ""
    try:
        for line in lines:
            if line:  # Controleer of de lijn niet leeg is
                try:
                    json_line = json.loads(line)
                    if "response" in json_line:
                        full_text += json_line["response"]
                except json.JSONDecodeError:
                    print(f"Fout bij verwerken van regel: {line}")
        return full_text
    except Exception as e:
        print(f"Fout bij verwerking van streaming data: {e}")
        return ""

# Functie om zinnen met datums uit een PDF te halen
def extract_sentences_with_dates(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)
    chunk_size = 2000
    date_sentences = []

    for i in range(0, len(pdf_text), chunk_size):
        chunk = pdf_text[i:i + chunk_size]
        prompt = f"Wat is de datum van het incident/voorval uit de volgende tekst:\n\n{chunk}\n\n"
        lines = query_llama_streaming(prompt)
        output = process_streaming_response(lines)

        if output:
            # Split de output in zinnen en filter op datums
            sentences = [line.strip() for line in output.split("\n") if line]
            for sentence in sentences:
                if re.search(r"\b(19|20)\d{2}\b", sentence):  # Controleer op jaartallen
                    date_sentences.append(sentence)

    print("Zinnen met datums:")
    for sentence in date_sentences:
        print("-", sentence)

# Opslaan en laden van het model
SAVE_PATH = "C:/Users/mkolb/Documents/llama_model_saved.bin"
LOAD_PATH = "C:/Users/mkolb/Documents/llama_model_saved.bin"

# Opslaan van het model
save_llama_model(API_URL, MODEL_NAME, SAVE_PATH)

# Laden van het model
load_llama_model(API_URL, MODEL_NAME, LOAD_PATH)

# Test met een voorbeeld-PDF
extract_sentences_with_dates(r"C:\Users\mkolb\Documents\ECLI_NL_RBROT_2010_BN3932.pdf")
