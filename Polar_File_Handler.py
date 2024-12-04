from Downloader import Downloader
import os
from pathlib import Path
import threading
from typing import Optional
from queue import Queue
import polars as pl
from xlsxwriter import Workbook

#Class for handling a file with download links
class FileHandler(object):
   
    #Creates an instance of the filehandler with a dictionary of successfull downloads
    def __init__(self,number_of_threads : Optional[int] = 10) -> None:
        self.number_of_threads = number_of_threads

    #Function that starts a download instance using the downloader class. Used in threads
    def download_thread(self,queue:Queue) -> None:
        while not queue.empty():
            
            link, destination, name, alt_link, finished_dict = queue.get()
            downloader = Downloader()
            Path(destination).mkdir(exist_ok=True)

            #Dictionaries are not necesarily thread safe but appending to it is so this is fine. If more complicated tasks where needed you would use a mutex lock etc
            ## RETTELSE finished_dict["BRnum"].append(name)
            downloaded = downloader.download(url=link,destination_path=os.path.join(destination, name+".pdf"), alt_url=alt_link)
            if downloaded:
                finished_dict[name]="yes" ## RETTELSE
            else:
                finished_dict[name]="no" ## RETTELSE
            queue.task_done()

    #Starts downlaoding files from urls listed in url_file which will be placed in the destination, and reported in the meta file
    def start_download(self, url_file : str,meta_file : str,destination : str, max_rows=20) -> None:

        file_data = pl.read_excel(source=url_file, columns= ["BRnum", "Pdf_URL", "Report Html Address"])
        
        #We index after the BRnums for now
        ID = "BRnum"

        #Initiates empty dataframe
        report_data = pl.DataFrame()
        #Tries reading the files listed as not downloaded if it fails it will make a new meta file that fullfills the structure
        try:
            report_data = pl.read_excel(meta_file, columns = [ID,"pdf_downloaded"])
            report_data=report_data.filter(pl.col("pdf_downloaded") == "yes")
            #Sort out files that are downloaded
            file_data = file_data.join(report_data,on=ID, how="anti")
        except:
            print("New meta data file will be created")

        queue = Queue()

        #Creates a dictionary of downloads
        finished_dict = {} ## RETTELSE
        #{ID:[],"pdf_downloaded":[]}

        #counter to only download 10 files
        j = 0
        #We thru each br number and starts a download
        for row in file_data.rows(named=True):
            if j == max_rows:
                break
            alt_link = row["Report Html Address"]
            link = row["Pdf_URL"]
            index = row[ID]            
            #Creates a new thread and adds them to the list so that we can make sure all downloads are done before exiting
            queue.put([link,destination,index,alt_link,finished_dict])
            j += 1
        #Makes sure each thread is done
        for i in range(self.number_of_threads):
            thread = threading.Thread(target=self.download_thread, args = (queue,))
            thread.start()

        queue.join()
        #Creates a dataframe from the dictionary of downloads
        ## RETTELSE
        #finished_data_frame = pl.from_dict(finished_dict)
        _finished_dict = {ID: [key for key in finished_dict], "pdf_downloaded": [finished_dict[key] for key in finished_dict]}
        finished_data_frame = pl.from_dict(_finished_dict)
        ## /RETTELSE
        if not report_data.is_empty():
            finished_data_frame = pl.concat([finished_data_frame,report_data],rechunk = True)
        with Workbook(meta_file) as file:
            finished_data_frame.write_excel(workbook = file)
        

if __name__ == "__main__":
    file_handler = FileHandler()
    file_handler.start_download(os.path.join("customer_data","GRI_2017_2020.xlsx"),os.path.join("customer_data","Metadata2017_2020.xlsx"),"files")
