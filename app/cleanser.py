import spacy
import re
from rich.console import Console
from faker import Faker

console = Console()
fake = Faker()

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    console.print("[bold yellow]Downloading spaCy model...[/bold yellow]")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def cleanse_text(raw_text):
    """
    Cleanses text by REPLACING sensitive data with realistic FAKE data.
    """
    console.print("  🛡️ [bold]Cleansing:[/] Synthesizing realistic fake data to replace PII...")
    if not raw_text: return ""

    doc = nlp(raw_text)
    cleansed_text = raw_text
    replacements = {}

    for ent in doc.ents:
        original_text = ent.text
        if original_text in replacements:
            continue

        if ent.label_ == "PERSON":
            replacements[original_text] = fake.name()
        elif ent.label_ == "ORG":
            replacements[original_text] = fake.company()
        elif ent.label_ in ["GPE", "LOC"]:
            replacements[original_text] = fake.city()
        elif ent.label_ == "DATE":
            replacements[original_text] = fake.date()
        # Add more entity types as needed

    for original, fake_data in replacements.items():
        cleansed_text = cleansed_text.replace(original, fake_data)

    cleansed_text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b', lambda m: fake.email(), cleansed_text)
    cleansed_text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', lambda m: fake.ipv4(), cleansed_text)

    snippet = cleansed_text.replace('\n', ' ').strip()[:150]
    console.print(f"  ↪ [dim]Synthesized snippet: \"{snippet}...\"[/dim]")

    return cleansed_text

def cleanse_images(image_paths):
    if image_paths:
        console.print("  🖼️ [bold]Image Scan:[/] [yellow]Note: Logo removal is a placeholder.[/yellow]")
    return image_paths