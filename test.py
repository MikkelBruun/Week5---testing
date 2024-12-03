from dataclasses import dataclass
import pytest, os, re
from Controller import Controller
from Downloader import Downloader
from Polar_File_Handler import FileHandler
from pathlib import Path
import polars as pl
@dataclass
class T_Paths:
    customer_data = Path("customer_data")
    def_metadata_file = customer_data / "Metadata2017_2020.xlsx"
    def_input_file = customer_data / "GRI_2017_2020.xlsx"
    downloaded_files_folder = Path("files")
class T_Data:
    working_urls = [
        "http://www.amgen.com/~/media/amgen/full/www-amgen-com/downloads/responsibility-report/amgen-2016-responsibility-highlights-report.pdf",
        "http://pdf.dfcfw.com/pdf/H2_AN201703200422135019_01.pdf"
    ]
    def get_working_url(): return T_Data.working_urls[0]
    failing_urls = [
        "http://web.ardentec.com/UserFiles/File/2016%20Ardentec%20CSR%20Report.pdf",
        
    ]
    def get_failing_url(): return T_Data.failing_urls[0]
    timeout_url = "http://about.americanexpress.com/csr/docs/Amex-CSR-Report-Full-2016.pdf"

class TestUnit:
    def test_download_file(self, tmp_path):
        fname = "testfile.pdf"
        DL = Downloader()
        DL.download(T_Data.get_working_url(),
                    tmp_path / fname)
        dirfiles = os.listdir(tmp_path)
        assert(len(dirfiles) == 1)
        assert(dirfiles[0] == fname)

    def test_download_file_backup(self, tmp_path):
        """Make sure a backup url is used when first url fails"""
        fname = "testfile.pdf"
        DL = Downloader()
        DL.download(T_Data.get_failing_url(), 
                    tmp_path / fname, 
                    alt_url=T_Data.get_working_url())
        dirfiles = os.listdir(tmp_path)
        assert (len(dirfiles) == 1)
        assert (dirfiles[0] == fname)


class TestIntegration:
    """
    tests ending with _R requires a previous run of the program under regular conditions.
    Will then cross-check the downloaded files with the meta files 
    """
    def fi
    def test_downloaded_nameformat_R(self,):
        for file in os.listdir(T_Paths.downloaded_files_folder):
            assert(re.match(r"^BR\d+\.pdf$",file))

    def test_meta_yes_in_files_R(self,):
        meta_data = pl.read_excel(
            source=T_Paths.def_metadata_file, 
            columns=["BRnum", "pdf_downloaded"]
        )
        files_folder = set(os.listdir(T_Paths.downloaded_files_folder))
        yes_set = {f"{id}.pdf" for id, status in meta_data.iter_rows()
                   if status == "yes"}
        # intersection of these sets should be identical
        assert(yes_set.intersection(files_folder) == yes_set)

    def test_meta_no_not_in_files_R(self):
        meta_data = pl.read_excel(
            source=T_Paths.def_metadata_file,
            columns=["BRnum", "pdf_downloaded"]
        )
        files_folder = set(os.listdir(T_Paths.downloaded_files_folder))
        no_set = {f"{id}.pdf" for id, status in meta_data.iter_rows()
                   if status == "no"}
        # these sets should have no overlap
        assert (no_set.intersection(files_folder) == {})

    def test_file_content(self):
        """
        Confirm that the downloaded files are pdfs by checking the first four bytes
        """
        startChars = []
        for file in os.listdir(T_Paths.downloaded_files_folder):
            with open(T_Paths.downloaded_files_folder / file, "rb") as F:
                startChars.append(F.read(4))
        assert (startChars == [b"%PDF" for _ in range(len(startChars))])
if __name__ == "__main__":
    pass