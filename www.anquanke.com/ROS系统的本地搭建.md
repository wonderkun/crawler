> 原文链接: https://www.anquanke.com//post/id/231474 


# ROS系统的本地搭建


                                阅读量   
                                **125951**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f8cf175fbd501405.png)](https://p3.ssl.qhimg.com/t01f8cf175fbd501405.png)



## 0x00 写在前面

[![](https://p3.ssl.qhimg.com/t010e6e743479f72c6b.png)](https://p3.ssl.qhimg.com/t010e6e743479f72c6b.png)

有关ROS系统的相关知识已经在上一篇文章中进行了阐述，在本篇文章中，将就ROS的进一步搭建方法做阐述。

**⚠️：本文中“消息代理”、“主服务器”、“Master Server”是相同的意思，可以互换。**



## 0x01 关于版本选择

目前稳定的ROS系统有三个版本可供选择

<th style="text-align: center;">ROS 系统版本号</th><th style="text-align: center;">最后支持期限</th><th style="text-align: center;">对应的Ubuntu系统</th><th style="text-align: center;">Logo</th>
|------
<td style="text-align: center;">ROS Kinetic Kame</td><td style="text-align: center;">2021年4月</td><td style="text-align: center;">Ubuntu 16.04 LTS</td><td style="text-align: center;">[![](https://p2.ssl.qhimg.com/t01320c4b41ebaf9941.png)](https://p2.ssl.qhimg.com/t01320c4b41ebaf9941.png)</td>
<td style="text-align: center;">ROS Melodic Morenia</td><td style="text-align: center;">2023年5月</td><td style="text-align: center;">Ubuntu 18.04 LTS</td><td style="text-align: center;">[![](https://p3.ssl.qhimg.com/t01b45e9165185cf0b7.png)](https://p3.ssl.qhimg.com/t01b45e9165185cf0b7.png)</td>
<td style="text-align: center;">ROS Noetic Ninjemys</td><td style="text-align: center;">2025年5月</td><td style="text-align: center;">Ubuntu 20.04 LTS</td><td style="text-align: center;">[![](https://p4.ssl.qhimg.com/t010edbe994c89e9ca4.png)](https://p4.ssl.qhimg.com/t010edbe994c89e9ca4.png)</td>

我们此处以`ROS Melodic Morenia`为例进行本地环境的搭建，选用`Ubuntu 18.04 LTS`。

⚠️：尽管实际的ROS交互并不需要任何的图形化界面，但是为了演示方便，我们此处还是选用带有用户图形界面的`Desktop`版本。



## 0x02 本地搭建ROS环境

### <a class="reference-link" name="%E9%85%8D%E7%BD%AEapt%E4%BB%93%E5%BA%93"></a>配置apt仓库

使用以下命令启用`restricted`、`universe`和`multiverse`存储库。

```
sudo add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) main universe restricted multiverse"
```

这里也可以换成阿狸云的存储库链接，但是必须是包含`restricted`、`universe`和`multiverse`的。

### <a class="reference-link" name="%E9%85%8D%E7%BD%AEsources.list"></a>配置sources.list

使用以下命令启用`ros`存储库。

```
sudo sh -c '. /etc/lsb-release &amp;&amp; echo "deb http://mirrors.sjtug.sjtu.edu.cn/ros/ubuntu/ `lsb_release -cs` main" &gt; /etc/apt/sources.list.d/ros-latest.list'
```

这里给出一些其他的镜像源以供选择：

```
🇨🇳中国科学技术大学：http://mirrors.ustc.edu.cn/ros/ubuntu/
🇨🇳清华大学：http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/
🇨🇳北京外国语大学：http://mirrors.bfsu.edu.cn/ros/ubuntu/
🇨🇳上海交通大学：http://mirrors.sjtug.sjtu.edu.cn/ros/ubuntu/
🇺🇸官方：http://packages.ros.org/ros/ubuntu
```

### <a class="reference-link" name="%E8%AE%BE%E7%BD%AEGPG%E5%AF%86%E9%92%A5"></a>设置GPG密钥

使用以下命令启用`GPG`密钥。

```
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
```

若多次超时，可以使用如下命令进行替换：

```
sudo apt-key adv --keyserver 'hkp://pgp.mit.edu:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
```

```
curl -sSL 'http://keyserver.ubuntu.com/pks/lookup?op=get&amp;search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | sudo apt-key add -
```

```
curl -sSL 'http://pgp.mit.edu/pks/lookup?op=get&amp;search=0xC1CF6E31E6BADE8868B172B4F42ED6FBAB17C654' | sudo apt-key add -
```

### <a class="reference-link" name="%E6%9B%B4%E6%96%B0%E8%BD%AF%E4%BB%B6%E5%8C%85%E5%B9%B6%E5%AE%89%E8%A3%85%E5%AE%8C%E6%95%B4%E7%89%88%E7%9A%84ROS%E8%BD%AF%E4%BB%B6%E5%8C%85"></a>更新软件包并安装完整版的ROS软件包

使用如下命令更新软件源与软件包

```
sudo apt-get update &amp;&amp; sudo apt-get upgrade
```

然后安装ROS系统(完整版)：包括ROS基本通讯协议包、`rqt`工具包、`rviz`工具、机器人通用库、`2D/3D`模拟器、导航以及`2D/3D`感知包。

```
sudo apt install ros-melodic-desktop-full
```

除了完整版我们还可以选择安装非完整版的子包
<li>桌面版(`Desktop`)：包括ROS基本通讯协议包、`rqt`工具包、`rviz`工具、机器人通用库
<pre><code class="lang-bash hljs">sudo apt install ros-melodic-desktop
</code></pre>
</li>
<li>核心版(`Core`)：包括ROS基本通讯协议包
<pre><code class="lang-bash hljs">sudo apt install ros-melodic-ros-base
</code></pre>
</li>
<li>独立版：
<pre><code class="lang-bash hljs">sudo apt install ros-melodic-PACKAGE
</code></pre>
例如：
<pre><code class="lang-bash hljs">sudo apt install ros-melodic-slam-gmapping
</code></pre>
若想知道所有的可安装独立模块，可使用以下命令查询
<pre><code class="lang-bash hljs">sudo apt search ros-melodic
</code></pre>
[![](https://p2.ssl.qhimg.com/t01e7cebfcd319b26a2.png)](https://p2.ssl.qhimg.com/t01e7cebfcd319b26a2.png)
</li>
### 初始化`rosdep`

接下来因为要与`raw.githubusercontent.com`交互获取内容以完成初始化动作，因此需要先对`host`配置进行修改

执行`sudo vi /etc/hosts`

在最后添加一行`151.101.84.133  raw.githubusercontent.com`

[![](https://p1.ssl.qhimg.com/t014e215a1ca917fa42.png)](https://p1.ssl.qhimg.com/t014e215a1ca917fa42.png)

接下来执行以下命令以完成初始化

```
sudo rosdep init
rosdep update
```

**🚫：在执行`rosdep update`时切勿使用`sudo`。**

至此，我们对于ROS环境的安装全部完成。

### <a class="reference-link" name="%E9%85%8D%E7%BD%AE%E7%8E%AF%E5%A2%83%E5%8F%98%E9%87%8F(%E9%9D%9E%E5%BF%85%E9%A1%BB)"></a>配置环境变量(非必须)

可以使用以下命令来自动的添加环境变量的配置

```
echo "source /opt/ros/melodic/setup.bash" &gt;&gt; ~/.bashrc
source ~/.bashrc
```

**⚠️：若不进行此步骤，在接下来进行测试操作以及后续构建工程时都需要执行`source /opt/ros/melodic/setup.bash`来使环境变量生效。**

### <a class="reference-link" name="%E5%AE%89%E8%A3%85%E5%BF%85%E8%A6%81%E5%B0%8F%E5%B7%A5%E5%85%B7"></a>安装必要小工具

可以使用以下命令来安装一些工具以方便我们后续构建项目。

```
sudo apt-get install python-rosinstall python-rosinstall-generator python-wstool build-essential
```



## 0x03 测试小乌龟项目【需要桌面环境】

小乌龟项目是内置在ROS系统中的用于测试的项目，此项目中同时用到了发布者-订阅者消息模式和客户端-服务端消息模式。

### 启动`Master Server`

首先，若还记得之前在”物联网协议——MQTT与ROS”一文中提到的消息代理的概念，对于ROS系统，不论是使用了哪种消息模式都需要启动一个消息代理用于将消息分发到合适的消息接收端。

那么，我们需要使用`roscore`启动一个主服务器以充当`master server`。

[![](https://p2.ssl.qhimg.com/t01e15063ec598e31d3.png)](https://p2.ssl.qhimg.com/t01e15063ec598e31d3.png)

这里我们做以下几点补充说明：
<li>
`roscore`会默认将**计算机名**作为主服务器的host，此时，ROS系统仅能用于**本地测试**。</li>
<li>可以使用环境变量来控制`roscore`的启动行为，其中，最重要的三个环境变量是：
<ul>
<li>
`ROS_ROOT`：此环境变量必须指向ROS环境的安装位置，当系统中安装了多个版本的ROS软件包时，需要使用此环境变量进行手动指定。(默认值：`/opt/ros/melodic/share/ros`)</li>
<li>
`ROS_MASTER_URI`：此环境变量必须指向ROS主服务器的完整地址，当我们想把主服务器暴露在网络中时，需要使用此环境变量进行手动指定。(默认值：(空)，建议值：`http://0.0.0.0:11311`)</li>
<li>
`PYTHONPATH`：此环境变量必须指向ROS系统所使用的Python环境位置，由于ROS系统底层的部分模块需要依赖Python，因此尽管我们可以使用其他语言构建项目，但是为了保证运行无误必须配置Python环境，ROS系统安装时已经默认一并安装了Python，当我们需要更换时需要手动指定。(默认值：`/opt/ros/melodic/lib/python2.7/dist-packages`)</li>
</ul>
</li>
1. 如果不使用`&amp;`标志符限定，默认此服务将会在前台运行，在进行接下来的测试时请务必不要关闭一开始的窗口。
### 启动`node`观察器

现在我们可以使用`rosnode`这个小工具来查看目前的ROS系统中存在哪些节点

[![](https://p2.ssl.qhimg.com/t01b463aa1a12844701.png)](https://p2.ssl.qhimg.com/t01b463aa1a12844701.png)

这个节点就是由消息代理启动的一个用于管理消息发送接收的节点，正如之前说过的，ROS系统与MQTT不同，他是一个高度集成的系统，同时支持两种消息模式。那么，`/rosout`事实上就拥有了三种属性：
- 订阅者：`/rosout`可以作为订阅者，订阅若干其他节点，用于具有多播特性的`Pub-Sub mode`。
- 发布者：`/rosout`可以作为发布者，向其他若干节点发布消息，用于具有多播特性的`Pub-Sub mode`。
- 服务者：`/rosout`可以作为服务端，提供若干服务以供其他节点发起调用，用于具有单播特性的`CS mode`。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e8df29260771483f.png)

我们可以使用`rosnode info`命令去看到其所有的订阅者、发布目标以及服务列表，此外，还能看到此节点的位置以及PID。

**⚠️：在ROS系统中，为了最高效的利用资源，当我们启动一个新节点时，默认策略会使得主服务器随机选择一个可用端口进行节点绑定，当有其他节点想要链接此节点时只需要向消息代理询问即可，这个策略尽管实现了空间解耦，但是阻碍了我们利用ROS系统进行CTF竞赛的命题，因为无法动态的进行docker的端口映射，如果有读者可以解决此问题，请在本文评论区发布评论，笔者在此感激不尽。**

### <a class="reference-link" name="%E5%90%AF%E5%8A%A8%E5%B0%8F%E4%B9%8C%E9%BE%9F%E8%8A%82%E7%82%B9%E3%80%90%E9%9C%80%E8%A6%81%E6%A1%8C%E9%9D%A2%E7%8E%AF%E5%A2%83%E3%80%91"></a>启动小乌龟节点【需要桌面环境】

接下来我们使用`rosrun turtlesim turtlesim_node`命令启动小乌龟节点

[![](https://p1.ssl.qhimg.com/t0110192f993f547833.png)](https://p1.ssl.qhimg.com/t0110192f993f547833.png)

此时或许可以发现，每次启动小乌龟节点时，小乌龟的皮肤都不相同，我们重新使用`rosnode`命令观察节点

[![](https://p3.ssl.qhimg.com/t01267a832082e6bb62.png)](https://p3.ssl.qhimg.com/t01267a832082e6bb62.png)

[![](https://p0.ssl.qhimg.com/t01b1bbc5675fc7ce71.png)](https://p0.ssl.qhimg.com/t01b1bbc5675fc7ce71.png)

我们可以发现以下几点：
- 小乌龟节点`/turtlesim`已经对`/rosout`这个节点产生了订阅关系。
<li>
`/turtlesim`同样提供了若干话题以及若干服务。</li>
那么，如果我们不想用`/turtlesim`这个节点名，ROS系统事实上提供了自定义节点名称的参数。

首先关闭小乌龟节点启动的节点或者在小乌龟节点的终端使用`Ctrl + C`来终止，之后使用命令`rosrun turtlesim turtlesim_node __name:=myturtle1`启动，启动后再次查看`node`信息：

[![](https://p2.ssl.qhimg.com/t0155dbef08c2d2dc11.png)](https://p2.ssl.qhimg.com/t0155dbef08c2d2dc11.png)

[![](https://p5.ssl.qhimg.com/t01138040992d443106.png)](https://p5.ssl.qhimg.com/t01138040992d443106.png)

可以发现，这个节点的名字已经改变了。
