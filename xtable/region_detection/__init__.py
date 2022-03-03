# -*- coding: utf-8 -*-
import os
import pathlib
from typing import Union

from source.pdf_table_extraction.helpers.img_utils import bboxes_pdf
from source.pdf_table_extraction.helpers.pdf_utils import norm_pdf_page, pdf_page2img
from source.pdf_table_extraction.table_extraction.detect_table_region.detect_func import (
    detectTable,
    parameters,
)


def output_yolo(output):
    """Gets the output of yolo model

    Args:
        output (str): output of yolo model in string format

    Returns:
        bboxes (tuple): list of boundaries of table in the pdf page in top-left, right-bottom format
    """

    output = output.split("\n")
    output.remove("")

    bboxes = []
    for x in output:
        cleaned_output = x.split(" ")
        cleaned_output.remove("")
        cleaned_output = [eval(x) for x in cleaned_output]
        bboxes.append(cleaned_output)

    return bboxes


def detect_table_regions(
    pdf_file: Union[pathlib.Path, str], page_number: int, img_size: int = 300
):
    """Detect the table in pdf page

    Args:
        pdf_file (path|str): path to pdf file
        pg (int): value of pdf page

    Returns:
        pdf_page (object): the pdf page
        output_DL (string): output of the model in string
        img_path (path): the path to temporary image
    """

    # convert pdf page to img and detect table from img
    img_path = pdf_file[:-4] + "-" + str(page_number) + ".jpg"
    pdf_page = norm_pdf_page(pdf_file, page_number)
    img = pdf_page2img(pdf_file, page_number, save_image=True)
    opt = parameters(img_path, img_size=img_size)
    output_detect = detectTable(opt)
    output_DL = output_yolo(output_detect)

    # Remove temporary files and folders
    os.remove(img_path)
    os.rmdir("data/parsing_outputs")

    return pdf_page, output_DL, img


def convert_table_regions_from_img_to_pdf(table_bounds, img, pdf_page):
    """Convert table bounds in image to table region in pdf page
    Args:
        table_bounds (list): list of table bounds
        img (object): image
        pdf_page (object): pdf page
    Returns:
        interesting_areas (list): list of table's regions
    """
    interesting_areas = []
    if len(table_bounds) != 0:
        for x in table_bounds:
            # Normalize the output of the model to fit with the size of pdf file
            [x1, y1, x2, y2] = bboxes_pdf(img, pdf_page, x)
            interesting_areas.append([x1, y1, x2, y2])

    # Correct the table boundary by comparing the output
    # If two tables are overlap, then correct the coordinate of the first one.
    if len(interesting_areas) == 1:
        interesting_areas[0][1] = interesting_areas[0][1] * 1.05
        interesting_areas[0][3] = interesting_areas[0][3] * 1.05

    if len(interesting_areas) == 2:
        if interesting_areas[0][1] > interesting_areas[1][3]:
            interesting_areas[1][3] = interesting_areas[0][1] * 1.15
            interesting_areas[0][1] = interesting_areas[0][1] * 1.05
        elif interesting_areas[1][1] > interesting_areas[0][3]:
            interesting_areas[0][3] = interesting_areas[1][1] * 1.15
            interesting_areas[1][1] = interesting_areas[1][1] * 1.05

    # Convert the boundaries of table to camelot format
    # x1,y1,x2,y2 where (x1, y1) -> left-top and (x2, y2) -> right-bottom in PDF coordinate space
    interesting_areas = [
        ",".join([str(coor) for coor in area]) for area in interesting_areas
    ]

    print("\n Boundaries of table:", interesting_areas)
    return interesting_areas
