from time import time
from typing import FrozenSet
import requests
import re
from bs4 import BeautifulSoup  # 引入BS库
import pymysql

import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


from googletrans import Translator
#fetch coins to databases
def fetch_data():
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "insert into swapcoin(coin_name,description_en,description_es,description_cn,svg) value(%s,%s,%s,%s,%s)"

    for page in range(1,8):
        url ='https://simpleswap.io/coins?page={0}'.format(page)
        res = requests.get(url)
        #print(res.text)
        soup = BeautifulSoup(res.text, 'lxml')


        #a=soup.find_all('img')
        for tag in soup.find_all(name="div", attrs={"class":re.compile(r"styles__Container-sc-1s4n6ik-0(\s\w+)?")}):
            #对每一个币种进行处理

            #print('\n')
            a = tag.find(name="a", attrs={"class":re.compile(r"styles__CoinName-sc-1s4n6ik-8(\s\w+)?")})
            coin_name = a.text
            print(coin_name)
            print('\n')
            try:
                b = tag.find(name="p", attrs={"class":re.compile(r"styles__Description-sc(\s\w+)?")})
                coin_description = b.text
            except:
                coin_description = 'no description now'
            print(coin_description)    
            print('\n')
            
            c=tag.find('img')
            src=c.get('src')
            res = requests.get(src)
            print(res.text)
            svg=res.text
            print('\n')
            #翻译西班牙语言
            #desc_es = translate(coin_description,'en','es')
            #es 翻译 中文
            #desc_cn = translate(desc_es,'en','zh')
            print('正在插入数据库..........')    
            # 使用 execute()  方法执行 SQL 查询 
            data = (coin_name,coin_description,'','',svg)
            count = cursor.execute(sql,data)
            db.commit()
        
    #关闭资源连接
    cursor.close()
    db.close()

def trans2de(field_name,language):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select * from swapcoin"

    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            text = row[3]
            #print('target text is '+text)
            # 翻译并处理
            des = translate(text,'en',language)
            print(des)
            update(row[0],des,field_name)
            #sql1 = "UPDATE swapcoin SET descrpition_es = '{0}'".format(translate(text))
            #cursor.execute(sql1)
        total = cursor.rowcount
        print("已经翻译总数: %s" % \
            (total))
    except:
        print("Error: unable to fetch data")
    finally:
        cursor.close()
        db.close()


def update(coin_name,description_fr,field_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "UPDATE swapcoin SET "+field_name+" =%s WHERE coin_name =%s"
    data= (description_fr,coin_name)
    #print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql,data)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

def translate(text,source,target):
    try: 
        cred = credential.Credential("AKIDbzPZS5wQxEGG0UINmvPdcLoZ0C8oJF2Z", "RijV2JM2RaVE1Xoqc9Se4F2g4xax3tWu") 
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-beijing", clientProfile) 

        req = models.TextTranslateRequest()
        params = {
            "SourceText": text,
            "Source": source,
            "Target": target,
            "ProjectId": 1
        }
        req.from_json_string(json.dumps(params))

        resp = client.TextTranslate(req) 
        #print(resp) 
        #print(resp.TargetText) 
        
        return resp.TargetText
    except TencentCloudSDKException as err: 
        print(err) 
        return "translate error"

#西班牙语翻译中文
def transes2zh():
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select * from swapcoin"

    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        for row in results:
            text = row[3]
            print('target text is '+text)
            # 翻译并处理
            des_cn = translate(text,'es','zh')
            print(des_cn)
            update1(row[0],des_cn)
            #sql1 = "UPDATE swapcoin SET descrpition_es = '{0}'".format(translate(text))
            #cursor.execute(sql1)
        total = cursor.rowcount
        print("已经翻译总数: %s" % \
            (total))
    except:
        print("Error: unable to fetch data")
    finally:
        cursor.close()
        db.close()
#更新数据库
def update1(coin_name,description_cn):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "UPDATE swapcoin SET description_cn =%s WHERE coin_name =%s"
    data= (description_cn,coin_name)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql,data)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

#trans2de('description_jp','jp')
#trans2de('description_id','id')
#trans2de('description_vi','vi')
#trans2de('description_kr','kr')

blog_url = 'https://simpleswap.io/blog/page/1'
def crawlBlogs():

    for page in range(1,10):
        url ='https://simpleswap.io/blog/page/{0}'.format(page)
        res = requests.get(url)
        #print(res.text)
        soup = BeautifulSoup(res.text, 'lxml')
        #a=soup.find_all('img')
        for tag in soup.find_all(name="div", attrs={"class":re.compile(r"post-container")}):
            #对每一个币种进行处理

            #print(tag)
            a = tag.find(name="a", attrs={"href":re.compile(r"https://simpleswap.io/blog/(\s\w+)?")})
            post_title = a['title']
            post_url = a['href']
            crawlSingleBlog(post_url)
        


