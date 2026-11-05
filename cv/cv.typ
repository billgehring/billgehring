// William J. Gehring — Curriculum Vitae
//
// Layout/template only. Content lives in data files:
//   cv.yaml            — front-matter sections (interests, positions, service, grants, …)
//   publications.yaml  — the publication list (SHARED with the website)
// Build:  typst compile --font-path ~/Library/Fonts cv/cv.typ cv/cv.pdf
//
// In cv.yaml, wrap italics in *asterisks*. Everything else is rendered
// verbatim (so $, &, :, % etc. need no escaping). Use en dashes (–) for
// numeric/date ranges and hyphens (-) only in compounds.

#let cv = yaml("cv.yaml")
#let pubs = yaml("publications.yaml")

#let accent = rgb("#0563c1") // hyperlink blue

// --- inline *italic* parser: returns content, input rendered verbatim ------
#let md(s) = {
  let out = []
  for (i, part) in s.split("*").enumerate() {
    out += if calc.odd(i) { emph(part) } else { [#part] }
  }
  out
}

// --- percent-encode a filename for a URL (handles spaces, (), &, …) --------
#let urlencode(s) = {
  let hexd = "0123456789ABCDEF"
  let out = ""
  for c in s {
    if c.match(regex("[A-Za-z0-9._~/-]")) != none {
      out += c
    } else {
      for b in array(bytes(c)) {
        out += "%" + hexd.at(calc.quo(b, 16)) + hexd.at(calc.rem(b, 16))
      }
    }
  }
  out
}

#let ends-punct(s) = s.trim().match(regex("[.?!]$")) != none
#let endp(s) = if ends-punct(s) { s } else { s + "." }

// ------------------------------- page setup --------------------------------
#set page(
  paper: "us-letter",
  margin: (x: 1in, top: 0.9in, bottom: 0.85in),
  header: context {
    if counter(page).get().first() > 1 {
      set text(size: 10.5pt)
      align(right, cv.name)
    }
  },
  footer: context {
    set text(size: 10.5pt)
    let here = counter(page).get().first()
    let total = counter(page).final().first()
    align(right)[Page #strong(str(here)) of #str(total)]
  },
)
#set text(font: "EB Garamond", size: 11pt, lang: "en")
#set par(justify: true, leading: 0.62em, spacing: 0.62em)

// ------------------------------- building blocks ---------------------------
#let section(title, centered: false) = {
  v(14pt, weak: true)
  let t = text(size: 12pt, weight: "bold", md(title))
  block(if centered { align(center, t) } else { t }, below: 4pt)
}

#let subheading(title, italic: true) = {
  v(5pt, weak: true)
  block(
    text(weight: "bold", style: if italic { "italic" } else { "normal" }, md(title)),
    below: 2pt,
  )
}

#let dated(entries, indent: false) = {
  let ind = if indent { 0.33in } else { 0pt }
  for e in entries {
    block(below: 3pt,
      grid(columns: (1.15in, 1fr), column-gutter: 0.12in,
        pad(left: ind, md(e.year)), md(e.text)),
    )
  }
}

#let hlist(items) = {
  for it in items {
    block(below: 3pt, {
      set par(hanging-indent: 0.3in, justify: false)
      md(it)
    })
  }
}

#let paragraph(s, italic: false) = block(below: 3pt,
  if italic { emph(md(s)) } else { md(s) },
)

// ------------------------------- publications ------------------------------
#let fmt-pub(p) = {
  let out = [#p.authors (#str(p.year)). ]
  let title = p.title
  if "note" in p { title = title + " " + p.note }
  out += [#endp(title) ]
  if "journal" in p {
    out += emph(p.journal)
    if "volume" in p { out += [, #emph(str(p.volume))] }
    if "issue" in p { out += [(#str(p.issue))] }
    if "pages" in p { out += [, #p.pages] }
    out += [. ]
  } else if "source" in p {
    out += [#md(endp(p.source)) ]
  }
  if "doi" in p {
    out += [#link("https://doi.org/" + p.doi, text(fill: accent)[\[doi\]]) ]
  }
  if "pdf" in p {
    out += link("https://billgehring.com/files/" + urlencode(p.pdf), text(fill: accent)[\[PDF\]])
  }
  out
}

// =============================== document ==================================
#block[
  #grid(
    columns: (1fr, auto),
    align: (left + bottom, right + bottom),
    text(size: 19pt, cv.name),
    text(size: 10.5pt)[
      #link("mailto:" + cv.email)[#cv.email] \
      #text(fill: accent, link(cv.website)[#cv.website])
    ],
  )
]
#v(2pt)

#for sec in cv.sections {
  section(sec.heading)
  let style = sec.style
  if style == "prose" {
    paragraph(sec.text)
  } else if style == "dated" {
    dated(sec.entries, indent: sec.at("indent", default: false))
  } else if style == "list" {
    hlist(sec.items)
  } else if style == "groups" {
    for g in sec.groups {
      subheading(g.subheading)
      if g.kind == "list" { hlist(g.items) } else { paragraph(g.text, italic: g.at("italic", default: false)) }
    }
  }
}

// Publications — pulled from the shared data file.
#section("Publications", centered: true)
#subheading("In press and published", italic: false)
#for p in pubs {
  block(below: 8pt, {
    set par(hanging-indent: 0.4in)
    fmt-pub(p)
  })
}
#subheading("Manuscripts in Preparation", italic: false)
#hlist(cv.manuscripts)
