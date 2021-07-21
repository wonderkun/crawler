> 原文链接: https://www.anquanke.com//post/id/89941 


# 360CERT：Wordpress Keylogger事件报告


                                阅读量   
                                **115869**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t019cef207e37c75fd4.png)](https://p4.ssl.qhimg.com/t019cef207e37c75fd4.png)



## 0x00 事件背景

Catalin Cimpanu发现几起针对WordPress站点的攻击，主要通过加载恶意脚本进行键盘记录，挖矿或者挂载广告。并且有证据表明，这种攻击从4月份活跃至今。360CERT对该事件十分关注。



## 0x01 事件描述

起因是WordPress被注入了一个混淆的js脚本，从主题的function.php文件进行植入。加载的js脚本地址为：

其中reconnecting-websocket.js用作websocket通信，cors.js中包含后门。Cors.js更改前端页面，释放javascript脚本进行输入监听，之后将数据发送给攻击者（wss://cloudflare[.]solutions:8085/）。

[![](https://cert.360.cn/static/fileimg/picture_1_1512729045.png)](https://cert.360.cn/static/fileimg/picture_1_1512729045.png)

[![](https://cert.360.cn/static/fileimg/picture_2_1512729056.png)](https://cert.360.cn/static/fileimg/picture_2_1512729056.png)



## 0x02攻击脚本分析

[![](https://cert.360.cn/static/fileimg/picture_3_1512729066.png)](https://cert.360.cn/static/fileimg/picture_3_1512729066.png)

用户WordPress首页底部有两个JS，第一个用来做websocket通信。后门核心文件http://cloudflare[.]solutions/ajax/libs/cors/cors.js。其中cors.js有混淆，简单处理后得到攻击脚本：

[![](https://cert.360.cn/static/fileimg/picture_4_1512729073.png)](https://cert.360.cn/static/fileimg/picture_4_1512729073.png)

攻击脚本会首先调用linter()，其中有对linterkey1，linterkey2的解码。

中，域名cdnjs.cloudflare.com是不存在的，根据代码逻辑，有用的部分应为？后的内容：

[![](https://cert.360.cn/static/fileimg/picture_5_1512729109.png)](https://cert.360.cn/static/fileimg/picture_5_1512729109.png)

解密出：

[![](https://cert.360.cn/static/fileimg/picture_6_1512729094.png)](https://cert.360.cn/static/fileimg/picture_6_1512729094.png)

逻辑很好理解，监听blur 事件(输入框失去焦点) 通过websocket发送用户input内容。

[![](https://cert.360.cn/static/fileimg/picture_7_1512729121.png)](https://cert.360.cn/static/fileimg/picture_7_1512729121.png)

最后，窗口加载后执行addyandexmetrix()。该函数是一个类似cnzz，做访问统计的js，具体用法：

[https://yandex.com/support/metrica/code/counter-initialize.xml](https://yandex.com/support/metrica/code/counter-initialize.xml)



## 0x03 攻击影响

查看cloudflare[.]solutions DNS请求记录：

[![](https://cert.360.cn/static/fileimg/picture_8_1512729145.png)](https://cert.360.cn/static/fileimg/picture_8_1512729145.png)

可以看到，在6月份有一个峰值。并且在近期，攻击趋势陡然上升。以下是今天，截至写稿时的请求记录：

[![](https://cert.360.cn/static/fileimg/picture_9_1512729156.png)](https://cert.360.cn/static/fileimg/picture_9_1512729156.png)

可以看到，今天时，该攻击已经激化。

对页面进行检索，发现全球有近五千多站点被感染：

[![](https://cert.360.cn/static/fileimg/picture_10_1512729164.png)](https://cert.360.cn/static/fileimg/picture_10_1512729164.png)

以下受感染的部分域名：

[![](https://cert.360.cn/static/fileimg/picture_11_1512729174.png)](https://cert.360.cn/static/fileimg/picture_11_1512729174.png)



## 0x04 缓解措施

查看页面源代码中是否有向cloudflare[.]solutions的JS请求，通过这种方法进行自检。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cert.360.cn/static/fileimg/picture_12_1512729183.png)

恶意的JS是通过WordPress主题的function.php文件进行植入。请立即删除文件中，页面渲染恶意JS的部分。此时，密码很有可能已经被偷取，请及时更改密码。



## 0x05 IOCs

资源请求：

hxxp://cloudflare[.]solutions/ajax/libs/reconnecting-websocket/1.0.0/reconnecting-websocket.js

hxxp://cloudflare[.]solutions/ajax/libs/cors/cors.js

数据接收：

wss://cloudflare[.]solutions:8085/



## 0x06 时间线

2017年12月7日 Catalin Cimpanu事件披露

2017年12月8日 360CERT及时跟进，发布预警



## 0x07 参考

[https://www.bleepingcomputer.com/news/security/keylogger-found-on-nearly-5-500-infected-wordpress-sites/](https://www.bleepingcomputer.com/news/security/keylogger-found-on-nearly-5-500-infected-wordpress-sites/)
