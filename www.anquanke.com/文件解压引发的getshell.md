> 原文链接: https://www.anquanke.com//post/id/192919 


# 文件解压引发的getshell


                                阅读量   
                                **1088177**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01680a0faa934e1a53.png)](https://p0.ssl.qhimg.com/t01680a0faa934e1a53.png)



## 声明！

本文仅供学习和研究，由于传播、利用此文所提供的信息而造成的任何直接或者间接的后果及损失，均由使用者本人负责，海青实验室及文章作者不承担任何责任。

安全狗海青实验室拥有此文章的修改和解释权，如欲转载或传播，必须保证此文的完整性，包括版权声明在内的全部内容，未经海青实验室同意，不得任意修改或者增减此文章内容，不得以任何方式将其用于商业目的。

攻击者可以快速的从文件上传功能点获得一个网站服务器的权限，所以一直是红蓝对抗中的“兵家必争之地“。而随着对抗不断升级，开发人员的安全意识的不断提高，多多少少也学会了使用黑名单或者白名单等一些手段进行防御，但刁钻的攻击者，依然发现了疏忽之处。本文以两个实例，简单介绍文件解压功能导致的getshell问题。



## PHPOK CMS后台任意文件上传

首先，准备一个包含了一个PHP文件的zip文件，然后在导入模块中将zip文件上传。

[![](https://pic2.zhimg.com/v2-46a7c83ceec201136c0933580dd740a5_b.jpg)](https://pic2.zhimg.com/v2-46a7c83ceec201136c0933580dd740a5_b.jpg)

在尝试的时候发现，导入模块失败了，但是查看文件夹内容，可以发现文件已经成功被写入了。

[![](https://pic4.zhimg.com/v2-7d427ba8f59ae3d9204dd63b25891bdb_b.jpg)](https://pic4.zhimg.com/v2-7d427ba8f59ae3d9204dd63b25891bdb_b.jpg)

### 流程分析

接下来我们从代码层面来看看整个流程是怎样的。

[![](https://pic1.zhimg.com/v2-48b4cc3c0511c4e5ac0161440f98bea4_b.jpg)](https://pic1.zhimg.com/v2-48b4cc3c0511c4e5ac0161440f98bea4_b.jpg)

当我们点击导入模块时，浏览器会发送两条请求。先看第一条POST请求。根据PHPOK CMS路由分发的规则，可以定位到upload控制器中的zip方法。

[![](https://pic1.zhimg.com/v2-42675a959c3858da67299dfd0ea500d0_b.jpg)](https://pic1.zhimg.com/v2-42675a959c3858da67299dfd0ea500d0_b.jpg)

而在43行处，引入了libsupload.php文件并且调用zipfile()函数。

[![](https://pic1.zhimg.com/v2-57309b4a076659f2e6eb4ec265170d5c_b.jpg)](https://pic1.zhimg.com/v2-57309b4a076659f2e6eb4ec265170d5c_b.jpg)

在第135行处，设定了文件后缀类型为zip,由于137行处的if条件不成立，流程进入140行，调用_save()方法。继续跟进_save()方法。

[![](https://pic1.zhimg.com/v2-11543042b09fc91cbb2d0d04afa5651c_b.jpg)](https://pic1.zhimg.com/v2-11543042b09fc91cbb2d0d04afa5651c_b.jpg)

_save()方法在276行处使用file_ext()方法对传入的name参数也就是文件名进行后缀判断，而如果判断通过，则会在之后将压缩文件保存下来。跟进一下file_ext()方法。

[![](https://pic1.zhimg.com/v2-25bb71ce12b6dae17ecf5db43d084e40_b.jpg)](https://pic1.zhimg.com/v2-25bb71ce12b6dae17ecf5db43d084e40_b.jpg)

在该方法中设置了一个白名单，文件名只能是jpg,gif,png,zip中的其中一种。为什么包含zip呢？不管是程序执行到第186或者189行处，在前面就已经给这两个变量设置值为zip了，所以在白名单中自然包含了zip。目前到此为止，整个上传流程没有什么问题，并且使用了白名单来限制后缀，所以只能上传zip压缩文件。

接着再来看第二处请求：

```
admin.php?c=module&amp;f=import&amp;zipfile=_cache%2Fa9414ae41044fc5a.zip&amp;_=1570603538199
```

同样根据路由规则，可以定位到module控制器下的import方法

程序会接受到zipfile参数，是刚刚压缩包保存在缓存文件夹里的文件名。在第705行处判断了是不是存在这个压缩包，如果存在则在708行处进行解压。其中引入了libs/phpzip.php中的unzip函数进行解压。跟进unzip函数，程序实例化了ZipArchive类进行解压，而目标路径$to则是缓存文件夹。

[![](https://pic4.zhimg.com/v2-dae39a6fd9323d1f9df2b9e8c5c33067_b.jpg)](https://pic4.zhimg.com/v2-dae39a6fd9323d1f9df2b9e8c5c33067_b.jpg)

到此不难看出问题，程序将压缩包中的文件解压出来之后，并未进一步的进行判断，以至于里面包含的 PHP文件可以绕过上传文件的限制，使得原本建立的安全防御土崩瓦解。



## ZZZCMS 后台解压文件导致任意文件上传

依照上文漏洞发掘方式，同样的在zzzcms的后台中找到了同样的问题。在项目中搜索关键字unzip。就可以找到解压功能的所在点，从而进行仔细的分析。

[![](https://pic4.zhimg.com/v2-5e0809efb6a11cb825f02fc66d32261b_b.jpg)](https://pic4.zhimg.com/v2-5e0809efb6a11cb825f02fc66d32261b_b.jpg)

### 流程分析

定位到解压功能的所在之处，具体代码如下。

[![](https://pic1.zhimg.com/v2-7cf991993b6073f16ee0c44f4679fddc_b.jpg)](https://pic1.zhimg.com/v2-7cf991993b6073f16ee0c44f4679fddc_b.jpg)

由于关注点在于解压功能，因此其他的case情况不去过多深究，只需要分析unzip处是否有问题即可。可以看到unzip的功能写在了up_data()函数之中，和上文所写到的一样，在解压完毕之后并未对解压出来的文件进行检测，因此不难考虑到压缩包里隐藏一个PHP文件的方法。

在784-785行处，分别定义了解压文件的保存路径（/runtime/updata/）和压缩包文件的存放路径（/runtime/zip/）。在第801行处，使用getfiles()函数来获取指定文件夹下的文件，也就是获取/runtime/zip/下的所有zip文件。然后在第803行处判断是否存在zip文件，如果存在则将压缩包里的文件解压出来。

分析至此，自然而然的可以想到如果能在/runtime/zip/中放置一个包含了PHP文件的压缩包，就可以在网站中植入webshell。因此，需要找到一个上传点，这个上传点的要允许上传zip文件，并且可以将上传文件保存到任意目录下。在整个项目里查找，找到了一个up_load()函数满足需求，具体代码如下所示：

[![](https://pic4.zhimg.com/v2-8c60c4ec2cbdcdac1bfa7bcd07254eeb_b.jpg)](https://pic4.zhimg.com/v2-8c60c4ec2cbdcdac1bfa7bcd07254eeb_b.jpg)

在第651-652行，定义了文件上传的类型和保存的路径，然后在660行处调用upload函数来进行上传的具体操作。跟进upload查看。

[![](https://pic4.zhimg.com/v2-96ec783412718fad94c7dcf899e2b2ab_b.jpg)](https://pic4.zhimg.com/v2-96ec783412718fad94c7dcf899e2b2ab_b.jpg)

在upload函数之中，由于传入的$type值为zip，因此程序流程进入到709行处，于是zip就成为允许上传的文件类型。在718行处会对文件后缀进行对比，如果后缀名在黑名单之中，则允许上传。在第725行处调用handle_upload()函数将上传文件保存下来，继续跟进该函数。

[![](https://pic2.zhimg.com/v2-a548cc253a2207ea5e208059226aa8d1_b.jpg)](https://pic2.zhimg.com/v2-a548cc253a2207ea5e208059226aa8d1_b.jpg)

根据配置文件的设置值datefolder默认为0，当该值为0则不会再多一层以时间戳命名的文件夹，注意$folder是可控的，并且没有过滤跳转符号../就在750行处直接拼接构造了路径。紧接着covermark值默认为1，如果该文件路径已经存在则删掉原有的路径，目的是为了覆盖写入。$newname是新的文件名，由于$format的值为NULL，所以新文件名的格式是以时间戳+随机数的方式命名的。也正是因为如此，新的文件名变得不可猜测，所以无法直接上传一个webshell。而在解压功能中，新的文件名被保存成什么并不重要。

整个利用链已经十分清晰了，通过上传功能上传一个包含PHP文件的压缩包路径穿越保存到/runtime/zip/文件夹下，然后再触发解压功能，即可将webshell植入。

[![](https://pic4.zhimg.com/v2-4db2dbfbf5b0c34b334214b834ec498f_b.jpg)](https://pic4.zhimg.com/v2-4db2dbfbf5b0c34b334214b834ec498f_b.jpg)

在save.php中，当$act为upload时，调用上传文件的功能，为updata时调用解压功能。由于并没有找到相应的前端页面，而且提交表单并没有检查refere值和设置csrf_token，因此可以自己编写一个上传页面，内容如下：

[![](https://pic2.zhimg.com/v2-0b71ccc3037fbfa3dfa1fde1bde30365_b.jpg)](https://pic2.zhimg.com/v2-0b71ccc3037fbfa3dfa1fde1bde30365_b.jpg)

以GET方式设置好文件类型和保存路径，然后将zip文件上传即可。

[![](https://pic1.zhimg.com/v2-34fb8642e7b263b8c329e24365dc6260_b.jpg)](https://pic1.zhimg.com/v2-34fb8642e7b263b8c329e24365dc6260_b.jpg)

当文件上传成功，可以看到文件成功被保存在了/runtime/zip/文件夹之下。接着触发解析功能。

[![](https://pic2.zhimg.com/v2-91af6d9813f0848b8ce9cc307a6d74bd_b.jpg)](https://pic2.zhimg.com/v2-91af6d9813f0848b8ce9cc307a6d74bd_b.jpg)

可以发现文件已经被成功解压，并且保存在了/runtime/updata/文件夹之中。访问效果如下：

[![](https://pic2.zhimg.com/v2-96f946e2f6d85930dad525547af234bd_b.jpg)](https://pic2.zhimg.com/v2-96f946e2f6d85930dad525547af234bd_b.jpg)



## 总结

从上述两则实例来看，压缩包里包含着webshell颇有些特洛伊木马的味道。当程序对上传后缀限制的相当严格，例如上文提到的PHPOK CMS，已经使用白名单的机制只能上传四种后缀的文件，却依然因为对压缩文件的处理不当，导致整个防御机制的失效。在ZZZCMS中的实例，猜测开发者的本意是zip文件夹内的内容应该别可控的，但在目录穿越的加持下，超出了开发者的预期从而防御机制土崩瓦解。

那么如何防御呢？建议开发者在实现文件解压功能时考虑以下要点：

1）限制文件的扩展名（如采用白名单的方式）；

2）限制文件的名称（以较为严谨的黑名单约束文件名）；

3）限制文件的大小（以免遭受压缩包炸弹的DDoS攻击）。

因此，在开发的各个环节，都要将安全意识贯彻其中。千里之堤毁于蚁穴，也正是这种细微之处的小问题，才使得攻击者有机可乘。
