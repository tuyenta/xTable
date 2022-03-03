# # -*- coding: utf-8 -*-

# import os
# import sys

# from PyPDF2 import PdfFileReader, PdfFileWriter

# from .core import TableList
# from .parsers import Stream, Lattice
# from .utils import (
#     TemporaryDirectory,
#     get_page_layout,
#     get_text_objects,
#     get_rotation,
#     is_url,
#     download_url,
# )


# class PDFHandler(object):
#     """Handles all operations like temp directory creation, splitting
#     file into single page PDFs, parsing each PDF and then removing the
#     temp directory.

#     Parameters
#     ----------
#     filepath : str
#         Filepath or URL of the PDF file.
#     pages : str, optional (default: '1')
#         Comma-separated page numbers.
#         Example: '1,3,4' or '1,4-end' or 'all'.
#     password : str, optional (default: None)
#         Password for decryption.

#     """

#     def __init__(self, filepath, pages="1", password=None):
#         if is_url(filepath):
#             filepath = download_url(filepath)
#         self.filepath = filepath
#         if not filepath.lower().endswith(".pdf"):
#             raise NotImplementedError("File format not supported")

#         if password is None:
#             self.password = ""
#         else:
#             self.password = password
#             if sys.version_info[0] < 3:
#                 self.password = self.password.encode("ascii")
#         self.pages = self._get_pages(pages)

#     def _get_pages(self, pages):
#         """Converts pages string to list of ints.

#         Parameters
#         ----------
#         filepath : str
#             Filepath or URL of the PDF file.
#         pages : str, optional (default: '1')
#             Comma-separated page numbers.
#             Example: '1,3,4' or '1,4-end' or 'all'.

#         Returns
#         -------
#         P : list
#             List of int page numbers.

#         """
#         page_numbers = []

#         if pages == "1":
#             page_numbers.append({"start": 1, "end": 1})
#         else:
#             with open(self.filepath, "rb") as f:
#                 infile = PdfFileReader(f, strict=False)

#                 if infile.isEncrypted:
#                     infile.decrypt(self.password)

#                 if pages == "all":
#                     page_numbers.append({"start": 1, "end": infile.getNumPages()})
#                 else:
#                     for r in pages.split(","):
#                         if "-" in r:
#                             a, b = r.split("-")
#                             if b == "end":
#                                 b = infile.getNumPages()
#                             page_numbers.append({"start": int(a), "end": int(b)})
#                         else:
#                             page_numbers.append({"start": int(r), "end": int(r)})

#         P = []
#         for p in page_numbers:
#             P.extend(range(p["start"], p["end"] + 1))
#         return sorted(set(P))

#     def _save_page(self, filepath, page, temp):
#         """Saves specified page from PDF into a temporary directory.

#         Parameters
#         ----------
#         filepath : str
#             Filepath or URL of the PDF file.
#         page : int
#             Page number.
#         temp : str
#             Tmp directory.

#         """
#         with open(filepath, "rb") as fileobj:
#             infile = PdfFileReader(fileobj, strict=False)
#             if infile.isEncrypted:
#                 infile.decrypt(self.password)
#             fpath = os.path.join(temp, f"page-{page}.pdf")
#             froot, fext = os.path.splitext(fpath)
#             p = infile.getPage(page - 1)
#             outfile = PdfFileWriter()
#             outfile.addPage(p)
#             with open(fpath, "wb") as f:
#                 outfile.write(f)
#             layout, dim = get_page_layout(fpath)
#             # fix rotated PDF
#             chars = get_text_objects(layout, ltype="char")
#             horizontal_text = get_text_objects(layout, ltype="horizontal_text")
#             vertical_text = get_text_objects(layout, ltype="vertical_text")
#             rotation = get_rotation(chars, horizontal_text, vertical_text)
#             if rotation != "":
#                 fpath_new = "".join([froot.replace("page", "p"), "_rotated", fext])
#                 os.rename(fpath, fpath_new)
#                 instream = open(fpath_new, "rb")
#                 infile = PdfFileReader(instream, strict=False)
#                 if infile.isEncrypted:
#                     infile.decrypt(self.password)
#                 outfile = PdfFileWriter()
#                 p = infile.getPage(0)
#                 if rotation == "anticlockwise":
#                     p.rotateClockwise(90)
#                 elif rotation == "clockwise":
#                     p.rotateCounterClockwise(90)
#                 outfile.addPage(p)
#                 with open(fpath, "wb") as f:
#                     outfile.write(f)
#                 instream.close()

