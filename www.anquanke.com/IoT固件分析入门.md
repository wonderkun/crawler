
# IoT固件分析入门


                                阅读量   
                                **232039**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01c81b270a8cf94b6c.jpg)](https://p4.ssl.qhimg.com/t01c81b270a8cf94b6c.jpg)



把前段时间GitHub 上 star 了的一个项目学一遍，地址：[IoT_Sec_Tutorial](https://github.com/G4rb3n/IoT_Sec_Tutorial/)<br>
访问慢的话，gitee上也有镜像可看

**Update：感觉算是一个很不错的IoT固件分析入门教程，今天收到《路由器0day》后在路上粗略地看了下目录，除了没有涉及到硬件外，这个教程差不多把固件分析的起始工作都涉及到了（至于是不是 a bit out of date 就另当别论，不过总的来说也还好⑧）**



## 0x0准备

因为kali是刚上大学的时候装的，现在都出到2021了，我的版本还是2019，所以先升级一波

```
echo "deb http://http.kali.org/kali kali-rolling main non-free contrib" | sudo tee /etc/apt/sources.list
sudo apt update &amp;&amp; sudo apt -y full-upgrade
[ -f /var/run/reboot-required ] &amp;&amp; sudo reboot -f
```
- 更新完后可以查看一下系统版本：
```
grep VERSION /etc/os-release
```
- 更新系统时间（我的时间好像之前一直都不对orz）
```
apt-get install -y ntpdate
rm -rf etc/localtime
cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
ntpdate -u ntp.api.bz
```
<li>切换shell（为啥升级后zsh没有直接变成默认orzz）<br>
先查看系统中有几种shell：</li>
```
cat /etc/shells
```

kali自带了zsh，直接切换就行了：

```
cp -i /etc/skel/.zshrc ~/
chsh -s /bin/zsh
```

zsh配合oh-my-zsh比较好用，安装：

```
wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | sh
```

添加全路径显示：

```
gedit ~/.oh-my-zsh/themes/robbyrussell.zsh-theme
#然后把%{$fg[cyan]%}%c%{$reset_color%}的%c改为[$PWD]
```

如果想用别的桌面系统：

```
update-alternatives --config x-session-manager
```



## 0x1提取固件

```
之前用过binwalk，但大多都是在misc题目里处理压缩文件、图片啥的，没有仔细看过binwalk的命令
其实除了binwalk之外，还有其他的固件分析/提取工具，在GitHub上用“firmware analysis”之类的关键词能查到
```

给了个华硕RT-N300路由器的固件，binwalk直接提取即可。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0121083a5295d4a1c9.png)

提取出来发现没有进行加密（…16年，这也太不安全了吧orz，不过现在基本都有了

可以看到这个路由器用的是squashfs文件系统

[![](https://p0.ssl.qhimg.com/t011a97779bc8074499.png)](https://p0.ssl.qhimg.com/t011a97779bc8074499.png)

其中squashfs-root可用于分析了

```
文件系统是操作系统的重要组成部分，是操作运行的基础。不同的路由器使用的文件系统格式不尽相同。根文件系统会被打包成当前路由器所使用的文件系统格式，然后组装到固件中。路由器希望文件系统越小越好，所以这些文件系统中各种压缩格式随处可见。

Squashfs是一个只读格式的文件系统，具有超高压缩率，其压缩率最高可达34%。当系统启动后，会将文件系统保存在一个压缩过的文件系统文件中，这个文件可以使用换回的形式挂载并对其中的文件进行访问，当进程需要某些文件时，仅将对应部分的压缩文件解压缩。

Squashfs文件系统常用的压缩格式有GZIP、LZMA、LZO、XZ（LZMA2）。路由器的根文件系统通常会按照Squashfs文件系统常用压缩格式中的一种进行打包，形成一个完整的Squashfs文件系统，然后与路由器操作系统的内核一起形成更新固件。

由于squashFS可以在不需要解压的情况下直接挂载，因此有许多应用场景，例如：
1、安装Linux时用的live cd
2、小型嵌入式设备中的rootfs。rootfs一般以压缩好的形式存放在ROM中，如果开机时把整个rootfs都解压到内存里再读取，对于ROM和RAM容量一般都很小的小型嵌入式设备来说性价比太低。
```

### <a class="reference-link" name="Binwalk%E5%91%BD%E4%BB%A4%E9%80%89%E9%A1%B9"></a>Binwalk命令选项

常规选项：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e633eb25876179e4.png)

提取选项：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01fbf045bb27da9bb1.png)

Diff：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018fba7271af68356d.png)

