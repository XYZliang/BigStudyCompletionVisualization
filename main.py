# -* - coding: UTF-8 -* -
import configparser
import os
import re
import time
import urllib

import orjson
import requests
from faker import Factory

# 全局变量
# 登录的账号密码
account = ""
password = ""
# token值
Token = ""
# 配置文件
IgnoreCourseBefore = ""
ShowCourseId = False

# 其他工具变量
headers = {
    "User-Agent": "",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}
proxies = {"http": None, "https": None}


# 效验token
def checkToken():
    global Token
    global headers
    data = readDataFromFile("loginToken", False)
    if (data == False):
        print("token不存在，重新获取")
        login()
    else:
        print(data)
        data = orjson.loads(data)
        Token = data["token"]
        headers["User-Agent"] = data["UA"]
        url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/list"
        values = {'pageSize': '1', 'pageNum': '1', 'accessToken': Token}
        status = sendGet(url, values)
        if (status == ""):
            login()


# 登录爬虫函数
def login():
    global Token
    global headers
    fc = Factory.create()
    UA = fc.user_agent()
    headers["User-Agent"] = UA
    # 登录API
    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/login"
    # application/json参数
    values = {"account": account, "password": password}
    Token = sendPostJson(url, values)['accessToken']
    headers["User-Agent"] = UA
    loginData = {"token": Token, "time": time.time(), "UA": UA}
    loginData = orjson.dumps(loginData)
    saveDataToFile("loginToken", loginData, True)


# POST请求函数
def sendPostJson(url, values):
    global proxies
    global headers
    # json.dump将python对象编码成json字符串
    values_json = orjson.dumps(values)
    # requests库提交数据进行post请求
    req = requests.post(url, data=values_json, headers=headers, proxies=proxies)
    # 使用json.dumps()时需要对象相应的类型是json可序列化的
    change = req.json()
    # 转换为JSON对象
    json_req = orjson.dumps(change)
    json_req = orjson.loads(json_req)
    result = json_req.get("result")
    if (json_req.get("status") != 200):
        print("请求错误")
        return ""
    return result


# GET请求函数
def sendGet(url, values):
    global proxies
    global headers
    # 对请求数据进行编码
    data = urllib.parse.urlencode(values)
    # 若为post请求以下方式会报错TypeError: POST data should be bytes, an iterable of bytes, or a file object. It cannot be of type str.
    # Post的数据必须是bytes或者iterable of bytes,不能是str,如果是str需要进行encode()编码
    # 将数据与url进行拼接
    req = url + '?' + data
    # 打开请求，获取对象
    response = requests.get(req, headers=headers, proxies=proxies)
    # 读取服务器返回的数据,对HTTPResponse类型数据进行读取操作
    the_page = response.text
    json_req = orjson.loads(the_page)
    result = json_req.get("result")
    if (json_req.get("status") != 200):
        print("请求错误" + response.text)
        return ""
    return result


def saveDataToFile(fileName, data, isByte):
    if (isByte):
        file = open(fileName + ".data", "wb")
    else:
        file = open(fileName + ".data", "w")
    file.write(data)
    file.close()


def readDataFromFile(fileName, isByte):
    try:
        if (isByte):
            file = open(fileName + ".data", "rb")
        else:
            file = open(fileName + ".data", "r")
        data = file.read()
        file.close()
    except:
        return False
    return data


def readConfig():
    # 判断配置文件是否存在
    if os.path.exists("BigStudyConfig.cfg") or os.path.exists("BigStudyConfigTemplate.cfg"):
        if os.path.exists("BigStudyConfig.cfg"):
            print("获取到配置文件")
        else:
            print("获取不到配置文件，请修改配置模板文件BigStudyConfigTemplate.cfg重命名为BigStudyConfig.cfg")
            exit()
    else:
        print("配置文件和配置模板文件均已丢失，请从github从新获取")
        print("")
        exit()
    # 生成config对象
    conf = configparser.ConfigParser()
    conf.sections()
    # 用config对象读取配置文件
    conf.read("BigStudyConfig.cfg")
    # 以列表形式返回所有的section
    sections = conf.sections()
    global account
    global password
    global IgnoreCourseBefore
    global ShowCourseId
    account = conf["DEFAULT"].get("Account", "")
    password = conf["DEFAULT"].get("Password", "")
    IgnoreCourseBefore = conf["DEFAULT"].get("IgnoreCourseBefore", "")
    try:
        ShowCourseId = conf["DEFAULT"].getboolean("ShowCourseId", "False")
    except ValueError:
        ShowCourseId = False
    if len(account) == 0 or len(password) == 0:
        print("请配置必填项 Account Password")
        exit()


def getCourse():
    global Token
    global IgnoreCourseBefore

    def printCourse(ii, course):
        global ShowCourseId
        print(str(ii) + "、" + course['title'], end="")
        if ShowCourseId:
            print(" " + course['id'])
        else:
            print()

    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/list"
    values = {'pageSize': '1000', 'pageNum': '1', 'accessToken': Token}
    result = sendGet(url, values)['list']
    total = len(result)
    result = list(reversed(result))
    for i in range(1, total + 1):
        if IgnoreCourseBefore != "":
            if int(re.findall("\d+", result[i - 1]['id'])[0]) < int(re.findall("\d+", IgnoreCourseBefore)[0]):
                break
        printCourse(i, result[i - 1])


if __name__ == '__main__':
    readConfig()
    checkToken()
    getCourse()