#     def parse(
#         self, flavor="lattice", suppress_stdout=False, layout_kwargs={}, **kwargs
#     ):
#         """Extracts tables by calling parser.get_tables on all single
#         page PDFs.

#         Parameters
#         ----------
#         flavor : str (default: 'lattice')
#             The parsing method to use ('lattice' or 'stream').
#             Lattice is used by default.
#         suppress_stdout : str (default: False)
#             Suppress logs and warnings.
#         layout_kwargs : dict, optional (default: {})
#             A dict of `pdfminer.layout.LAParams <https://github.com/euske/pdfminer/blob/master/pdfminer/layout.py#L33>`_ kwargs.
#         kwargs : dict
#             See xtable.read_pdf kwargs.

#         Returns
#         -------
#         tables : xtable.core.TableList
#             List of tables found in PDF.

#         """
#         tables = []
#         with TemporaryDirectory() as tempdir:
#             for p in self.pages:
#                 self._save_page(self.filepath, p, tempdir)
#             pages = [os.path.join(tempdir, f"page-{p}.pdf") for p in self.pages]
#             parser = Lattice(**kwargs) if flavor == "lattice" else Stream(**kwargs)
#             for p in pages:
#                 t = parser.extract_tables(
#                     p, suppress_stdout=suppress_stdout, layout_kwargs=layout_kwargs
#                 )
#                 tables.extend(t)
#         return TableList(sorted(tables))

# -*- coding: utf-8 -*-

import os
import sys
import fitz
import pathlib
from typing import Union

from .core import TableList
from .parsers import Stream, Lattice
from .helpers.utils import (
    TemporaryDirectory,
    get_page_layout,
    get_text_objects,
    get_rotation,
    is_url,
    download_url,
)


