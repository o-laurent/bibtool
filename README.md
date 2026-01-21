# bibtool.py

A small vibe-coded Python script to help clean and organize BibTeX files. It focuses on simplifying conference names, removing unnecessary metadata, and keeping your bibliography tidy. We provide an example bibliography and the corresponding cleaned version in the `example` folder.

## Features

- **Standardization:** Shortens common conference and journal names (e.g., *NeurIPS*, *ICML*)
- **Cleanup:** Removes extra fields like `abstract`, `url`, and `doi` to keep the file lightweight
- **Optional Re-keying:** Can rename citation keys to a consistent `author-year-word` format
- **Deduplication:** Removes duplicate entries based on the title

## Setup

The script requires Python and a few libraries. You can install them via pip:

```bash
pip install typer bibtexparser rich
```

## Usage

Run the script by providing the path to your `.bib` file. By default, it will create a new file with a `cleaned_` prefix.

```bash
python bibtool.py references.bib
```

## Options

- `--reset-keys`: Generates new, consistent citation keys
- `--keep-metadata`: Prevents the script from deleting fields like DOI, volume, and page numbers
- `-o` or `--output`: Specify a custom name for the output file

### Example

```bash
python bibtool.py library.bib --reset-keys -o cleaned.bib
```

## Note

This script is provided as-is, without any guarantees. It is designed to be aggressive in removing fields that are often considered clutter. Please back up your original `.bib` files before use.
