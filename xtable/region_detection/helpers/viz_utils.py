import os
import pathlib
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np

from source.pdf_table_extraction.helpers.img_utils import img_dim


def save_viz_img(
    pdf_file: Union[pathlib.Path, str],
    pgno: int,
    img: np.array,
    table_bounds: List,
    output_path: str = "data/OUTPUT/",
):
    """Save pdf page to image"""
    plt.figure()
    if len(table_bounds) != 0:
        # save output image
        for out in table_bounds:
            [
                [x1_img, y1_img, x2_img, y2_img],
                [w_table, h_table],
                [H_img, W_img],
            ] = img_dim(img, out)
            plt.plot(
                [x1_img, x2_img, x2_img, x1_img, x1_img],
                [y1_img, y1_img, y2_img, y2_img, y1_img],
                linestyle="-.",
                alpha=1,
            )
            plt.scatter([x1_img, x2_img], [y1_img, y2_img])
            # imgplot = plt.imshow(img)
    # else:
    #     imgplot = plt.imshow(img)
    # save image
    file_name = pdf_file.split("/")[-1]
    path = output_path + file_name[:-4]
    if not os.path.isdir(path):
        os.makedirs(path)
    plt.savefig(
        path + "/" + file_name[:-4] + "-" + str(pgno) + ".png", format="png", dpi=200
    )
    # plt.close()
    plt.imshow(img)
