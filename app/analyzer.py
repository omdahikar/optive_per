import google.generativeai as genai
import os
from dotenv import load_dotenv
from rich.console import Console
import json

console = Console()

try:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        model = None
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    console.print(f"[bold red]AI Configuration Error: {e}[/bold red]")
    model = None

def analyze_content(cleansed_text, file_name):
    if not model:
        console.print("[bold red]  ↪ AI model not configured. Skipping analysis.[/bold red]")
        return None

    console.print(f"  🧠 [bold]Analyzing:[/] Sending cleansed data to AI for deep analysis...")
    prompt = f"""
    You are a Senior Security Consultant. Your task is to analyze the following ANONYMIZED data from a file named '{file_name}' with maximum accuracy and detail.

    **Instructions:**
    Based *only* on the provided text, generate two distinct sections:
    1.  **File Description:** In a detailed paragraph, describe exactly what this document contains. Be specific about the type of data, its structure, and its likely purpose.
    2.  **Insights & Extracted Features:** As a bulleted list, extract the most critical insights, features, and key data points useful for a security analysis.

    **Anonymized Data:**
    ---
    {cleansed_text[:6000]}
    ---

    **Deliver your response in this exact JSON format:**
    {{
      "description": "Your detailed, accurate paragraph describing the file's content.",
      "insights": [
        "- Detailed insight or extracted feature 1.",
        "- Detailed insight or extracted feature 2."
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        clean_response = response.text.strip().replace("```json", "").replace("```", "")
        analysis = json.loads(clean_response)
        console.print("  ↪ [green]AI analysis successful.[/green]")
        return analysis
    except Exception as e:
        console.print(f"[bold red]  ↪ AI Analysis Error for {file_name}: {e}[/bold red]")
        return None

def generate_final_summary(all_results):
    if not model: return "AI model not available for final summary."
    summary_input = ""
    for result in all_results:
        summary_input += f"File: {result['file_name']}\nDescription: {result['description']}\nInsights: {' '.join(result['insights'])}\n---\n"
    prompt = f"""
    As a lead security consultant, you have reviewed the analysis of several client documents.
    Provide a high-level executive summary of the overall situation based on the collected findings.
    Synthesize the key themes and most critical risks into a 3-4 sentence narrative.
    
    **Collected Data:**
    {summary_input}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception:
        return "Could not generate a final summary due to an API error."