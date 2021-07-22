> 原文链接: https://www.anquanke.com//post/id/147153 


# CBC字节翻转攻击


                                阅读量   
                                **120362**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01eb2d94c48226d3fe.png)](https://p0.ssl.qhimg.com/t01eb2d94c48226d3fe.png)



## 前言

以前有听说过这种攻击，但是没有详细去研究，这次ISCC刚好出了这种类型的题（虽然是原题），所以就详细学习一下。先来了解一下这种方式是如何进行加解密的。



## CBC原理

[![](https://mochazz.github.io/img/CBC_Attack/1.jpg)](https://mochazz.github.io/img/CBC_Attack/1.jpg)

如果用公式来表示的话，如下：（C表示密文，E表示进行加密，P表示明文，D表示进行解密，IV表示初始向量）

[![](https://mochazz.github.io/img/CBC_Attack/2.png)](https://mochazz.github.io/img/CBC_Attack/2.png)

再来看看如何进行攻击：（下面图片摘自《图解密码技术》一书）

[![](https://mochazz.github.io/img/CBC_Attack/3.jpg)](https://mochazz.github.io/img/CBC_Attack/3.jpg)



[![](https://mochazz.github.io/img/CBC_Attack/4.jpg)](https://mochazz.github.io/img/CBC_Attack/4.jpg)

### 

## 实例分析

[![](https://mochazz.github.io/img/CBC_Attack/5.png)](https://mochazz.github.io/img/CBC_Attack/5.png)

51行，当我们以admin账号登录时，程序会直接终止，若为其他则正常登录，并将用户信息存在info数组中传入login函数，并调用show_homepage函数。23行，发现当账号为admin，才会显示flag，这与之前矛盾。但是代码中使用了cbc加密方式，而且35行的cipher和36行的iv变量均中cookie数组中取，cookie数组又是我们可以控制的，这也是导致攻击发生的地方。

那么，我们的思路就是构造一个Admin用户，然后将大写的A翻转成小写的a，即是admin。我们点击登录之后，可以在cookie中获取到iv和cipher的值（看14行的login函数），然后我们先将cipher的第9个字符使用异或运算翻转成小写字母a，因为info数组序列化后，我们要翻转的大写字母A在下标为9的位置，每个分组的长度为16，因为返回的iv变量长度为16（要先经过base64解密）

[![](https://mochazz.github.io/img/CBC_Attack/7.png)](https://mochazz.github.io/img/CBC_Attack/7.png)



[![](https://mochazz.github.io/img/CBC_Attack/6.jpg)](https://mochazz.github.io/img/CBC_Attack/6.jpg)

翻转这一比特位，在解密下一块明文数据时，只会影响下一组明文翻转的那一位，但是却会影响本组明文的全部。因为我们翻转过的明文要先经过解密，然后才和IV变量进行异或，解密的时候是整串数据进行，所以整串明文受其影响。甚至可能会导致生成的明文部分乱码，至少绝对不再是原来的明文了。如果你还是不理解，那你可以看看[CBC字节翻转攻击-101Approach](http://wooyun.jozxing.cc/static/drops/tips-7828.html)中 **一个例子（CBC Blocks of 16 bytes）** 部分的解释，我这里就贴其中的一张图片（将6翻转成7）：

[![](https://mochazz.github.io/img/CBC_Attack/9.png)](https://mochazz.github.io/img/CBC_Attack/9.png)

在这道题目中，我们又要保证这堆乱码数据必须是`a:2:`{`s:8:"userna` ，因为这样等下才能和其他明文块组成正常的序列化字符串，正常进行反序列（看38行代码）。所以我们考虑控制IV变量，使得IV与Decryption(Ciphertext1)异或的结果是`a:2:`{`s:8:"userna` ，这样就能变成admin用户登录了。

最后我们再来说一下如何控制成我们想要的字符。直接丢几个公式，简洁明了：)

```
本组明文 = Decrypt(本组密文) ^ 上一组密文
A              B                 C
=========================================================
A = B ^ C
A ^ A = 0;   0 ^ A = A
C = A ^ A ^ C = B ^ C ^ A ^ C = A ^ B
(即C = A ^ B ，即：上一组密文 = 本组明文 ^ Decrypt(本组密文) )
ascii('a') ^ C ^ A ^ B = ascii('a') ^ A ^ B ^ A ^ B = ascii('a') ^ 0 = ascii('a')
(假设我们想要翻转成a，使用如上公式即可,即：想要的字符 = 上一组密文 ^ 本组明文 ^ Decrypt(本组密文) ^ 想要的字符 )
```

所以最终我们可以编写python程序来实现CBC字节翻转攻击，程序如下：

```
import urllib,base64,requests,re

url = "http://*.*.*.*/index.php"
datas = `{`
    "username" : "Admin",
    "password" : "admin"
`}`

r = requests.post(url,data=datas)
cipher = r.cookies.get("cipher")
cipher = base64.b64decode(urllib.unquote(cipher))
offset = 9
new_cipher = cipher[:offset] + chr(ord(cipher[offset])^ord("A")^ord("a")) + cipher[offset+1:]
new_cookies = requests.utils.dict_from_cookiejar(r.cookies)
new_cookies["cipher"] = urllib.quote_plus(base64.b64encode(new_cipher))

r2 = requests.get(url,cookies=new_cookies)
plain = base64.b64decode(re.findall("decode('(.*)')",r2.text)[0])
iv = base64.b64decode(urllib.unquote(new_cookies["iv"]))
old = plain[:len(iv)]
new = 'a:2:`{`s:8:"userna'
new_iv = "".join([chr(ord(iv[i])^ord(old[i])^ord(new[i])) for i in xrange(16)])
new_cookies["iv"] = urllib.quote_plus(base64.b64encode(new_iv))

r3 = requests.get(url,cookies=new_cookies)
print(r3.text)
```

[![](https://mochazz.github.io/img/CBC_Attack/8.png)](https://mochazz.github.io/img/CBC_Attack/8.png)

参考：

[分组密码模式: CBC模式(密码分组链接模式)](http://www.cnblogs.com/dacainiao/p/5521866.html)

[CBC字节翻转攻击-101Approach](http://wooyun.jozxing.cc/static/drops/tips-7828.html)

[CTF中常见的Web密码学攻击方式](http://seaii-blog.com/index.php/2017/05/13/60.html)
