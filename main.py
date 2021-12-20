# -* - coding: UTF-8 -* -
import configparser
import os
import re
import shutil
import time
import urllib
import pandas as pd

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
# 组织信息
organizationInfo = ""
# 课程信息
courseId = ""
courseName = ""
# 其他工具变量
headers = {
    "User-Agent": "",
    "Accept": "application/json, text/javascript, */*; q=0.01"
}
proxies = {"http": None, "https": None}


# 效验token
def checkToken():
    print("效验登录状态...")
    global Token
    global headers
    data = readDataFromFile("loginToken", False)
    if (data == False):
        print("token不存在，重新获取...")
        login()
    else:
        data = orjson.loads(data)
        Token = data["token"]
        headers["User-Agent"] = data["UA"]
        url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/info"
        values = {'accessToken': Token}
        status = sendGet(url, values)
        # print(status)
        global organizationInfo
        organizationInfo = status
        if (status == ""):
            login()
            return
        print("效验成功...")
        print("欢迎" + organizationInfo['branch'])
        # time.sleep(3)


# 登录爬虫函数
def login():
    print("尝试登录...")
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
            print("读取配置文件...")
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


def getCourseInfo():
    global Token
    global IgnoreCourseBefore

    def printCourse(ii, course):
        global ShowCourseId
        if ShowCourseId:
            width = 30
            name = (str(ii) + "、" + course['title'])
            values = course['id']
            print(
                '{name:<{leftLen}}\t{value:>{rightLen}}'.format(name=name, value=values,
                                                                leftLen=(int(width * 3 / 4)) - len(
                                                                    name.encode('GBK')) + len(name),
                                                                rightLen=(int(width / 4)) - len(
                                                                    values.encode('GBK')) + len(values)))
        else:
            width = 20
            name = str(ii) + "、"
            values = course['title']
            print(
                '{name:<{leftLen}}{value:>{rightLen}}'.format(name=name, value=values,
                                                              leftLen=(int(width / 4)) - len(name.encode('GBK')) + len(
                                                                  name),
                                                              rightLen=(int(width * 3 / 4)) - len(
                                                                  values.encode('GBK')) + len(values)))

    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/list"
    values = {'pageSize': '1000', 'pageNum': '1', 'accessToken': Token}
    result = sendGet(url, values)['list']
    total = len(result)
    end = total
    result = list(reversed(result))
    print("\033c", end="")
    for i in range(1, total + 1):
        if IgnoreCourseBefore != "":
            if int(re.findall("\d+", result[i - 1]['id'])[0]) < int(re.findall("\d+", IgnoreCourseBefore)[0]):
                end = i
                break
        printCourse(i, result[i - 1])
    print("请输入需要进行操作的序号(1~" + str(end - 1) + "):")
    chose = input()
    if chose == '':
        chose = 1
    print("\033c", end="")
    print("已选中青年大学习的" + result[int(chose) - 1]['title'] + "数据")
    global courseId
    courseId = result[int(chose) - 1]['id']
    global courseName
    courseName = result[int(chose) - 1]['title']


def mymovefile(srcfile, dstfile):
    fpath, fname = os.path.split(dstfile)  # 分离文件名和路径
    if not os.path.exists(fpath):
        os.makedirs(fpath)  # 创建路径
    shutil.move(srcfile, dstfile)  # 移动文件


def getStudyInfo():
    global courseId
    global courseName
    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/statis"
    values = {'course': courseId, 'nid': organizationInfo['nid'], 'accessToken': Token}
    result = sendGet(url, values)
    result = sorted(result, key=lambda info: info['title'])
    df = pd.DataFrame(result)
    #  数据清洗
    df = df[~df['users'].isin([0])]
    excel = pd.ExcelWriter(str(courseName + "大学习完成情况.xlsx"))
    df.to_excel(excel)
    excel.save()
    mymovefile(str("./"+courseName + "大学习完成情况.xlsx"), "./处理结果/" + courseName + "大学习完成情况.xlsx")

    # df = df.sort_values(by="id", 、ascending=False)
    # print(df)
    # df = df.sort_values(by="title", ascending=False)
    # print(df)


if __name__ == '__main__':
    readConfig()
    checkToken()
    getCourseInfo()
    getStudyInfo()
