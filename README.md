# BigStydyCompletionVisualization
 江西高校青年大学习完成情况数据可视化（正在制作），适用于江西省云瓣大学习系统，江西共青团公众号

## 如何使用？

1. 将仓库获取/下载到本地

2. 修改默认配置文件BigStudyConfigTemplate.cfg中的账号密码为自己系统的账号密码

3. 将BigStudyConfigTemplate.cfg修改为BigStudyConfig.cfg

4. pip install 以下依赖

   ```shell
   pip install configparser
   pip install orjson
   pip install faker
   pip install orjson
   pip install --upgrade "pip>=20.3" # 绝大多数linux_x_y的支持, 以及苹果M1芯片的适配
   ```

5. 运行main.py

   ```
   python3 main.py
   ```

   

## 要干什么？

- [x] 爬虫登录
- [ ] 爬虫爬取
- [ ] 可视化输出
- [ ] 输出至网页
- [ ] 输出未完成名单EXCEL

## 测试环境

python3.9

macOS 12.2 beta 1

PyCharm 2021.2.3
