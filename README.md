# BigStudyCompletionVisualization

江西高校青年大学习完成情况数据可视化（正在制作），适用于江西省云瓣大学习系统，江西共青团公众号

## 实现功能!

1. 导出某期大学习各班完成率表格及统计图

2. 导出总大学习完成情况情况表格及折线图

3. 导出某班每次大学习完成率情况表格及折线图

4. 导出最新一期未完成名单

   ⚠️以上功能基于三级团组织实现（省属本科院校团委-江西财经大学团委-软件与物联网工程学院团委），理论上三级团组织完全适用，其他级别团组织自测。

## 如何使用？

1. 将仓库获取/下载到本地

2. 修改默认配置文件BigStudyConfigTemplate.cfg中的账号密码为自己系统的账号密码（必填）

2. 根据默认配置文件BigStudyConfigTemplate.cfg中的提示，配置其他功能（影响功能23）

3. 将BigStudyConfigTemplate.cfg修改为BigStudyConfig.cfg

3. 将大学习名单（需要大学习的人的姓名、四级团支部名称）写入大学习名单Template.xlsx并改名为大学习名单.xlsx（影响功能4）

4. pip install 以下依赖或者双击exe文件（需要windows10+）

   ```shell
   pip install -r requirements.txt
   ```
   
5. 运行main.py或者双击exe文件（需要windows10+）

   ```
   python3 main.py
   ```

## 正在路上~

- [x] 爬虫登录
- [x] 爬虫爬取
- [x] 可视化输出
- [ ] 输出至网页
- [x] 输出未完成名单EXCEL

## 测试环境

python3.9

macOS 12.2 beta 1

PyCharm 2021.2.3.1
