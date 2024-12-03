from Polar_File_Handler import FileHandler
from typing import Optional
import os
import argparse

#Class for instantiating a download from a file into a given path. 
class Controller(object):

    #Initiates the controller class with default values
    def __init__(self) -> None:
        self.url_file_name = os.path.join("customer_data","GRI_2017_2020.xlsx")
        self.report_file_name = os.path.join("customer_data","Metadata2017_2020.xlsx")
        self.destination = "files"

    #Overwrites the file containing the url's
    def set_url_file(self,url_file_name : str) -> None:
        self.url_file_name = url_file_name
    
    #Overwrites the file to report succesfull downloads
    def set_report_file(self,report_file_name : str) -> None:
        self.report_file_name = report_file_name
    
    #Overwrites download destination
    def set_destination(self,destination : str) -> None:
        self.destination = destination

    #Runs the filehandler
    def run(self,number_of_threads : Optional[int] = None)->None:
        if number_of_threads: 
            file_handler = FileHandler(number_of_threads)
        else:
            file_handler = FileHandler()
        file_handler.start_download(self.url_file_name,self.report_file_name,self.destination)

#My main function
if __name__ == "__main__":
    controller = Controller()

    #Adds a commandline parser
    parser = argparse.ArgumentParser()

    #Adss the parameters for overwriting files, paths and number of threads
    parser.add_argument("-uf","--url_file",help = "Path to where the file containing the url's are")
    parser.add_argument("-rf","--report_file", help = "The path to where the report should go")
    parser.add_argument("-d","--destination",help="Folder where the downloaded files should go")
    parser.add_argument("-t","--threads", help = "The number of threads")

    #Gets the parameters from the commandline and applies them where appropriate
    args = parser.parse_args()
    if args.url_file:
        controller.set_url_file(args.url_file)
    if args.report_file:
        controller.set_report_file(args.report_file)
    if args.destination:
        controller.set_destination(args.destination)
    if args.threads:
        try:
            controller.run(int(args.threads))
        except:
            print("Thread should be an integer")
    else:
        controller.run()
