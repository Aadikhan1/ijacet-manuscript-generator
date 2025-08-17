import os, shutil, subprocess, re, tempfile
from jinja2 import Environment, FileSystemLoader

LATEX_BIN_CANDIDATES = ["xelatex", "pdflatex"]
BIB_BIN_CANDIDATES = ["biber", "bibtex"]

def _find_bin(candidates):
    for c in candidates:
        if shutil.which(c):
            return c
    return None

def escape_latex(s: str) -> str:
    if s is None: return ""
    # Simple escaping for common special chars
    subs = {
        "\\": r"\\textbackslash{}",
        "&": r"\\&",
        "%": r"\\%",
        "$": r"\\$",
        "#": r"\\#",
        "_": r"\\_",
        "{": r"\\{",
        "}": r"\\}",
        "~": r"\\textasciitilde{}",
        "^": r"\\textasciicircum{}",
    }
    out = []
    for ch in s:
        out.append(subs.get(ch, ch))
    return "".join(out)

def render_tex(template_dir, output_dir, context, bibtex_text=None, figure_files=None):
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    tpl = env.get_template("ijacet_template.tex")

    # Ensure dirs
    os.makedirs(output_dir, exist_ok=True)

    # Write references.bib
    bib_path = os.path.join(output_dir, "references.bib")
    if bibtex_text:
        with open(bib_path, "w", encoding="utf-8") as f:
            f.write(bibtex_text)
    else:
        # minimal file to avoid errors if bibliography absent
        with open(bib_path, "w", encoding="utf-8") as f:
            f.write("% empty bib file\n")

    # Copy figures into output_dir and track names
    fig_names = []
    if figure_files:
        for idx, (name, data) in enumerate(figure_files):
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)
            target = os.path.join(output_dir, safe)
            with open(target, "wb") as fp:
                fp.write(data)
            fig_names.append(safe)
    context["figure_files"] = fig_names

    # Render manuscript.tex
    tex_out = os.path.join(output_dir, "manuscript.tex")
    with open(tex_out, "w", encoding="utf-8") as f:
        f.write(tpl.render(**context))
    return tex_out, bib_path

def compile_pdf(work_dir, tex_file):
    latex = _find_bin(LATEX_BIN_CANDIDATES)
    bib = _find_bin(BIB_BIN_CANDIDATES)

    if not latex:
        return None, "LaTeX compiler not found. Install TeXLive/MiKTeX (xelatex/pdflatex)."

    basename = os.path.splitext(os.path.basename(tex_file))[0]
    try:
        # 1st pass
        subprocess.run([latex, "-interaction=nonstopmode", basename + ".tex"],
                       cwd=work_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # bibliography
        if bib:
            if bib.endswith("biber"):
                subprocess.run(["biber", basename], cwd=work_dir, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                subprocess.run(["bibtex", basename], cwd=work_dir, check=True,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # 2nd + 3rd pass
        subprocess.run([latex, "-interaction=nonstopmode", basename + ".tex"],
                       cwd=work_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run([latex, "-interaction=nonstopmode", basename + ".tex"],
                       cwd=work_dir, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        pdf_path = os.path.join(work_dir, basename + ".pdf")
        if os.path.exists(pdf_path):
            return pdf_path, None
        return None, "Compilation finished but PDF not found."
    except subprocess.CalledProcessError as e:
        return None, f"LaTeX error: {e}"

