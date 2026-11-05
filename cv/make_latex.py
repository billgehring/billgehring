#!/usr/bin/env python3
"""Generate cv/cvbody.tex from cv.yaml + publications.yaml (the shared data).

LaTeX counterpart of cv.typ: same content, same single source. Run:
    uv run --with pyyaml python cv/make_latex.py
"""
import re
import sys
import urllib.parse
from pathlib import Path

import yaml

HERE = Path(__file__).parent
cv = yaml.safe_load((HERE / "cv.yaml").read_text())
pubs = yaml.safe_load((HERE / "publications.yaml").read_text())

ACCENT = "accent"


def esc(s: str) -> str:
    s = s.replace("\\", r"\textbackslash{}")
    for a, b in [("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("_", r"\_"), ("{", r"\{"), ("}", r"\}")]:
        s = s.replace(a, b)
    return s.replace("~", r"\textasciitilde{}").replace("^", r"\textasciicircum{}")


def inline(s: str) -> str:
    """*italics* -> \\emph{}, everything else escaped."""
    return "".join(
        (rf"\emph{{{esc(p)}}}" if i % 2 else esc(p))
        for i, p in enumerate(s.split("*"))
    )


def ends_punct(s: str) -> bool:
    return bool(re.search(r"[.?!]$", s.strip()))


def endp(s: str) -> str:
    return s if ends_punct(s) else s + "."


def href(url: str, text: str) -> str:
    u = url.replace("%", r"\%").replace("#", r"\#")
    return rf"\href{{{u}}}{{\textcolor{{{ACCENT}}}{{{text}}}}}"


def fmt_pub(p: dict) -> str:
    out = [f"{esc(p['authors'])} ({p['year']}). "]
    title = p["title"] + (" " + p["note"] if "note" in p else "")
    out.append(esc(endp(title)) + " ")
    if "journal" in p:
        out.append(rf"\emph{{{esc(p['journal'])}}}")
        if "volume" in p:
            out.append(rf", \emph{{{esc(str(p['volume']))}}}")
        if "issue" in p:
            out.append(f"({esc(str(p['issue']))})")
        if "pages" in p:
            out.append(f", {esc(p['pages'])}")
        out.append(". ")
    elif "source" in p:
        out.append(inline(endp(p["source"])) + " ")
    if "doi" in p:
        out.append(href("https://doi.org/" + p["doi"], "[doi]") + " ")
    if "pdf" in p:
        url = "https://billgehring.com/files/" + urllib.parse.quote(p["pdf"], safe="")
        out.append(href(url, "[PDF]"))
    return "".join(out).rstrip()


L = []
w = L.append

w(r"\thispagestyle{titlestyle}")
# --- name header ---
w(r"\noindent")
w(rf"\begin{{minipage}}[b]{{0.62\textwidth}}{{\fontsize{{19}}{{21}}\selectfont {esc(cv['name'])}}}\end{{minipage}}\hfill")
w(r"\begin{minipage}[b]{0.36\textwidth}\raggedleft\small")
w(rf"\href{{mailto:{cv['email']}}}{{{esc(cv['email'])}}}\\[2pt]")
w(rf"\textcolor{{{ACCENT}}}{{\href{{{cv['website']}}}{{{esc(cv['website'])}}}}}")
w(r"\end{minipage}\par\addvspace{2pt}")

for sec in cv["sections"]:
    w(rf"\cvsection{{{esc(sec['heading'])}}}")
    style = sec["style"]
    if style == "prose":
        w(rf"\prose{{{inline(sec['text'])}}}")
    elif style == "dated":
        cmd = r"\dentedi" if sec.get("indent") else r"\dented"
        for e in sec["entries"]:
            w(rf"{cmd}{{{esc(e['year'])}}}{{{inline(e['text'])}}}")
    elif style == "list":
        for it in sec["items"]:
            w(rf"\hitem{{{inline(it)}}}")
    elif style == "groups":
        for g in sec["groups"]:
            w(rf"\cvsubi{{{esc(g['subheading'])}}}")
            if g["kind"] == "list":
                for it in g["items"]:
                    w(rf"\hitem{{{inline(it)}}}")
            else:
                body = inline(g["text"])
                w(rf"\prose{{{{\itshape {body}}}}}" if g.get("italic") else rf"\prose{{{body}}}")

# --- publications (shared data) ---
w(r"\cvsectionc{Publications}")
w(r"\cvsubb{In press and published}")
for p in pubs:
    w(rf"\pub{{{fmt_pub(p)}}}")
w(r"\cvsubb{Manuscripts in Preparation}")
for m in cv["manuscripts"]:
    w(rf"\pub{{{inline(m)}}}")

body = "\n".join(L) + "\n"
(HERE / "cvbody.tex").write_text(body)

# --- standalone, self-contained file for Overleaf -------------------------
# Overleaf can't run this script, so inline the body into the preamble and
# ship one flat .tex (+ the fonts/ folder). Upload steps are in the header.
header = (
    "% !TeX program = xelatex\n"
    "%\n"
    "% ============================ OVERLEAF README ============================\n"
    "% This is a self-contained copy of the CV (content baked in -- no YAML,\n"
    "% no Python needed). To use it on Overleaf:\n"
    "%   1. New Project -> Upload Project -> pick cv_overleaf.zip\n"
    "%      (it contains this file + the fonts/ folder it needs).\n"
    "%   2. Menu -> Compiler -> XeLaTeX  (the line above also sets this).\n"
    "%   3. Recompile.\n"
    "% To refresh after editing the YAML on your Mac, re-run make_latex.py and\n"
    "% re-upload this one file (the fonts never change).\n"
    "% ========================================================================\n"
)
preamble = (HERE / "cv.tex").read_text()
standalone = header + preamble.replace("\\input{cvbody.tex}", body.rstrip())
(HERE / "cv_overleaf.tex").write_text(standalone)

print(f"wrote cvbody.tex and cv_overleaf.tex  ({len(pubs)} publications)",
      file=sys.stderr)
