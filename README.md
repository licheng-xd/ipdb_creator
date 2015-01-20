ipdb_creator
============

从网络上爬出ip库的工具

#文件说明

1. query.py: 最基本的组件,定义了一个query_ip函数，可以传递ip进行,通过淘宝的接口查询ip数据。
2. build_rtree.py: 定义了ipRadixDB类，该类主要是对radix的一些功能进行封装和外部数据交互的封装。
3. fully_update_cn.py:生成国内ip数据库，运行fully_update_cn.py会生成ip_data_cn_merged文件,该文件即淘宝上的国内ip数据信息。国内ip会扫描所有24网段。
4. fully_update_fn.py:生成国外ip数据库，运行fully_update_fn.py会生成ip_data_fn_merged文件,该文件即国外ip数据信息.国外ip只根据delegated文件中分配得简称来确定国家，如果没有国家简称，则通过taobao查询。
4. starter.py:启动器，会分别调用fully_update.py和fully_update_cn.py，最后通过合并ip_data_cn_merged和ip_data_fn_merged，得到ipdb.dat，就是完整的ip数据库结果。
5. delegated-*-latest:5个文件是ip分配组织提供的ip的数据集，需要先将这些文件进行更新.最新地址参看附录。
6. country_code:国家简称表
6. log.py: 日志打印

#执行说明

1. 确保delegated-*-latest的文件已经更新到最新的版本。
2. 确保output文件夹为空。
3. python已经安装py-radix，netaddr，requests这三个模块，可以用pip安装。
4. 通过`python starter.py`启动，运行时间较长，如果要使用后台启动，自己加nohup。
5. 大约需要10天左右才能跑完所有数据库。
6. TODO:如果有多个出口ip的条件，可以想办法优化查询速度。

# 附录

最新delegated文件地址：http://ftp.apnic.net/stats/

国家码地址：http://zh.wikipedia.org/wiki/%E5%9C%8B%E5%AE%B6%E4%BB%A3%E7%A2%BC
