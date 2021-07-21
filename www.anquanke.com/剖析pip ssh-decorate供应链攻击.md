> 原文链接: https://www.anquanke.com//post/id/127383 


# 剖析pip ssh-decorate供应链攻击


                                阅读量   
                                **79129**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01c29358b3160e0293.jpg)](https://p4.ssl.qhimg.com/t01c29358b3160e0293.jpg)

文/图 阿里安全猎户座实验室

近日，国外媒体有安全人员爆出Python pip ssh-decorate被发现存在后门代码！对，又是pip污染。

pip是Python的开源包资源库。然而，这个开源库的管理是十分松散的。尤其在安全方面并没有严格的审核机制。一个用户只需要一个email即可注册账户，然后即可上传其源文件到pip资源中。而这个pip资源是被世界上所有python用户使用下载的。如果有人夹杂恶意代码上传了某个包，并以常见程序的名字命名，比如zip，ssh，smb，ftp。那么当有用户尝试搜索并下载使用这个名字的包时，这个用户就会中招，可谓神不知鬼不觉。这就是存在于pip中的供应链安全问题。回头看，针对pip的攻击已经并不新鲜，早在几年前就有国外研究者进行过类似实验。而真正让大家重视起来是在2017年，国内白帽子也针对pip源进行了投毒测试，结果令人震惊，各大厂商主机纷纷被感染。但是无论如何，之前我们看到的全部都是以渗透测试为目的的pip污染事件，而这次，我们看到的真正的backdoor！我们看一下其具体技术相关的内容。

ssh-decorate是一个github开源项目，其地址：[https://github.com/urigoren/ssh_decorate。其功能应该是实现类似ssh](https://github.com/urigoren/ssh_decorate%E3%80%82%E5%85%B6%E5%8A%9F%E8%83%BD%E5%BA%94%E8%AF%A5%E6%98%AF%E5%AE%9E%E7%8E%B0%E7%B1%BB%E4%BC%BCssh) client一样的功能，python实现，提供一些更友好的接口。现在这个工程已经被原作者删除干净，只有google cache中的可以看一下其之前的内容。在pypi上的ssh_decorate的地址是：[https://pypi.org/project/ssh-decorate。当前的恶意包也已经被pypi移除，目前页面也无法找到了。](https://pypi.org/project/ssh-decorate%E3%80%82%E5%BD%93%E5%89%8D%E7%9A%84%E6%81%B6%E6%84%8F%E5%8C%85%E4%B9%9F%E5%B7%B2%E7%BB%8F%E8%A2%ABpypi%E7%A7%BB%E9%99%A4%EF%BC%8C%E7%9B%AE%E5%89%8D%E9%A1%B5%E9%9D%A2%E4%B9%9F%E6%97%A0%E6%B3%95%E6%89%BE%E5%88%B0%E4%BA%86%E3%80%82)

这个backdoor的事件最早被爆出是reddit上的用户发帖，并且贴出了恶意代码片段，如图1所示。从图中可以看出，恶意代码的实现是比较直接的，没有代码加密、混淆之类的对抗手段。主要的动作就是发送ssh服务器的用户名，密码，ip地址，端口，私钥信息到远程服务器。服务器地址：[http://ssh-decorate.cf/index.php。这其中的很重要一点就是其收集了密码和私钥信息。有了这些信息，相当于盗取了ssh服务器的账户。再看这个攻击者的服务器网址，可见域名还是有很大迷惑性的，使用ssh-decorate字符串。另外，有安全研究人员通过其DNS](http://ssh-decorate.cf/index.php%E3%80%82%E8%BF%99%E5%85%B6%E4%B8%AD%E7%9A%84%E5%BE%88%E9%87%8D%E8%A6%81%E4%B8%80%E7%82%B9%E5%B0%B1%E6%98%AF%E5%85%B6%E6%94%B6%E9%9B%86%E4%BA%86%E5%AF%86%E7%A0%81%E5%92%8C%E7%A7%81%E9%92%A5%E4%BF%A1%E6%81%AF%E3%80%82%E6%9C%89%E4%BA%86%E8%BF%99%E4%BA%9B%E4%BF%A1%E6%81%AF%EF%BC%8C%E7%9B%B8%E5%BD%93%E4%BA%8E%E7%9B%97%E5%8F%96%E4%BA%86ssh%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%9A%84%E8%B4%A6%E6%88%B7%E3%80%82%E5%86%8D%E7%9C%8B%E8%BF%99%E4%B8%AA%E6%94%BB%E5%87%BB%E8%80%85%E7%9A%84%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%BD%91%E5%9D%80%EF%BC%8C%E5%8F%AF%E8%A7%81%E5%9F%9F%E5%90%8D%E8%BF%98%E6%98%AF%E6%9C%89%E5%BE%88%E5%A4%A7%E8%BF%B7%E6%83%91%E6%80%A7%E7%9A%84%EF%BC%8C%E4%BD%BF%E7%94%A8ssh-decorate%E5%AD%97%E7%AC%A6%E4%B8%B2%E3%80%82%E5%8F%A6%E5%A4%96%EF%BC%8C%E6%9C%89%E5%AE%89%E5%85%A8%E7%A0%94%E7%A9%B6%E4%BA%BA%E5%91%98%E9%80%9A%E8%BF%87%E5%85%B6DNS) Record系统发现这个域名注册时间是2018-05-08。也就是这次攻击这个域名的存活期，其实还比较短。<br>[![](https://p4.ssl.qhimg.com/t0168a45b0593408004.png)](https://p4.ssl.qhimg.com/t0168a45b0593408004.png)<br>
图1

那么，一个很重要的问题：这个pip的恶意包到底是怎么来的呢？实际上ssh-decorate这个开源包存在github和pypi都已经很久了，作者是urigoren。那么，为什么这个pypi上的包被插入了恶意代码了呢？原作者没必要这么做。终于，通过github的一个issue我们发现了原因。这个issue是一个发现恶意代码的用户质问开发者urigoren，为什么其pypi源中包含有恶意代码。这个issue已经被删除，但是可以从cache链接[https://webcache.googleusercontent.com/search?q=cache:vjUIkPX1-0EJ:https://github.com/urigoren/ssh_decorator/issues/11+&amp;cd=6&amp;hl=zh-CN&amp;ct=clnk](https://webcache.googleusercontent.com/search?q=cache:vjUIkPX1-0EJ:https://github.com/urigoren/ssh_decorator/issues/11+&amp;cd=6&amp;hl=zh-CN&amp;ct=clnk) 查看，同时，图2，图3是也是来源于这个issue的讨论的截图。<br>[![](https://p1.ssl.qhimg.com/t01a254754c8adfa178.jpg)](https://p1.ssl.qhimg.com/t01a254754c8adfa178.jpg)<br>
图2<br>[![](https://p1.ssl.qhimg.com/t01c6b4720cd25aceb6.jpg)](https://p1.ssl.qhimg.com/t01c6b4720cd25aceb6.jpg)<br>
图3

通过对话，我们得出推测：urigoren的pypi账号很可能被黑了。这样导致，攻击者利用他的账号就可以push更新包到pypi，这就造成了github是好的代码，但是pypi的包已经被污染。经过这个事情，urigoren一气之下（也许是惊吓）删除了github和pypi的所有相关repo。对于这个情况，Pypi之前已经我们提过，其安全很脆弱，其账户体系也是一样的。当然，到底是原作者使用弱密码还是pypi有其他弱点来让攻击者达到最后盗取其账户，这个我们暂时不得而知。但是，这是一种巧妙的攻击方式。黑掉一个缺乏安全意识的开发者的账户并不那么复杂，而这个开发者的背后可能掌管着世界级的开源应用的代码更新权限。这又是一个相对低成本的攻击。

通过对这个真实的供应链安全问题的分享，希望提高大家对这类安全问题的感知。供应链安全是个复杂而庞大的问题。需要不断地去重视，思考，一步一步地去解决。出于对近几年来供应链安全问题的重视，为了促进安全行业内相关方向的发展以及对此类攻击解法的探索，阿里巴巴安全部在今年专门举办了一届“软件供应链安全大赛”，赛事目前正在紧张进行中，测试赛即将打响，有兴趣的同学请移步官方网站（[https://softsec.security.alibaba.com）了解更多信息，现在加入PK还来得及！](https://softsec.security.alibaba.com%EF%BC%89%E4%BA%86%E8%A7%A3%E6%9B%B4%E5%A4%9A%E4%BF%A1%E6%81%AF%EF%BC%8C%E7%8E%B0%E5%9C%A8%E5%8A%A0%E5%85%A5PK%E8%BF%98%E6%9D%A5%E5%BE%97%E5%8F%8A%EF%BC%81)
