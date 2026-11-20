"""Assemble a send-ready drawing set: a cover sheet + every sheet PDF, one file.

    python tools_drawing_set.py PDF_DIR OUT.pdf [DATE]
        [--title T] [--sub S] [--status "HEADLINE|line 2|line 3"] [--checks C]

The cover (A1 landscape, like the sheets) names the project, lists every
sheet in PDF_DIR in issue order (plans, elevations, section, presentation),
and states the status of the drawings. Sheets keep their true scale. The
defaults are the Fairway's cover; another project passes its own title,
subtitle and status (sheet PDFs must be named A-101_SITE_PLAN.pdf etc.).
"""
from __future__ import annotations

import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymupdf

TITLE = "THE FAIRWAY VILLA  --  DUBAI HILLS ESTATE"
SUB = "5 bedroom villa with basement  |  plot 1,210.8 m2 (13,033 sq ft)  |  BUA 1,188 m2 (12,788 sq ft)"
STATUS = ("STUDY RECREATION -- NOT THE REAL HOUSE'S DRAWINGS",
          "Designed from a public sale listing's published figures and photographs; no plans were "
          "available, so the layout, dimensions and levels are assumptions.",
          "The original design belongs to its architect and builder. Not for construction, permit "
          "submission, or marketing of that property.")
CHECKS = ("Checked by the design pipeline's automated checks (Dubai Building Code 2021 rules as data): "
          "0 FATAL / 0 MAJOR. This is not a review by a licensed architect or the authority.")
SUBJECT = "Study recreation; not for construction"           # PDF metadata


def order_key(fn):
    m = re.match(r"A-(\d)(\d\d)(P?)_", fn)
    if not m:
        return (9, 0, 0)
    series, num, pres = int(m.group(1)), int(m.group(2)), m.group(3) == "P"
    return (1 if pres else 0, series, num)


def title_of(fn):
    m = re.match(r"(A-\d\d\dP?)_(.+)\.pdf$", fn)
    no, name = m.group(1), m.group(2).replace("_", " ")
    return no, name


def cover(sheets, path, date):
    fig = plt.figure(figsize=(841 / 25.4, 594 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    ax.set_xlim(0, 841); ax.set_ylim(0, 594)
    ax.add_patch(plt.Rectangle((20, 20), 801, 554, fill=False, lw=1.2))
    ax.text(60, 520, TITLE, fontsize=40, weight="bold", family="DejaVu Sans")
    ax.text(60, 494, SUB, fontsize=17)
    ax.text(60, 470, f"DRAWING SET  --  {len(sheets)} SHEETS  --  1:100 AT A1  --  {date}", fontsize=17)
    ax.add_patch(plt.Rectangle((60, 380), 721, 70, fill=True, fc="#fff4e5", ec="#c77700", lw=1.5))
    ax.text(75, 428, STATUS[0], fontsize=19, weight="bold", color="#8a4b00")
    ax.text(75, 408, STATUS[1], fontsize=12.5)
    ax.text(75, 391, STATUS[2], fontsize=12.5)
    ax.text(60, 350, "DRAWING REGISTER", fontsize=17, weight="bold")
    y = 330
    ax.text(60, y, "No.", fontsize=12.5, weight="bold"); ax.text(140, y, "Title", fontsize=12.5, weight="bold")
    ax.text(560, y, "Scale", fontsize=12.5, weight="bold"); ax.text(640, y, "Type", fontsize=12.5, weight="bold")
    ax.plot([60, 781], [y - 5, y - 5], color="k", lw=0.8)
    for fn in sheets:
        y -= 17.5
        no, name = title_of(fn)
        kind = "colour presentation" if no.endswith("P") else (
            "section" if no.startswith("A-3") else "elevation" if no.startswith("A-2") else "plan")
        ax.text(60, y, no, fontsize=12.5); ax.text(140, y, name, fontsize=12.5)
        ax.text(560, y, "1:100", fontsize=12.5); ax.text(640, y, kind, fontsize=12.5)
    ax.text(60, 45, CHECKS, fontsize=11, color="#444")
    ax.text(60, 30, "All dimensions in millimetres. Do not scale from drawings. AutoCAD files: the DWG "
                    "folder accompanying this set.", fontsize=11, color="#444")
    fig.savefig(path)
    plt.close(fig)


def main(pdf_dir, out, date="2026-09-27"):
    sheets = sorted((f for f in os.listdir(pdf_dir)
                     if f.endswith(".pdf") and re.match(r"A-\d\d\dP?_", f) and "~plot" not in f),
                    key=order_key)
    tmp = out + ".cover.pdf"
    cover(sheets, tmp, date)
    doc = pymupdf.open(tmp)
    for f in sheets:
        doc.insert_pdf(pymupdf.open(os.path.join(pdf_dir, f)))
    toc = [[1, "Cover and drawing register", 1]] + [
        [1, " ".join(title_of(f)), i + 2] for i, f in enumerate(sheets)]
    doc.set_toc(toc)
    doc.set_metadata({"title": f"{TITLE} - Drawing set", "subject": SUBJECT,
                      "creator": "architectural-cad pipeline"})
    doc.save(out, garbage=3, deflate=True)
    doc.close()
    os.remove(tmp)
    print(f"{len(sheets) + 1} pages -> {out} ({os.path.getsize(out) // 1024} KB)")
    for f in sheets:
        print("  ", f)


if __name__ == "__main__":
    args = sys.argv[1:]
    for flag in ("--title", "--sub", "--status", "--checks"):
        if flag in args:
            i = args.index(flag)
            if i + 1 >= len(args):
                raise SystemExit(f"{flag} needs a value")
            value = args[i + 1]
            del args[i:i + 2]
            if flag == "--title":
                TITLE = value
            elif flag == "--sub":
                SUB = value
            elif flag == "--checks":
                CHECKS = value
            else:
                parts = value.split("|")
                STATUS = tuple((parts + ["", "", ""])[:3])
                SUBJECT = STATUS[0].capitalize()
    if len(args) < 2:
        raise SystemExit(__doc__)
    main(args[0], args[1], *(args[2:3]))
