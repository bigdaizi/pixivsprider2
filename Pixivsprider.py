import re,urllib,threading,urllib2

#--------------------need------------------------
rootURL = 'http://www.pixiv.net'
startURL = 'http://www.pixiv.net'
cookie = 'p_ab_id=3; visit_ever=yes; login_ever=yes; device_token=f4caaf122678037f5fc9edfafe074280; module_orders_mypage=%5B%7B%22name%22%3A%22everyone_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22spotlight%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22featured_tags%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22contests%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22following_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22mypixiv_new_illusts%22%2C%22visible%22%3Atrue%7D%2C%7B%22name%22%3A%22booth_follow_items%22%2C%22visible%22%3Atrue%7D%5D; _ga=GA1.2.1333308821.1450873638; __utmt=1; PHPSESSID=89c0ef50a24a4f2ae2f3bf43a626f5b6; __utma=235335808.1333308821.1450873638.1450941690.1450943735.7; __utmb=235335808.3.10.1450943735; __utmc=235335808; __utmz=235335808.1450873638.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^5=gender=male=1^6=user_id=11258010=1; _ga=GA1.3.1333308821.1450873638'
#ver0.1修改cookie
Path = 'F:/'
pixiv_start = 'http://www.pixiv.net/search.php?word='
pixiv_end = '&order=date_d&p='
pixiv_keyword = str(raw_input(u'请输入查找目标\n'))
pixiv_url = pixiv_start + pixiv_keyword + pixiv_end 
start_page = int(raw_input(u'请输入第一个页面\n'))
class spider:
    def __init__(self,keyword,startPage):  #初始化
        self.rootURL = rootURL
        self.startURL = pixiv_url
        self.page = startPage
        self.keyword = urllib.quote(keyword)    
        
    def getHrefList(self,page): #获取小图超链接
        print ('4')
        pattern = r'(/member_illust\.php\?mode.*?)"'.encode('utf-8')
        Newpage = re.compile(pattern)
        print ('5')
        return re.findall(Newpage,page)
        
    def getPage(self):
        pageURL =self.startURL + str(self.page)
        req = urllib2.Request(pageURL)
        req.add_header('Cookie',cookie)
        print ('Opening',pageURL)
        resp = urllib2.urlopen(req)
        self.page += 1
        try:
            print ('2')
            page = resp.read()
        except ValueError:
            print ('GGGGGGGGGG') #页面无法读出    
        return page    
                
    def saveImg(self):
        counter = 0
        while True:
            page = self.getPage()  #搜索记录
            print ('1')
          #  page = re.sub('"' , '', page) 
            hrefList = self.getHrefList(page)
            print ('3')
            for href in hrefList:
                imgPageURL = self.rootURL + href.decode('utf-8') 
                req = urllib2.Request(imgPageURL)
                req.add_header('Cookie', cookie)
                print ('Opening image page ', imgPageURL)
                try:
                    resp = urllib2.urlopen(req)
                    print ('6')
                except:
                    print ('Error opening ',imgPageURL)
                    status = urllib.urlopen(imgPageURL).getcode()
                    print status
                    continue
                imgPage = resp.read()
                pattern = r'src="(http://i1.pixiv.net/c/600x600.*?)\.jpg"'.encode('utf-8')
                print ('7')
                imgRe = re.compile(pattern)
                imgList = re.findall(imgRe,imgPage)
                for img in imgList:
                    filename = RemoveIllegalChars(img.decode('utf-8') )
                    imgURL = img.decode('utf-8') + '.jpg'#第一组是文件名，第二组是图片URL
                    print ('Downloading ',filename.encode('gb18030'),' from ',imgURL) 
                    try:
                        req = urllib2.Request(imgURL)
                        referer = imgPageURL
                        req.add_header('Referer',referer) #没有这个header会出现403 error
                        resp = urllib2.urlopen(req,timeout=30)
                        data = resp.read()
                    except:
                        print ('Error saving image from ', imgURL)
                        continue
                    image = open(RemoveIllegalChars(filename)+'.jpg','wb')
                    image.write(data)
                    image.close()
                    print (filename.encode('gb18030'),' saved')
                    #gb18030能编码日文汉字，gbk有时会出错
                    counter += 1

class spiderThread(threading.Thread):
    def __init__(self,startPage = 1):
        threading.Thread.__init__(self)
        self.spider = spider(pixiv_keyword,start_page)
        print ('Start page',start_page)
    def run(self):
        lock = threading.RLock()
        with lock:
            self.spider.saveImg()      

def RemoveIllegalChars(filename):
    pattern =r'[\\/?\:\-;\*",.\_|]'    #正则表达式处理文件名
    return re.sub(pattern,"",filename)
        
         
for i in range(1):
    page = i
    t = spiderThread(page)
    t.start()
     
   
