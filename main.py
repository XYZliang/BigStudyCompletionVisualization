# -* - coding: UTF-8 -* -

import configparser
import os
import platform
import re
import shutil
import time
import urllib
import sys
import orjson
import pandas as pd
import requests
from faker import Factory
from matplotlib import pyplot as plt
from openpyxl import load_workbook
from tqdm import tqdm

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
# 总人数
Total = 0
# 其他工具变量
headers = {
    "User-Agent": "",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    'Connection': 'close',
}
proxies = {"http": None, "https": None}


# 效验token
def checkToken():
    print("效验登录状态...")
    global Token
    global headers
    data = readDataFromFile("loginToken", False)
    if not data:
        print("token不存在，重新获取...")
        login()
        # checkToken()
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
        if status == "":
            login()
            # checkToken()
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
    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/info"
    values = {'accessToken': Token}
    status = sendGet(url, values)
    global organizationInfo
    organizationInfo = status


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
    if json_req.get("status") != 200:
        print("请求错误")
        return ""
    return result


# GET请求函数
def sendGet(url, values):
    global proxies
    global headers
    requests.adapters.DEFAULT_RETRIES = 5  # 增加重连次数
    s = requests.session()
    s.keep_alive = False
    # 对请求数据进行编码
    data = urllib.parse.urlencode(values)
    # 若为post请求以下方式会报错TypeError: POST data should be bytes, an iterable of bytes, or a file object.
    # Post的数据必须是bytes或者iterable of bytes,不能是str,如果是str需要进行encode()编码
    # 将数据与url进行拼接
    req = url + '?' + data
    # 打开请求，获取对象
    response = s.get(req, headers=headers, proxies=proxies)
    # 读取服务器返回的数据,对HTTPResponse类型数据进行读取操作
    the_page = response.text
    json_req = orjson.loads(the_page)
    result = json_req.get("result")
    if json_req.get("status") != 200:
        print("请求错误" + response.text)
        return ""
    return result


def saveDataToFile(fileName, data, isByte):
    if isByte:
        file = open(fileName + ".data", "wb")
    else:
        file = open(fileName + ".data", "w")
    file.write(data)
    file.close()


def readDataFromFile(fileName, isByte):
    try:
        if isByte:
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
    global Total
    account = conf["DEFAULT"].get("Account", "")
    password = conf["DEFAULT"].get("Password", "")
    IgnoreCourseBefore = conf["DEFAULT"].get("IgnoreCourseBefore", "")
    try:
        ShowCourseId = conf["DEFAULT"].getboolean("ShowCourseId", "False")
    except ValueError:
        ShowCourseId = False
    Total = conf["DEFAULT"].getint("Total", 0)
    if len(account) == 0 or len(password) == 0:
        print("请配置必填项 Account Password")
        exit()


