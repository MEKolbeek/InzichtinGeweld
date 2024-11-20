import requests
import fitz  # PyMuPDF om PDF te lezen
import re

# Stel de Hugging Face API-URL en headers in met je token
API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B"
headers = {"Authorization": "Bearer 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"}

# Functie om tekst uit een PDF te lezen
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Functie om zinnen met een mogelijke datum te filteren met regex
def get_date_sentences_candidates(text):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)  # Slimme splitsing in zinnen
    date_pattern = r"\b\d{2}-\d{2}-\d{4}\b"  # Datum in DD-MM-YYYY
    return [sentence.strip() for sentence in sentences if re.search(date_pattern, sentence)]

# Functie om het LLaMA-model te bevragen
def query_llama(sentence):
    payload = {
        "inputs": f"Bevestig of deze zin een datum bevat en geef alleen de zin terug als er een datum in staat:\n\n{sentence}\n\n",
        "parameters": {"max_new_tokens": 400}
    }
    response = requests.post(API_URL, headers=headers, json=payload, timeout=300)
    return response.json()

# Hoofdfunctie om PDF te verwerken en zinnen met datums te extraheren
def extract_sentences_with_dates(pdf_path):
    # Stap 1: Tekst uit PDF halen
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Stap 2: Filter zinnen met regex om de input te beperken
    candidate_sentences = get_date_sentences_candidates(pdf_text)
    print(f"Aantal zinnen met mogelijke datums: {len(candidate_sentences)}")
    
    # Stap 3: Stuur zinnen één voor één naar LLaMA
    confirmed_date_sentences = []
    for sentence in candidate_sentences:
        response = query_llama(sentence)
        
        if isinstance(response, dict) and 'error' in response:
            print("Fout:", response['error'])
            continue
        
        if isinstance(response, list) and 'generated_text' in response[0]:
            generated_text = response[0]['generated_text'].strip()
            if generated_text:  # Controleer of er een geldige output is
                confirmed_date_sentences.append(generated_text)
    
    # Stap 4: Toon resultaten
    print("Bevestigde zinnen met datums:")
    for sentence in confirmed_date_sentences:
        print("-", sentence)

# Test met een voorbeeld-PDF-bestand
extract_sentences_with_dates(r"C:\Users\mkolb\Documents\ECLI_NL_RBROT_2010_BN3932.pdf")
