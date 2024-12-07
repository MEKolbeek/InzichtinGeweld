import re
import fitz  # PyMuPDF om PDF te lezen

# Functie om tekst uit een PDF te lezen
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Functie om zinnen met jaartallen te extraheren
def extract_sentences_with_years(pdf_path):
    # Lees de tekst uit de PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    print(f"DEBUG: Lengte van uitgelezen tekst: {len(pdf_text)} karakters")
    
    # Regex om zinnen met jaartallen te vinden (zoek zinnen die eindigen op een punt, vraagteken of uitroepteken)
    year_sentence_pattern = r'([^.?!]*\b\d{4}\b[^.?!]*[.?!])'
    matches = re.findall(year_sentence_pattern, pdf_text)
    
    # Tel het aantal jaartallen
    year_count = sum(len(re.findall(r'\b\d{4}\b', match)) for match in matches)
    
    # Resultaten printen
    print(f"Aantal jaartallen gevonden: {year_count}")
    print("Zinnen met jaartallen:")
    for match in matches:
        print("-", match.strip())

# Test met een voorbeeld-PDF-bestand
extract_sentences_with_years(r"C:\Users\mkolb\Documents\ECLI_NL_RBROT_2010_BN3932.pdf")
