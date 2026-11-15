"""Cut the before/after comparison images for the technical changes document.

Each entry crops one region of one page of Report_Before.pdf or
Report_After.pdf (the folder above this one) at 150 dpi. Regions are given as
fractions of the page height; the width is the text block plus a small margin.
Needs pdftoppm (Poppler) and Pillow.

    python make_figures.py
"""
import os
import subprocess
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPORTS = os.path.dirname(HERE)
OUT = os.path.join(HERE, "images")
DPI = 150
X_RANGE = (0.07, 0.93)          # text block of an A4 page with 1 in margins, plus a margin

# name: (report, page, top, bottom)
CROPS = {
    "item1_before": ("Report_Before.pdf", 31, 0.055, 0.36),
    "item1_after": ("Report_After.pdf", 36, 0.055, 0.38),
    "item2_before": ("Report_Before.pdf", 30, 0.74, 1.00),
    "item2_after": ("Report_After.pdf", 36, 0.555, 1.00),
    "item3_before": ("Report_Before.pdf", 13, 0.495, 0.74),
    "item3_after_vehicle": ("Report_After.pdf", 15, 0.515, 0.88),
    "item3_after_footpath": ("Report_After.pdf", 16, 0.055, 0.48),
    "item4_before": ("Report_Before.pdf", 44, 0.400, 0.90),
    "item4_after": ("Report_After.pdf", 50, 0.055, 0.73),
    "item5_before": ("Report_Before.pdf", 51, 0.060, 0.74),
    "item5_after": ("Report_After.pdf", 57, 0.055, 0.92),
    "item6_before": ("Report_Before.pdf", 13, 0.155, 0.49),
    "item6_after": ("Report_After.pdf", 15, 0.165, 0.50),
    "summary_before": ("Report_Before.pdf", 3, 0.055, 0.74),
    "summary_after": ("Report_After.pdf", 6, 0.055, 0.73),
}


def crop(report: str, page: int, top: float, bottom: float, name: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        stem = os.path.join(tmp, "page")
        subprocess.run(["pdftoppm", "-f", str(page), "-l", str(page), "-r", str(DPI), "-singlefile",
                        "-png", os.path.join(REPORTS, report), stem], check=True)
        with Image.open(stem + ".png") as img:
            w, h = img.size
            box = (int(X_RANGE[0] * w), int(top * h), int(X_RANGE[1] * w), int(bottom * h))
            img.crop(box).save(os.path.join(OUT, name + ".png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, (report, page, top, bottom) in CROPS.items():
        crop(report, page, top, bottom, name)
        print(f"{name}: {report} p.{page}")