class PDFHandler(object):
    """Handles all operations like temp directory creation, splitting
    file into single page PDFs, parsing each PDF and then removing the
    temp directory.

    Parameters
    ----------
    filepath : str
        Filepath or URL of the PDF file.
    pages : str, optional (default: '1')
        Comma-separated page numbers.
        Example: '1,3,4' or '1,4-end' or 'all'.
    password : str, optional (default: None)
        Password for decryption.

    """

    def __init__(
        self,
        filepath: Union[pathlib.Path, str],
        pages: str = "1",
        password: Union[str, None] = None,
    ):
        if is_url(filepath):
            filepath = download_url(filepath)
        self.filepath = filepath
        if not filepath.lower().endswith(".pdf"):
            raise NotImplementedError("File format not supported")

        if password is None:
            self.password = ""
        else:
            self.password = password
            if sys.version_info[0] < 3:
                self.password = self.password.encode("ascii")
        self.layout = self._get_layout(filepath)
        self.pages = self._get_pages(pages)

    def _get_layout(self, filepath: Union[pathlib.Path, str]):
        """Get the layout of pdf file.
        Parameters
        ----------
        filepath : pathlib.Path|str
            Filepath or URL of the PDF file.

        Returns
        -------
        layout : object
            Object of pdf layout in pyMuPDF structure.
        """
        with open(filepath, "rb") as f:
            infile = fitz.Document(f)

            if infile.is_encrypted:
                if self.password is not None:  # decrypt if password provided
                    rc = infile.authenticate(self.password)
                    if not rc > 0:
                        raise ValueError("wrong password")
                    return rc
            else:
                return infile

    def _get_pages(self, pages):
        """Converts pages string to list of ints.

        Parameters
        ----------
        filepath : str
            Filepath or URL of the PDF file.
        pages : str, optional (default: '1')
            Comma-separated page numbers.
            Example: '1,3,4' or '1,4-end' or 'all'.

        Returns
        -------
        P : list
            List of int page numbers.

        """
        page_numbers = []

        if pages == "1":
            page_numbers.append({"start": 1, "end": 1})
        else:
            with open(self.filepath, "rb") as f:
                infile = fitz.open(f)

                if infile.is_encrypted:
                    infile.authenticate(self.password)

                if pages == "all":
                    page_numbers.append({"start": 1, "end": infile.page_count})
                else:
                    for r in pages.split(","):
                        if "-" in r:
                            a, b = r.split("-")
                            if b == "end":
                                b = infile.page_count
                            page_numbers.append({"start": int(a), "end": int(b)})
                        else:
                            page_numbers.append({"start": int(r), "end": int(r)})

        P = []
        for p in page_numbers:
            P.extend(range(p["start"], p["end"] + 1))
        return sorted(set(P))

    def _save_page(self, pgno: int, temp: Union[pathlib.Path, str]):
        """Extract specified page from PDF file and save into temporary directory.
        Parameters
        ----------
        pgno : int
            Page number.
            Example: 1.
        temp: pathlib.Path|str
            Temporary directory.
        """
        # read the pdf file
        with open(self.filepath, "rb") as fileobj:
            infile = fitz.open(fileobj)
            if infile.is_encrypted:
                infile.authenticate(self.password)

        # create new pdf file and get the pdf page
        newdoc_path = pathlib.Path(temp) / str(f"page-{pgno}.pdf")
        new_doc = fitz.open()
        new_doc.insert_pdf(self.layout, from_page=pgno, to_page=pgno)
        new_doc.save(newdoc_path)
        new_doc.close()
        layout, dim = get_page_layout(newdoc_path)

        # fix rotated PDF
        chars = get_text_objects(layout, ltype="char")
        horizontal_text = get_text_objects(layout, ltype="horizontal_text")
        vertical_text = get_text_objects(layout, ltype="vertical_text")
        rotation = get_rotation(chars, horizontal_text, vertical_text)
        if rotation != "":
            # init new document
            rotate_newdoc_path = pathlib.Path(temp) / str(f"page-{pgno}-rotated.pdf")
            rotate_doc = fitz.open()
            # rotate and save
            if rotation == "anticlockwise":
                # rotate page by 90 degrees anticounter-clockwise
                rotate_doc.insert_pdf(
                    self.layout, from_page=pgno, to_page=pgno, rotate=90
                )
            elif rotation == "clockwise":
                # rotate page by -90 degrees counter-clockwise
                rotate_doc.insert_pdf(
                    self.layout, from_page=pgno, to_page=pgno, rotate=-90
                )
                # save pdf file
            rotate_doc.save(rotate_newdoc_path)
            rotate_doc.close()

    def parse(
        self, flavor="lattice", suppress_stdout=False, layout_kwargs={}, **kwargs
    ):
        """Extracts tables by calling parser.get_tables on all single
        page PDFs.

        Parameters
        ----------
        flavor : str (default: 'lattice')
            The parsing method to use ('lattice' or 'stream').
            Lattice is used by default.
        suppress_stdout : str (default: False)
            Suppress logs and warnings.
        layout_kwargs : dict, optional (default: {})
            A dict of `pdfminer.layout.LAParams <https://github.com/euske/pdfminer/blob/master/pdfminer/layout.py#L33>`_ kwargs.
        kwargs : dict
            See camelot.read_pdf kwargs.

        Returns
        -------
        tables : camelot.core.TableList
            List of tables found in PDF.

        """
        tables = []
        with TemporaryDirectory() as tempdir:
            for p in self.pages:
                self._save_page(p, tempdir)
            pages = [os.path.join(tempdir, f"page-{p}.pdf") for p in self.pages]
            parser = Lattice(**kwargs) if flavor == "lattice" else Stream(**kwargs)
            for p in pages:
                t = parser.extract_tables(
                    p, suppress_stdout=suppress_stdout, layout_kwargs=layout_kwargs
                )
                tables.extend(t)
        return TableList(sorted(tables))
