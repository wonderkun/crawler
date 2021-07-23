> 原文链接: https://www.anquanke.com//post/id/203909 


# SpringBoot2.2.x 版本CPU增高BUG分析


                                阅读量   
                                **360820**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01798a1ee53318da6c.jpg)](https://p1.ssl.qhimg.com/t01798a1ee53318da6c.jpg)



## 一、发现问题

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E5%9C%A8%E4%B8%8A%E7%BA%BF%E4%B9%8B%E5%90%8E%EF%BC%8C%E8%BF%90%E8%A1%8C24%E5%B0%8F%E6%97%B6%E4%B9%8B%E5%90%8ECPU%E7%AA%81%E7%84%B6%E5%A2%9E%E9%AB%98%EF%BC%8C%E5%AF%BC%E8%87%B4%E4%B8%8D%E5%BE%97%E4%B8%8D%E9%87%8D%E5%90%AF%E6%9C%BA%E5%99%A8%E3%80%82"></a>项目在上线之后，运行24小时之后CPU突然增高，导致不得不重启机器。



## 二、分析及定位问题

<a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E5%9C%A8%E4%B8%8A%E7%BA%BF%E5%89%8D%E6%98%AF%E7%BB%8F%E8%BF%87%E5%8E%8B%E5%8A%9B%E6%B5%8B%E8%AF%95%EF%BC%8C%E5%88%9A%E5%BC%80%E5%A7%8B%E5%AE%9A%E4%BD%8D%E6%98%AFQPS%E8%BF%87%E5%A4%A7%EF%BC%8C%E9%80%9A%E8%BF%87%E5%A2%9E%E5%8A%A0%E6%9C%BA%E5%99%A8%E3%80%82%E4%BD%86%E7%BB%93%E6%9E%9C%E5%B9%B6%E4%B8%8D%E6%98%AF%E7%89%B9%E5%88%AB%E7%90%86%E6%83%B3%EF%BC%8C%E5%A7%8B%E7%BB%88%E4%BC%9A%E6%9C%89%E5%87%A0%E5%8F%B0%E6%9C%BA%E5%99%A8%E5%A2%9E%E9%AB%98%E3%80%82"></a>项目在上线前是经过压力测试，刚开始定位是QPS过大，通过增加机器。但结果并不是特别理想，始终会有几台机器增高。

### <a class="reference-link" name="%E9%A1%B9%E7%9B%AE%E7%8E%AF%E5%A2%83"></a>项目环境
- 测试机 1c2g
### <a class="reference-link" name="1%E3%80%81%E6%B5%8B%E8%AF%95"></a>1、测试

通过jmeter对该机器接口进行压力测试，qps为90，cpu增高到40%持续没多久下降到10%，一直持续稳定。并未产生CPU过高的情况，该机器配置比正式环境要低4倍，第一步得出的结论应该不在接口上

### <a class="reference-link" name="2%E3%80%81%E6%9B%B4%E6%8D%A2%E9%A1%B9%E7%9B%AE%E4%B8%AD%E6%AF%94%E8%BE%83%E6%97%A9%E6%9C%9F%E7%89%88%E6%9C%AC%E7%9A%84%E6%8F%92%E4%BB%B6%E5%8F%8A%E7%BA%BF%E7%A8%8B%E6%B1%A0"></a>2、更换项目中比较早期版本的插件及线程池

重新上线项目之后，运行1天之后，依然有2台机器的CPU持续增高，并且越往后增加越大

### <a class="reference-link" name="3%E3%80%81%E5%BC%80%E5%A7%8B%E9%92%88%E5%AF%B9%E7%BA%BF%E4%B8%8A%E9%AB%98CPU%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%8E%92%E6%9F%A5"></a>3、开始针对线上高CPU服务器排查

```
#查看java的pid
top  
#查看pid下的占用高的tid 
top -Hp pid  
#打印tid16进制
printf "%xn" tid  
#查看栈 输出到xx.log
jstack pid|grep -A 2000 tid的16进制 &gt; xx.log

#查看gc 打印每2000ms输出一次，共10次
jstat -gcutil pid 2000 10
```

结论：栈信息基本都是RUN或TIME_WATING 并没有相关的死锁的线程，但是通过gc发现大量的YGC持续的增高，这时候考虑到可能堆的信息有异常

### <a class="reference-link" name="4%E3%80%81%E9%92%88%E5%AF%B9%E5%A0%86%E4%BF%A1%E6%81%AF%E6%9F%A5%E7%9C%8B"></a>4、针对堆信息查看

```
#查看堆
jmap pid  
jmap -heap pid  
jmap -histo:live pid  
...

#常用的是最后一个 加一个more 防止过多内容刷屏 
jmap -histo:live pid|more
```

执行多次最后一个命令，发现一个队列在持续的增高，几百几百的增加并无然后减少的情况

```
1:        111885      139385304  [Ljava.lang.Object;
   3:         10515       15412904  [I
   4:        142407       13450056  [C
   5:         13892        4170928  [B
   6:        135968        3263232  java.lang.String
   .....
  34:          6423         308304  java.util.HashMap
  35:         12459         299016  java.util.concurrent.ConcurrentLinkedQueue$Node
```

最后一行就是发现增长过快的队列，到此算是发现了一个比较有用的信息，回头就去分析代码。但依然没有什么结论，代码逻辑并不复杂也并未使用到该队列。

### <a class="reference-link" name="5%E3%80%81%E5%92%A8%E8%AF%A2%E5%A4%A7%E4%BD%AC%EF%BC%8C%E5%BB%BA%E8%AE%AE%E9%80%9A%E8%BF%87%E7%81%AB%E7%84%B0%E5%9B%BE%E5%AE%9A%E4%BD%8D%E6%9F%90%E4%B8%AA%E9%98%B6%E6%AE%B5%E6%89%A7%E8%A1%8C%E8%BF%87%E7%A8%8B%E7%9A%84%E6%B6%88%E8%80%97%E6%83%85%E5%86%B5"></a>5、咨询大佬，建议通过火焰图定位某个阶段执行过程的消耗情况

```
#开始安装火陷图插件
#具体安装插件的过程，大家自行搜索，本文不具体描述如何安装火陷图
```

### <a class="reference-link" name="6%E3%80%81%E6%89%A7%E8%A1%8C%E5%91%BD%E4%BB%A4%E7%94%9F%E6%88%90%E7%81%AB%E9%99%B7%E5%9B%BE"></a>6、执行命令生成火陷图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0143d6090a83f4b767.jpg)

通过上图，我们能直观的看到在MimeTypeUtils方法中，使用到了过多的这个队列，然后就直接去看源码了。目前官方已经修复了一版在2.2.6版本中（但是很不幸运，并没有完全修复）

下面是2.2.6版本修复一版的代码，去除了之前的一些没有意义判断,MimeTypeUtils.java文件

```
private static class ConcurrentLruCache&lt;K, V&gt; `{`

        private final int maxSize;

        private final ConcurrentLinkedQueue&lt;K&gt; queue = new ConcurrentLinkedQueue&lt;&gt;();

        ....

        public V get(K key) `{`
            this.lock.readLock().lock();
            try `{`
                if (this.queue.size() &lt; this.maxSize / 2) `{`
                    V cached = this.cache.get(key);
                    if (cached != null) `{`
                        return cached;
                    `}`
                `}`
                else if (this.queue.remove(key)) `{`
                    this.queue.add(key);
                    return this.cache.get(key);
                `}`
            `}`
            finally `{`
                this.lock.readLock().unlock();
            `}`
            this.lock.writeLock().lock();
            try `{`
                // retrying in case of concurrent reads on the same key
                if (this.queue.remove(key)) `{`
                    this.queue.add(key);
                    return this.cache.get(key);
                `}`
                if (this.queue.size() == this.maxSize) `{`
                    K leastUsed = this.queue.poll();
                    if (leastUsed != null) `{`
                        this.cache.remove(leastUsed);
                    `}`
                `}`
                V value = this.generator.apply(key);
                this.queue.add(key);
                this.cache.put(key, value);
                return value;
            `}`
            finally `{`
                this.lock.writeLock().unlock();
            `}`
        `}`
    `}`
```

单纯的阅读代码，并没有什么大的BUG，但是我们可以去关注队列本身的问题。

查看ConcurrentLinkedQueue remove 源码

```
public boolean remove(Object o) `{`
    if (o != null) `{`
      Node&lt;E&gt; next, pred = null;
      for (Node&lt;E&gt; p = first(); p != null; pred = p, p = next) `{`
        boolean removed = false;
        E item = p.item;
        if (item != null) `{`
          if (!o.equals(item)) `{`
            next = succ(p);
            continue;
          `}`
          removed = p.casItem(item, null);
        `}`

        next = succ(p);
        if (pred != null &amp;&amp; next != null) // unlink
          pred.casNext(p, next);
        if (removed)
          return true;
      `}`
    `}`
    return false;
`}`
```

如果存在多个则删除第一个，并返回true，否者返回false，例如：多个线程同时要获取到同一个要删除的元素，则只删除一个，其他返回false，再结合MimeTypeUtils方法，会再去执行add，这就导致会对队列出现无限的增长【可能】（非百分百）。

### <a class="reference-link" name="7%E3%80%81%E7%BB%93%E8%AE%BA"></a>7、结论

造成CPU性能过高，是因为队列长度过长，remove方法需要遍历整个队列内容。队列过长的原因是因为remove 并发情况下返回false，开发过程中可能并未关注到remove会返回false，导致无限的执行add方法的可能。



## 三、验证问题

通过debug发现spring boot在执行过程中会针对用户请求的Accept和返回的Content-Type都会调用该方法。这时候其实就可以恶意构造Accept去请求某个api，Accept中每个用逗号分割都会过一次方法，导致大量性能消耗。本地通过构造多个Accpet值，发现在MimeTypeUtils中确实可以超出本身对队列的长度设置，导致缓慢增长。

<a class="reference-link" name="1%E3%80%81%E9%80%9A%E8%BF%87%E5%AE%98%E6%96%B9github-issues%E6%90%9C%E7%B4%A2%E7%9B%B8%E5%85%B3%E9%97%AE%E9%A2%98%EF%BC%8C%E5%8F%91%E7%8E%B0%E5%B7%B2%E7%BB%8F%E6%9C%89%E4%BA%BA%E5%9C%A8%E6%9C%80%E8%BF%91%E6%8F%90%E5%88%B0%E8%BF%87%E8%AF%A5%E9%97%AE%E9%A2%98%EF%BC%8C%E5%B9%B6%E5%B7%B2%E7%BB%8F%E8%A2%ABclose%E3%80%82"></a>1、通过官方github-issues搜索相关问题，发现已经有人在最近提到过该问题，并已经被close。

<a class="reference-link" name="2%E3%80%81%E9%80%9A%E8%BF%87%E5%86%8D%E6%AC%A1%E5%9B%9E%E5%A4%8D%E5%AE%98%E6%96%B9%E7%A0%94%E5%8F%91%E4%BA%BA%E5%91%98%EF%BC%8C%E5%B9%B6%E6%8F%90%E4%BE%9B%E6%9B%B4%E5%A4%9A%E7%9A%84%E7%9B%B8%E5%85%B3%E4%BF%A1%E6%81%AF%E8%AF%81%E6%98%8E2.2.6%E7%89%88%E6%9C%AC%E4%BF%AE%E5%A4%8D%E4%B9%8B%E5%90%8E%E4%BE%9D%E7%84%B6%E5%AD%98%E5%9C%A8%E8%AF%A5%E9%97%AE%E9%A2%98"></a>2、通过再次回复官方研发人员，并提供更多的相关信息证明2.2.6版本修复之后依然存在该问题
- [https://github.com/spring-projects/spring-framework/issues/24671#issuecomment-611427157](https://github.com/spring-projects/spring-framework/issues/24671#issuecomment-611427157)
<a class="reference-link" name="3%E3%80%81%E5%9C%A8%E6%AD%A4%E6%9C%9F%E9%97%B4%E5%8F%88%E6%9C%89%E4%BA%BA%E7%BB%99%E5%87%BA%E9%80%9A%E8%BF%87MediaType%20%E4%B8%8A%E4%BC%A0%E7%B1%BB%E5%9E%8B%E6%9E%84%E9%80%A0%E7%9A%84Accept"></a>3、在此期间又有人给出通过MediaType 上传类型构造的Accept
- [https://github.com/spring-projects/spring-framework/issues/24767](https://github.com/spring-projects/spring-framework/issues/24767)
<a class="reference-link" name="4%E3%80%81%E5%85%B7%E4%BD%93%E6%9E%84%E9%80%A0%E9%AA%8C%E8%AF%81"></a>4、具体构造验证

找一台低配版的服务 1c2g

使用jmeter，设置线程组，不需要特别高50个线程，永久发送

设置header的Accpet，可以先使用内容如下：

```
application/stream+x-jackson-smile, application/vnd.spring-boot.actuator.v3+json, application/vnd.spring-boot.actuator.v2+json, application/json, multipart/form-data; boundary=----WebKitFormBoundaryVHfecvFDYeDEjhu4, multipart/form-data; boundary=----WebKitFormBoundarymKzwdDkWNDNzQFP0, multipart/form-data; boundary=----WebKitFormBoundaryiWpMXOUbWwBwq2AX, application/x-www-form-urlencoded, text/html;charset=UTF-8, application/octet-stream, application/vnd.ms-excel;charset=utf8, application/msword, multipart/form-data; boundary=----WebKitFormBoundaryGF2AJ2ZdPqbWOyEO, multipart/form-data; boundary=----WebKitFormBoundaryTZLPpyBs2F0ycmkB, multipart/form-data; boundary=----WebKitFormBoundaryBUClXdZPA3oxpUpx, image/jpeg;charset=UTF-8, multipart/form-data; boundary=----WebKitFormBoundarysODcdeMwzfHwEjtw, multipart/form-data; boundary=----WebKitFormBoundary26i2en6YQUSXUBzs, multipart/form-data; boundary=----WebKitFormBoundaryxUUWAyZnZjwlM1oy, multipart/form-data; boundary=----WebKitFormBoundarysVMYk11tVTTsXuEB, multipart/form-data; boundary=----WebKitFormBoundaryXsI4dpNsVTCWWrRo, multipart/form-data; boundary=----WebKitFormBoundaryiV1owCGwTHyQzja0, multipart/form-data; boundary=----WebKitFormBoundarygf1XpLmgasAQU9fi, multipart/form-data; boundary=----WebKitFormBoundaryBNaQtUvpQ2VV7YYA, multipart/form-data; boundary=----WebKitFormBoundaryW1rdrg4AbJ5Jn3Po, multipart/form-data; boundary=----WebKitFormBoundaryoBwFj2ABM5LflDmW, multipart/form-data; boundary=----WebKitFormBoundary40xI2TxryjbkSCtO, multipart/form-data; boundary=----WebKitFormBoundarytaCC9B6g8u4urnLF, multipart/form-data; boundary=----WebKitFormBoundaryOrhplGKYP9ozLkCs, multipart/form-data; boundary=----WebKitFormBoundaryvEUouFAr3R3YJYBh, multipart/form-data; boundary=----WebKitFormBoundaryuQ9tEKtn59w5hPLY, multipart/form-data; boundary=----WebKitFormBoundaryRGvPXUBAuZ6xJ95u, application/vnd.openxmlformats-officedocument.wordprocessingml.document, multipart/form-data; boundary=----WebKitFormBoundary7jpljZi4k61KhCNN, multipart/form-data; boundary=----WebKitFormBoundary7GVKDTHVuBABvjGB, multipart/form-data; boundary=----WebKitFormBoundaryZbNBPl3T4VZ44q6B, audio/mp3, multipart/form-data; boundary=----WebKitFormBoundaryI6rUM76YvxrIEcqv, multipart/form-data; boundary=----WebKitFormBoundaryag4BDWrzifHRdDiR, multipart/form-data; boundary=----WebKitFormBoundary1YRsWAdVqDin8g8p, multipart/form-data; boundary=----WebKitFormBoundaryDaatlrV3KAyZu7wA, multipart/form-data; boundary=----WebKitFormBoundaryyhvikZJdRGH1AjQq, multipart/form-data; boundary=----WebKitFormBoundary2z4SJhqeEx5XtVj4, multipart/form-data; boundary=----WebKitFormBoundaryeDLd1MTvuhmcmzNe, multipart/form-data; boundary=----WebKitFormBoundarybKizrvRESfhxHAMQ, multipart/form-data; boundary=----WebKitFormBoundary24U8tmsOluZqcRXX, multipart/form-data; boundary=----WebKitFormBoundarye4j6KdQyBjY4FqSk, multipart/form-data; boundary=----WebKitFormBoundaryjPmgLdzMcMYYB3yS, multipart/form-data; boundary=----WebKitFormBoundaryxzBZ9w6Je3IJ53NM, multipart/form-data; boundary=----WebKitFormBoundaryScy0j73cvx3iCFyY, multipart/form-data; boundary=----WebKitFormBoundaryTBoS8s4YWwmBGTDA, image/*, multipart/form-data; boundary=----WebKitFormBoundaryRUutFo3RXlNPgoBS, text/html;charset=utf-8, multipart/form-data; boundary=----WebKitFormBoundarykLObBi1tJMf158kt, multipart/form-data; boundary=----WebKitFormBoundary8M8MfCWBEFcsxnBU
```

开始进行请求，然后我们再通过服务器中针对堆信息查看命令，查看 ConcurrentLinkedQueue队列增长情况

持续压测，然后再打开另三个jemter，做同样的请求操作，将header的Accept分别设置如下三种情况，也可以更多：

```
#第一种
text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
#第二种
text/css,*/*;q=0.1
#第三种
application/json
```

以上三个线程可以设置每个为30，永久。

我们再通过打印堆信息可以发现ConcurrentLinkedQueue队列开始突破限制突然增高，又突然减少，这时候可以把第一个jmeter请求先暂停。然后再持续观察堆信息

```
[xx[@xxx](https://github.com/xxx) ~]$ jmap -histo:live 10114|grep java.util.concurrent.ConcurrentLinkedQueue
  33:          4809         115416  java.util.concurrent.ConcurrentLinkedQueue$Node
 768:            36            864  java.util.concurrent.ConcurrentLinkedQueue
[xx[@xxx](https://github.com/xxx) ~]$ jmap -histo:live 10114|grep java.util.concurrent.ConcurrentLinkedQueue
  30:          5530         132720  java.util.concurrent.ConcurrentLinkedQueue$Node
 768:            36            864  java.util.concurrent.ConcurrentLinkedQueue
[xx[@xxx8](https://github.com/xxx8) ~]$ jmap -histo:live 10114|grep java.util.concurrent.ConcurrentLinkedQueue
  30:          5530         132720  java.util.concurrent.ConcurrentLinkedQueue$Node
 767:            36            864  java.util.concurrent.ConcurrentLinkedQueue
[xx[@xxx](https://github.com/xxx) ~]$ jmap -histo:live 10114|grep java.util.concurrent.ConcurrentLinkedQueue
  29:          6994         167856  java.util.concurrent.ConcurrentLinkedQueue$Node
 768:            36            864  java.util.concurrent.ConcurrentLinkedQueue
[xx[@xxx](https://github.com/xxx) ~]$ jmap -histo:live 10114|grep java.util.concurrent.ConcurrentLinkedQueue
  29:          7262         174288  java.util.concurrent.ConcurrentLinkedQueue$Node
 768:            36            864  java.util.concurrent.ConcurrentLinkedQueue
[xx[@xxx](https://github.com/xxx) ~]$ jmap -histo:live 10114|grep java.util.concurrent.ConcurrentLinkedQueue
  26:          9829         235896  java.util.concurrent.ConcurrentLinkedQueue$Node
 777:            36            864  java.util.concurrent.ConcurrentLinkedQueue
```

明显可以发现ConcurrentLinkedQueue在增高。到此针对SpringBoot在2.2.6版本中cpu持续增高情况已经可以完全的复现，复现过程可能会存在不成功，可以多试几次。



## 四、解决方案

<a class="reference-link" name="1%E3%80%81%E7%9B%AE%E5%89%8D%E5%8F%91%E7%8E%B0%E5%9C%A8%E5%A4%9A%E6%A0%B8CPU%E7%9A%84%E6%83%85%E5%86%B5%E4%B8%8B%E5%A2%9E%E9%95%BF%E6%AF%94%E8%BE%83%E7%BC%93%E6%85%A2%EF%BC%8C%E4%BD%86%E6%98%AF%E5%88%B0%E4%B8%80%E5%AE%9A%E7%9A%84%E9%95%BF%E5%BA%A6%E4%B9%8B%E5%90%8E%E4%B9%9F%E4%BC%9A%E5%8A%A0%E9%80%9F%E5%8A%A0%E5%A4%A7CPU%E7%9A%84%E6%B6%88%E8%80%97%EF%BC%8C%E6%89%80%E4%BB%A5%E9%AB%98%E9%85%8D%E7%BD%AE%E5%8F%AF%E8%83%BD%E6%98%AF%E4%B8%80%E4%B8%AA%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88"></a>1、目前发现在多核CPU的情况下增长比较缓慢，但是到一定的长度之后也会加速加大CPU的消耗，所以高配置可能是一个解决方案

<a class="reference-link" name="2%E3%80%81%E9%99%8D%E7%BA%A7%E6%96%B9%E6%A1%88%EF%BC%8C%E7%9B%AE%E5%89%8D%E9%80%9A%E8%BF%87%E5%AF%B9%E6%AF%94%E3%80%82SpringFramework%E5%9C%A85.1.x%E7%89%88%E6%9C%AC%E6%97%A0%E5%A4%AA%E5%A4%A7%E5%BD%B1%E5%93%8D%E3%80%82"></a>2、降级方案，目前通过对比。SpringFramework在5.1.x版本无太大影响。

<a class="reference-link" name="3%E3%80%81%E7%AD%89%E5%BE%85%E6%9B%B4%E6%96%B0%20%E7%9B%AE%E5%89%8Dmaster%E5%86%8D%E6%AC%A1%E4%BF%AE%E5%A4%8D%E4%B8%80%E7%89%88%EF%BC%8C%E9%A2%84%E8%AE%A14.27%E5%8F%91%E5%B8%83%EF%BC%8C%E5%AE%98%E6%96%B9%E4%B9%9F%E5%B0%86MimeTypeUtils%E5%88%97%E4%B8%BA5.3.x%E7%89%88%E6%9C%AC%E9%87%8D%E6%9E%84%E4%B9%8B%E4%B8%80"></a>3、等待更新 目前master再次修复一版，预计4.27发布，官方也将MimeTypeUtils列为5.3.x版本重构之一

```
#修复方案从 ConcurrentLinkedQueue 队列切换到了 ConcurrentLinkedDeque 队列
```



## 五、补充

验证 ConcurrentLinkedQueue 队列，出现false情况

```
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class Main `{`
    private static ConcurrentLinkedQueue&lt;Integer&gt; queue = new ConcurrentLinkedQueue&lt;&gt;();

    public static void main(String[] args) `{`
        for (int i = 0; i &lt; 1000; i++) `{`
            Thread thread1 = new QueueThread(String.valueOf(i));
            thread1.start();
        `}`
        try `{`
            Thread.sleep(5000);
        `}` catch (InterruptedException e) `{`
            e.printStackTrace();
        `}`
        System.out.println("end");
    `}`

    static class QueueThread extends Thread `{`
        private int value = 0;

        private String name;

        public QueueThread(String name) `{`
            this.name = name;
            queue.add(value);
        `}`

        @Override
        public void run() `{`
            for (int i = 1; i &lt; 1000; i++) `{`
                try `{`
                    boolean flag = queue.remove(value);
                    System.out.println("remove: " + value + " "+ flag);
                    queue.add(value);
                    value++;
                `}` catch (Exception e) `{`
                    System.out.println(e);
                `}`
            `}`
        `}`
    `}`
`}`
```

备注：如果是2.2.1-2.2.5 版本是会造成频繁的拿锁与解锁，本篇是以2.2.6版本为分析
