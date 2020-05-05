import pymongo
from requests import get
import bs4 as bs
import sys
#connection to mongoDB free Atlas server for testing
client = pymongo.MongoClient("mongodb+srv://TCPizza:1478963250n@datacrawled-i1kaj.mongodb.net/test?retryWrites=true&w=majority")

FirmwareDB = client["DATA"]
metadata = FirmwareDB["metadata"]
verbose = False

def main():
    global verbose
    if sys.argv[0] == None: raise Exception("Please read README and provide arguments")
    for arg in sys.argv[1:]:
        if arg =='--h':
            print('''
            Command format: "python3 WebCrawler.py <option> <site_url>
            --h - list of all commands
            --v - verbose
            ''')
            break
        elif arg == '--v':
            verbose = True
        elif arg == "https://www.rockchipfirmware.com/":
            PageCrawl()
            print("Done!")
            break
        elif "http://" in arg or 'https://' in arg:
            print("This webpage is not supported yet")
        else:
            print("Incorect format, please check README for more info")



def PageCrawl():
    global verbose
    pages = list()
    id = 0 #unique index to check if there is a duplicate
    numberOfPages = findAmountOfPagesToCrawl()
    #get all pages into a list for further parsing
    for index in range(int(numberOfPages)+1):
        pages.append(get("http://www.rockchipfirmware.com/firmware-downloads?page="+str(index)).text)
    #parse each page in found pages
    for page in pages:
        html_soup = bs.BeautifulSoup(page, 'html.parser')
        data = html_soup.find_all('tr', class_ = ['odd','even','odd views-row-first','even views-row-last'])
        '''
        logic flow:
        create dict of metadata+data ==>
        if same dict exists in Database, raise duplicate alert==>
        if id is in Database but data is diffrent, update database with new dict==>
        if id doesn't exist, add dict to collection.
        '''
        for item in data:
            item = createObject(item, id)
            #if dict item exists in the dbthen alert duplicate
            if item == metadata.find_one({"_id":id}):
                if verbose: print("DUPLICATE ALERT on id: "+str(id))
            else:
                if type(metadata.find_one({"_id":id})) != type(None):
                    metadata.update_one(metadata.find_one({"_id":id}), item)
                else:
                    metadata.insert_one(item)
                    if verbose: print(str(item)+"\n\n")
            id += 1#_id auto increment
            


'''
create object to add to mongoDB with the folowing fields:
id, model, name, Node(refrence for downloading file),andriod version, Author
returns as dict to add to mongoDB
'''        
def createObject(item, id):
    FRef = ""
    CHUNK = ''
    node = item.find_all('a',href=True)[0]['href']
    if '\\' in node:
        node = node.replace('\\','/')
    #print(node) - DEBUG
    File = (bs.BeautifulSoup(get("http://www.rockchipfirmware.com/"+node).text, 'html.parser')).find_all('a',href=True)
    #print(File) - DEBUG
    for x in File:
        if "rockchip" in x['href']:
            FRef = x['href']
            break
    if FRef != '':
        CHUNK = get(FRef,stream = True).raw.read(1024)
    else:
        CHUNK=None
    return {"_id":id,
            "Brand":item.find('td', class_ = "views-field views-field-field-brand").get_text(strip=True),
            "Model":item.find('td', class_ = "views-field views-field-field-model").get_text(strip=True),
            "Name":item.find('td', class_ = "views-field views-field-title").get_text(strip=True),
            "Node":node,
            "FileRef":FRef,
            "AndriodVersion":item.find('td', class_ = "views-field views-field-field-android-version2").get_text(strip=True),
            "Author":item.find('td', class_ = "views-field views-field-field-firmware-author").get_text(strip=True),
            "DOWNLOADED":CHUNK
            }


#for a dynamic Crawl 
#the number of pages could change so i take the current amount
def findAmountOfPagesToCrawl():
    htmlS = bs.BeautifulSoup(get("http://www.rockchipfirmware.com/firmware-downloads?page=0").text, 'html.parser')
    #get text in format "1 to <lastPage>"
    res = htmlS.find('li', class_ = 'pager-current').get_text(strip=True)

    #Return index of last page
    return res[res.rindex(' ')+1:len(res)]


if __name__ == "__main__": 
    try:
        main()   
    except Exception as e:
        print(e)
     
    