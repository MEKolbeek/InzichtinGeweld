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
        response = requests.post(API_URL, json=payload, timeout=300, stream=True)
        response.raise_for_status()

        # Verwerk de streaming response
        lines = response.iter_lines(decode_unicode=True)
        full_text = process_streaming_response(lines)
        return full_text.strip()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Fout bij API-aanroep: {e}")

# Functie om specifieke indicatoren uit een tekst te halen met focus op geweldsincidenten
def extract_indicators_with_context(pdf_text):
    # Relevante secties filteren op basis van contextuele woorden
    relevant_text = extract_relevant_section(pdf_text)
    
    indicators = {
        "incident_date": (
            "In de volgende tekst staan meerdere datums. Identificeer de datum die het meest waarschijnlijk "
            "verwijst naar een geweldsincident waarbij de politie betrokken was. Gebruik contextuele aanwijzingen zoals "
            "'optreden van de politie', 'politiegeweld', 'gebruik van geweld', 'aanhouding', of soortgelijke termen. "
            "Negeer datums die gerelateerd zijn aan juridische processen, rapportages, of administratieve vermeldingen. "
            "Geef alleen de datum terug in het formaat DD-MM-YYYY."
        ),
        "incident_location": (
            "In de volgende tekst worden meerdere locaties genoemd. Identificeer de locatie die het meest waarschijnlijk "
            "verband houdt met een geweldsincident waarbij de politie betrokken was. Gebruik contextuele aanwijzingen zoals "
            "'plaats van het geweld', 'locatie van de aanhouding', 'optreden van de politie', of soortgelijke termen. "
            "Geef alleen de naam van de locatie terug, zonder extra tekst."
        ),
        "weather_conditions": "Wat waren de weersomstandigheden tijdens het geweldsincident?",
        "time_of_day": "Was het dag of nacht ten tijde van het geweldsincident? Geef 'dag' of 'nacht' als antwoord."
    }
    results = {}

    for key, prompt_question in indicators.items():
        prompt = (
            f"Hier is een tekst:\n\n{relevant_text}\n\n"
            f"{prompt_question}\n"
            f"Geef alleen een kort antwoord zonder andere tekst."
        )
        output = query_llama(prompt)
        results[key] = output.strip()

    return results

# Functie om relevante secties te filteren op basis van contextuele woorden
def extract_relevant_section(pdf_text):
    keywords = [
        "geweld", "politie", "incident", "aanhouding", "optreden", "gebruik van geweld",
        "mishandeling", "bedreiging", "schermutseling", "arrestatie", "escalatie", "confrontatie",
        "schoten", "geweldsgebruik", "politieoptreden", "politie-inzet", "verdachte", "overtreding",
        "interventie", "openbaar gezag", "politieonderzoek", "rel", "plaats delict", "locatie",
        "situatie", "omgeving", "openbare ruimte", "politiebureau", "straat", "woning",
        "feitenrelaas", "proces-verbaal", "verklaring", "getuigenverslag", "tenlastelegging",
        "datum", "tijdstip", "moment", "periode"
    ]
    relevant_text = []
    for line in pdf_text.splitlines():
        if any(keyword in line.lower() for keyword in keywords):
            relevant_text.append(line)
    return "\n".join(relevant_text) if relevant_text else pdf_text

# Functie om alle PDF-bestanden in een map te vinden
def find_pdfs_in_directory(directory):
    return [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.pdf')]

# Functie om een unieke bestandsnaam te genereren
def generate_unique_filename(base_name):
    if not os.path.exists(base_name):
        return base_name

    counter = 1
    while True:
        new_name = f"{os.path.splitext(base_name)[0]}_{counter}{os.path.splitext(base_name)[1]}"
        if not os.path.exists(new_name):
            return new_name
        counter += 1

# Functie om meerdere PDF's te verwerken
def process_multiple_pdfs_with_indicators(pdf_directory, output_file):
    pdf_files = find_pdfs_in_directory(pdf_directory)
    results = []

    for pdf_file in pdf_files:
        print(f"Verwerken van bestand: {pdf_file}")
        pdf_text = extract_text_from_pdf(pdf_file)
        indicators = extract_indicators_with_context(pdf_text)
        indicators["file_name"] = os.path.basename(pdf_file)
        results.append(indicators)

    # Controleer of het CSV-bestand al bestaat en genereer een unieke naam indien nodig
    output_file = generate_unique_filename(output_file)

    # Schrijf de resultaten naar een CSV-bestand
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["file_name", "incident_date", "incident_location", "weather_conditions", "time_of_day"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Verwerking voltooid. Resultaten opgeslagen in {output_file}")

# Specificeer de map met PDF's en de output-bestandsnaam
pdf_directory = r"C:\Users\mkolb\Documents\Uitspraken
output_file = r"C:\Users\mkolb\Documents\incident_indicators.csv"

# Verwerk alle PDF's
process_multiple_pdfs_with_indicators(pdf_directory, output_file)
