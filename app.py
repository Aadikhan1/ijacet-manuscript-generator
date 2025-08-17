import io, os, zipfile, datetime as dt
import streamlit as st
from utils import render_tex, compile_pdf, escape_latex

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")

st.set_page_config(page_title="IJACET Manuscript Generator", page_icon="📝", layout="wide")

st.title("📝 IJACET-Style Manuscript Generator")
st.caption("Enter manuscript details below. Generate a LaTeX PDF in one click.")

with st.form("meta"):
    col1, col2 = st.columns([2,1])
    with col1:
        title = st.text_input("Paper Title*", placeholder="Resilient Cloud Architectures for Optimized Big Data Storage and Real-Time Processing")
        doi = st.text_input("DOI", placeholder="https://doi.org/10.xxxx/xxxxx")
        license_url = st.text_input("License URL", value="https://creativecommons.org/licenses/by/4.0")
        issue = st.text_input("Volume-Issue (e.g., Vol: 01 - Issue 02 (2025))", value="Vol: 01 - Issue 03 (2025)")
        journal_full = st.text_input("Journal Full Name", value="International Journal of Advanced Computing & Emerging Technologies (IJACET)")
        journal_short = st.text_input("Journal Short Name", value="IJACET")
        issn_print = st.text_input("ISSN (Print)", value="3105-3904")
        issn_online = st.text_input("ISSN (Online)", value="3105-3912")
        site_url = st.text_input("Journal Website", value="https://ijacet.com")
    with col2:
        submitted = st.date_input("Article Submitted", value=dt.date.today())
        accepted = st.date_input("Article Accepted", value=dt.date.today())
        published = st.date_input("Article Published", value=dt.date.today())
        corresponding_mark = st.text_input("Corresponding Author Marker", value="*")

    st.subheader("Authors & Affiliations")
    affils = st.text_area("Affiliations (one per line)", value="Department of Computer Science, University of Agriculture Faisalabad\nDepartment of Software Engineering, The University of Lahore\nDepartment of Mathematics, University of Agriculture Faisalabad")
    st.caption("Affiliations will be auto-numbered 1..N.")

    a1, a2, a3 = st.columns(3)
    with a1:
        authors_raw = st.text_area("Authors (one per line: Name|affil_number|email|corresponding(yes/no))",
                                   value="Muhammad Talha Tahir Bajwa|1|talhabajwa6p@gmail.com|no\nAwais Rasool|2|awais.rasool@se.uol.edu.pk|yes\nZartasha Kiran|2|zartasha.kiran@se.uol.edu.pk|no\nAmara Latif|3|amaralatif501@gmail.com|no",
                                   height=120)
    with a2:
        abstract = st.text_area("Abstract*", height=160)
    with a3:
        keywords = st.text_input("Keywords (comma-separated)", value="Cloud computing, Big Data, Apache Spark, Hadoop, AWS, Scalability, Fault tolerance")

    st.subheader("Sections")
    intro = st.text_area("1. Introduction", height=180)
    methodology = st.text_area("2. Methodology / System", height=160)
    results = st.text_area("3. Results / Analysis", height=160)
    conclusion = st.text_area("4. Conclusion / Future Work", height=140)

    st.subheader("References (BibTeX)")
    bibtex = st.text_area("Paste your .bib entries here", height=180)

    st.subheader("Figures (optional)")
    figures = st.file_uploader("Upload images (PNG/JPG/PDF)", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)

    generate = st.form_submit_button("⚙️ Generate PDF / LaTeX")

if generate:
    # Parse affiliations
    affil_list = [line.strip() for line in affils.splitlines() if line.strip()]
    affil_map = {str(i+1): affil_list[i] for i in range(len(affil_list))}

    # Parse authors
    authors = []
    for line in authors_raw.splitlines():
        if not line.strip(): continue
        try:
            name, affno, email, corr = [p.strip() for p in line.split("|")]
        except ValueError:
            st.error("Each author line must be: Name|affil_number|email|corresponding(yes/no)")
            st.stop()
        authors.append({
            "name": name,
            "affno": affno,
            "email": email,
            "corresponding": (corr.lower() in ["yes","y","1","true"])
        })

    # Prepare context for template
    context = {
        "title": title,
        "doi": doi,
        "license_url": license_url,
        "issue": issue,
        "journal_full": journal_full,
        "journal_short": journal_short,
        "issn_print": issn_print,
        "issn_online": issn_online,
        "site_url": site_url,
        "submitted": submitted.strftime("%d-%m-%Y"),
        "accepted": accepted.strftime("%d-%m-%Y"),
        "published": published.strftime("%d-%m-%Y"),
        "corresponding_mark": corresponding_mark,
        "affiliations": affil_map,
        "authors": authors,
        "abstract": abstract,
        "keywords": keywords,
        "sections": [
            {"num": 1, "title": "Introduction", "text": intro},
            {"num": 2, "title": "Methodology", "text": methodology},
            {"num": 3, "title": "Results and Analysis", "text": results},
            {"num": 4, "title": "Conclusion and Future Work", "text": conclusion},
        ]
    }

    # Handle figures
    fig_data = []
    if figures:
        for f in figures:
            fig_data.append((f.name, f.read()))

    work_dir = os.path.abspath("build")
    os.makedirs(work_dir, exist_ok=True)

    tex_out, bib_out = render_tex(TEMPLATE_DIR, work_dir, context, bibtex_text=bibtex, figure_files=fig_data)
    pdf_path, err = compile_pdf(work_dir, tex_out)

    # Always provide a ZIP with sources
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(tex_out, arcname="manuscript.tex")
        z.write(os.path.join(TEMPLATE_DIR, "ijacet_template.tex"), arcname="ijacet_template.tex")
        if os.path.exists(bib_out):
            z.write(bib_out, arcname="references.bib")
        # include figures
        for root, _, files in os.walk(work_dir):
            for fn in files:
                if fn.lower().endswith((".png",".jpg",".jpeg",".pdf")):
                    fp = os.path.join(root, fn)
                    z.write(fp, arcname=fn)
    zip_buf.seek(0)

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("📦 Download LaTeX package (ZIP)", data=zip_buf, file_name="manuscript_sources.zip", mime="application/zip")

    with c2:
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download Compiled PDF", data=f.read(), file_name="manuscript.pdf", mime="application/pdf")
            st.success("PDF compiled successfully ✅")
        else:
            st.warning("PDF compilation not available in this environment. Download the ZIP and compile locally.")

st.markdown("---")
st.caption("Tip: For perfect reference formatting, prefer BibTeX pasted above. The template uses biblatex (biber/bibtex).")
