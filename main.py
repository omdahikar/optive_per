import os
import glob
from rich.console import Console
from rich.panel import Panel
import time # Import the time library

from app.parser import extract_content
from app.cleanser import cleanse_text, cleanse_images
from app.analyzer import analyze_content, generate_final_summary
from app.output_generator import generate_report

# --- CONFIGURATION ---
UPLOADS_DIR = "data/raw_files"
REPORTS_DIR = "data/output_reports"
PROCESSED_DIR = "data/processed_files"
TEMPLATE_NAME = "Case_Study_Final_Presentation_Template.pptx"
# ---------------------

console = Console()

def main():
    """Main function to orchestrate the file cleansing and analysis pipeline."""
    console.print(Panel.fit("[bold cyan]🚀 AI File Cleansing & Analysis Pipeline STARTED 🚀[/bold cyan]"))

    # --- Pre-flight Checks ---
    if not os.path.exists(TEMPLATE_NAME):
        console.print(f"[bold red]Fatal Error:[/bold red] Template file '{TEMPLATE_NAME}' not found.")
        return

    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    files_to_process = glob.glob(os.path.join(UPLOADS_DIR, "*"))
    if not files_to_process:
        console.print(f"[bold yellow]Warning:[/bold yellow] No files found in '{UPLOADS_DIR}'.")
        return

    console.print(f"Found {len(files_to_process)} files. Template located. Starting pipeline...\n")
    all_results = []

    # --- PIPELINE STAGES ---
    for i, file_path in enumerate(files_to_process):
        file_name = os.path.basename(file_path)
        console.print(f"[bold]Processing file {i+1}/{len(files_to_process)}: [cyan]{file_name}[/cyan][/bold]")

        content = extract_content(file_path)
        if not content or not content.get("text", "").strip():
            console.print(f"[yellow]  ↪ Skipping {file_name} due to parsing error or empty content.[/yellow]\n")
            continue

        cleansed_text = cleanse_text(content['text'])
        _ = cleanse_images(content.get('images', []))

        with open(os.path.join(PROCESSED_DIR, f"{file_name}_cleansed.txt"), "w", encoding="utf-8") as f:
            f.write(cleansed_text)

        analysis = analyze_content(cleansed_text, file_name)

        if not analysis:
            console.print(f"[yellow]  ↪ Skipping {file_name} as AI analysis failed.[/yellow]\n")
            time.sleep(5) # Still wait to avoid cascading API errors
            continue

        import json
        with open(os.path.join(PROCESSED_DIR, f"{file_name}_analysis.json"), "w") as f:
            json.dump(analysis, f, indent=2)

        file_result = {
            "file_name": file_name,
            "file_type": os.path.splitext(file_name)[1],
            **analysis
        }
        all_results.append(file_result)
        console.print(f"[green]  ↪ Finished processing.[/green]\n")
        
        # --- INCREASED API DELAY ---
        # Wait for 5 seconds before the next file to respect the API rate limit.
        time.sleep(5)
        # ---------------------------

    # --- GENERATE FINAL REPORT ---
    if all_results:
        generate_report(all_results, TEMPLATE_NAME, REPORTS_DIR)
        console.print("\n[bold]📝 Generating Executive Summary...[/bold]")
        final_summary = generate_final_summary(all_results)
        console.print(Panel(final_summary, title="[bold cyan]Executive Summary[/bold cyan]", border_style="cyan"))
    else:
        console.print("[bold yellow]No results were generated. Skipping report creation.[/bold yellow]")

    console.print(Panel.fit("[bold cyan]✅ Pipeline COMPLETED ✅[/bold cyan]"))

if __name__ == "__main__":
    main()