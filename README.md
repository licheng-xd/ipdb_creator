ipdb_creator
============

从网络上爬出ip库的工具

#文件说明

1. query.py: 最基本的组件,定义了一个query_ip函数,可以传递ip进行,通过淘宝和sina的接口查询ip数据.
2. build_rtree.py: 定义了ipRadixDB类,该类主要是对radix的一些功能进行封装和外部数据交互的封装.该文件本来是用来生成数据库文件的,但后来用了所有24网段扫一遍的方法,该文件下面的main函数就被放弃了.
3. fully_update.py,fully_update_cn.py:这两个文件是具体执行功能的地方.运行fully_update_cn.py会生成raw_data_cn_taobao_merged的文件,该文件便是淘宝上关于国内ip数据库的信息.以此为基础,再运行fully_update.py,该文件会生成,raw_latest_fn, raw_latest_fn_merged和raw_latest_complete_merged三个文件.其中merged的文件是最终的ip数据库.这两个脚本会对国内国外的数据进行区别对待.国内的数据是所有的24网段全部扫描一遍,国外的数据是arin,apnic等几个文件中提供的国家的信息中网段进行查询的.fully_update_cn.py文件上有一些功能是繁碎的,这是由于当时写的比较急且有一些其他数据进行参照的缘故.如果觉得不爽,请改之.
4. delegated-*-latest:5个文件是5个ip分配组织提供的ip的数据集.需要先将这些文件进行更新.直接在google上搜索上相应的文件名应该就能找到相应的下载链接.
5. raw_data_cn_taobao:初始数据文件.该文件本来是由build_rtree生成的一个数据文件再经过处理得到的.现在没有在使用build_rtree文件了,该文件提供个空文件就ok了.
6. merge.py,same_prefix.py:无关文件,当时写的帮助确定问题的几个文件,目前已经无用.
7. .continue_file:和build_rtree.py有关,目前无用

#执行

1. 确保delegated-*-latest的文件已经更新到最新的版本
2. 确保raw_data_cn_taobao为空
3. python已经安装py-radix和netaddr这两个模块,可以用pip安装
3. python fully_update_cn.py生成相应的文件.会在终端输出相应的ip和网段
4. pytho fully_update.py 生成相应的文件.

最新delegated文件地址：ftp.apnic.net/stats/
国家码地址：http://zh.wikipedia.org/wiki/%E5%9C%8B%E5%AE%B6%E4%BB%A3%E7%A2%BC