def getCourseInfo(info=False):
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

    if info:
        courseList = []
    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/list"
    values = {'pageSize': '1000', 'pageNum': '1', 'accessToken': Token}
    result = sendGet(url, values)['list']
    total = len(result)
    end = total
    result = list(reversed(result))
    cleanWin()
    for i in range(1, total + 1):
        if IgnoreCourseBefore != "":
            if int(re.findall("\d+", result[i - 1]['id'])[0]) < int(re.findall("\d+", IgnoreCourseBefore)[0]):
                if info:
                    return courseList
                else:
                    end = i
                    break
        if info:
            courseList.append(result[i - 1])
        else:
            printCourse(i, result[i - 1])
    print("请输入需要进行操作的序号(1~" + str(end - 1) + "):")
    chose = input()
    if chose == '':
        chose = 1
    cleanWin()
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
    df = df.drop(['rate'], axis=1)
    df.columns = ['团委id', '团委名称', '团员人数', '已学习人数', '已学习人次', '完成率']
    df['团员人数'].astype(int)
    df['已学习人数'].astype(int)
    df['已学习人次'].astype(int)
    df['学习期数old'] = courseName
    df['完成率'].astype(float)
    newLow = df.pop('学习期数old')
    df.insert(3, '大学习课程', newLow)
    excel = pd.ExcelWriter(str(courseName + "大学习完成情况.xlsx"))
    df.to_excel(excel, index=True, header=False)
    excel.save()
    excel.close()
    mymovefile(str("./" + courseName + "大学习完成情况.xlsx"), "./处理结果/" + courseName + "大学习完成情况.xlsx")
    # for u in df['团委名称']:
    #     u = str(u).replace("团支部", "")
    for indexs in df.index:
        df.loc[indexs, '团委名称'] = df.loc[indexs, '团委名称'].replace("团支部", "")
    # print(df)
    print("已导出本期各班完成情况表EXCEL表到处理结果文件夹")
    a = ""
    for i in df['团委名称']:
        a += i
    # print(a)
    # print((len(a)+len(df['团委名称'])*5))
    # print(len(df['团委名称'])*5)
    # plt.figure(figsize=((len(a)+len(df['团委名称'])*5)/100, 5))
    # ax = plt.subplot(111)  # 这是画布哦，说明只在一张图显示，也可分割多图
    plt.rcParams['font.sans-serif'] = ['FangSong']  # 显示中、文
    plt.rcParams['axes.unicode_minus'] = False  # 显示负号
    # df.plot.bar(y=['完成率'], x='团委名称')
    # plt.xlabel("团委名称")
    # plt.ylabel("完成率（单位：%）")
    # plt.savefig(courseName + "大学习完成情况.png")
    # plt.show()
    # plt.figure(dpi=300)
    plt.figure(figsize=(df.shape[0], df.shape[0] / 2), dpi=100)
    plt.bar(df['团委名称'], df['完成率'], color='#002EA6')
    ax = plt.subplot(111)
    plt.xticks(range(len(df['团委名称'])), df['团委名称'], rotation=45, fontsize=20)
    plt.yticks(fontsize=80)
    # plt.title = ((courseName + "大学习完成情况"))
    ax.set_title((courseName + "大学习完成情况"), fontsize=80)
    plt.xlabel("团委名称", fontsize=70)
    plt.ylabel("完成率（单位：%）", fontsize=70)
    plt.savefig(courseName + "大学习完成情况.png", bbox_inches='tight')
    mymovefile(str("./" + courseName + "大学习完成情况.png"), "./处理结果/" + courseName + "大学习完成情况.png")
    print("已导出本期各班完成情况可视化统计图到处理结果文件夹")


def outMenu(name, values, width):
    print(
        '{name:<{leftLen}}\t{value:>{rightLen}}'.format(name=name, value=values,
                                                        leftLen=(int(width / 8)) - len(
                                                            name.encode('GBK')) + len(name),
                                                        rightLen=(int(width * 7 / 8)) - len(
                                                            values.encode('GBK')) + len(values)))


def showMenu():
    cleanWin()
    print("欢迎" + organizationInfo['branch'])
    menu = ['导出某期大学习各班完成率表格及统计图', '导出总大学习完成情况情况表格及折线图', '导出某班每次大学习完成率情况表格及折线图', '导出最新一期未完成名单', '退出程序']

    info = ("欢迎使用BigStudyCompletionVisualization，请选择功能(1~" + str(len(menu)) + ")：")
    for i in range(1, len(menu) + 1):
        outMenu(str(i), menu[i - 1], len(info.encode('GBK')) - 1)
    print(info)
    fun1 = input()
    return fun1


def getLearnTime(thisCourseId):
    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/statis"
    values = {'course': thisCourseId, 'nid': organizationInfo['nid'], 'accessToken': Token}
    result = sendGet(url, values)
    total = 0
    for i in result:
        total += int(i['users'])
    return total


def getLearnTimeGroupByClass(thisCourseId):
    url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/statis"
    values = {'course': thisCourseId, 'nid': organizationInfo['nid'], 'accessToken': Token}
    result = sendGet(url, values)
    res = {}
    for i in result:
        if i['memberCnt'] != '0':
            res[i['title']] = i['score']
    return res


