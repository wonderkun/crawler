> 原文链接: https://www.anquanke.com//post/id/103819 


# 如何通过7个漏洞攻破ShareFile本地环境


                                阅读量   
                                **79052**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dirkjanm，文章来源：blog.fox-it.com
                                <br>原文地址：[https://blog.fox-it.com/2018/04/06/compromising-sharefile-on-premise-via-7-chained-vulnerabilities/](https://blog.fox-it.com/2018/04/06/compromising-sharefile-on-premise-via-7-chained-vulnerabilities/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01b7a9a20d6e35ed2a.jpg)](https://p1.ssl.qhimg.com/t01b7a9a20d6e35ed2a.jpg)



## 一、前言

前一段时间，我们配置了带有StorageZone控制器的一个Citrix ShareFile环境。[ShareFile](https://www.citrix.com/products/sharefile/)是面向企业的文件同步及共享解决方案，尽管有一些版本完全依赖于云端，但Citrix也提供了另一种混合版本，其中数据可以通过StorageZone控制器存储在本地（on-premise）。在本文中，我们介绍了Fox-IT如何挖掘该环境中存在的多个漏洞，利用这些漏洞，攻击者可以通过任意账户访问ShareFile中存储的任意文件。向Citrix披露这些漏洞信息后，Citrix通过云平台及时更新修复了这些缺陷。这些漏洞全部位于StorageZone控制器组件中，因此完全基于云端的部署方案不会受到影响。根据Citrix的描述，财富500强中有多家企业和组织在使用ShareFile解决方案（纯云端或者带有本地组件），这些企业和组织涉及政府、科技、医疗、银行以及关键基础设施。

[![](https://p3.ssl.qhimg.com/t01ec890c80566a0b41.png)](https://p3.ssl.qhimg.com/t01ec890c80566a0b41.png)



## 二、获取访问权限

在了解应用整体情况以及工作流程后，我们决定研究上传流程以及云端与ShareFile本机端组件的连接情况。一般来说，我们可以采用两种方法将文件上传到ShareFile中：一种基于HTML5，另一种则是基于Java Applet。在接下来的例子中，我们使用的是基于Java的上传方式。我们进行了一些配置，使得Burp可以捕捉到所有请求（Burp是我们用来测试Web应用的首选工具）。当准备上传时，会有一个请求发送到ShareFile的云组件，该组件地址为`name.sharefile.eu`（其中`name`为采用该解决方案的公司名称）：

[![](https://p1.ssl.qhimg.com/t01d0f7d9645047da9f.png)](https://p1.ssl.qhimg.com/t01d0f7d9645047da9f.png)

从上图中可知，该请求包含上传信息，具体包括文件名、文件大小（字节数）、上传所使用的工具（本例中为Java上传器）以及我们是否愿意执行unzip操作（后面会解释这一点）。该请求返回的响应数据如下：

[![](https://p3.ssl.qhimg.com/t01db3ab86c33c93d23.png)](https://p3.ssl.qhimg.com/t01db3ab86c33c93d23.png)

在响应数据中，我们可以看到两种不同的上传URL，都包含指向本地StorageZone控制器地址的URL前缀（这里隐去了敏感信息）。因此，云组件可以生成将文件上传到本地组件所对应的URL地址。

第一种URL为`ChunkUri`，单个文件分块会分别上传到这些地址。当文件传输完成后，可以使用`FinishUri`来完成服务器上的文件上传流程。在这两种URL中，我们都可以看到其中附带了文件名、文件大小等各种信息，也可以看到用来标识上传会话的`uploadid`。最后还有一个`h=`参数，后面跟着的是经过base64编码后的哈希值。该哈希值用来确保URL中的参数没有被篡改过。

我们首先注意到的是`unzip`参数。如下图所示，上传器给用户提供了一个选项，支持压缩文档（如`.zip`文件）上传后的自动解压功能。

[![](https://p0.ssl.qhimg.com/t01e37d013b7f2e2b81.png)](https://p0.ssl.qhimg.com/t01e37d013b7f2e2b81.png)

解压zip文档时经常会犯的错误就是没有去验证zip文件中路径的有效性。如果在zip文件中使用相对路径，攻击者可能会触及超出脚本限制范围的不同目录。这种漏洞就是著名的目录遍历或者[路径遍历](https://www.owasp.org/index.php/Path_Traversal)漏洞。

如下一段python代码可以创建名为`out.zip`的一个特殊zip文件，该文件中包含两个文件，其中一个使用了相对路径。

```
import sys, zipfile
#the name of the zip file to generate
zf = zipfile.ZipFile('out.zip', 'w')
#the name of the malicious file that will overwrite the origial file (must exist on disk)
fname = 'xxe_oob.xml'
#destination path of the file
zf.write(fname, '../../../../testbestand_fox.tmp')
#random extra file (not required)
#example: dd if=/dev/urandom of=test.file bs=1024 count=600
fname = 'test.file'
zf.write(fname, 'tfile')
```

当我们将这个文件上传到ShareFile后，我们可以看到如下信息：

```
ERROR: Unhandled exception in upload-threaded-3.aspx - 'Access to the path '\company.internaldatatestbestand_fox.tmp' is denied.'
```

该信息表明StorageZone控制器尝试将我们的文件解压到缺乏权限的那个目录中，但我们还是可以成功修改文件解压的目标目录。只要StorageZone控制器具备某些目录的权限，我们就可以利用这个漏洞将我们可控的文件解压到这些目录中。想象一下，默认的解压路径为`c:appdatacitrixsharefiletemp`，我们可以构造路径为`../storage/subdirectory/filename.txt`的一个文件，这样就能将这个文件解压到`c:appdatacitrixsharefilestoragesubdirectory`目录中。相对路径中的`../`表示操作系统应该跳到目录树中的上一层目录，然后在当前目录中使用相对路径中的剩余部分来进行寻址。

> 漏洞1：文档解压过程中的路径遍历漏洞。



## 三、从任意写入到任意读取

虽然将任意文件写入存储目录中的任意位置的确是个高风险漏洞，但漏洞的影响范围取决于应用如何使用磁盘上的文件，以及目标上是否会检查这些文件完整性。为了验证这种能力的影响范围，我们来看一下StorageZone控制器的具体工作原理。我们发现有三个主目录可以存储较为有趣的一些数据：
- files
- persistenstorage
- tokens
其中，`files`目录用来存放与上传有关的临时数据；已上传到ShareFile中的文件存储在`persistentstorage`目录中；`tokens`目录包含与令牌相关的一些数据，这些数据用来控制文件的下载。

当新的上传任务初始化时，URL地址中包含名为`uploadid`的一个参数。显然，从这个名称中我们知道该参数是与上传有关的一个ID值，本例子中这个参数值为`rsu-2351e6ffe2fc462492d0501414479b95`。在`files`目录中，我们可以看到与该ID匹配的各种上传目录。

在这些目录中都包含名为`info.txt`的一个文件，该文件包含我们上传过程中的一些信息：

[![](https://p3.ssl.qhimg.com/t018b6d38ee3f3695c0.png)](https://p3.ssl.qhimg.com/t018b6d38ee3f3695c0.png)

在`info.txt`中包含我们在前面看到过的一些参数，比如`uploadid`、文件名、文件大小（13个字节），还包括一些新的参数。最后我们还可以看到包含32个大写字母的的字符串，该哈希字符串用来标识数据的完整性。

我们还可以看到其他ID值，为`fi591ac5-9cd0-4eb7-a5e9-e5e28a7faa90`以及`fo9252b1-1f49-4024-aec4-6fe0c27ce1e6`，分别对应了此次上传的文件ID以及存放文件的目录ID。

经过一段时间的研究后，我们发现该服务使用MD5哈希算法来校验文件的完整性，通过`info.txt`文件中其他数据计算出哈希值。需要注意的是，这里数据的编码格式为UTF-16-LE，这也是Windows系统默认使用的Unicode字符串编码格式。

掌握这些知识后，我们可以写一段简单的python脚本，能够计算修改后`info.txt`文件的正确哈希值，并将该值写回磁盘中：

```
import md5
with open('info_modified.txt','r') as infile:
instr = infile.read().strip().split('|')
instr2 = u'|'.join(instr[:-1])
outhash = md5.new(instr2.encode('utf-16-le')).hexdigest().upper()
with open('info_out.txt','w') as outfile:
outfile.write('%s|%s' % (instr2, outhash))
```

这里我们也找出了第二个漏洞：应用并没有使用私有的密钥来校验`info.txt`文件的完整性，相反使用了简单的MD5哈希值来防止文件内容被破坏。这样一来，如果攻击者拥有数据存储目录的写入权限，就有可能篡改上传信息。

> 漏洞2：数据文件（`info.txt`）的完整性没有经过合适的校验。

利用前一个漏洞，我们可以将文件写入任意目录中，因此我们可以上传自己的`info.txt`，修改上传信息。

此外，我们发现应用在上传数据时，会使用`fi591ac5-9cd0-4eb7-a5e9-e5e28a7faa90`这个文件ID作为该文件的临时名称，上传后的数据会写入该文件中。当上传结束时，该文件会加入用户的ShareFile账户中。这里我们来尝试一下另一个路径遍历漏洞。使用上述脚本，我们将文件ID修改成另一个文件名，尝试提取名为`secret.txt`的一个测试文件（`files`目录中已经有一个`secret.txt`文件，`files`目录是临时文件所在目录的上一层目录）。经过修改的`info.txt`文件如下所示：

[![](https://p1.ssl.qhimg.com/t0126ff42db737b072d.png)](https://p1.ssl.qhimg.com/t0126ff42db737b072d.png)

当我们继续使用`upload-threaded-3.aspx`页面来完成上传任务时，我们得到了如下错误：

[![](https://p1.ssl.qhimg.com/t01df1f3b238bfa8d9a.png)](https://p1.ssl.qhimg.com/t01df1f3b238bfa8d9a.png)

显然，我们尝试获取的`secret.txt`文件的大小为14个字节，并非`info.txt`文件中指定的13个字节。我们可以上传包含正确文件大小信息的新的`info.txt`文件，这样`secret.txt`文件就可以成功上传到我们的ShareFile账户中：

[![](https://p3.ssl.qhimg.com/t0172e835a7b49d3325.png)](https://p3.ssl.qhimg.com/t0172e835a7b49d3325.png)

因此我们挖掘出了第二个路径遍历漏洞，该漏洞位于`info.txt`文件中。

> 漏洞3：`info.txt`文件中存在路径遍历漏洞。

原先我们可以将任意文件写入系统中，到目前为止，我们已经可以将该漏洞变成读取任意文件的漏洞，只需要知道目标文件的文件名即可。需要注意的是，攻击者可以通过监控Web接口的流量了解到`info.txt`文件中包含的所有信息，因此攻击者在发起这种攻击时并不需要拥有一个`info.txt`文件。



## 四、研究文件下载过程

前面我们一直关注的是新文件上传方面的漏洞，文件的下载同样由ShareFile云组件来控制，云组件会指示StorageZone控制器来为用户请求的文件提供服务。典型的下载链接如下所示：

[![](https://p5.ssl.qhimg.com/t019b86a33eeffb470d.png)](https://p5.ssl.qhimg.com/t019b86a33eeffb470d.png)

如上图所示，`dt`参数为下载中涉及的令牌信息，`h`参数包含URL剩余部分的HMAC信息，以便向StorageZone控制器证明我们拥有下载此文件的正确权限。

下载的令牌信息存放在`tokens`目录的一个XML文件中，典型的文件内容如下所示：

```
&lt;!--?xml version="1.0" encoding="utf-8"?--&gt;&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;ShareFileDownloadInfo authSignature="866f075b373968fcd2ec057c3a92d4332c8f3060" authTimestamp="636343218053146994"&gt;
&lt;DownloadTokenID&gt;dt6bbd1e278a634e1bbde9b94ff8460b24&lt;/DownloadTokenID&gt;
&lt;RequestType&gt;single&lt;/RequestType&gt;
&lt;BaseUrl&gt;https://redacted.sf-api.eu/&lt;/BaseUrl&gt;
&lt;ErrorUrl&gt;https://redacted.sf-api.eu//error.aspx?type=storagecenter-downloadprep&lt;/ErrorUrl&gt;
&lt;StorageBasePath&gt;\s3sf-eu-1;&lt;/StorageBasePath&gt;
&lt;BatchID&gt;dt6bbd1e278a634e1bbde9b94ff8460b24&lt;/BatchID&gt;
&lt;ZipFileName&gt;tfile&lt;/ZipFileName&gt;
&lt;UserAgent&gt;Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0&lt;/UserAgent&gt;
&lt;Metadata&gt;
&lt;Item key="operatingsystem" value="Linux" /&gt;
&lt;/Metadata&gt;
&lt;IrmEnabled&gt;false&lt;/IrmEnabled&gt;
&lt;IrmPolicyServerUrl /&gt;
&lt;IrmAccessId /&gt;
&lt;IrmAccessKey /&gt;
&lt;Items&gt;
&lt;File name="testfile" path="a4ea881a-a4d5-433a-fa44-41acd5ed5a5ffffi0f0f2e_3477_4647_9cdd_e89758c21c37" size="61" id="" /&gt;
&lt;/Items&gt;
&lt;Log&gt;
&lt;EventID&gt;fif11465-ba81-8b77-7dd9-4256bc375017&lt;/EventID&gt;
&lt;UserID&gt;c7add7af-91ac-4331-b48a-0aeed4a58687&lt;/UserID&gt;
&lt;OwnerID&gt;c7add7af-91ac-4331-b48a-0aeed4a58687&lt;/OwnerID&gt;
&lt;AccountID&gt;a4ea881a-a4d5-433a-fa44-41acd5ed5a5f&lt;/AccountID&gt;
&lt;UserEmailAddress&gt;fox-it@redacted&lt;/UserEmailAddress&gt;
&lt;Name&gt;tfile&lt;/Name&gt;
&lt;FileCount&gt;1&lt;/FileCount&gt;
&lt;AdditionalInfo&gt;fif11465-ba81-8b77-7dd9-4256bc375017&lt;/AdditionalInfo&gt;
&lt;FolderID&gt;foh160ab-aa5a-4e43-96fd-e41caed36cea&lt;/FolderID&gt;
&lt;ParentID&gt;foh160ab-aa5a-4e43-96fd-e41caed36cea&lt;/ParentID&gt;
&lt;Path&gt;/root/a4ea881a-a4d5-433a-fa44-41acd5ed5a5f/foh160ab-aa5a-4e43-96fd-e41caed36cea&lt;/Path&gt;
&lt;IncrementDownloadCount&gt;false&lt;/IncrementDownloadCount&gt;
&lt;ShareID /&gt;
&lt;/Log&gt;
&lt;/ShareFileDownloadInfo&gt;
```

这里有两个地方比较有趣。第一个地方为`File`元素的`path`属性，该属性指定了该令牌适用于哪一个文件。`path`开头为一个ID，值为`a4ea881a-a4d5-433a-fa44-41acd5ed5a5f`，这也是ShareFile的AccountID，每个ShareFile实例都不一样。第二个ID值为`fi0f0f2e_3477_4647_9cdd_e89758c21c37`，每个文件都不一样（因此使用的是`fi`这个前缀），这个ID开头为两个`0f`子目录，应该是为了避免过长的目录列表。

第二个值得注意的地方是`ShareFileDownloadInfo`元素中的`authSignature`属性。该属性表明XML文件经过签名处理，可以确保文件的真实性，避免恶意令牌被下载。

现在起我们来研究一下StorageZone控制器这个软件，这是采用.NET开发的一个程序，在IIS下运行，因此我们很容易就可以使用诸如JustDecompile之类的工具来反编译相关程序。我们从服务器端拿到了StorageZone控制器程序，但Citrix也在官网上提供了该组件的下载链接。

反编译处理后，我们很快就找到了负责验证令牌的那些函数。Citrix通过`AuthenticatedXml`这个函数生成XML文件的签名。我们在代码中找到了一个**静态秘钥**，该秘钥可以用来验证XML文件的完整性（所有StorageZone控制器上这个值都一样）：

[![](https://p4.ssl.qhimg.com/t019b2647cdac23d1d5.png)](https://p4.ssl.qhimg.com/t019b2647cdac23d1d5.png)

> 漏洞4：XML令牌文件本身的完整性没有经过正确校验。

在研究过程中，我们尝试过在不修改签名的前提下直接编辑XML文件，结果发现攻击者并不需要计算出正确的签名值，因为如果签名不匹配，应用本身就会告诉我们正确的值：

[![](https://p3.ssl.qhimg.com/t018ab26b30837c3181.png)](https://p3.ssl.qhimg.com/t018ab26b30837c3181.png)

> 漏洞5：调试信息泄露。

此外，当我们查看负责计算签名的代码时，我们发现应用会将秘钥附加到数据尾部，然后计算整段数据的sha1哈希值。这样一来，签名很有可能会受到[哈希长度扩展攻击](https://en.wikipedia.org/wiki/Length_extension_attack)的影响，但目前我们没有时间去验证这一点。

[![](https://p3.ssl.qhimg.com/t0110997323ab74dea5.png)](https://p3.ssl.qhimg.com/t0110997323ab74dea5.png)

即使我们没有在整个攻击链条中使用这种潜在的漏洞，我们也发现XML文件容易受到[XML外部实体（XML External Entity，XXE）](https://www.owasp.org/index.php/XML_External_Entity_(XXE)_Processing)注入影响：

[![](https://p5.ssl.qhimg.com/t01bf09b90a8e30b55b.png)](https://p5.ssl.qhimg.com/t01bf09b90a8e30b55b.png)

> 漏洞6（此次攻击链中没有使用）：XML令牌文件存在XXE漏洞。

总之，我们发现令牌文件为我们提供了从ShareFile下载任意文件的另一条途径。此外，这些文件本身的完整性没有经过充分的验证，无法防范攻击者。与前面修改上传数据不同的是，如果ShareFile启用了加密存储功能，这种方法也可以**解密经过加密的文件**。



## 五、获取令牌及文件

到目前为止，我们可以将任意文件写入任意目录，如果知道文件路径我们还可以下载其他文件。然而，在实际环境中，文件路径包含随机的ID值，我们无法在有效时间内猜测出正确的值。因此，攻击者还需要找到另一种方法，枚举ShareFile上存储的文件以及对应的ID。

为完成这个任务，我们回过头来看看`unzip`功能。负责解压zip文件的部分代码如下所示。

[![](https://p1.ssl.qhimg.com/t0137eb65ddc5c625a2.png)](https://p1.ssl.qhimg.com/t0137eb65ddc5c625a2.png)

从上图可知，代码创建了一个临时目录，将归档文件解压到该目录中，临时目录名称用到了`uploadId`这个参数。由于在这里我们并没有看到任何路径验证机制，因此该操作很有可能受到路径遍历攻击影响。之前我们在上传文件的URL中看到过`uploadId`这个参数，但这个URL同样包含HMAC值，因此貌似我们无法修改这个参数：

[![](https://p4.ssl.qhimg.com/t012709896574e9a8de.png)](https://p4.ssl.qhimg.com/t012709896574e9a8de.png)

但先别放弃，我们来看一下具体实现。我们的请求首先会传入`ValidateRequest`函数，如下图所示：

[![](https://p0.ssl.qhimg.com/t011bb1654c7bc54318.png)](https://p0.ssl.qhimg.com/t011bb1654c7bc54318.png)

该函数再将请求传递给第二个验证函数：

[![](https://p0.ssl.qhimg.com/t01099b852ff0f9e7ce.png)](https://p0.ssl.qhimg.com/t01099b852ff0f9e7ce.png)

上述代码会从请求中提取处`h`参数，用来验证url中在`h`参数**之前**的所有参数。因此URL中在`h`之后的所有参数完全没有经过校验。

因此，如果我们在HMAC之后添加其他参数会出现什么情况？当我们将URL修改成如下形式：

[![](https://p4.ssl.qhimg.com/t017ab384c070234a32.png)](https://p4.ssl.qhimg.com/t017ab384c070234a32.png)

我们可以得到如下信息：

```
`{`"error":true,"errorMessage":"upload-threaded-2.aspx: ID='rsu-becc299a4b9c421ca024dec2b4de7376,foxtest' Unrecognized Upload ID.","errorCode":605`}`
```

由于`uploadid`参数被多次指定，因此IIS会将被逗号分隔开的值拼接在一起。由于程序并没有单独处理每个参数值，而是处理整个查询字符串，并且只验证在`h`参数前的那部分字符串，因此只有第一个`uploadid`会经过HMAC的校验。这种漏洞也就是所谓的[HTTP参数污染（HTTP Parameter Pollution）](https://www.owasp.org/index.php/Testing_for_HTTP_Parameter_pollution_(OTG-INPVAL-004))漏洞。

> 漏洞7：没有正确实现的URL参数校验机制（参数污染）。

再来看一下上传逻辑，当文件解压到临时目录后，代码调用了`UploadLogic.RecursiveIteratePath`函数，该函数会将所有文件递归添加到攻击者的ShareFile账户中（为了便于阅读，我删掉了某些代码）：

[![](https://p2.ssl.qhimg.com/t0187ac6ff6e655073f.png)](https://p2.ssl.qhimg.com/t0187ac6ff6e655073f.png)

为了利用这个过程，我们需要做以下几件事情：

1、在`files`目录中创建名为`rsu-becc299a4b9c421ca024dec2b4de7376`的一个目录。

2、将一个`info.txt`文件上传到这个目录。

3、创建名为`ulz-rsu-becc299a4b9c421ca024dec2b4de7376,`的一个临时目录。

4、添加指向`tokens`目录的`uploadid`参数，开始上传文件。

最开始我们在`unzip`操作中发现的目录遍历漏洞可以创建任何不存在的目录，因此我们可以利用该漏洞创建所需目录。为了利用第三个路径遍历漏洞，我们可以提交如下URL请求：

[![](https://p4.ssl.qhimg.com/t015f6a23f42ecb94c8.png)](https://p4.ssl.qhimg.com/t015f6a23f42ecb94c8.png)

**备注：这里我们使用的是`tokens_backup`目录，因为我们不想去动原始的`tokens`目录。**

我们可以看到如下成功信息：

[![](https://p0.ssl.qhimg.com/t010966adc45d957cc9.png)](https://p0.ssl.qhimg.com/t010966adc45d957cc9.png)

回到我们的ShareFile账户，现在可以看到带有可用下载令牌的数百个XML文件，这些文件都链接到ShareFile中已存储的文件。

[![](https://p2.ssl.qhimg.com/t0189f2f1513b3e4751.png)](https://p2.ssl.qhimg.com/t0189f2f1513b3e4751.png)

> 漏洞8：`uploadID`中存在路径遍历漏洞。

由于我们拥有经过授权的下载URL，因此我们可以在自己的下载令牌文件中修改相应路径来下载这些文件。

虽然这种方法能够将文件添加到攻击者的账户中，但存在一个副作用，那就是会递归地删除临时目录中的所有文件以及目录。如果我们将路径指向`persistentstorage`目录，我们也可以删掉存储在ShareFile实例中的所有文件。



## 六、总结

综合利用这些漏洞，攻击者就可能借助任何账户，通过文件上传来访问存储在ShareFile本地端StorageZone控制器中的所有文件。

根据我们的研究报告，Fox-IT于2017年7月4日向Citrix报告了如下漏洞：

1、归档文件解压中的路径遍历。

2、数据文件（`info.txt`）完整性没有经过合适的校验。

3、`info.txt`文件中的路径遍历。

4、XML令牌文件本身的完整性没有经过正确校验。

5、调试信息泄露（包含认证签名、哈希值、文件大小、网络路径信息）。

6、XML令牌文件存在XXE漏洞。

7、没有正确实现的URL参数校验机制（参数污染）。

8、`uploadID`中存在路径遍历漏洞。

Citrix及时跟进这些问题，推出缓解措施、禁用了ShareFile云组件中的`unzip`功能。虽然Fox-IT发现有多家大型组织和企业正在使用ShareFile，但并不清楚这些单位是否采用了存在漏洞配置的混合解决方案。因此，我们并不清楚具体受影响的数量，也不知这些漏洞是否已被攻击者滥用。



## 七、披露时间线
<li>
**2017年7月4日**：Fox-IT将所有漏洞提交给Citrix。</li>
<li>
**2017年7月7日**：Citrix确认第1个漏洞可以复现。</li>
<li>
**2017年7月11日**：Citrix确认大部分其他漏洞也可以复现。</li>
<li>
**2017年7月12日**：Citrix为第1个漏洞部署了缓解措施，打破整个攻击链条，并通知我们会在后面以纵深防御措施修复其他漏洞。</li>
<li>
**2017年10月31日**：Citrix为基于云端的ShareFile组件部署其他补丁。</li>
<li>
**2018年4月6日**：漏洞披露。</li>