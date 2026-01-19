#!/usr/bin/env python3
import typer
import bibtexparser
import re
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import track
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

console = Console()
app = typer.Typer(help="🚀 The Ultimate BibTeX Cleaner: Mappings, Lowercase Keys, and Aggressive Cleaning.")

# --- COMPREHENSIVE MAPPINGS ---
CONFERENCE_MAPPINGS = {
    "proceedings of the neural information processing systems": "NeurIPS",
    "advances in neural information processing systems": "NeurIPS",
    "international conference on machine learning": "ICML",
    "international conference on learning representations": "ICLR",
    "computer vision and pattern recognition": "CVPR",
    "international conference on computer vision": "ICCV",
    "european conference on computer vision": "ECCV",
    "association for the advancement of artificial intelligence": "AAAI",
    "international joint conference on artificial intelligence": "IJCAI",
    "knowledge discovery and data mining": "KDD",
    "association for computational linguistics": "ACL",
    "empirical methods in natural language processing": "EMNLP",
    "computer graphics and interactive techniques": "SIGGRAPH",
    "robotics: science and systems": "RSS",
    "international conference on robotics and automation": "ICRA",
    "international conference on intelligent robots and systems": "IROS",
}

JOURNAL_MAPPINGS = {
    "j. mach. learn. res.": "Journal of Machine Learning Research",
    "jmlr": "Journal of Machine Learning Research",
    "nature communications": "Nature Communications",
    "nat. commun.": "Nature Communications",
    "proceedings of the national academy of sciences": "Proceedings of the National Academy of Sciences",
    "pnas": "Proceedings of the National Academy of Sciences",
    "ieee trans. pattern anal. mach. intell.": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
    "tpami": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
    "ieee trans. image process.": "IEEE Transactions on Image Processing",
    "tip": "IEEE Transactions on Image Processing",
    "ieee transactions on neural networks and learning systems": "IEEE Transactions on Neural Networks and Learning Systems",
    "tnnls": "IEEE Transactions on Neural Networks and Learning Systems",
    "journal of artificial intelligence research": "Journal of Artificial Intelligence Research",
    "jair": "Journal of Artificial Intelligence Research",
}

# Aggressive field removal
JUNK_FIELDS = [
    "abstract",
    "file",
    "url",
    "doi",
    "issn",
    "isbn",
    "note",
    "timestamp",
    "keywords",
    "mendeley-groups",
    "language",
    "number",
    "pages",
    "volume",
    "month",
    "publisher",
    "editor",
    "series",
    "bdsk-url-1",
    "bdsk-url-2",
    "archiveprefix",
    "eprint",
    "primaryclass",
]


def get_clean_text(text: str) -> str:
    """Removes LaTeX braces, punctuation, and returns lowercase alphanumeric string."""
    clean = re.sub(r"[\{\}]", "", text)
    return re.sub(r"\W+", "", clean).lower()


def generate_lowercase_key(entry: dict) -> str:
    """Generates a lowercase key: firstauthoryearfirstword."""
    # 1. First Author Last Name
    author_field = entry.get("author", "unknown")
    first_author_raw = author_field.split(" and ")[0].split(",")[0].split(" ")[-1]
    author_part = get_clean_text(first_author_raw)

    # 2. Year
    year_part = get_clean_text(entry.get("year", "0000"))

    # 3. First Word of Title (min 4 chars to avoid 'the', 'a', etc.)
    title = entry.get("title", "paper")
    words = [w for w in title.split() if len(get_clean_text(w)) >= 4]
    first_word = get_clean_text(words[0]) if words else "paper"

    return f"{author_part}{year_part}{first_word}"


def clean_entry(entry: dict, strip_junk: bool, reset_keys: bool) -> dict:
    # 1. Conference & Journal Standardization
    for field, mapping in [
        ("booktitle", CONFERENCE_MAPPINGS),
        ("journal", JOURNAL_MAPPINGS),
    ]:
        if field in entry:
            val = entry[field].lower()
            for long_name, short_name in mapping.items():
                if long_name in val:
                    entry[field] = short_name
                    break

    # 2. Aggressive Junk Removal (includes pages, volume, number)
    if strip_junk:
        for field in JUNK_FIELDS:
            entry.pop(field, None)

    # 3. Lowercase Re-keying
    if reset_keys:
        entry["ID"] = generate_lowercase_key(entry)

    return entry


@app.command()
def clean(
    input_path: Path = typer.Argument(..., help="Path to .bib file", exists=True),
    output_path: Optional[Path] = typer.Option(None, "--output", "-o"),
    reset_keys: bool = typer.Option(False, "--reset-keys", help="Apply lowercase firstauthoryearfirstword keys"),
    keep_junk: bool = typer.Option(False, "--keep-metadata", help="Keep volume, pages, DOI, etc."),
):
    """
    Cleans, re-keys, and sorts your BibTeX library with expanded mappings.
    """
    if not output_path:
        output_path = input_path.parent / f"cleaned_{input_path.name}"

    with open(input_path, "r", encoding="utf-8") as f:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        db = bibtexparser.load(f, parser=parser)

    # 1. Processing and Cleaning
    cleaned = [clean_entry(e, not keep_junk, reset_keys) for e in db.entries]

    # 2. Deduplication
    unique_entries = []
    seen_titles = set()
    for e in track(cleaned, description="Processing..."):
        title_key = get_clean_text(e.get("title", ""))
        if title_key and title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_entries.append(e)

    # 3. Sorting by (First Author, Year, First Word)
    def sort_key(e):
        author = e.get("author", "zzz").split(" and ")[0].split(",")[-1].strip().lower()
        year = e.get("year", "0000")
        title = e.get("title", "zzz").lower().split()[0]
        return (author, year, title)

    unique_entries.sort(key=sort_key)

    # 4. Writing Output
    new_db = BibDatabase()
    new_db.entries = unique_entries
    writer = BibTexWriter()
    writer.indent = "  "

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(writer.write(new_db))

    console.print("\n[bold green]Success![/bold green]")
    console.print(f" • Cleaned file: [cyan]{output_path}[/cyan]")
    console.print(f" • Sorted {len(unique_entries)} entries by Author, Year, then Title.")


if __name__ == "__main__":
    app()
