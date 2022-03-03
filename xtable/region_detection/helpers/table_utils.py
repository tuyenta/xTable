import re
from typing import List

import pandas as pd


def extract_table_styles(
    df: pd.DataFrame,
    page_styles: List[dict],
):
    """Get a list of list mapping of the cells styles in the table df

    Args:
        df (pd.DataFrame): input dataframe of the table
        page_styles (List[dict]): styles of all text in the page

    Returns:
        table_styles(List[List[dict]]): styles of textboxes in the table
    """

    df = df.to_numpy().tolist()
    table_styles = [
        [
            page_styles.get(
                re.sub(
                    "\s\s+",
                    " ",
                    i.replace("<s> \x83</s>", "")
                    .replace("<s>(1)</s>", "")
                    .replace(" \n ", " ")
                    .split("\n", 1)[0]
                    .strip(),
                ),
                {},
            )
            if i != ""
            else {}
            for i in data
        ]
        for data in df
    ]

    return table_styles


def get_cell_style(
    df: pd.DataFrame,
    row_index: int,
    col_index: int,
    table_styles: List[List[dict]],
    info="size",
):
    """Get some information on a cell of the table

    Mainly used to distinguish titles and subtitles when merging the headers of a table by comparing the sizes.
    Available informations in the argument 'table_styles' are size; flags; color and bbox. This method depends
    on the way table_styles are extracted  (see the previous method :extract_table_styles). If any changes occur
    in the format of the table_styles extraction, this method should  be updated accordingly.
    In some cases the cell in the table_styles could contain an empty dict, meaning the cell style is missing.

    Args:
        df (pd.DataFrame): needed to check the mapping of the styles
        row_index (int): index of the row
        col_index (int): index of the column
        table_styles (List[List[dict]]): mapping of the table cells styles
        info (str, optional): Defaults to 'size'.

    Returns:
        Depends on the fetched info
        in the case of size:
            [int]: 0 if the style of the correspondant cell is missing
    """

    cell_text = df.iat[row_index, col_index]
    cell_dict = table_styles[row_index][col_index]

    for (key, value) in cell_dict.items():
        if key.strip(". ") == cell_text.strip(". "):
            if info in value.keys():
                return value[info]

    return 0