def crawlSingleBlog(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    post_title = soup.find(name="h1", attrs={"class":re.compile(r"post-title(\s\w+)?")})
    print(post_title.text)
    img_url = soup.find(name="img", attrs={"src":re.compile(r"https://simpleswap.io/blog/wp-content/uploads/(\s\w+)?")})
    print(img_url['src'])
    body = soup.find(name="div", attrs={"class":re.compile(r"post-content(\s\w+)?")})
    print(body.text)
    time = soup.find(name="p", attrs={"class":re.compile(r"post-date-footer(\s\w+)?")})
    print(time.text)
    img_data = requests.get(img_url['src']).content
    file_name = post_title.text.replace('|','')
    file_name = file_name.replace('!','')
    file_name = file_name.replace('?','')
    file_name = file_name.replace(' ','_')
    file_name = file_name+'.jpg'
    with open(file_name, 'wb') as handler:
        handler.write(img_data)
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "insert into blog(title,body,image_name,time) value(%s,%s,%s,%s)"
    data = (post_title.text,body.text,file_name,time.text)
    try:
        # 执行SQL语句
        cursor.execute(sql,data)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    #关闭资源连接
    cursor.close()
    db.close()

#crawlBlogs()


#从调用coinmarket cap 接口
def coinmarketCap():
    from requests import Request, Session
    from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
    import json

    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
    parameters = {
    'id':'1,2'
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': '1e437ea9-ad30-4b9b-a467-8b4f314b4781',
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        print(data)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

#从coinmarketcap 抓取币信息
def getCoinInfo(key,url):
    url = url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    markDown=""
    try:
        content = soup.find_all(name="div", attrs={"class":re.compile(r"sc-1lt0cju-0(\s\w+)?")})   
        print(content[0].contents)
        first_header = content[0].find(re.compile("^h(\s\w+)?"))
        print(first_header)
        sliblings = first_header.find_next_siblings()
        flag = 0
        markDown = "# "+first_header.text
        for element in sliblings:
            
            #print(element)
            #如果 是 tag 为 h开头 把之前段落做成一句话
            #如果 tage 是 P 将加入之前段落
            if "p" in element.name:
                if flag==0:
                    #print("是段落")
                    markDown+='\r\n'
                    markDown+=element.text
                    markDown+='\r\n'
            if "h" in element.name:
                #print("是标题")
                #如果是标题，看看是否是有相关网站信息 标题 如果是 不处理
                if "Related Pages" in element.text or "Where Can You Buy" in element.text:
                    flag = 1
                else:
                    #翻译成 markDown 格式
                    flag = 0
                    markDown+='\r\n'
                    markDown+='# '
                    markDown+=element.text
                    markDown+='\r\n'
        #print(flag)
    except:
        markDown = "# No Brief Found Now"
        
        #print('\r\n')
    #print(markDown)
    markDown= bytes(markDown, encoding = "utf8")
    # 向数据库写入 代币信息
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "UPDATE coinbrief SET coinbrief.breif =%s WHERE coinbrief.key =%s"
    #print(key,markDown)
    data= (markDown,key)
    print(data)
    print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql,data)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

import time
def getCoinBrief():
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select coinbrief.key,coins.slug from coinbrief,coins where coinbrief.key = coins.symbol AND coinbrief.breif is NULL"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        
        for row in results:
            #time.sleep(5)
            key = row[0]
            url = "https://coinmarketcap.com/currencies/{0}/".format(row[1])
            print('processing url :'+url)
            # 获取当前代币信息
            getCoinInfo(key,url)
        total = cursor.rowcount
        print("已经处理总数: %s" % \
            (total))
    except:
        print("Error: unable to fetch data")
    finally:
        cursor.close()
        db.close()    

def update_brief(key,brief,field_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "UPDATE coinbrief SET "+field_name+" =%s WHERE coinbrief.key =%s"
    data= (brief,key)
    #print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql,data)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()





from multiprocessing import Process, Queue
import threading
import time
 
tran_text = ''
def process_data(threadName, q,language):
    global tran_text
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            print("%s processing %s" % (threadName, data))
            res = translate(data,'en',language)
            if data[0] == '#':
                res='# '+res
            tran_text+=res    
        else:
            queueLock.release()
        time.sleep(1)
class myThread (threading.Thread):
    def __init__(self, threadID, name, q,launguage):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
        self.launguage = launguage
    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.q ,self.launguage)
        print("Exiting " + self.name)



    
 

exitFlag = 0
threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5"]
queueLock = threading.Lock()
workQueue = Queue(1000)
threads = []
threadID = 1
def trans_brief(language):
    # 打开数据库连接
    global exitFlag
    global threadList 
    global queueLock 
    global workQueue 
    global threads 
    global threadID
    global tran_text
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select coinbrief.key,coinbrief.en from coinbrief"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        
        for row in results:
            #time.sleep(5)
            key = row[0]
            en = row[1]
            print('正在翻译 :'+key)
            # 翻译代币信息 2000个字一次
            print(len(en))
            sentences = str.splitlines(en)
            #去空串 ['','']
            sentences = list(filter(None, sentences)) 
            # 创建新线程
            exitFlag = 0
            print(threadList)
            for tName in threadList:
                thread = myThread(threadID, tName, workQueue,language)
                thread.start()
                threads.append(thread)
                threadID += 1
            print(threadList)
            print('1')
            # 填充队列
            queueLock.acquire()
            for word in sentences:
                workQueue.put(word)
            queueLock.release()
            print('2')
            # 等待队列清空
            
            while not workQueue.empty():
                #print(workQueue.qsize())
                pass
            print('3')
            # 通知线程是时候退出
            exitFlag = 1
            print('4')
            # 等待所有线程完成
            for t in threads:
                t.join()
            print("Exiting Main Thread")
            #print(tran_text)
            tran_text =''
            #print(threads)
            #print(threadID)
            # for i in sentences:
            #     #如果 i 以# 开始，那么把# 从里面摘除之后翻译
                
            #     a= translate(i,'en',language)
            #     print(a)
            #     if i[0] == '#':
            #         a='# '+a
            #     res+= a
            #     res+='\r\n'
            # #再 res 中 # 后面加空格
            # update_brief(key,res,field_name)
        total = cursor.rowcount
        print("已经处理总数: %s" % \
            (total))
    except:
        print("Error: unable to fetch data")
    finally:
        cursor.close()
        db.close()        
#trans_brief('jp')
#trans_brief('id')
#trans_brief('iv')
#trans_brief('kr')

#trans_brief('jp','jp')

#trans_brief('id','id')

#trans_brief('iv','vi')


#trans_brief('kr','kr')
def trans_brief(field_name,language):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select coinbrief.key,coinbrief.en from coinbrief"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        
        for row in results:
            #time.sleep(5)
            key = row[0]
            en = row[1]
            print('正在翻译 :'+key)
            # 翻译代币信息 2000个字一次
            print(len(en))
            sentences = str.splitlines(en)
            #去空串 ['','']
            sentences = list(filter(None, sentences)) 
            res = ""
            for i in sentences:
                i = i.strip()
                print(i)
                if i[0] == '#':
                    a= '# '+translate(i[1:],'en',language)
                    res=res+a
                else:
                    res+= translate(i,'en',language)
                #print(res)
                res+='\r\n'
            #再 res 中 # 后面加空格
            #res = res.replace('#', '#  ')
            update_brief(key,res,field_name)
        total = cursor.rowcount
        print("已经处理总数: %s" % \
            (total))
    except:
        print("Error: unable to fetch data")
    finally:
        cursor.close()
        db.close()       

def update_page(key,brief,field_name):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "UPDATE pages SET "+field_name+" =%s WHERE pages.key =%s"
    data= (brief,key)
    #print(sql)
    try:
        # 执行SQL语句
        cursor.execute(sql,data)
        # 提交到数据库执行
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()
    # 关闭数据库连接
    db.close()

def trans_page(field_name,language):
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "select pages.key,pages.en from pages where pages.key='terms'"
    try:
        # 执行SQL语句
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        
        for row in results:
            #time.sleep(5)
            key = row[0]
            en = row[1]
            print('正在翻译 :'+key)
            # 翻译代币信息 2000个字一次
            print(len(en))
            sentences = str.splitlines(en)
            #去空串 ['','']
            sentences = list(filter(None, sentences)) 
            res = ""
            for i in sentences:
                i = i.strip()
                print(i)
                if i[0] == '#':
                    a= '# '+translate(i[1:],'en',language)
                    res=res+a
                else:
                    res+= translate(i,'en',language)
                #print(res)
                res+='\r\n'
            #再 res 中 # 后面加空格
            #res = res.replace('#', '#  ')
            update_page(key,res,field_name)
        total = cursor.rowcount
        print("已经处理总数: %s" % \
            (total))
    except:
        print("Error: unable to fetch data")
    finally:
        cursor.close()
        db.close()            

trans_page('es','es')
trans_page('de','de')
trans_page('fr','fr')
trans_page('ru','ru')
trans_page('pt','pt')
trans_page('jp','jp')
trans_page('id','id')
trans_page('vi','vi')
trans_page('kr','kr')