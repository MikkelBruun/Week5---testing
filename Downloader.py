import requests
from typing import Optional

#Class for handling a single download. The function main functionality is to take an url and download it into the path
class Downloader(object):

    #uses a url link and a destination to download a file. Optionally one can use an alt url if applicaple
    #Returns success is file got downlaoded
    def download(self,url : str, destination_path : str, alt_url : Optional[str] = None) -> bool:
        print("DOWNLOAD")
        success = True
        if not url and not alt_url:
            return False
        #Tries downloading with the main url
        try:
            response = requests.get(url,stream = True, timeout=30)
            #Checks if the response was a pdf file
            if not "application/pdf" in response.headers.get("content-type"):
                raise Exception("Not pdf type")
        except Exception as e:
            print(e)
            success = False
        
        #If it fails to download try the alternative url
        if not success:
            try:
                response = requests.get(alt_url, stream = True, timeout=30)
                #Checks if the response was a pdf file
                if not "application/pdf" in response.headers.get("content-type"):
                    raise Exception("Not pdf type")

                success = True
            except:
                return False
       
        #Sace file to the distination
        with open(destination_path, "wb") as file:
            try:
                file.write(response.content)
            except:
                return False
        return success
if __name__ == "__main__":
    downloader = Downloader()
    downloader.download("http://arpeissig.at/wp-content/uploads/2016/02/D7_NHB_ARP_Final_2.pdf", "test.pdf")
