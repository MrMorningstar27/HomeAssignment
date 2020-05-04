import pymongo
from requests import get
import bs4 as bs

def DataBaseInit():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    mydb = myclient["mydatabase"]
    myCol = mydb["Brand"]
def PyCrawler():
    DataBaseInit()
    

def PageCrawl():
    current_page = list()
    for index in range(7):
        current_page.append(get("http://www.rockchipfirmware.com/firmware-downloads-5?page="+str(index)).text)
    html_soup = bs(current_page, 'html.parser')
    html_soup.find_all('div', class_ = 'views-field views-field-field-brand')



def findAmountOfPagesToCrawl():
    htmlS = bs( get("http://www.rockchipfirmware.com/firmware-downloads-5?page=0").text, 'html.parser')
    res = str(htmlS.find('div', class_ = 'pager-current').get_text(strip=True))
    return res[res.rindex(' '):len(res)]
if __name__ == "__main__":    
    crawler = PyCrawler()    
    crawler.start()