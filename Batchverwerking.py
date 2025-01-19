import os
import csv
import fitz  # PyMuPDF om PDF's te lezen
import requests
import json
import re

API_URL = "http://localhost:11434/api/generate"  # Zorg dat deze klopt
MODEL_NAME = "llama3.2"

# Functie om tekst uit een PDF te halen
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

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

# Functie om een prompt naar LLaMA te sturen en de response te verwerken
def query_llama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 200,
    }
    try:
        response = requests.post(API_URL, json=payload, timeout=500, stream=True)
        response.raise_for_status()

        # Verwerk de streaming response
        lines = response.iter_lines(decode_unicode=True)
        full_text = process_streaming_response(lines)
        return full_text.strip()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Fout bij API-aanroep: {e}")

# Functie om de incidentdatum uit een enkele PDF te halen
def extract_incident_date(pdf_path):
    pdf_text = extract_text_from_pdf(pdf_path)

    # Gebruik de volledige tekst in één keer
    prompt = (
        f"Hier is een tekst die meerdere datums bevat. Gebruik de context van de tekst "
        f"om te bepalen welke datum hoort bij een incident of voorval.\n\n"
        f"Tekst:\n{pdf_text}\n\n"
        f"Wat is de datum van het incident? Als je twijfelt, kies dan de meest waarschijnlijke datum "
        f"op basis van context. Geef alleen de datum terug in het formaat DD-MM-YYYY."
    )
    output = query_llama(prompt)

    # Controleer of de output een datum bevat
    match = re.search(r"\b\d{2}-\d{2}-\d{4}\b", output)
    if match:
        return match.group()
    else:
        print("Geen geldige datum gevonden in de API-response:", output)
        return "Geen geldige datum gevonden"

# Functie om alle PDF-bestanden in een map te vinden
def find_pdfs_in_directory(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.pdf')]

# Functie om meerdere PDF's te verwerken
def process_multiple_pdfs(pdf_directory, output_file):
    pdf_files = find_pdfs_in_directory(pdf_directory)
    results = []

    for pdf_file in pdf_files:
        print(f"Verwerken van bestand: {pdf_file}")
        incident_date = extract_incident_date(pdf_file)
        results.append({
            "file_name": os.path.basename(pdf_file),
            "incident_date": incident_date
        })
    
    # Resultaten opslaan in een CSV-bestand
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["file_name", "incident_date"])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Verwerking voltooid. Resultaten opgeslagen in {output_file}")

# Specificeer de map met PDF's en de output-bestandsnaam
pdf_directory = r"C:\Users\mkolb\Documents\Uitspraken"  
output_file = r"C:\Users\mkolb\Documents\incident_dates.csv"

# Verwerk alle PDF's
process_multiple_pdfs(pdf_directory, output_file)
