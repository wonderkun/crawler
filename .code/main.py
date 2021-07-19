from tomd import Tomd
from parsel import Selector
import asyncio
import json
import time
from selenium import webdriver
import os
import logging
import re

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
        self.client.set_page_load_timeout(10)
        self.client.set_script_timeout(10)

    def get(self,url):
        # 重试 3 次 
        self.client.implicitly_wait(3)
        for i in range(5):
            try:
                self.client.get(url)
            except Exception as e:
                logging.warning("Read url error info :{},retrying ... {}.".format( url,i))
                time.sleep(1)
            else:
                break

        for i in range(1, 21):
            # 滑到页面底部，让所有懒加载的图片全部加载出来
            self.client.execute_script(
                "window.scrollTo(0, document.body.scrollHeight/20*%s);" % i
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

    def validateTitle(self,title):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
        new_title = re.sub(rstr, "_", title)  # 替换为下划线
        new_title = new_title.replace("【","[")
        new_title = new_title.replace("】","]")
        return new_title

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
        logging.info("Deal with {} index content.".format(self.name))
        text = httpx.get(self.url)
        # 
        if text:
            selector = Selector(text)
            articles = selector.xpath('//*[@id="post-list"]/div').getall()

            hrefs = list()
            # print(articles)
            for article in articles:
                # print(article)
                selector = Selector(article)
                href = selector.xpath('//div/div[2]/div/div[1]/a/@href').get()
                if href:
                    hrefs.append(href)
                    
            logging.info("article: {},len: {}".format( hrefs,len(hrefs) ))

            hrefs = list(set(hrefs) - set(self.config["id"]))
            logging.info("Index page have start page hrefs:{}.".format(hrefs)) 
            #读取历史的所有文章
            if not hrefs:
                return 
            loop = asyncio.get_event_loop()

            # Python 3.6之前用ayncio.ensure_future或loop.create_task方法创建单个协程任务
            # Python 3.7以后可以用户asyncio.create_task方法创建单个协程任务
            tasks = []

            for href in hrefs:
                tasks.append(self.get_article( href ))

            # 还可以使用asyncio.gather(*tasks)命令将多个协程任务加入到事件循环
            loop.run_until_complete(asyncio.wait(tasks))
            loop.close()

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
        title = self.validateTitle(title)
        content = selector.xpath("/html/body/main/div/div/div[1]/div[1]").get()

        tomd = Tomd(content,
            options = {
                "base":"../",
                "store":self.store,
                "img":"img",
                "article":articleId,
                "localimg":False
            }
        )
        markdown = tomd.markdown.encode()       
        articlePath = os.path.join("../",self.store,title+".md")
        with open(articlePath,"wb") as fd:
            fd.write(markdown)

        self.downArticles.add(article)
        self.articleUrls[title] = "./" + title + ".html"
        

config = {
    "Anquanke":"www.anquanke.com"
}

def main():
    for subclass in Article.__subclasses__():
        name = config[subclass.__name__]
        instance = subclass(name)
        if not instance.config["read"]:
            instance.get_history()
            instance.update_config()
            instance.update_readme()
        else:
            instance.get_index()
            instance.update_config()
            instance.update_readme()

if __name__ == "__main__":
    main()

