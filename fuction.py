import requests
import time
import os
import re
from bs4 import BeautifulSoup
from 打码 import base64_api

ss = requests.Session()
headers = {
    'Accept': 'image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'http://xk.tjut.edu.cn/xsxk/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
}


def login(username, password):
    params = {
        'd': str(int(time.time() * 1000)),
    }

    response = ss.get(
        'http://xk.tjut.edu.cn/xsxk/servlet/ImageServlet',
        params=params,
        headers=headers,
    )
    with open('./code.jpg', 'wb') as fp:
        fp.write(response.content)

    img_path = "./code.jpg"
    global code
    code = base64_api(uname='1559156683', pwd='lxq123456', img=img_path, typeid=3)

    os.remove(img_path)
    params = {
        'method': 'checkLogin',
        'username': f'{username}',
        'password': f'{password}',
        'verifyCode': f'{code}',
    }

    response = ss.get('http://xk.tjut.edu.cn/xsxk/loadData.xk', params=params, headers=headers)
    params = {
        'username': f"{username}",
        'password': f'{password}',
        'verifyCode': f'{code}',
    }
    ss.post('http://xk.tjut.edu.cn/xsxk/login.xk', headers=headers, params=params)
    return response.json()['message']

def refresh_table(username,password):
    params = {
        'username': f"{username}",
        'password': f'{password}',
        'verifyCode': f'{code}',
    }
    py = ss.post('http://xk.tjut.edu.cn/xsxk/login.xk', headers=headers, params=params)
    pyfaid = re.findall("loadFaxklcs\('(.*)',", py.text)
    params = {
        'pyfaid': pyfaid,
        'jxqdm': '1',
        'data-frameid': 'main',
        'data-timer': '2000',
        'data-proxy': 'proxy.xk',
    }
    ss.get('http://xk.tjut.edu.cn/xsxk/xkjs.xk', headers=headers, params=params)
    r = ss.get('http://xk.tjut.edu.cn/xsxk/qxgxk.xk', headers=headers, verify=False)

    soup = BeautifulSoup(r.text, 'lxml')
    data = []
    i = soup.body.find_all('script')
    for j in range(0, len(i)+1,2):
        try:
            a = i[j].string.split(',')
            c = []
            c.append(re.findall("'(.*?)'",a[0])[0])
            c.append(re.findall("'(.*?)'",a[1])[0])
            c.append(re.findall("'(.*?)'",a[2])[0])
            c.append(re.findall("'(.*?)'",a[14])[0])
            data.append(c)
        except:
            pass
    return data
def xjd():
    p = ss.get('http://xk.tjut.edu.cn/xsxk/index.xk', headers=headers, verify=False)
    z = re.findall('loadXklcs\((.*?)\);',p.text,re.DOTALL)[0]
    z = z.split(',')
    l = []
    l.append(z[1].strip().strip("'"))
    l.append(z[3].strip().strip("'"))
    l.append(z[5].strip().strip("'"))
    l.append(z[6].strip().strip("'"))
    l.append(z[7].strip().strip("'"))
    return l

def return_ss():
    return ss
def check_login():
    try:
        result = ss.get('http://xk.tjut.edu.cn/xsxk/loadData.xk?method=loginCheck',headers=headers).json()
        return result['success']
    except Exception as e:
        return e

def user():
    p = ss.get('http://xk.tjut.edu.cn/xsxk/index.xk', headers=headers,verify=False)
    return re.findall('<b>(.*?)</b>同学，',p.text)[0]
