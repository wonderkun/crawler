from tomd import Tomd
from parsel import Selector
import asyncio
import json
import time
from selenium import webdriver
import os
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a %d %b %Y %H:%M:%S')

class Httpx():
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-xss-auditor')
        chrome_options.add_argument('--no-sandbox')
        # driverpath = '/usr/local/bin/chromedriver'

        self.client = webdriver.Chrome(options=chrome_options)
        # client = webdriver.Chrome(chrome_options=chrome_options)
        self.client.set_page_load_timeout(20)
        self.client.set_script_timeout(20)

    def get(self,url):
        # 重试 3 次 
        self.client.implicitly_wait(8)
        for i in range(5):
            try:
                self.client.get(url)
            except Exception as e:
                logging.warning("Read url error info :{},retrying ... {}.".format( url,i))
                time.sleep(1)
            else:
                break

        for i in range(1, 11):
            # 滑到页面底部，让所有懒加载的图片全部加载出来
            self.client.execute_script(
                "window.scrollTo(0, document.body.scrollHeight/10*%s);" % i
            )
            time.sleep(0.5)
        return self.client.page_source

httpx = Httpx()

class Article(object):
    def __init__(self,name):
        self.name = name
        self.url = "http://{}/".format(self.name)
        self.store = self.name
        # self.attachment = "{}/img/".format(self.store)
        self.config_file = os.path.join("../",self.store,"all.json")
        self.readme_file = os.path.join("../",self.store,"README.md")

        with open(self.config_file,"r") as fd:
            self.config = json.load(fd)
        self.downArticles = set()
        self.articleUrls = {}

    def get_name(self):
        raise NotImplementedError

    def get_history(self):
        #读取历史的所有文章
        loop = asyncio.get_event_loop()

        # Python 3.6之前用ayncio.ensure_future或loop.create_task方法创建单个协程任务
        # Python 3.7以后可以用户asyncio.create_task方法创建单个协程任务
        tasks = []
        if not self.config["id"]:
            return
        for article in self.config["id"]:
            tasks.append(self.get_article( article ))
        
        # 还可以使用asyncio.gather(*tasks)命令将多个协程任务加入到事件循环
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

    def get_index(self):
        #读取首页解析最新的文章
        raise NotImplementedError

    async def get_article(self,article):
        # 读取一篇具体的文章
        raise NotImplementedError

    def update_config(self):
        self.config["read"] = True
        oldId = set( self.config["id"] )
        self.config["id"] = list( oldId | self.downArticles )
        with open(self.config_file,"w") as fd:
            json.dump(self.config,fd)

    def update_readme(self):
        with open(self.readme_file,"rb") as fd:
            oldContent = fd.read()
        date = time.strftime("%Y-%m-%d", time.localtime())
        content = "# {}\n".format(date)
        for key,value in self.articleUrls.items():
            content += "1. [{}]({})\n".format(key,value)

        content = content.encode()
        content += oldContent
        with open(self.readme_file,'wb') as fd:
            fd.write(content)

# class Xianzhi(Article):
#     def __init__(self,name):
#         super(Anquanke, self).__init__(name)
        

#     def get_name(self):
#         # raise NotImplementedError
#         return self.name

#     def get_history(self):
#         #读取历史的所有文章
#         raise NotImplementedError
    
#     def get_index(self):
#         #读取首页解析最新的文章
#         raise NotImplementedError

#     def get_article(self):
#         # 读取一篇具体的文章
#         raise NotImplementedError

class Anquanke(Article):
    def __init__(self,name):
        super(Anquanke, self).__init__(name)
        self.url = "https://{}/knowledge".format(self.name)

    def get_name(self):
        # raise NotImplementedError
        return self.name

    def get_index(self):
        #读取首页解析最新的文章
        logging.info("Deal with index content.")
        text = httpx.get(self.url)
        
        if text:
            selector = Selector(text)
            articles = selector.xpath('//*[@id="includeList"]/table/tbody/tr/td').getall()
            hrefs = list()
            for article in articles:
                selector = Selector(article)
                href = selector.xpath('//p[1]/a/@href').get()
                hrefs.append(href)
            logging.info("article: {},len: {}".format( hrefs,len(hrefs) ))
            return hrefs

        else:
            logging.error("Get url content error!")
            return None
    
    async def get_article(self,article):
        # 读取一篇具体的文章
        articleId = article.split("/")[-1]
        if not articleId:
            articleId = article.split("/")[-2]

        url = "https://{}/{}".format(self.name,article)
        logging.info("Read the article {} .".format(url))
        # /html/body/main/div/div/div[1]/div[1]
        text = httpx.get(url)
        # print(text)
        
        if not text:
            logging.error("Get article {} content error!".format( url ))
            return
        selector = Selector(text) 

        title = selector.xpath("/html/body/main/div/div/div[1]/div[1]/h1/text()").get().strip()
        content = selector.xpath("/html/body/main/div/div/div[1]/div[1]").get()

        tomd = Tomd(content,options = {"base":"../","store":self.store,"img":"img","article":articleId})
        markdown = tomd.markdown.encode()       
        articlePath = os.path.join("../",self.store,title+".md")
        with open(articlePath,"wb") as fd:
            fd.write(markdown)

        self.downArticles.add(article)
        self.articleUrls[title] = "./" + title + ".html"
        
