import requests
import fitz  # PyMuPDF om PDF te lezen

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

# Functie om het Llama-model op Hugging Face te bevragen voor zinnen met het woord "verdachte"
def query_llama(text):
    payload = {
        "inputs": f"Geef alleen de zinnen met het woord 'verdachte' in de volgende tekst:\n\n{text}\n\n",
        "parameters": {"max_new_tokens": 200}
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# Hoofdfunctie om PDF te verwerken en zinnen met "verdachte" te extraheren
def extract_sentences_with_suspect(pdf_path):
    # Stap 1: Tekst uit PDF halen
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Deel de tekst in kleinere stukken om het volledige document te doorzoeken
    chunk_size = 2000  # Limiteer de tekst tot 2000 karakters per query
    suspect_sentences = []
    suspect_count = 0
    
    for i in range(0, len(pdf_text), chunk_size):
        chunk = pdf_text[i:i+chunk_size]
        
        # Stap 2: Stuur het tekstfragment naar Llama-model om zinnen met "verdachte" te vinden
        response = query_llama(chunk)
        
        if isinstance(response, dict) and 'error' in response:
            print("Fout:", response['error'])
            continue
        
        # Stap 3: Verwerk het resultaat en voeg de gevonden zinnen toe aan de lijst
        if isinstance(response, list) and 'generated_text' in response[0]:
            generated_text = response[0]['generated_text']
            sentences = generated_text.splitlines()
            
            # Filteren van zinnen die daadwerkelijk "verdachte" bevatten
            chunk_suspect_sentences = [sentence.strip() for sentence in sentences if "verdachte" in sentence.lower()]
            suspect_sentences.extend(chunk_suspect_sentences)
            
            # Tellen van het aantal keer dat "verdachte" voorkomt in dit fragment
            suspect_count += sum(sentence.lower().count("verdachte") for sentence in chunk_suspect_sentences)
    
    # Weergave resultaten
    print("Aantal keer dat 'verdachte' voorkomt in het document:", suspect_count)
    print("Zinnen met 'verdachte':")
    for sentence in suspect_sentences:
        print("-", sentence)

# Test met een voorbeeld-PDF-bestand
extract_sentences_with_suspect(r"C:\Users\mkolb\Documents\ECLI_NL_RBROT_2010_BN3932.pdf")
