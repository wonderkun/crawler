> 原文链接: https://www.anquanke.com//post/id/235074 


# draytek漏洞分析


                                阅读量   
                                **116982**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t016299eb8eb23c6eb9.png)](https://p2.ssl.qhimg.com/t016299eb8eb23c6eb9.png)



分析复现一下几个draytek的漏洞

## 1.CVE-2020-8515

漏洞描述如下

```
DrayTek Vigor2960 1.3.1_Beta, Vigor3900 1.4.4_Beta, and Vigor300B 1.3.3_Beta, 1.4.2.1_Beta, and 1.4.4_Beta devices allow remote code execution as root (without authentication) via shell metacharacters to the cgi-bin/mainfunction.cgi URI. This issue has been fixed in Vigor3900/2960/300B v1.5.1.
```

我这里选取Vigor2960 1.5.0版本的固件和1.5.1版本的固件作为对比。

首先提取固件：

[![](https://p0.ssl.qhimg.com/t01fd1abe596081fc25.png)](https://p0.ssl.qhimg.com/t01fd1abe596081fc25.png)

固件是ubi类型的，需要使用[ubi_reader](https://github.com/jrspruitt/ubi_reader.git)这个工具进行提取，提取出来之后就是一个完整的文件系统。

[![](https://p2.ssl.qhimg.com/t01f54651a60791264d.png)](https://p2.ssl.qhimg.com/t01f54651a60791264d.png)

lighttpd是一个轻量级的web服务器，一般会有cgi文件作为支持，在`./etc/lighttpd/lighttpd.conf`中可以看到服务器的各个配置项。

根据漏洞通告，问题出现在`cgi-bin`目录下的`mainfunction.cgi`程序

那么我们就来分析这个文件，IDA打开，看到main函数：

[![](https://p1.ssl.qhimg.com/t01cc7fdcbfec5b2ac2.png)](https://p1.ssl.qhimg.com/t01cc7fdcbfec5b2ac2.png)

在33行中获取到`PATH_INFO`这个环境变量，这个环境变量表示紧接在CGI程序名之后的其他路径信息，它常常作为CGI程序的参数出现。比如：`http://192.168.0.1:80/cgi-bin/mainfunction.cgi/webrestore`,`PATH_INFO=/webrestore`.

一直看到最下面：

[![](https://p1.ssl.qhimg.com/t01050dd3cc103b2edc.png)](https://p1.ssl.qhimg.com/t01050dd3cc103b2edc.png)

除了通过PATH_INFO来确定要访问的路径，main函数还通过action参数来确定要执行的动作，跟进`sub_B44C`函数中。

在0x4240c地址处有一张函数表：

[![](https://p2.ssl.qhimg.com/t011eca968e46be732e.png)](https://p2.ssl.qhimg.com/t011eca968e46be732e.png)

遍历函数表名，并且和用户传入的action的值进行比较来确定要执行的函数。

main函数的逻辑大概理清楚了，接下来开始分析漏洞。

漏洞点在登录时的keyPath参数中，通过搜索字符串定位到函数，并且这个函数位于上面的函数表中，函数名为login：

[![](https://p0.ssl.qhimg.com/t018168ab61fc9fcb91.png)](https://p0.ssl.qhimg.com/t018168ab61fc9fcb91.png)

这也是为什么这个漏洞能够导致未认证的命令注入，因为是发生在登录过程中的命令注入。

[![](https://p3.ssl.qhimg.com/t017b7d131300bdfac5.png)](https://p3.ssl.qhimg.com/t017b7d131300bdfac5.png)

[![](https://p3.ssl.qhimg.com/t018a325b6ff2e65334.png)](https://p3.ssl.qhimg.com/t018a325b6ff2e65334.png)

首先是获取keypath的值，然后进行对这个值进行check，check函数如下：

[![](https://p2.ssl.qhimg.com/t01867b1172615fc52e.png)](https://p2.ssl.qhimg.com/t01867b1172615fc52e.png)

过滤了常用的``;|&gt;$(空格`等命令拼接字符，但是问题不大，依然可以绕过

在unix上可以通过如下字符来执行多条命令。

```
%0a
%0d 
;
&amp;
|
$(shell_command)
`shell_command`
`{`shell_command,`}`
```

`;&amp;|被过滤了，可以考虑使用%0a来绕过，而且**$(**的检测也不对，这里是先检测当前字符是否为$,并且下一个字符得为**(**才会发生替换，目的是为了检测$(shellcommand)这种类型的命令执行，但并没有过滤单独的$,这样子的话空格就可以使用**$`{`IFS`}`**来绕过。

check之后，通过snprintf函数将路径拼接在一起，类似于这样：

```
/tmp/rsa/private_key_keypath
```

后面接着再使用一个snprintf函数来将命令拼接。

```
openssl rsautl -inkey '/tmp/rsa/private_key_keypath' -decrypt -in /tmp/rsa/binary_login
```

之后将这条命令作为参数传递给run_command函数，run_command如下：

[![](https://p1.ssl.qhimg.com/t01ee89e7d467c6a735.png)](https://p1.ssl.qhimg.com/t01ee89e7d467c6a735.png)

使用popen函数执行这条命令，由此便造成了未授权的命令执行。

分析完原理，来实际操作一下，以vigor2960为例：

[![](https://p5.ssl.qhimg.com/t01ec8bf2da24ab8400.png)](https://p5.ssl.qhimg.com/t01ec8bf2da24ab8400.png)

随便输入用户名和密码，然后抓包：

[![](https://p5.ssl.qhimg.com/t017cd9219759385039.png)](https://p5.ssl.qhimg.com/t017cd9219759385039.png)

可以看到以POST方式访问`/cgi-bin/mainfunction.cgi`，传入的action=login，要执行的动作为login，按照上面分析的，我们修改keypatch的值为：

[![](https://p0.ssl.qhimg.com/t0107808aacb90496ca.png)](https://p0.ssl.qhimg.com/t0107808aacb90496ca.png)

执行效果如下：

[![](https://p1.ssl.qhimg.com/t01cd90ee642b3a4135.png)](https://p1.ssl.qhimg.com/t01cd90ee642b3a4135.png)

成功地执行了ls。

再换一个需要空格的命令。

[![](https://p3.ssl.qhimg.com/t017cc42bc1223f8b66.png)](https://p3.ssl.qhimg.com/t017cc42bc1223f8b66.png)

执行效果如下：

[![](https://p1.ssl.qhimg.com/t013620d0559adbaa9d.png)](https://p1.ssl.qhimg.com/t013620d0559adbaa9d.png)

keypatch的值前面加上`'`的作用是为了闭合命令中的单引号，因为在单引号包围中的命令是不会执行的。

实际上如果固件版本小于1.4.2.1，在rtick参数中也存在命令注入，这里使用1.4.1版本的固件来说明。

还是在login函数中。

[![](https://p3.ssl.qhimg.com/t018600d1abd2ef0775.png)](https://p3.ssl.qhimg.com/t018600d1abd2ef0775.png)

这里会取rtick作为时间戳来生成验证码。

查找rtick或者formcaptcha这两个字符串的交叉引用可以定位到验证码的生成函数。

[![](https://p5.ssl.qhimg.com/t019fdf99c0a0943e32.png)](https://p5.ssl.qhimg.com/t019fdf99c0a0943e32.png)

[![](https://p4.ssl.qhimg.com/t018917b3ac61c6685c.png)](https://p4.ssl.qhimg.com/t018917b3ac61c6685c.png)

可以看到这个函数里面直接将rtick的值作为验证码名，然后调用system函数执行，因此只需要修改rtick就可以达成未认证命令执行。

实际操作这一块就跳过了，感兴趣的可以自己尝试。

下面来和1.5.1的版本进行比较，直接定位到login函数。

[![](https://p5.ssl.qhimg.com/t01f8d357926ff60537.png)](https://p5.ssl.qhimg.com/t01f8d357926ff60537.png)

除了有过滤函数还有一个判断，判断字符是否为十六进制字符，而且check函数也完善了。

[![](https://p5.ssl.qhimg.com/t01c3ff1cc0e1c3f139.png)](https://p5.ssl.qhimg.com/t01c3ff1cc0e1c3f139.png)

再看到rtick那边：

[![](https://p4.ssl.qhimg.com/t01167a03286bdfd878.png)](https://p4.ssl.qhimg.com/t01167a03286bdfd878.png)

将rtick的值限制在数字之内。



## 2.CVE-2020-15415

漏洞描述如下：

```
On DrayTek Vigor3900, Vigor2960, and Vigor300B devices before 1.5.1, cgi-bin/mainfunction.cgi/cvmcfgupload allows remote command execution via shell metacharacters in a filename when the text/x-python-script content type is used, a different issue than CVE-2020-14472.
```

在1.5.1版本下，当访问`cgi-bin/mainfunction.cgi/cvmcfgupload`这个路径时，如果`content type`为`text/x-python-script`，则在filename中存在命令注入。

知道了漏洞所在，直接定位过去。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018a359094951d94e3.png)

看路径名猜测这个是一个用来上传文件的页面。

`getenv("QUERY_STRING")`，如果服务器与CGI程序信息的传递方式是GET，这个环境变量的值即使所传递的信息。这个信息经跟在CGI程序名的后面，两者中间用一个问号’?’分隔。

首先获取`QUERY_STRING`的值，然后判断是否存在`session=`字符串，如果不存在的话就进入到`sub_13450`函数中，跟进去看看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b2f6bd9b2316e3f3.png)

看到了一个system的执行点，但该怎么利用,漏洞通告中的filename并未在这里出现，出现filename的函数又和`/cvmcfgupload`路径不对应。

结合已有[POC](https://github.com/CLP-team/Vigor-Commond-Injection)继续分析。

```
POST /cgi-bin/mainfunction.cgi/cvmcfgupload?1=2 HTTP/1.1
Host: xxx.xxx.xxx.xxx:xxxx
Content-Length: 174
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh,en;q=0.9,zh-CN;q=0.8,la;q=0.7
Connection: close

------WebKitFormBoundary
Content-Disposition: form-data; name="abc"; filename="t';id;echo '1_"
Content-Type: text/x-python-script



------WebKitFormBoundary--

```

`/cgi-bin/mainfunction.cgi/cvmcfgupload?1=2`使得`getenv("QUERY_STRING")`能够获取到值，顺利进入到`sub_13450`函数；接着看到`Content-Type`=`multipart/form-data; boundary=----WebKitFormBoundary`，以及body部分的`Content-Disposition`等属性，这几个需要说明一下。

这篇[文章](https://zhuanlan.zhihu.com/p/122912935)中介绍了multipart/form-data，在往服务器发送表单数据之前需要对数据进行编码，multipart/form-data的编码规则为不做编码，发送二进制数据。对于multipart/form-data的编码规则有以下规范特征：1.必须以POST方式发送数据；2.Content-Type格式为multipart/form-data; boundary=$`{`boundary`}`。其中的boundary是长度为16的随机base64字符，浏览器会自动创建，类似下面这样：

```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary222BPd3etU0TLTOv
```

不过我们使用这种方式来传输数据的时候自然是没有boundary的。

然后，这个`boundary=----WebKitFormBoundary222BPd3etU0TLTOv`作为数据的起始符、分隔符，终结标记符多了—。

> 数据内容主要包括：Content-Disposition、Content-Type、数据内容等；其中数据内容前面有\n\r标记的空行；Content-Disposition是必选项，其它都是可选项；Content-Disposition 包含了 type 和 一个名字为 name 的 parameter，type 是 form-data，name 参数的值则为表单控件（username）的名字，如果是文件，那么还有一个 filename 参数，值就是文件名。

了解了这些前置知识后再看POC就明白漏洞通告中的filename在哪了，就是我们上传的文件名。

我们看到文件名：

```
filename="t';id;echo '1_"
```

双引号之内的就是文件名，`t';id;echo '1_`，熟悉的单引号，说明了filename会被写到’’之中，注意到filename最后还有一个`_`,经测试之后，发现去掉`_`的话命令就无法执行成功，说明需要`_`来作为一个‘引导’。

根据以上分析，最终确定了漏洞的发生点在上方所给截图的system调用中，接下来继续分析`sub_13450`函数。

先看三个函数：

```
NAME
cgiGetFiles - Returns a list of CGI file variables
char **cgiGetFiles (s_cgi *parms);

DESCRIPTION
This routine returns a NULL terminated array of names of CGI file variables that are available.

RETURN VALUE
On success a NULL terminated array of strings is returned. The last element is set to NULL. If an error occurred or if no files variables are available NULL is returned.
返回值为一个数组指针，最后一个元素会被设置为NULL
```

```
NAME
cgiGetFile - Return information of a CGI file variable
s_file *cgiGetFile (s_cgi *parms, const char *name);

DESCRIPTION
This routine returns a pointer to a datastructure associated with the value of a CGI file variable. The pointer must not be freed.
The s_file structure is declared as follows:
typedef struct file_s `{`
    char   *name,
           *type,
           *filename,
           *tmpfile;
`}` s_file;

返回值为s_file类型的指针
```

```
NAME
cgiEscape - HTML escape certain characters in a string
char *cgiEscape (char *string);

DESCRIPTION
This function returns a pointer to a sanitised string. It converts &lt;, &amp; and &gt; into HTML entities so that the result can be displayed without any danger of cross-site scripting in a browser. The result may be passed to free(3) after use. This routine is meant to be called before any user provided strings are returned to the browser.

RETURN VALUE
cgiEscape() returns a pointer to the sanitised string or NULL in case of error.
这个函数就是防止xss攻击，将&lt;, &amp;和&gt;转换成html实体，返回一个字符串指针

```

首先先用`cgiGetFiles`获得一个文件数组指针，然后进入一个循环，使用`cgiGetFile`获取s_file类型的指针。

[![](https://p4.ssl.qhimg.com/t013d63966f52cc9d6e.png)](https://p4.ssl.qhimg.com/t013d63966f52cc9d6e.png)

[![](https://p0.ssl.qhimg.com/t0196cf10f164f232e9.png)](https://p0.ssl.qhimg.com/t0196cf10f164f232e9.png)

接着使用`cgiEscape`将filename进行html转义(filename位于s**file结构体中的第三个，在32位机器下，char*类型的长度为4字节，因此+8就是filename的位置)，再从中寻找`**`，如果可以找到，就进入if代码块，之后就是将html转义之后的filename和`/data/%s/%s/`拼接，最后再和`mkdir -p`命令拼接，所以最终形成的命令就是如下所示：

```
mkdir -p /data/cvm/files/'&lt;filename&gt;'
```

漏洞分析完毕，来实际测试一下。

[![](https://p5.ssl.qhimg.com/t01cb28d567f6f46e50.png)](https://p5.ssl.qhimg.com/t01cb28d567f6f46e50.png)

另外，在测试中发现传输数据的`content-type`不是必要的。

[![](https://p1.ssl.qhimg.com/t01f381f11689c7460d.png)](https://p1.ssl.qhimg.com/t01f381f11689c7460d.png)

这个漏洞也是一个未认证的命令执行。

最后我们再看到1.5.1.2版本的固件是如何修复这个漏洞的。

[![](https://p2.ssl.qhimg.com/t01a19faf7603c0e0fb.png)](https://p2.ssl.qhimg.com/t01a19faf7603c0e0fb.png)

简单粗暴，直接过滤filename的值。



## 3.CVE-2020-19664

漏洞通告：

> DrayTek Vigor2960 1.5.1 allows remote command execution via shell metacharacters in a toLogin2FA action to mainfunction.cgi.

根据描述，漏洞发生在toLogin2FA 动作中，通过字符串定位到对应函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018e7acf0b7201a352.png)

首先获取环境变量，`HTTP_COOKIE`、`REMOTE_ADDR`、`HTTP_HOST`，接着以`HTTP_COOKIE`作为参数传入`sub_12864`函数，跟进查看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010a6486ee6c5c6f98.png)

如果参数1即`HTTP_COOKIE`的值存在的话就进入if代码块，假如我们是未认证用户，那么`HTTP_COOKIE`自然没有，直接返回-10。

然后将`sub_12864`函数的返回值，也就是-10拷贝到dest中，接着将dest和`HTTP_HOST`作为参数一并传入`sub_273B0`函数，跟进查看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0190dee732042b479a.png)

将a2，a3和`/sbin/auth_check.sh Interface`拼接，其中a2为-10，a3为`HTTP_HOST`的值，然后将拼接完后的命令传入`run_command`函数，实现命令执行。

[![](https://p3.ssl.qhimg.com/t01beb508c536047ef1.png)](https://p3.ssl.qhimg.com/t01beb508c536047ef1.png)

但遗憾的是按照这个思路我无法实现命令执行，可能是思路不对。为了弄清楚到底是哪里出了问题，我选择对比固件查看不同点。

目前最新固件版本为1.5.1.2，所以我使用1.5.1.1和1.5.1.2的固件进行对比，查看哪里进行了修复。

由于bindiff不支持高版本IDA，所以我使用[diaphora](https://github.com/joxeankoret/diaphora)这个IDA插件来进行比较，首先用IDA打开1.5.1.1版本的manfunction.cgi

在IDA中选择File-&gt;Script file,然后选择diaphora.py，会弹出一个框：

[![](https://p0.ssl.qhimg.com/t01e34c9119b627f140.png)](https://p0.ssl.qhimg.com/t01e34c9119b627f140.png)

然后点击确定，会生成一个sqlite数据库文件。

再用IDA打开1.5.1.2版本的manfunction.cgi，打开diaphora.py

[![](https://p5.ssl.qhimg.com/t01774abac740086529.png)](https://p5.ssl.qhimg.com/t01774abac740086529.png)

在diff against那里选择1.5.1.1版本的sqlite数据文件。

最终会生成这样的页面：

[![](https://p0.ssl.qhimg.com/t01c8d8a7758d1e94a4.png)](https://p0.ssl.qhimg.com/t01c8d8a7758d1e94a4.png)

Ratio表示两个函数的相似度，我们从中找到toLogin2FA 动作要执行的函数。

[![](https://p5.ssl.qhimg.com/t01a0c2b19070e18648.png)](https://p5.ssl.qhimg.com/t01a0c2b19070e18648.png)

diff pseudo-code可以查看伪代码对比。

[![](https://p0.ssl.qhimg.com/t01940d026c5c5520db.png)](https://p0.ssl.qhimg.com/t01940d026c5c5520db.png)

对比很清晰，左边的是1.5.1.2的伪代码，右边的是1.5.1.1的，新版本对HTTP_COOKIE处理函数进行了修改。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01aaad070b771aa809.png)

如果HTTP_COOKIE的值为空，那么经过处理后传入run_command的第二个则为NULL。

但我依然不清楚该如何利用该漏洞，很可惜。

根据这个[GitHub仓库](https://github.com/minghangshen/bug_poc)描述的，我的大致方向应该是没问题的，如果有知道如何利用的师傅希望能告知，这里主要是说明一下我的一个思路。。



## 4.CVE-2020-14993

漏洞通告：

> A stack-based buffer overflow on DrayTek Vigor2960, Vigor3900, and Vigor300B devices before 1.5.1.1 allows remote attackers to execute arbitrary code via the formuserphonenumber parameter in an authusersms action to mainfunction.cgi.

在1.5.1.1版本中，formuserphonenumber参数存在栈溢出。

通过字符串定位到函数。

[![](https://p0.ssl.qhimg.com/t01db847454f37fcd01.png)](https://p0.ssl.qhimg.com/t01db847454f37fcd01.png)

获取到formuserphonenumber的值，然后直接拷贝到栈上。

[![](https://p5.ssl.qhimg.com/t01808e97d78e85b4bc.png)](https://p5.ssl.qhimg.com/t01808e97d78e85b4bc.png)

确定了v31的大小之后就可以溢出了，并且经测试之后，vigor2960是没有开启ASLR和NX的，所以可以直接ret2shellcode，动态调试确定下来栈地址之后就能直接利用了。

这个函数在authusersms动作中，利用起来比较麻烦，可以看看这篇[文章](https://nosec.org/home/detail/4631.html),这里就不进行利用了。



## 5.总结

draytek其实爆出来的漏洞不止这些，不过大都是认证后的，最危险的还是CVE-2020-8515和CVE-2020-15415这两个不需要认证的漏洞。

公网上draytek的数量还是很大的，仅仅只是vigor2960就存在两万多条IP。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b5544ab72f1f5fc3.png)



## 6.参考链接

[https://nosec.org/home/detail/4631.html](https://nosec.org/home/detail/4631.html)

[https://github.com/CLP-team/Vigor-Commond-Injection](https://github.com/CLP-team/Vigor-Commond-Injection)

[https://blog.netlab.360.com/two-zero-days-are-targeting-draytek-broadband-cpe-devices/](https://blog.netlab.360.com/two-zero-days-are-targeting-draytek-broadband-cpe-devices/)

[https://baike.baidu.com/item/getenv/935515](https://baike.baidu.com/item/getenv/935515)

[https://manpages.debian.org/jessie/cgilib/cgiGetFiles.3.en.html](https://manpages.debian.org/jessie/cgilib/cgiGetFiles.3.en.html)

[https://manpages.debian.org/jessie/cgilib/cgiGetFile.3.en.html](https://manpages.debian.org/jessie/cgilib/cgiGetFile.3.en.html)

[https://manpages.debian.org/unstable/cgilib/cgiEscape.3.en.html](https://manpages.debian.org/unstable/cgilib/cgiEscape.3.en.html)