文件签名：[![](https://p4.ssl.qhimg.com/t01e38920258b710fb7.png)](https://p4.ssl.qhimg.com/t01e38920258b710fb7.png)

熵值：[![](https://p2.ssl.qhimg.com/t01efd7c49d0ecc6da9.png)](https://p2.ssl.qhimg.com/t01efd7c49d0ecc6da9.png)

Raw Compression：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012aaecb79062835ca.png)

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E6%89%8B%E5%8A%A8%E6%8F%90%E5%8F%96%E5%9B%BA%E4%BB%B6"></a>如何手动提取固件

squashfs文件系统头部特征较多，有sqsh、hsqs、qshs、shsq、hsqt、tqsh、sqlz。我们用hexdump搜索特征在文件中的地址
<li>hexdump：一个二进制文件的查看工具，可转为OCT、DEC、HEX进制查看[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bb8a63f40b3cd129.png)
</li>
得到如下搜索结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bbc57418466a59a1.png)

hsqs位于文件的0xe20c0，用dd命令截取出固件：
- 注：dd命令中skip指定的值只能为十进制。用shell转换进制可以使用：$((BASE#NUM))
- [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a95e508fb1cb15bd.png)
得到了一个squashfs格式的文件

[![](https://p1.ssl.qhimg.com/t012bb59e163c966c30.png)](https://p1.ssl.qhimg.com/t012bb59e163c966c30.png)

用unsquashfs解压得到squashfs-root，即用binwalk提取出的同名文件。

[![](https://p1.ssl.qhimg.com/t01bb72a19abd0daf56.png)](https://p1.ssl.qhimg.com/t01bb72a19abd0daf56.png)

如果遇到binwalk之类的工具无法提取的情况，大多都是经过混淆，需要进一步处理

### <a class="reference-link" name="Binwalk%E5%A6%82%E4%BD%95%E8%BF%9B%E8%A1%8C%E6%8F%90%E5%8F%96%EF%BC%9A"></a>Binwalk如何进行提取：

通过maigc特征集与文件进行比对，但识别效率比file命令高多了<br>
特征集：[https://github.com/ReFirmLabs/binwalk/tree/62e9caa164/src/binwalk/magic](https://github.com/ReFirmLabs/binwalk/tree/62e9caa164/src/binwalk/magic)

识别过程主要使用libmagic库的4个函数：

```
magic_t magic_open(int flags);//创建并返回一个magic cookie指针。

void magic_close(magic_t cookie);//关闭magic签名数据库并释放所有使用过的资源。

const char *magic_buffer(magic_t cookie,const void *buffer,size_t len);//读取buffer中指定长度的数据并与magic签名数据库进行对比，返回对比结果描述。

Int magic_load(magic_t cookie,const char *filename);//从filename指定文件加载magic签名数据库，Binwalk把多个magic签名文件组合到一个临时文件中用于加载
```



## 0x2 静态分析

给了个从Dlink固件里提取的样本，打开发现被加密了，得爆破。

kali自带了一些关于压缩文件的工具，比如生成字典用的crunch、rsmangler，爆破用的frackzip等，这些工具用法都不难
<li>crunch:[Kali使用crunch生成密码字典 – 青檬小栈 ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://bystart.cn/index.php/17/linux/07)
</li>
直接用frackzip破解，（根据教程的提示）得到密码beUT9Z

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011cf91e156712600b.png)

解压得到以下文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eb1cb697197a10ba.png)
- .mbn：高通的一套用于加载网络环境的文件（modem software configuration）
- .yaffs2：针对NAND芯片设计的嵌入式文件系统，可用unyaffs提取
unyaffs提取yaffs2

核心应该是2K-mdm-image-mdm9625.yaffs2，不确定的话可以把三个.yaffs2都提取了（然后就该复习一下嵌入式系统的目录结构了）

[![](https://p0.ssl.qhimg.com/t01442233934b52f344.png)](https://p0.ssl.qhimg.com/t01442233934b52f344.png)

接下来查看配置文件，有可能从配置文件中发现敏感信息

[![](https://p4.ssl.qhimg.com/t017c050f048bad9d06.png)](https://p4.ssl.qhimg.com/t017c050f048bad9d06.png)

> 其中的inadyn-mt.conf文件引起了我们注意，这是no-ip应用的配置文件，no-ip就是一个相当于花生壳的东西，可以申请动态域名

cat 一看，果然no-ip的用户名和密码都出现了（这么明显真的难以置信）

接下来使用firmwalker来自动化遍历

> Firmwalker:
A simple bash script for searching the extracted or mounted firmware file system.
It will search through the extracted or mounted firmware file system for things of interest such as:
<ul>
- etc/shadow and etc/passwd
- list out the etc/ssl directory
- search for SSL related files such as .pem, .crt, etc.
- search for configuration files
- look for script files
- search for other .bin files
- look for keywords such as admin, password, remote, etc.
- search for common web servers used on IoT devices
- search for common binaries such as ssh, tftp, dropbear, etc.
- search for URLs, email addresses and IP addresses
- Experimental support for making calls to the Shodan API using the Shodan CLI
</ul>
（其实就相当于一个遍历查找后缀、内容的批处理脚本）

使用脚本获得所有可能可以利用的文件（建议进入脚本目录执行）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0165c7f95dd740069e.png)

除了配置文件外，分析存在风险的二进制程序也很重要。

在etc/init.d目录下存放启动时运行的程序和脚本，其中有一个叫start_appmgr，mgr一般指固件的主控。查看脚本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013bfd0caf7b4c9595.png)

把appmgr拖到ida[![](https://p3.ssl.qhimg.com/t01065f98787b192c39.png)](https://p3.ssl.qhimg.com/t01065f98787b192c39.png)

凭借一点点pwn的经验，我们发现了一个backdoor[![](https://p5.ssl.qhimg.com/t016658bcc929373872.png)](https://p5.ssl.qhimg.com/t016658bcc929373872.png)

这个漏洞被收录到CVE-2016-10178：[Multiple vulnerabilities found in the Dlink DWR-932B (backdoor, backdoor accounts, weak WPS, RCE …) – IT Security Research by Pierre (pierrekim.github.io)](https://pierrekim.github.io/blog/2016-09-28-dlink-dwr-932b-lte-routers-vulnerabilities.html)

即向192.168.1.1:39889发送HELODBG可以直接getshell（不太清楚为啥是39889端口，静态看了好久没看出来，~~猜测是跟下图和label_66有关~~）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01096d334cb745ebbe.png)

update:用Ghidra搜到了[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0109c3d3067c72ffd2.png)

这个漏洞确实明显2333

这个固件还有好几个漏洞，太拉了吧Orz…



## 0x3 动态分析

### <a class="reference-link" name="QEMU%E5%92%8CFirmadyne"></a>QEMU和Firmadyne

QEMU这个模拟器想必都不陌生，一个近乎能够模拟所有硬件设备的软件；倒是第一次听说Firmadyne这个工具，查了一下是一个基于QEMU的分析平台，包含模拟、固件提取、调试等功能，但似乎支持的硬件设备较少？orz

### <a class="reference-link" name="%E9%83%A8%E7%BD%B2Firmadyne"></a>部署Firmadyne

```
Tutorial里用的是attifyti提供的Ubuntu 14（因为作者说部署这玩意太麻烦了），但Firmadyne的作者在项目的某个issue里说了句“Ubuntu 14 也太早了”之类的话，于是打算自己部署一下
Also，如果想用直接用attifyti的AttifyOS，https://github.com/adi0x90/attifyos，目前的系统基于Ubuntu18.04，官方的下载地址在谷歌网盘
```

**<a class="reference-link" name="%E5%87%86%E5%A4%87"></a>准备**

因为涉及到GitHub上一些项目的下载，网络不太好的话可能需要一些帮助：

```
clash on kali:
下载clash并运行：https://github.com/Dreamacro/clash/releases
导入节点：wget -O ~/.config/clash/config.yaml  clash_url

配置代理：
gsettings set org.gnome.system.proxy mode 'manual'
gsettings set org.gnome.system.proxy.http port 7890
gsettings set org.gnome.system.proxy.http host '127.0.0.1'
gsettings set org.gnome.system.proxy.socks port 7891
gsettings set org.gnome.system.proxy.socks host '127.0.0.1'
gsettings set org.gnome.system.proxy ignore-hosts "['localhost', '127.0.0.0/8', '::1']"\

进行配置，访问：
http://clash.razord.top/
```

** 注：以下绕了好多弯，最后也没成功，用了AttifyOS 😅😅😅😅😅

**<a class="reference-link" name="%E3%80%90%E6%96%B9%E6%A1%881%E3%80%91%E5%AE%89%E8%A3%85Firmadyne"></a>【方案1】安装Firmadyne**

```
apt-get install qemu-system-arm qemu-system-mips qemu-system-x86 qemu-utils
apt-get install busybox-static fakeroot git dmsetup kpartx netcat-openbsd nmap python-psycopg2 python3-psycopg2 snmp uml-utilities util-linux vlan
git clone --recursive https://github.com/firmadyne/firmadyne.git
cd ./firmadyne
./download.sh
```

配置Postgresql：

```
# 安装数据库
sudo apt-get install postgresql
# 创建用户,注意要设置密码为 firmadyne
sudo -u postgres createuser -P firmadyne
# 创建数据库
sudo -u postgres createdb -O firmadyne firmware
# 初始化数据库
sudo -u postgres psql -d firmware &lt; ./firmadyne/database/schema
```

如果出现如下错误

> could not connect to database template1: could not connect to server: No such file or directory.
Is the server running locally and accepting
connections on Unix domain socket “var/run/postgresql/.s.PGSQL.5432”?

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e62423431e566995.png)

有可能是没有初始化数据库（至少我是因为这个），用如下方法解决：

```
# 设置postgres用户的密码
passwd postgres

# 创建postgresql的文件夹
sudo mkdir /data
sudo chmod o+w /data
su - postgres
mkdir /data/postgresql
mkdir /data/postgresql/data

# postgres用户初始化数据库
/usr/lib/postgresql/13/bin/initdb -D /data/postgresql/data

# 启动数据库
/usr/lib/postgresql/13/bin/pg_ctl -D /data/postgresql/data -l logfile start

#查看是否监听了端口(结果应类似下图)
netstat -nlp |grep 5432

参考：https://www.cnblogs.com/0x200/p/14026460.html
```

[![](https://p4.ssl.qhimg.com/t0114d62955e2fbf5bf.png)](https://p4.ssl.qhimg.com/t0114d62955e2fbf5bf.png)

接下来应该就能按照官方的Usage来使用了（没试）：[firmadyne: Platform for emulation and dynamic analysis of Linux-based firmware ](https://github.com/firmadyne/firmadyne#usage)

**[firmware-analysis-plus](https://github.com/liyansong2018/firmware-analysis-plus)**

因为用Firmadyne直接进行调试比较麻烦，所以用了FAP这个项目。

这是个国人写的中文项目，没啥好说的：[liyansong2018/firmware-analysis-plus: 开源固件仿真平台，使用 firmadyne 一键模拟固件 (github.com)](https://github.com/liyansong2018/firmware-analysis-plus)

安装作者提供的binwalk的时候一直报错(kali2021 &amp; ubuntu18 both)，导致一直卡在提取固件的步骤（emmmm哪位大哥部署成功后教我一下)

[![](https://p1.ssl.qhimg.com/t0183cee528f432f3af.png)](https://p1.ssl.qhimg.com/t0183cee528f432f3af.png)

对此提了个issue

**<a class="reference-link" name="%E3%80%90%E6%96%B9%E6%A1%883%E3%80%91AttifyOS"></a>【方案3】AttifyOS**

这个方法比较稳，自己部署也太折磨人了（外加考试周给娃弄傻了）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a5ac0650627afe9f.png)

**注：密码是attify**

### <a class="reference-link" name="%E6%A8%A1%E6%8B%9F%E6%89%A7%E8%A1%8C%E5%9B%BA%E4%BB%B6"></a>模拟执行固件

模拟固件运行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015c2d05389e996651.png)通过192.168.0.50即可访问固件

### <a class="reference-link" name="%E8%B0%83%E8%AF%95%E5%9B%BA%E4%BB%B6"></a>调试固件

这个部分用到了Damn Vulnerable Router Firmware这个项目，大小400M+，建议上gitee clone

安装以下工具：

```
sudo apt install gdb-multiarch
wget -q -O- https://github.com/hugsy/gef/raw/master/scripts/gef.sh | sh
sudo pip3 install capstone unicorn keystone-engine
```

进入DVRF/Firmware/，用binwalk提取DVRF_v03.bin

[![](https://p2.ssl.qhimg.com/t0124abb8e841155eb8.png)](https://p2.ssl.qhimg.com/t0124abb8e841155eb8.png)

提取出来的目录里有个文件夹pwnable，里面存放着漏洞程序示例，选取stack_bof_01程序进行实验，程序的源代码可以在DVRF/Pwnable Source/Intro/里查看

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e7ffdafa852bc991.png)

首先用reasdelf查看程序架构

![![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010aa0070ac310bdba.png)

（顺手试了一下checksec，这里居然有装😀）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e443cd57299643eb.png)

拷贝qwmu-mipsel-static到固件根目录：

```
cp (which qemu-mipsel-static) .
```

用qemu虚拟运行stack_bof_01：

[![](https://p0.ssl.qhimg.com/t016aab6cf915d13f97.png)](https://p0.ssl.qhimg.com/t016aab6cf915d13f97.png)

以调试的方式启动程序，并在1234端口进行监听：

```
sudo chroot . ./qemu-mipsel-static -g 1234 ./pwnable/Intro/stack_bof_01
```

打开一个新的shell，运行以下命令：

```
gdb-multiarch pwnable/Intro/stack_bof_01

# 设置架构
set architecture mips

#设置调试端口
target remote 127.0.0.1:1234
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fca001d4e0765cfe.png)

创建trash触发溢出：

```
pattern create 300
```

带上它重新进行调试

gdb attach后继续让程序运行，触发vul

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e847f5d778e84c20.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0174eb0892a9c09b29.png)

接下来就直接ret2system，但经过尝试后发现，如果直接把跳转地址设置为后门函数dat_shell的起始地址0x400950会触发异常

查看函数汇编代码（MIPS…看不懂的话可以边看边学一波，[MIPS 通用寄存器_flyingqr的专栏-CSDN博客_mips寄存器](https://blog.csdn.net/flyingqr/article/details/7073088)；[MIPS汇编指令集 – 深海之炎 – 博客园 ](https://www.cnblogs.com/glodears/p/9762615.html)；[MIPS的汇编指令 · 语雀 ](https://www.yuque.com/liyanfu/mq65pb/bv7xb5)）

[![](https://p2.ssl.qhimg.com/t01025df0052effbf01.png)](https://p2.ssl.qhimg.com/t01025df0052effbf01.png)

调试中发现，当执行到0x400970时，gp寄存器指向了不可访问的地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0180d0145eb43c0654.png)

而gp的值是由上一条指令得到的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011b4aaf351baf9d54.png)

本来执行后v0要指向 指向__DT_MIPS_BASE_ADDRESS的指针

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c6a55c6f52789792.png)

简单来说就是强行跳转到backdoor之后，因为t9（默认在运行中指向当前函数的起始地址）没有发生改变，导致在执行0x400970时产生异常访问

但可以发现（其实是按照exp来推…）main函数中的gp在-0x7fe4后刚好指向PTR__DT_MIPS_BASE_ADDRESS*（猜测原因是源代码中后门函数在main函数后面且没有被调用，导致编译时认为main函数和后门函数的 gp和表的偏移 相等）

于是得到[![](https://p2.ssl.qhimg.com/t014fa4772501d98391.png)](https://p2.ssl.qhimg.com/t014fa4772501d98391.png)

update：

main函数中[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0109943e2404e46811.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013071359a2f718e81.png)

所以gp在函数执行完毕后依旧指向的是基地址表

**感觉对于mips程序的分析，Ghidra比IDA好用些**

从这题也能看出mips和x86、x64的不同之处，**除了这种特殊情况外，大多数情况下还是应该寻找gadget来进行跳转改变t9寄存器**

**这一节就到这，DVRF这个项目还设计了一些别的漏洞程序可以再进行分析**



## 0x4 解密固件

访问dlink的ftp服务器获得几个DIR-882的固件（图中选中的文件），时间跨度为2017~2020年

```
ftp://ftp2.dlink.com/PRODUCTS/DIR-882/REVA/
```

[![](https://p3.ssl.qhimg.com/t019c49a4fd6d5b601a.png)](https://p3.ssl.qhimg.com/t019c49a4fd6d5b601a.png)

解压得到固件和对应的版本说明

[![](https://p3.ssl.qhimg.com/t01aed6810f38da3a12.png)](https://p3.ssl.qhimg.com/t01aed6810f38da3a12.png)

### <a class="reference-link" name="%E5%8A%A0%E5%AF%86%E5%9B%BA%E4%BB%B6%E5%8F%91%E5%B8%83%E6%96%B9%E6%A1%88"></a>加密固件发布方案

一般来说，有三种发布固件的方案
<li>出厂时未加密，解密例程在高版本固件v1.1中给出，为后续的加密固件做准备<br>
对于这个方案，我们可以通过解密v1.1来获得解密例程</li>
<li>出厂时的固件已经加密，供应商决定更改高版本固件的加密方式，并发布了包含解密例程的未加密中间版本v1.2<br>
这一方案与上面那个类似</li>
<li>出厂时的固件已经加密，供应商决定更改高版本固件的加密方式，并发布了包含解密例程的使用原加密方式加密的过渡版本v1.3<br>
这种方案对获取解密例程的难度较大，可从硬件中直接提取固件或对发布的v1.3进行分析</li>
DIR-882的固件发布方案为第一种，示意图如下[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0124031f12b470eaad.png)

**虽然个人认为第三种方案才是较为常见的，但教程中并没有讲到。猜测除了从硬件中提取外，还可以通过模拟器模拟然后进行patch或拿头还原**

### <a class="reference-link" name="%E8%A7%A3%E5%AF%86%E8%BF%87%E7%A8%8B"></a>解密过程

用binwalk分析最新和最早的两个固件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e0d0054d7ec4e821.png)

经过binwalk分析，FW104B02正是存在解密程序的中间版本（从文件名也能看出）

> 对于判断固件是否被加密/混淆还可以使用之前提到的binwalk -E 来查看文件各个区域的熵值

提取该固件

```
binwalk -eM DIR882A1_FW104B02_Middle_FW_Unencrypt.bin
```

在最终目录下搜索找到imgdecrypt，从名字看出是下个版本固件的解密例程

[![](https://p1.ssl.qhimg.com/t01c4b02482c44ca941.png)](https://p1.ssl.qhimg.com/t01c4b02482c44ca941.png)

可以静态分析程序的解密算法，也可以直接运行程序来对加密固件进行解密。

在本地运行时依旧需要借助qemu-mipsel-static模拟器，使用方法和上一节的模拟过程类似，不表。

利用imgdecrypt还可以还原出ftp服务器上提供的最新的固件，所以可能后续版本和Dlink其它型号的路由器也能用这个程序还原固件？Orz



## 0x5 修复固件运行环境

有一些固件因为硬件依赖等原因导致qemu和firmadyne之类的软件无法正确模拟

比如下面这个

> <pre><code class="hljs cpp">ftp://ftp2.dlink.com/PRODUCTS/DIR-605L/REVA/DIR-605L_FIRMWARE_1.13.ZIP
</code></pre>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0141e2e3f5295b732c.png)

> 模拟固件运行的实质其实就是把固件的Web程序跑起来，而模拟失败则说明Web程序运行出错了，我们接下来就要看看Web程序报错的原因以及如何修复运行环境。

### <a class="reference-link" name="%E5%B0%9D%E8%AF%95%E8%BF%90%E8%A1%8C%E5%9B%BA%E4%BB%B6"></a>尝试运行固件

首先binwalk提取固件，进入文件系统目录squashfs-root-0

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0130700746396af066.png)

找到web服务程序Boa

> Boa程序是一个轻量级的web服务器程序，常见于嵌入式系统中。dlink就是在boa开源代码的基础上新增了很多功能接口以实现路由器上的不同功能。boa程序的路径为/bin/boa，同时我们发现在/etc/boa路径下还有个boa的密码配置文件，我们可以直接获取到boa加密后的密码。

用qemu-mips-static运行，结果产生了段错误

> mips 是32位大端字节序
mipsel 是32位小端字节序

[![](https://p0.ssl.qhimg.com/t015a28827c7ecf388c.png)](https://p0.ssl.qhimg.com/t015a28827c7ecf388c.png)

### <a class="reference-link" name="%E5%88%86%E6%9E%90%E9%94%99%E8%AF%AF%E5%B9%B6%E4%BF%AE%E5%A4%8D"></a>分析错误并修复

> 注：APMIB 是个Realtek的玩意（原来realtek还有做路由器相关的东西…）
<ul>
<li>apmib_init(), 從 flash 讀出 mib 值寫入 RAM —[Realtek apmib library @ 邱小新の工作筆記 ](https://jyhshin.pixnet.net/blog/post/47162002)
</li>
</ul>
有些CVE（如CVE-2019-19823）就跟APMIB有关 —[TOTOLINK and other Realtek SDK based routers – full takeover (sploit.tech)](https://sploit.tech/2019/12/16/Realtek-TOTOLINK.html)
MIB：management information base，与SNMP有关，可在维基里进一步了解：[Management information base – Wikipedia](https://en.wikipedia.org/wiki/Management_information_base)

由于没有flash，导致读mib失败

拖到反编译工具中分析。先定位到字符串“Initialize AP MIB failed!”的位置。注意到在输出这个字符串前有个调用APMIB初始化的跳转，在此下断点，IDA远程调试

QEMU的远程调试不需要gdbserver，-g 指定端口，ida 远程调试选项指定相应端口就行[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01beb64b576fc9b3fb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01724a4b256570edea.png)

简单调试后发现，程序进入APMIB初始化函数后将返回值赋给v0，返回后对返回值进行判断。（跟着教程做完后，发现其实用静态分析看的就很明显，但多调试总是没有坏处的嘛）

跳转回去的位置在这：[![](https://p2.ssl.qhimg.com/t01184dde07ba25e6e4.png)](https://p2.ssl.qhimg.com/t01184dde07ba25e6e4.png)

我们先试试看把原来的跳转patch一下能不能运行正常固件boa。

有以下两个可行方案：
<li>hxd（或其他二进制编辑器），把benz（0x14，不为0跳转）改为beqz（0x10，为0跳转）<br>
这个方法比较直接，定位到指令后把0x14改为0x10即可</li>
1. Ghidra，把bne改为beq（Ghidra中反编译出的原指令为bne）- **如何用Ghidra进行patch并保存：**<li>下载python脚本[ghidra_SavePatch](https://github.com/schlafwandler/ghidra_SavePatch) 并放到Ghidra存放python脚本的目录（找不到目录的话，如图）。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f72b3f031417bad3.png)
</li>
1. 按照下图导入脚本。
<li>patch[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014fe1eaa03828f495.png)
</li>
1. 光标放在更改的指令，在script manager里运行脚本。
参考：[Patching Binaries With Ghidra – RangeForce](https://materials.rangeforce.com/tutorial/2020/04/12/Patching-Binaries/)
- **不用ida的原因：**
把patch保存到文件中时，发现报错，稍微搜了一下，依然不知道是啥原因orz

> 418228: has no file mapping (original: 14 patched: 10)…skipping…

再次运行试试，发现又报错了：[![](https://p0.ssl.qhimg.com/t010fd8cf5d487d49e0.png)](https://p0.ssl.qhimg.com/t010fd8cf5d487d49e0.png)

再放到Ghidra里分析，依旧通过字符串定位错误触发点。[![](https://p1.ssl.qhimg.com/t0123dd146d40794833.png)](https://p1.ssl.qhimg.com/t0123dd146d40794833.png)

两个函数（调用的地方位于websAspInit）里的报错由open函数造成（图为create_chklist_file()，但两个报错类似，均为一开始打开某个文件出错）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eca5220cf8b5e85b.png)

用IDA调试发现报错后仍然继续运行，异常发生在执行apmib_get()时：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0199811c8468fbadf8.png)

具体在0x4084c9b0时，把[0+v0]里的值赋给v1，而0x1001明显是一个访问不了的地址

[![](https://p4.ssl.qhimg.com/t01d29cab1ca9c3811a.png)](https://p4.ssl.qhimg.com/t01d29cab1ca9c3811a.png)

[![](https://p2.ssl.qhimg.com/t012580bbd39adb5928.png)](https://p2.ssl.qhimg.com/t012580bbd39adb5928.png)

查一下apmib_get是干啥的。似乎是用来获取硬件配置信息，但我们要想让固件跑起来可以不需要这个。那么直接把获得apmib_get入口后的跳转语句nop掉

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016177bde69979eced.png)

重新尝试运行[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01efcf4ef930d5c9e1.png)

[![](https://p4.ssl.qhimg.com/t01ce44bd8b44d4f80f.png)](https://p4.ssl.qhimg.com/t01ce44bd8b44d4f80f.png)

固件会一直尝试朝 ioctl（设备驱动的控制接口）发送0x89f0（应该是一个SIOCDEVPRIVATE），我们模拟的固件并不支持，但没啥大影响。（用Google搜一下“Unsupported ioctl: cmd=0x89f0”可以找到一些蛮有意思的东西2333）

> 关于ioctl：[ioctl()函数详解_shanshanpt的专栏-CSDN博客](https://blog.csdn.net/shanshanpt/article/details/19897897)

查看报错的页面（用vim看代码舒服一些），嗯，前端的东西：

[![](https://p2.ssl.qhimg.com/t01baa89f0b103550fd.png)](https://p2.ssl.qhimg.com/t01baa89f0b103550fd.png)

从文件名可以猜到是个跟路由器界面语言选择有关的文件。

文件不长，注意到有个函数跟语言和硬件有关：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012155c596f8927034.png)

那么我们可以不让它运行到这个页面。

查找调用了*LangSelect.asp的页面，发现只有一个first.asp

[![](https://p1.ssl.qhimg.com/t0167736fea3ecaaa4c.png)](https://p1.ssl.qhimg.com/t0167736fea3ecaaa4c.png)

[![](https://p0.ssl.qhimg.com/t012063767e7338f4d8.png)](https://p0.ssl.qhimg.com/t012063767e7338f4d8.png)

直接修改，重新运行完事[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019f4de40f45c4ca8f.png)

> 这个固件成功运行后可以顺便看一看这个洞： [（CVE-2018-20057）D-Link DIR-619L&amp;605L 命令注入漏洞 – Wiki ](https://wiki.96.mk/IOT%E5%AE%89%E5%85%A8/D-Link/%EF%BC%88CVE-2018-20057%EF%BC%89D-Link%20DIR-619L%26605L%20%E5%91%BD%E4%BB%A4%E6%B3%A8%E5%85%A5%E6%BC%8F%E6%B4%9E/) ，直接用了后门

这节的错误解决方法均通过修改指令，《路由器0day》书中的方法是伪造.so来劫持函数，也值得一学：[分析固件第一步](https://p1kk.github.io/2020/04/15/%E8%B7%AF%E7%94%B1%E5%99%A8/%E8%B7%AF%E7%94%B1%E5%88%86%E6%9E%90/)



## 结束

纯初学者，如果有啥地方写的不到位或者出错了，还请指出<br>
以上
