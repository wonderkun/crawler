> 原文链接: https://www.anquanke.com//post/id/82319 


# PHP应用安全静态代码分析工具 – WAP 2.0【附使用方法】


                                阅读量   
                                **133482**
                            
                        |
                        
                                                                                    



WAP 2.0是一个静态源代码安全分析和数据挖掘工具，可以发现PHP Web应用程序中的安全漏洞，同时具有较低的误报率。

使用过后发现常规的文件包含等漏洞可以检测出，但是不能检测出防注入方法比较复杂的注入。

使用方法：

切到wap目录下执行 java -jar wap.jar –h 得到wap的帮助文档。

wap  [选项]  -p  &lt;项目&gt;

wap  [选项]  &lt;单个php文件&gt;

选项：

-a   检测漏洞，不进行纠正

-s    只显示简要总结

-sqli        SQL注入漏洞检测，如果不使用-a，将进行自动纠正。

java -jar wap.jar –sqli  /root /wap-2.0/login.php login.php

–dbms &lt;dbms&gt;     指定应用程序所使用的数据库。可选的数据库为：mysql, db2, pg（PostgreSQL）。此选项只与-sqli选项配合使用，默认选择MySQL。

java -jar wap.jar -sqli –dbms mysql /root /wap-2.0/login.php login.php

-ci    检测RFI / LFI / DT / SCD /OS/ PHP注入漏洞，如果不使用-a，将进行自动纠正。

java -jar wap.jar -ci /root /wap-2.0/login.php

– XSS     检测反射型和存储型XSS漏洞，如果不使用-a，将进行自动纠正。

java -jar wap.jar -xss /root /wap-2.0/login.php

-p ＜项目&gt;    指定项目的完整路径

java -jar wap.jar -sqli -ci -xss -p /root /wap-2.0/cms/

file(s)     指定完整路径的一个或多个php文件。

java -jar wap.jar -sqli login.php upload_file.php

-h    帮助。

-out &lt;arg&gt; 将结果输出到指定位置。

java -jar wap.jar -sqli login.php upload_file.php -out  /result

[![](https://p3.ssl.qhimg.com/t01a772cc2fbaf0b932.png)](https://p3.ssl.qhimg.com/t01a772cc2fbaf0b932.png)

SQL注入漏洞 (SQLI)

跨站脚本漏洞 (XSS)

远程文件包含漏洞 (RFI)

本地文件包含漏洞 (LFI)

目录遍历漏洞 (DT/PT)

源代码泄漏漏洞 (SCD)

系统命令执行漏洞 (OSCI)

PHP代码注入漏洞

WAP可以基于语义分析应用的源代码，并对数据流进行分析，比如它会追踪$_GET, $_POST等入口点，并且追踪确认是否最终有敏感的方法可被执行。在探测结束后，这个工具还会通过数据挖掘确认漏洞是否真的存在或误报。

WAP使用Java编写，支持PHP 4.0及以上版本的Web应用。

[****下载： 点这里点这里****](http://sourceforge.net/projects/awap/)