# class Lesuo360(object):
#     def __init__(self):
#         self.ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
#         self.cookie = "csrftoken=vD7jwzx5yCcPCSXBh7JnzuXQl6OHZbaIg0MP1iD3rMGlssk8XvKsBTvmvVfP9E59; aliyun_lang=zh; aliyun_choice=CN; UM_distinctid=179f9d68a80ad5-06fad2edd4f851-1f3a6255-1fa400-179f9d68a81a8b; bs_n_lang=zh_CN; cna=EGBlGdRwUFICASp4S/NrOVtO; activeRegionId=cn-hangzhou; currentRegionId=cn-hangzhou; UC-XSRF-TOKEN=969e6b96-a967-4758-8b75-8c220e56d54d; FECS-UMID=%7B%22token%22%3A%22Yc1a3dbd31eb091a8c086c8337436f68c%22%2C%22timestamp%22%3A%2220576943535C5C475740617E%22%7D; _samesite_flag_=true; login_aliyunid_pk=1068723216148614; login_aliyunid_ticket=WQgyKFeuf0vpmV*s*CT58JlM_1t$w39y$p4twKxc1erIygRICzRsPgWHvg6H8xf3gqqHQlMp_wdpof_BNTwUhTOoNC1ZBeeMfKJzxdnb95hYssNIZor6q7SCxRtgmGCbifG2Cd4ZWazmBdHI6sgXZqX40; login_aliyunid_csrf=_csrf_tk_1286326428422898; hssid=; hsite=6; aliyun_country=CN; aliyun_site=CN; login_aliyunid_luid=BG+O08kl5GP9e32a13a7176349814bfdc8e4f6d4125+Bvxb1irp5DJfV+qLrKLT9A==; login_aliyunid_pks=BG+DaCJkdvf9+1W+vvt90XA3buterxglpvQYkaqxu6WD/8=; login_aliyunid_abi=BG+geXJf5cq8b66d07f9bc56395f53529b9afaa7548+0APhZdT0hDJvW/OE3OBv82aVC2OGonwWVx9/6M84VlCUu0bzsw0=; login_aliyunid=s****@aliyun-inner.com; FECS-XSRF-TOKEN=426f0bcc; isg=BMHBJy9wReJhM5YUDuO-tm9w0Avb7jXgMQGRliMWsEgjCuHcazzdsP4I6H5MRs0Y; tfstk=cNmlBPTalS1_7K4m53ZSEp1T4k5lZoLzsDox0DORu2a0HJnViN7V7SsJn7lovw1..; l=eBOcZH2qOSOcBzxEBOfZlurza77OIIRYfuPzaNbMiOCPOCXyzvJRW6T4pMK2CnGVh6JWR3k0kl4WBeYBcIf1cAfNFIstRVHmn; CNZZDATA1260716569=794856705-1596520585-https%253A%252F%252Fwww.google.com.hk%252F%7C1626563318; acw_tc=2f624a6916265679509188473e1b5d8078eddbcbef72cb82a07d4c44b64d2c; acw_sc__v2=60f3751868fd0ce818a99605e6a120ea789d62b1"
#         self.headers = {"User-Agent": self.ua,"Cookie":self.cookie}
#         self.data = list()
#         self.url = "https://xz.aliyun.com/"
#         self.id = []
#         self.httpx = Httpx()

#     def get_max_page(self):
#         text = self.httpx.get(self.url)
#         if text:
#         # 创建Selector类实例
#             selector = Selector(text)
#             # 采用css选择器获取最大页码div Boxl
#             c = selector.xpath("/html/body/div[2]/div/div[1]/div/div/div[3]/ul/li[2]/a/text()")
#             max_page = int(c.get().split("/")[1])
#             # a = selector.css('a[class="last"]')
#             # # 使用eval将page-data的json字符串转化为字典格式
#             # max_page = int(a.xpath('string(.)')[0].get().strip('.'))

#             print("[*] 最大页码数:{} .".format(max_page))
#             return max_page
#         else:
#             # print("请求失败 status:{}".format())

#             return None

#     async def parse_page_id(self, url):
#         return

#     def get_all_pages_id(self,max_page):
        
#         ALL_ID = []
#         for i in range(1,max_page+1):
#             url = "https://xz.aliyun.com/?page={}".format(i)
#             print("[*] Deal with url : {}.".format(url))

#             # response = httpx.get(self.url, headers=self.headers)
#             text = self.httpx.get(url)

#             # import IPython
#             # IPython.embed()

#             selector = Selector(text)
#             a = selector.xpath('//*[@id="includeList"]/table/tbody/tr/td').getall()
#             # print(a)
#             allar = []
#             for i in a:
#                 t = Selector(i)
#                 # title = t.xpath('//*[@class="topic-title"]/').get()
#                 allar.append( t.xpath('//p[1]/a/@href').get())

#             print("[*] get id : {},len: {}.".format( allar,len(allar) ))
#             ALL_ID.extend(allar)

#         time.sleep(0.1)

#         return ALL_ID


config = {
    "Anquanke":"www.anquanke.com"
}

def main():
    for subclass in Article.__subclasses__():
        name = config[subclass.__name__]
        instance = subclass(name)
        if not instance.config["read"]:
            instance.get_history()
            # instance.update_config()
            instance.update_readme()
        

if __name__ == "__main__":
    main()

