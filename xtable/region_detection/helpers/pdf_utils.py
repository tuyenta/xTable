import multiprocessing
import pathlib
import re
from operator import itemgetter
from typing import Union

import fitz
import numpy as np
from pdf2image import convert_from_path
from PyPDF2 import PdfFileReader


def norm_pdf_page(pdf_path: Union[pathlib.Path, str], pgno: int):
    """Read Pdf page and return page object
    Args:
        pdf_path (str): path to pdf file
        pgno (int): page number
    Returns:
        The pdf page object of Pypdf2
    """
    pdf_doc = PdfFileReader(open((pdf_path), "rb"), strict=False)

    # get page
    pdf_page = pdf_doc.getPage(pgno - 1)
    pdf_page.cropBox.upperLeft = (0, list(pdf_page.mediaBox)[-1])
    pdf_page.cropBox.lowerRight = (list(pdf_page.mediaBox)[-2], 0)
    return pdf_page


def pdf_page2img(
    pdf_path: Union[pathlib.Path, str],
    pgno: int,
    save_image: bool = False,
    save_path: pathlib.Path = None,
    dpi: int = 300,
):
    """Convert pdf page to image
    Args:
        pdf_path (str): path to pdf file
        pgno (int): page number
        save_image (bool): True if save image, False if no. Default is False
        save_path (str|pathlib.Path): path to save the created image
        dpi (int): dpi value

    Returns:
        set of image files
    """
    img_page = convert_from_path(
        str(pdf_path),
        first_page=pgno,
        last_page=pgno,
        dpi=dpi,
        thread_count=multiprocessing.cpu_count(),
        grayscale=False,
    )[0]
    if save_image:
        if save_path is not None:
            img = str(save_path) + "/" + str(pgno).split("/")[-1]
        else:
            img = pdf_path[:-4] + "-" + str(pgno) + ".jpg"

        img_page.save(img)

    return np.array(img_page)


def box_convert(page_size, bbox):
    """Convert bbox format from camelot to pdfminer format

    Args:
        page_size (_type_): dimension of the page as (width, height)
        bbox (_type_): the coordinate of the object in [x0, yo, x1, y1] format

    Returns:
        The coordinate of the object in pdfminer format
    """
    H_pdf = page_size[1]
    x_0, y_0, x_1, y_1 = bbox
    return [x_0, H_pdf - y_0, x_1, H_pdf - y_1]


def get_fonts_info(doc, page):
    """Extracts fonts and their usage in PDF documents.

    Args:
        doc (<class 'fitz.fitz.Document'>): PDF document to iterate through
        page (int): page number

    Returns:
       font_counts (int): number of fonts
       styles (dict): text format in dictionary with size, flags, font and color
    """
    styles = {}
    font_counts = {}
    page = doc[page - 1]  # count from 0
    blocks = page.getText("dict")["blocks"]
    for b in blocks:  # iterate through the text blocks
        if b["type"] == 0:  # block contains text
            for line in b["lines"]:  # iterate through the text lines
                identifier = "{0}".format(
                    re.sub(
                        "\s\s+",
                        " ",
                        " ".join(
                            [
                                s["text"].strip()
                                for s in line["spans"]
                                if s["text"] != ""
                            ]
                        )
                        .replace(" . ", ". ")
                        .strip(),
                    )
                )
                identifier = re.sub("\s\s+", " ", identifier)
                styles[identifier] = {}
                for s in line["spans"]:  # iterate through the text spans
                    styles[identifier][s["text"]] = {
                        "size": s["size"],
                        "flags": [
                            "superscripted"
                            if s["flags"] <= 1
                            else (
                                "italic"
                                if s["flags"] <= 2
                                else (
                                    "serifed"
                                    if s["flags"] <= 4
                                    else ("monospaced" if s["flags"] <= 8 else "bold")
                                )
                            )
                        ][0],
                        "font": s["font"],
                        "color": hex(s["color"]).replace("0x", ""),
                        "bbox": s["bbox"],
                    }

                font_counts[identifier] = (
                    font_counts.get(identifier, 0) + 1
                )  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles


def extract_font_info(pdf_path: str, page: int):
    """Extract font information

    Args:
        pdf_path (str|ospath|path): part to pdf file
        page (int): page number

    Returns:
        stypes (dict): Page information with text and font metadata

    """
    with fitz.open(pdf_path) as doc:
        _, styles = get_fonts_info(doc, page)

    return styles
