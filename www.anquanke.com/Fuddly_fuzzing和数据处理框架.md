> 原文链接: https://www.anquanke.com//post/id/83474 


# Fuddly：fuzzing和数据处理框架


                                阅读量   
                                **69216**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://github.com/k0retux/fuddly](https://github.com/k0retux/fuddly)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01c9315194d477e82b.jpg)](https://p2.ssl.qhimg.com/t01c9315194d477e82b.jpg)

       ** Fuddly是一个fuzzing和data处理框架。**

 

**功能列表**

        1.       图形化的数据模型：

                    .能够以图像的方式表达一些复杂的数据。

                    .对复杂的数据进行管理

                    .对现有的数据进行分析和管理

                    .能够对fuzzing的策略进行生成和变异

        2.       Fuzzing自动化测试框架：

                    .自动扫描目标

                    .以一个独立的探针（probes）对目标进行监视与分析

                    .自动存放检测的历史记录，随时可以查看

                    .自动处理从攻击目标获得的数据(可以实现一些特定是数据转换)



**目前所缺乏的：**

        1.       完整的文档

        2.       详情请参考TODO文件

 

**关于Fuddly文档的结构**

        .这个链接展示了这个框架的文档结构。链接[http://fuddly.readthedocs.org/en/develop/](http://fuddly.readthedocs.org/en/develop/)

        .请根据下面的步骤生成Fuddly文件：

            i.                     先进入docs/目录

            ii.                   使用make html命令生成HTML文档

            iii.                  使用make latexpdf命令生成PDF文档

            iv.                  生成的文档会存放在docs/build/目录下

 

**Fuddly启动及测试例子**

        fuzzfmk/test.py，这个文件包含了所有Fuddly的测试组件。所以只要运行这个文件即可。

        下面我来说说具体的命令。

            .开启测试，选用全部组件

```
&gt;&gt; python fuzzfmk/test.py –a
```



            .开启测试，但是只选用部分组件

```
&gt;&gt; python fuzzfmk/test.py
```



            .避免数据模型发生错误，比如替换相同数据，减少错误的数据。

```
--ignore-dm-specifics
```



            .一般情况下进行测试的命令

```
&gt;&gt; python fuzzfmk/test.py &lt;Test_Class&gt;.&lt;test_method&gt;
```



 

**其它：**

        如果你有自己设计的数据模型，可以放到imported_data/目录下，之后就可以使用它了。

 

**依赖的组件：**

        支持Python2和Python3

        必须按照的：

            **1.Python2或者Python3的Compatibility库**

            可以参考这个页面

[            http://pythonhosted.org/six/](http://pythonhosted.org/six/)

           ** 2.必须按照SQLite3数据库**

                可选择安装的：

                Xtermcolor:一个终端的色彩组件

                cups: Python绑定libcups

                rpyc: 远程调用Python Call

          **  3.文档生成**

[                sphinx](http://sphinx-doc.org/): sphinx 必须大于等于 1.3

                texlive (可选): 生成PDF文档的组件

                readthedocs theme(可选)：对HTML文档的一个优化

        **工具地址在原文链接中**<br>
