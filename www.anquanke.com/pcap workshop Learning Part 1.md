> 原文链接: https://www.anquanke.com//post/id/239638 


# pcap workshop Learning Part 1


                                阅读量   
                                **211293**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01f310522145ea965b.png)](https://p4.ssl.qhimg.com/t01f310522145ea965b.png)



链接：[https://pan.baidu.com/s/1rH2jLScXAFST8OXDd_C6ng](https://pan.baidu.com/s/1rH2jLScXAFST8OXDd_C6ng)<br>
提取码：anq6

## 2017-03-25-traffic-analysis-exercise

打开流量包，看到了http的流量。我们其实能直接去看http流量的。但是还是先通过三板斧来分析该流量包吧。

存在dns,tcp,http,tls协议。

[![](https://p3.ssl.qhimg.com/t010ac7731eda05d25f.png)](https://p3.ssl.qhimg.com/t010ac7731eda05d25f.png)

在对话中的tcp中发现了异常多的Packets

[![](https://p4.ssl.qhimg.com/t01b7108c8c7680af90.png)](https://p4.ssl.qhimg.com/t01b7108c8c7680af90.png)

那么我们跟进并追踪一下这个tcp流（这里为什么要这么麻烦的去看这些东西呢，以为这个数据包的流量比较大，有近10000个数据流左右，不能遍历去找数据流，我们要理智地去分析）

[![](https://p4.ssl.qhimg.com/t01d71132e6069b6588.png)](https://p4.ssl.qhimg.com/t01d71132e6069b6588.png)

[![](https://p5.ssl.qhimg.com/t0182cfd850beed1578.png)](https://p5.ssl.qhimg.com/t0182cfd850beed1578.png)



## 木马文件

MZ开头的文件，很明显是一个exe文件+一个php文件这里Content-Type显示为 image/png。是非常奇怪的一个点。（因为这是一个响应数据包，服务器居然返回了一个假的Content-type）。可以看出操作者应该在访问木马文件。

[![](https://p1.ssl.qhimg.com/t0187feecc6429f91e2.png)](https://p1.ssl.qhimg.com/t0187feecc6429f91e2.png)

我们先对这个php中的代码进行还原。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012cbc653083cec718.png)

[![](https://p2.ssl.qhimg.com/t01d0efa4afdc94eb3e.png)](https://p2.ssl.qhimg.com/t01d0efa4afdc94eb3e.png)

因为我没有使用linux系统且目录中存在汉字，导致脚本运行出错。这里我输出一下。

[![](https://p2.ssl.qhimg.com/t01a7cf8772fb100302.png)](https://p2.ssl.qhimg.com/t01a7cf8772fb100302.png)

最后发现这个脚本从C://users/开始遍历了所有文件！然后进行了写文件和重命名的操作，害怕，不敢运行，以后有了win虚拟机就来运行。

[![](https://p1.ssl.qhimg.com/t018609f365116124e8.png)](https://p1.ssl.qhimg.com/t018609f365116124e8.png)

[![](https://p1.ssl.qhimg.com/t01a2733f964a926deb.png)](https://p1.ssl.qhimg.com/t01a2733f964a926deb.png)

然后我们来看一下另外一个exe文件。先把win Defender打开。然后（害怕）打开1.exe文件。果然，d=====(￣▽￣*)b。文件被删掉了。

[![](https://p3.ssl.qhimg.com/t0188b5cb585b4b6075.png)](https://p3.ssl.qhimg.com/t0188b5cb585b4b6075.png)

我们来看一下win defender怎么评价它。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fe919fb16253da71.png)

然后通过foremost 对这个文件进行分离得到了三个gif图，dll文件和exe文件。

[![](https://p5.ssl.qhimg.com/t01fc8669d0394bf128.png)](https://p5.ssl.qhimg.com/t01fc8669d0394bf128.png)

再通过strings进行分析dll文件。猜测这是一个php文件在通过zend进行加密后的exe文件。（猜测为之前分析过的php文件）

[![](https://p3.ssl.qhimg.com/t01fb18bc5c8d6a3a81.png)](https://p3.ssl.qhimg.com/t01fb18bc5c8d6a3a81.png)

那么提示就是通过dezend来解密之前进行加密过的php文件。 （我只想说这么短的代码我都手动还原了）

[![](https://p1.ssl.qhimg.com/t0130e21eaf4cf3c863.png)](https://p1.ssl.qhimg.com/t0130e21eaf4cf3c863.png)

导出文件后通过shasum命令拿到病毒样本hash值并进行搜索。

```
shasum -a 256 1.exe
```

[![](https://p0.ssl.qhimg.com/t01b6dc70422b7f219d.png)](https://p0.ssl.qhimg.com/t01b6dc70422b7f219d.png)

那么逐渐远离了主题——流量分析了。我们回到正题。继续看wireshark。



## 导出对象

[![](https://p4.ssl.qhimg.com/t010a144b1400a5f2d8.png)](https://p4.ssl.qhimg.com/t010a144b1400a5f2d8.png)

一般要根据文件的大小来进行排列（越大的文件越可疑）。第一个文件就是我们之前分析的exe文件，第三个是php后门文件，还有两个是结果输出文件。后面就是几个证书和没用的文件了。



## 解析

### <a class="reference-link" name="1.%E6%97%B6%E9%97%B4%E4%BF%A1%E6%81%AF"></a>1.时间信息

从第一个数据包的发出到最后一个数据包的时间为

[![](https://p2.ssl.qhimg.com/t014d910ccdc8448194.png)](https://p2.ssl.qhimg.com/t014d910ccdc8448194.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b3637306eae793a8.png)

### <a class="reference-link" name="2.Server%20name%20and%20ip"></a>2.Server name and ip

解析中有一个我没找到的信息(unusual Server and the ip of it)：

[![](https://p3.ssl.qhimg.com/t01806359d1d46fc462.png)](https://p3.ssl.qhimg.com/t01806359d1d46fc462.png)

[![](https://p0.ssl.qhimg.com/t013f9e2be5bb9a62c1.png)](https://p0.ssl.qhimg.com/t013f9e2be5bb9a62c1.png)

然后我就模仿这位师傅进行了列名添加服务器名和请求uri的操作。具体设置：

[![](https://p2.ssl.qhimg.com/t01dbe1e25e2803669a.png)](https://p2.ssl.qhimg.com/t01dbe1e25e2803669a.png)

现在来看就清晰了许多。（后面请自己根据过滤器添加列）

[![](https://p2.ssl.qhimg.com/t010dd132260e1b1bdd.png)](https://p2.ssl.qhimg.com/t010dd132260e1b1bdd.png)

[![](https://p2.ssl.qhimg.com/t013a2abc191aaa19c7.png)](https://p2.ssl.qhimg.com/t013a2abc191aaa19c7.png)

[![](https://p2.ssl.qhimg.com/t017af6ad5800d8ae24.png)](https://p2.ssl.qhimg.com/t017af6ad5800d8ae24.png)

[![](https://p5.ssl.qhimg.com/t01e12fc9c4ef269929.png)](https://p5.ssl.qhimg.com/t01e12fc9c4ef269929.png)

### <a class="reference-link" name="3.tls%E8%A7%A3%E5%AF%86"></a>3.tls解密

然后它对这个流量包进行了tls的解密。在流量包中找到了国家和其他的一些信息。这里为什么之前我没有解出这个tls流呢（文件里没给我 Key Log File）后来去网上查到了这个key file。解密后：

通过过滤器查，标红的以及后面的大部分流量包都是解密后的结果。

```
http.request or tls.handshake.type eq 1
```

[![](https://p2.ssl.qhimg.com/t013460a74f7a241dd2.png)](https://p2.ssl.qhimg.com/t013460a74f7a241dd2.png)

只不过解密后的内容还是经过未知加密方法的数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fe29530f4f147f7d.png)

### <a class="reference-link" name="4.country%E4%BF%A1%E6%81%AF"></a>4.country信息

在解密后的tls数据流中，仔细观察可以看到US,Manchester等字符串。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014db6937e1789d851.png)

将其作为列进行过滤，方便查看。

[![](https://p5.ssl.qhimg.com/t01222a35063dae7bd3.png)](https://p5.ssl.qhimg.com/t01222a35063dae7bd3.png)

然后，对这个流量包的分析就到这里了。如果有大师傅还有别的看法可以联系我一起学习。



## 参考链接：

[https://unit42.paloaltonetworks.com/wireshark-tutorial-decrypting-https-traffic/](https://unit42.paloaltonetworks.com/wireshark-tutorial-decrypting-https-traffic/)

[https://unit42.paloaltonetworks.com/unit42-customizing-wireshark-changing-column-display/](https://unit42.paloaltonetworks.com/unit42-customizing-wireshark-changing-column-display/)
