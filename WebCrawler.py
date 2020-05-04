import pymongo
from requests import get
import bs4 as bs

client = pymongo.MongoClient("mongodb+srv://TCPizza:1478963250n@datacrawled-i1kaj.mongodb.net/test?retryWrites=true&w=majority")

FirmwareDB = client["DATA"]
metadata = FirmwareDB["metadata"]


def main(*args):
    for arg in args:
        pass
    PageCrawl()



def PageCrawl():
    pages = list()
    id = 0 #unique index to check if there is a duplicate
    numberOfPages = findAmountOfPagesToCrawl()
    #get all pages into a list for further parsing
    for index in range(int(numberOfPages)+1):
        pages.append(get("http://www.rockchipfirmware.com/firmware-downloads?page="+str(index)).text)
    for page in pages:
        html_soup = bs.BeautifulSoup(page, 'html.parser')
        data = html_soup.find_all('tr', class_ = ['odd','even','odd views-row-first','even views-row-last'])
        for item in data:
            item = createObject(item, id)
            if item == metadata.find_one({"_id":id}):
                print("DUPLICATE ALERT")
            else:
                try:
                    metadata.update_one(metadata.find_one({"_id":id}), item)
                except:
                    metadata.insert_one(item)
            id += 1
            #print(id)


'''
create object to add to mongoDB with the folowing fields:
id, model, name, Node(refrence for downloading file),andriod version, Author
returns as dict to add to mongoDB
'''        
def createObject(item, id):
    FRef = ""
    node = item.find_all('a',href=True)[0]['href']
    if '\\' in node:
        node = node.replace('\\','/')
    #print(node)
    File = (bs.BeautifulSoup(get("http://www.rockchipfirmware.com/"+node).text, 'html.parser')).find_all('a',href=True)
    #print(File)
    for x in File:
        if "rockchip" in x['href']:
            FRef = x['href']
            break

    return {"_id":id,
            "Brand":item.find('td', class_ = "views-field views-field-field-brand").get_text(strip=True),
            "Model":item.find('td', class_ = "views-field views-field-field-model").get_text(strip=True),
            "Name":item.find('td', class_ = "views-field views-field-title").get_text(strip=True),
            "Node":node,
            "FileRef":FRef,
            "AndriodVersion":item.find('td', class_ = "views-field views-field-field-android-version2").get_text(strip=True)
            ,"Author":item.find('td', class_ = "views-field views-field-field-firmware-author").get_text(strip=True)}

###FULLY WORKING
#for a dynamic Crawl 
#the number of pages could change so i take the current amount
def findAmountOfPagesToCrawl():
    htmlS = bs.BeautifulSoup(get("http://www.rockchipfirmware.com/firmware-downloads-5?page=0").text, 'html.parser')
    #get text in format "1 to <lastPage>"
    res = htmlS.find('li', class_ = 'pager-current').get_text(strip=True)

    #Return index of last page
    return res[res.rindex(' ')+1:len(res)]


if __name__ == "__main__":    
    main()    
    