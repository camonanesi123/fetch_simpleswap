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
trans2de('description_id','id')
trans2de('description_vi','vi')
#trans2de('description_kr','kr')