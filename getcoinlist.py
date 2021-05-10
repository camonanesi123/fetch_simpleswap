import requests
import re
from bs4 import BeautifulSoup  # 引入BS库
import pymysql

#fetch coins to databases
def fetch_data():
    # 打开数据库连接
    db = pymysql.connect(host='localhost', port=3306,user='root', passwd='123qwe', db='gatherinfo', charset='utf8')
    # 使用 cursor() 方法创建一个游标对象 cursor
    cursor = db.cursor()
    sql = "insert into swapcoin(coin_name,description_cn,description_en,svg) value(%s,%s,%s,%s)"

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

            print('正在插入数据库..........')    
            # 使用 execute()  方法执行 SQL 查询 
            data = (coin_name, '', coin_description, svg)
            count = cursor.execute(sql,data)
            db.commit()
        
    #关闭资源连接
    cursor.close()
    db.close()

fetch_data()
