# IJACET-Style Manuscript Generator (Streamlit + LaTeX)

This is a starter app that lets you enter manuscript details in a web form and generates a journal-formatted **PDF** (IJACET style).

## Features
- Form fields for: title, authors (with affiliations), abstract, keywords
- Article info: DOI, submission/accept/publish dates, license
- Sections: Introduction, Methodology, Results/Discussion, Conclusion (you can add custom)
- References: paste BibTeX, auto-included via `biblatex`
- Figure uploads (optional)
- Output: compiles to **PDF** using LaTeX; if LaTeX isn't installed, you can download the `.tex`/assets to compile locally

## Quick start (local)
```bash
python -m venv .venv
. .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Open: http://localhost:8501

## PDF compilation
- The app tries `xelatex` then `pdflatex` automatically (requires a LaTeX distribution: TeXLive/MiKTeX).
- If neither is found, you'll still get a downloadable ZIP containing:
  - generated `manuscript.tex`
  - figures you uploaded
  - `references.bib`
  - `ijacet_template.tex`
You can compile later via:
```bash
xelatex manuscript.tex
biber manuscript
xelatex manuscript.tex
xelatex manuscript.tex
```

## Deploy options
- **Streamlit Cloud** (easy), or any server with Python/LaTeX installed.
- For Streamlit Cloud, ensure a TeX distribution is available (or compile offline).

## Folder structure
```
ijacet-manuscript-generator/
  app.py
  utils.py
  requirements.txt
  template/
    ijacet_template.tex
  README.md
```