def cleanWin():
    # if platform.system().lower() == 'windows':
    #     os.system('cls')
    # else:
    #     os.system('alias cls=\'print "\033c"\' && cls')
    os.system("alias cls='print '\033c'';clear&cls")
    time.sleep(0.1)


if __name__ == '__main__':
    print("程序初始化中。。")
    readConfig()
    checkToken()
    fun = showMenu()
    if int(fun) == 1:
        getCourseInfo()
        getStudyInfo()
    elif int(fun) == 2:
        if Total <= 0:
            print("未配置总人数为Total或总人数Total不合法！")
            exit()
        courseHis = []
        courseList = getCourseInfo(True)
        for i in courseList:
            courseHis.append({'大学习期数': i['title'], '完成率%': 100.0 * getLearnTime(i['id']) / Total})
        courseHis.reverse()
        df = pd.DataFrame(courseHis)
        excel = pd.ExcelWriter("总大学习完成情况.xlsx")
        df.to_excel(excel)
        excel.save()
        excel.close()
        mymovefile("总大学习完成情况.xlsx", "./处理结果/总大学习完成情况.xlsx")
        print("已导出总完成情况表EXCEL表到处理结果文件夹")
        plt.rcParams['font.sans-serif'] = ['FangSong']  # 显示中、文
        plt.rcParams['axes.unicode_minus'] = False  # 显示负号
        plt.figure(dpi=300)
        plt.title(organizationInfo['branch'] + '总大学习完成情况', fontsize='20')
        plt.xlabel("大学习期数", fontsize='16')
        plt.xticks(range(len(df['大学习期数'])), df['大学习期数'], rotation=45)
        plt.ylabel("完成率（单位：%）", fontsize='16')
        plt.plot(df['大学习期数'], df['完成率%'], color='#002EA6', linewidth=2, linestyle=':', marker='o')
        # df.plot()
        # plt.show()
        outfile = organizationInfo['branch'] + '总大学习完成情况.png'
        plt.savefig(outfile, bbox_inches='tight')
        mymovefile(organizationInfo['branch'] + '总大学习完成情况.png',
                   "./处理结果/" + organizationInfo['branch'] + '总大学习完成情况.png')
        plt.close()
        print("已导出总大学习完成情况可视化统计图到处理结果文件夹")
    elif int(fun) == 3:
        print("获取数据中")
        courseHis = {}
        courseList = getCourseInfo(True)
        with tqdm(total=len(courseList), desc='数据统计', leave=True) as pbar:
            for i in courseList:
                res = getLearnTimeGroupByClass(i['id'])
                for ii in res:
                    if ii.replace("团支部", "") not in courseHis.keys():
                        courseHis[ii.replace("团支部", "")] = []
                    courseHis[ii.replace("团支部", "")].append({i['title']: res[ii]})
                pbar.update(1)
        noti = "请输入需要导出的班级的序号（1~" + str(len(courseHis)) + ")："
        for i in courseHis:
            courseHis[i].reverse()
        classList = sorted(list(courseHis.keys()))
        classList.reverse()
        for i in range(1, len(classList) + 1):
            outMenu(str(i), classList[i - 1], len(noti.encode('GBK')) - 1)
        print(noti)
        c = input()
        cleanWin()
        data = courseHis[classList[int(c) - 1]]
        datas = {'大学习期数': [], '完成率%': []}
        # dataList = list(data.keys())
        for i in data:
            # print(i)
            datas['大学习期数'].append(list(i.keys())[0])
            datas['完成率%'].append(i[list(i.keys())[0]])
        df = pd.DataFrame(datas)
        excel = pd.ExcelWriter(classList[int(c) - 1] + "总大学习完成情况.xlsx")
        df.to_excel(excel)
        excel.save()
        excel.close()
        mymovefile(classList[int(c) - 1] + "总大学习完成情况.xlsx", "./处理结果/" + classList[int(c) - 1] + "总大学习完成情况.xlsx")
        print("已导出" + classList[int(c) - 1] + "总完成情况表EXCEL表到处理结果文件夹")
        plt.rcParams['font.sans-serif'] = ['FangSong']  # 显示中、文
        plt.rcParams['axes.unicode_minus'] = False  # 显示负号
        plt.figure(dpi=300)
        plt.title(classList[int(c) - 1] + '总大学习完成情况', fontsize='20')
        plt.xlabel("大学习期数", fontsize='16')
        plt.xticks(range(len(df['大学习期数'])), df['大学习期数'], rotation=45)
        plt.ylabel("完成率（单位：%）", fontsize='16')
        plt.plot(df['大学习期数'], df['完成率%'], color='#002EA6', linewidth=2, linestyle=':', marker='o')
        # df.plot()
        # plt.show()
        outfile = classList[int(c) - 1] + '总大学习完成情况.png'
        plt.savefig(outfile, bbox_inches='tight')
        mymovefile(classList[int(c) - 1] + '总大学习完成情况.png',
                   "./处理结果/" + classList[int(c) - 1] + '总大学习完成情况.png')
        plt.close()
        print("已导出" + classList[int(c) - 1] + "总大学习完成情况可视化统计图到处理结果文件夹")
    elif int(fun) == 4:
        courseList = getCourseInfo(True)
        courseId = courseList[0]['id']
        df = pd.read_excel("大学习名单.xlsx")
        biaoshi = []
        for i in range(1, df.shape[0] + 1):
            biaoshi.append(df.loc[[i - 1]].values[0][0] + df.loc[[i - 1]].values[0][1])
        df.insert(df.shape[1], '标识符', biaoshi)
        dfJson = orjson.loads(df.to_json(orient='records'))
        datas = {}
        for i in dfJson:
            datas[i['标识符']] = {'姓名': i['姓名'], '所在团支部': i['所在团支部'], '完成情况': '未完成'}
        url = "https://jxtw.h5yunban.cn/jxtw-qndxx/cgi-bin/branch-api/course/records"
        values = {'course': courseId, 'nid': organizationInfo['branch'], 'accessToken': Token,
                  'pageSize': '1000',
                  'pageNum': 1}
        resData = {}
        while True:
            result = sendGet(url, values)
            if values['pageNum'] != 1:
                resData.extend(result['list'])
            else:
                resData = result['list']
            if int(result['pagedInfo']['total']) > int(result['pagedInfo']['pageSize']) * int(
                    result['pagedInfo']['pageNum']):
                values['pageNum'] = values['pageNum'] + 1
            else:
                break
        errorTxt = ""
        with tqdm(total=len(resData), desc='数据处理中', leave=True) as pbar:
            for i in resData:
                try:
                    perData = orjson.loads(str(i).replace('\'', '\"'))
                    datas[i['cardNo'] + i['branchs'][-1].replace('团支部', '')]['完成情况'] = '已完成'
                except KeyError:
                    errorTxt = errorTxt + (
                            "姓名 " + i['cardNo'] + "  或者 " + i['branchs'][-1].replace('团支部',
                                                                                     '') + " 团支部不存在或此人不属于此团支部，已跳过!\n")
                time.sleep(0.001)
                pbar.update(1)
        edf = pd.DataFrame(datas)
        edf = pd.DataFrame(edf.values.T, index=edf.columns, columns=edf.index)
        excel = pd.ExcelWriter("大学习未完成情况.xlsx")
        edf.to_excel(excel)
        excel.save()
        excel.close()
        mymovefile("大学习未完成情况.xlsx", "./处理结果/大学习未完成情况.xlsx")
        filename = r'./处理结果/大学习未完成情况.xlsx'
        wb = load_workbook(filename)
        ws = wb.active
        ws.delete_cols(1)  # 删除第 13 列数据
        wb.save(filename)

        if errorTxt != "":
            print("已导出未完成情况表EXCEL表到处理结果文件夹，其中一些数据似乎有误：\n" + errorTxt)
            print("按任意键退出！")
            c = input()
        else:
            print("已导出未完成情况表EXCEL表到处理结果文件夹")
    elif int(fun) == 5:
        exit()
    else:
        print("输入菜单无效，请重新输入！")
