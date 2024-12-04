from dataclasses import dataclass
from pprint import pprint
from queue import Queue
import pytest
import os
import re
import shutil
import time
from Controller import Controller
import Downloader
from Polar_File_Handler import FileHandler
from pathlib import Path
import polars as pl
from Polar_File_Handler import FileHandler

@dataclass()
class T_Paths:
    customer_data:Path = Path("customer_data")
    def_metadata_file: Path = customer_data / "Metadata2017_2020.xlsx"
    def_input_file: Path = customer_data / "GRI_2017_2020.xlsx"
    test_sheet_file: Path = Path("test_files/test_sheet.xlsx")
    downloaded_files_folder: Path = Path("files")
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
    """
    Test that when a get request fails, the secondary url is tried
    """
    def test_download_file_backup(self, tmp_path, monkeypatch: pytest.MonkeyPatch):
        """Make sure a backup url is used when first url fails"""
        fname = "testfile.pdf"
        DL = Downloader.Downloader()
        get_calls = []
        def mock_get(*args,**kwargs):
            get_calls.append(args[0] in T_Data.working_urls)
            return None
        monkeypatch.setattr("Downloader.requests.get", mock_get)
        DL.download(T_Data.get_failing_url(),
                    tmp_path / fname,
                    alt_url=T_Data.get_working_url())
        assert(get_calls == [False,True])
        
    def test_excel_reading(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        # values recived by download_thread as triples (BRid, url1, url2)
        values = {}
        def mock_download_thread(self, queue: Queue) -> None:
            while not queue.empty():
                link, destination, name, alt_link, finished_dict = queue.get()
                time.sleep(0.1)
                values[name] = (link,alt_link)
                queue.task_done()
        monkeypatch.setattr(FileHandler, "download_thread", mock_download_thread)
        expected = {f"BR{id}":(f"http://internet.site.BR{id}.com", f"http://internet.backup.BR{id}.com")
                    for id in range(50100, 50157)}
        FH = FileHandler()
        FH.start_download(T_Paths.test_sheet_file,tmp_path / "metafilepath","testfiles",max_rows=-1)
        del values["BRnum"] # remove header
        assert(values == expected)



class TestIntegration:
    """
    tests ending with _R requires a previous run of the program under regular conditions.
    Will then cross-check the downloaded files with the meta files 
    """
    @pytest.fixture(scope="class",)
    def prep_integration(self):
        tmp = Path("./tmp")
        os.makedirs(tmp,exist_ok=True)
        os.makedirs(tmp / "customer_data", exist_ok=True)
        C = Controller()
        tmp_path = T_Paths(**{
            "customer_data" : "customer_data",
            "def_metadata_file": tmp/"customer_data"/"Metadata2017_2020.xlsx",
            "def_input_file" : tmp/"customer_data" / "GRI_2017_2020.xlsx",
            "downloaded_files_folder" : tmp / "files",
        })
        pprint(tmp_path)
        os.makedirs(tmp_path.downloaded_files_folder, exist_ok=True)
        os.makedirs(tmp_path.customer_data, exist_ok=True)
        C.set_destination(tmp_path.downloaded_files_folder)
        C.set_report_file(tmp_path.def_metadata_file)
        C.run()
        print("setup")
        yield tmp_path
        shutil.rmtree(tmp)
        print("teardown")

    def test_download_file(self, tmp_path):
        fname = "testfile.pdf"
        DL = Downloader.Downloader()
        DL.download(T_Data.get_working_url(),
                    tmp_path / fname)
        dirfiles = os.listdir(tmp_path)
        assert (len(dirfiles) == 1)
        assert (dirfiles[0] == fname)
        
    def test_downloaded_nameformat_R(self, prep_integration):
        for file in os.listdir(prep_integration.downloaded_files_folder):
            assert(re.match(r"^BR\d+\.pdf$",file))

    def test_meta_yes_in_files_R(self, prep_integration):
        meta_data = pl.read_excel(
            source=prep_integration.def_metadata_file, 
            columns=["BRnum", "pdf_downloaded"]
        )
        files_folder = set(os.listdir(prep_integration.downloaded_files_folder))
        yes_set = {f"{id}.pdf" for id, status in meta_data.iter_rows()
                   if status == "yes"}
        # intersection of these sets should be identical
        assert(yes_set.intersection(files_folder) == yes_set)

    def test_meta_no_not_in_files_R(self, prep_integration):
        meta_data = pl.read_excel(
            source=prep_integration.def_metadata_file,
            columns=["BRnum", "pdf_downloaded"]
        )
        files_folder = set(os.listdir(prep_integration.downloaded_files_folder))
        no_set = {f"{id}.pdf" for id, status in meta_data.iter_rows()
                   if status == "no"}
        # these sets should have no overlap (empty set)
        assert (no_set.intersection(files_folder) == set())

    def test_file_content(self, prep_integration):
        """
        Confirm that the downloaded files are pdfs by checking the first four bytes
        """
        startChars = []
        for file in os.listdir(prep_integration.downloaded_files_folder):
            with open(prep_integration.downloaded_files_folder / file, "rb") as F:
                startChars.append(F.read(4))
        assert (startChars == [b"%PDF" for _ in range(len(startChars))])
if __name__ == "__main__":
    pass