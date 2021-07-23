> 原文链接: https://www.anquanke.com//post/id/86350 


# 【权威报告】Petya勒索蠕虫完全分析报告


                                阅读量   
                                **155535**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01c4d5650ab7d356c0.png)](https://p2.ssl.qhimg.com/t01c4d5650ab7d356c0.png)

**前言**

2017年6月27日晚，乌克兰、俄罗斯、印度、西班牙、法国、英国以及欧洲多国遭受大规模Petya勒索病毒袭击，该病毒远程锁定设备，然后索要赎金。其中，乌克兰地区受灾最为严重，政府、银行、电力系统、通讯系统、企业以及机场都不同程度的受到了影响，包括首都基辅的鲍里斯波尔国际机场（Boryspil International Airport）、乌克兰国家储蓄银行（Oschadbank）、船舶公司（AP Moller-Maersk）、俄罗斯石油公司（Rosneft）和乌克兰一些商业银行以及部分私人公司、零售企业和政府系统都遭到了攻击。

此次黑客使用的是Petya勒索病毒的变种，使用的传播攻击形式和WannaCry类似，但该病毒除了使用了永恒之蓝（MS17-010）漏洞，还罕见的使用了黑客的横向渗透攻击技术。在勒索技术方面与WannaCry等勒索软件不同之处在于，Petya木马主要通过加密硬盘驱动器主文件表（MFT），使主引导记录（MBR）不可操作，通过占用物理磁盘上的文件名、大小和位置的信息来限制对完整系统的访问，从而让电脑无法启动，故而其影响更加严重。如果想要恢复，需要支付价值相当于300美元的比特币。

由于这次攻击有很强的定向性，所以目前欧洲被感染的受害者较多。目前国内感染量较少，但是考虑到其横向攻击传播能力，未来存在较高风险在国内传播。



**Petya老样本简介**

2016年4月，敲诈勒索类木马Petya被安全厂商曝光，被称作是第一个将敲诈和修改MBR合二为一的恶意木马。木马Petya的主要特点是会先修改系统MBR引导扇区，强制重启后执行MBR引导扇区中的恶意代码，加密受害者硬盘数据后显示敲诈信息，并通过Tor匿名网络索取比特币。

Petya与其他流行的勒索软件的不同点在于，Petya不是逐个加密文件，而是通过攻击磁盘上的低级结构来拒绝用户访问完整的系统。这个敲诈勒索木马的作者不仅创建了自己的引导加载程序，还创建了一个32个扇区长的小内核。

Petya的木马释放器会将恶意代码写入磁盘的开头。被感染的系统的主引导记录（MBR）将被加载一个小型恶意内核的自定义引导加载程序覆盖，然后该内核会进一步加密。 Petya的敲诈信息显示其加密了整个磁盘，但这只是木马作者放出的烟雾弹，事实上，Petya只是加密了主文件表（MFT），使文件系统不可读，来拒绝用户访问完整的系统。

[![](https://p1.ssl.qhimg.com/t011691e7842f6d5e44.jpg)](https://p1.ssl.qhimg.com/t011691e7842f6d5e44.jpg)

图 1 Petya的敲诈信息



**Petya新样本详细介绍 **

病毒样本类型为DLL，有一个导出序号为1的函数。当这个函数被调用时，首先尝试提升当前进程的权限并设置标记，查找是否有指定的安全软件，后面会根据是否存在指定的安全软件跳过相应的流程。绕过安全软件的行为监控。

接下来修改磁盘的MBR，并将生成的Key，IV，比特币支付地址以及用户序列号写入磁盘的固定扇区。然后创建计划任务于1小时后重启。遍历局域网可以连通的ip列表，用于后续的局域网攻击。释放并执行抓取密码的进程，释放psexec进程用于后续执行远程命令。对系统的网络资源列表进行过滤，筛选本地保存的凭据，使用保存的凭据连接，成功后执行远程命令，进行局域网感染。

下一步生成随机ip，连接445端口进行永恒之蓝漏洞攻击。然后遍历磁盘，对指定扩展名的文件进行加密。执行完所有流程后，清除日志并强行重启。

[![](https://p5.ssl.qhimg.com/t011a0f942242872c14.png)](https://p5.ssl.qhimg.com/t011a0f942242872c14.png)

图 2总体流程图

**Petya勒索蠕虫感染传播趋势分析**

自6月27日在欧洲爆发的起，Petya勒索病毒在短时间内袭击了多国。

根据360互联网安全中心的监测，对每一个小时的远程攻击进程的主防拦截进行了统计。从6月28号0点至6月28日晚上7点整，平均每小时攻击峰值在5000次以内。上午10点攻击拦截达到最高峰，后缓慢波动，在14点达到一个小高峰，然后攻击频率开始缓慢下降。由此可见，Petya的攻击趋势在国内并不呈现几何级增长的趋势，而是缓慢下降的，并不具备进一步泛滥的趋势。

[![](https://p0.ssl.qhimg.com/t01ee8504396eb8a7c4.jpg)](https://p0.ssl.qhimg.com/t01ee8504396eb8a7c4.jpg)

图 3 攻击频率



除乌克兰、俄罗斯、印度、西班牙、法国、英国以及欧洲多国遭受大规模的Petya攻击外，我国也遭受了同样的攻击。针对我国的攻击，主要集中在北京、上海、广州、深圳、香港等大城市，根据360互联网安全中心的监测，在全中国八十多个城市拦截到了攻击。

<br>

**Petya横向移动及传播技术分析 **

**1、提升权限，设置执行标记**

首先，Petya病毒会尝试提升当前进程的3种权限：SeShutdownPrivilege、SeDebugPrivilege和SeTcbPrivilege，根据是否成功设置标记，后面执行相应的流程时会判断此标记，以防没有权限时系统报错。

[![](https://p4.ssl.qhimg.com/t01dee9763d1ad5aad2.jpg)](https://p4.ssl.qhimg.com/t01dee9763d1ad5aad2.jpg)

然后，通过CreateToolhelp32Snapshot枚举系统进程，判断是否有指定的安全软件，并设置标记。

[![](https://p3.ssl.qhimg.com/t013b048c1aae006e5e.jpg)](https://p3.ssl.qhimg.com/t013b048c1aae006e5e.jpg)

枚举过程中，通过将进程名称进行异或计算得出一个值，将该值与预设的值进行比较，此处病毒是在寻找特定名称的进程，通过对算法进行逆向还原，我们找出预设值对应的进程名称：

[![](https://p5.ssl.qhimg.com/t01d1cbcbdc04a9fc08.png)](https://p5.ssl.qhimg.com/t01d1cbcbdc04a9fc08.png)

当存在NS.exe(诺顿)或ccSvcHst.exe(诺顿)进程时，不执行漏洞感染流程。

当存在avp.exe(卡巴斯基)进程时，不执行MBR感染流程。



**2、MBR修改**

获取分区类型，当为MBR格式时执行修改MBR流程。

[![](https://p4.ssl.qhimg.com/t012af15df86be5802d.jpg)](https://p4.ssl.qhimg.com/t012af15df86be5802d.jpg)

随后，Petya将修改机器的MBR，具体流程如下：

1）通过微软的CryptoAPI生成长度为 60 字节的随机数

[![](https://p5.ssl.qhimg.com/t01fb4dc8f87eae85d3.jpg)](https://p5.ssl.qhimg.com/t01fb4dc8f87eae85d3.jpg)

对生成的随机数对58进行取模，取模后的值作为下述数组的索引

123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz，生成勒索界面显示的序列号

2）将病毒内置的MBR写入，长度为0x13个扇区

[![](https://p4.ssl.qhimg.com/t0195de1bdeb02595bd.jpg)](https://p4.ssl.qhimg.com/t0195de1bdeb02595bd.jpg)

3）将随机生成的key，IV，硬编码的比特币支付地址以及用户序列号写入磁盘第0x20个扇区

[![](https://p0.ssl.qhimg.com/t01c143b015861baed9.jpg)](https://p0.ssl.qhimg.com/t01c143b015861baed9.jpg)

**<br>**

**3、设置重启计划任务**

创建计划任务，设定当前时间1小时后重启计算机。

[![](https://p4.ssl.qhimg.com/t01537464a7f882e620.jpg)](https://p4.ssl.qhimg.com/t01537464a7f882e620.jpg)

[![](https://p5.ssl.qhimg.com/t019be48c8cb39a4c82.jpg)](https://p5.ssl.qhimg.com/t019be48c8cb39a4c82.jpg)

重启之后将执行病毒的MBR，加密扇区。

**<br>**

**4、遍历IP**

首先，Petya检查被感染的机器是否为Server或者域控服务器

[![](https://p2.ssl.qhimg.com/t01e3da2e328decaa7d.jpg)](https://p2.ssl.qhimg.com/t01e3da2e328decaa7d.jpg)

当检测到主机为服务器或者域控时，会枚举该主机DHCP已分配的IP信息，保存在列表中用于网络攻击。

[![](https://p4.ssl.qhimg.com/t018fff7c56ce57b21b.jpg)](https://p4.ssl.qhimg.com/t018fff7c56ce57b21b.jpg)

<br>

**5、释放并运行资源**

进程首先从资源中解压缩ID为1的资源，在系统的%TEMP%目录下生成一个临时文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017d7ca3d0d0fdaaf4.jpg)

随后程序启动线程尝试连接特定的命名管道并读取数据，随后将该临时文件作为进程启动，并且等待1分钟。

[![](https://p2.ssl.qhimg.com/t010ba64282ae5eb08c.jpg)](https://p2.ssl.qhimg.com/t010ba64282ae5eb08c.jpg)

对启动的临时文件进行分析，其代码功能与mimikatz，一款Windows下抓取密码的工具类似，Petya通过命名管道从该工具进程中获取本机账户密码。

[![](https://p5.ssl.qhimg.com/t01ee9a07654b314dc2.jpg)](https://p5.ssl.qhimg.com/t01ee9a07654b314dc2.jpg)

之后程序加载资源序号3并且解压缩，首先获取系统文件夹目录，若失败则获取%APPDATA%目录，并将解压后的资源命名为dllhost.dat写入到该目录下。

[![](https://p2.ssl.qhimg.com/t0121f43874a810b888.jpg)](https://p2.ssl.qhimg.com/t0121f43874a810b888.jpg)

dllhost.dat的本质为PsExec.exe，是一款属于sysinternals套件的远程命令执行工具，带有合法的签名。



**6、枚举网络资源**

接下来，病毒遍历所有连接过的网络资源，从中筛选类型为TERMSRV的凭据保存。

[![](https://p3.ssl.qhimg.com/t01b7c6f026edd4a5b6.jpg)](https://p3.ssl.qhimg.com/t01b7c6f026edd4a5b6.jpg)

[![](https://p4.ssl.qhimg.com/t01f6ad0015ad97252e.jpg)](https://p4.ssl.qhimg.com/t01f6ad0015ad97252e.jpg)

接下来尝试使用保存的凭据连接网络资源

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01234d6accc57480f0.jpg)

连接成功则执行下列命令：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012a3028d05498744e.jpg)[![](https://p1.ssl.qhimg.com/t01e95a6d801034253e.jpg)](https://p1.ssl.qhimg.com/t01e95a6d801034253e.jpg)

该命令将在目标主机上执行rundll32。exe调用自身dll的第1个导出函数，完成局域网感染功能。

<br>

**7、使用永恒之蓝漏洞攻击**

接下来，启动线程进行永恒之蓝漏洞攻击。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015c8ccc510c3126f2.jpg)

[![](https://p3.ssl.qhimg.com/t01a42909b02cf0ecbd.jpg)](https://p3.ssl.qhimg.com/t01a42909b02cf0ecbd.jpg)

病毒使用异或的方式加密了部分数据包，在内存中重构后发送数据包，这样就避免了杀毒软件的静态查杀。

[![](https://p0.ssl.qhimg.com/t01da086b102d5d7cbf.jpg)](https://p0.ssl.qhimg.com/t01da086b102d5d7cbf.jpg)

**8、文件加密**

Petya采用RSA2048 + AES128的方式对文件进行加密，程序中硬编码RSA公钥文件，每一个盘符会生成一个AES128的会话密钥，该盘符所有文件均对该AES Key进行加密。

<br>

**9、清除日志并重启**

执行完加密文件和网络传播流程后，病毒将清除Windows系统日志并强制重启。重启后将执行病毒写入的MBR并加密磁盘。加密完成后显示勒索信息并等待用户输入key。[![](https://p0.ssl.qhimg.com/t01d3cdaf5c9061d4fb.jpg)](https://p0.ssl.qhimg.com/t01d3cdaf5c9061d4fb.jpg)

[![](https://p3.ssl.qhimg.com/t01cfe376c3b42d69b6.jpg)](https://p3.ssl.qhimg.com/t01cfe376c3b42d69b6.jpg)



**Petya勒索加密技术分析 **

**1、篡改MBR**

当系统重启后，执行病毒的MBR，伪装成CHKDSK进行加密磁盘，加密完成后弹出敲诈信息对用户进行敲诈。

[![](https://p5.ssl.qhimg.com/t0108f3b736e5e2020d.jpg)](https://p5.ssl.qhimg.com/t0108f3b736e5e2020d.jpg)

图 4 Petya敲诈信息



下面，我们来对修改后的MBR进行分析:

1）读取第20个扇区判断是否已经加密，执行相应流程

[![](https://p2.ssl.qhimg.com/t017d58302a123b65de.jpg)](https://p2.ssl.qhimg.com/t017d58302a123b65de.jpg)

2）加密流程，读取病毒配置信息， 病毒加密用的key存在第0x20个扇区

[![](https://p0.ssl.qhimg.com/t01eebb4eb7c5db1f34.jpg)](https://p0.ssl.qhimg.com/t01eebb4eb7c5db1f34.jpg)

3）设置已经加密的标志位，并把配置信息中的key清0， 写回磁盘第20扇区

[![](https://p0.ssl.qhimg.com/t01203b5815b248a52a.jpg)](https://p0.ssl.qhimg.com/t01203b5815b248a52a.jpg)

4）使用用户输入的key尝试解密

[![](https://p2.ssl.qhimg.com/t0178d15069a74507b1.jpg)](https://p2.ssl.qhimg.com/t0178d15069a74507b1.jpg)



**2、加密文件**

勒索木马Petya采用RSA2048 + AES128的方式对文件进行加密，程序中硬编码RSA公钥文件，针对每一个盘符都会生成一个AES128的会话密钥，该盘符所有文件均对该AES Key进行加密。

根据后缀名对相关文件进行分类，涉及的文件格式如下表：

**“.3ds “,”.7z “,”.accdb “,”.ai “,”.asp “,”.aspx “,”.avhd “,”.back “,”.bak “,”.c “,”.cfg “,”.conf “,”.cpp “,”.cs “,”.ctl “,”.dbf “,”.disk “,”.djvu “,”.doc “,”.docx “,”.dwg “,”.eml “,”.fdb “,”.gz “,”.h “,”.hdd “,”.kdbx “,”.mail “,”.mdb “,”.msg “,”.nrg “,”.ora “,”.ost “,”.ova “,”.ovf “,”.pdf “,”.php “,”.pmf “,”.ppt “,”.pptx “,”.pst “,”.pvi “,”.py “,”.pyc “,”.rar “,”.rtf “,”.sln “,”.sql “,”.tar “,”.vbox “,”.vbs “,”.vcb “,”.vdi “,”.vfd “,”.vmc “,”.vmdk “,”.vmsd “,”.vmx “,”.vsdx “,”.vsv “,”.work “,”.xls “,”.xlsx “,”.xvd “,”.zip “**

Petya的加密流程如下图：

[![](https://p0.ssl.qhimg.com/t01b1d1c6566014ee0d.png)](https://p0.ssl.qhimg.com/t01b1d1c6566014ee0d.png)

图 5 加密流程



1）启动加密文件线程

[![](https://p5.ssl.qhimg.com/t01fd07ba4deb0e6de7.jpg)](https://p5.ssl.qhimg.com/t01fd07ba4deb0e6de7.jpg)

[![](https://p0.ssl.qhimg.com/t01559ea25643e94433.jpg)](https://p0.ssl.qhimg.com/t01559ea25643e94433.jpg)[![](https://p5.ssl.qhimg.com/t0144f4deb975b2a6c1.jpg)](https://p5.ssl.qhimg.com/t0144f4deb975b2a6c1.jpg)



2）递归枚举目录并加密

[![](https://p3.ssl.qhimg.com/t0131bda77ea8099d02.jpg)](https://p3.ssl.qhimg.com/t0131bda77ea8099d02.jpg)

3）写入Readme .txt文件

Readme .txt文件中包含比特币支付地址。

[![](https://p5.ssl.qhimg.com/t01a2e4696244c9c9e0.jpg)](https://p5.ssl.qhimg.com/t01a2e4696244c9c9e0.jpg)

<br>

**Petya勒索杀毒软件攻防分析**

在提权阶段，Petya会通过CreateToolhelp32Snapshot枚举系统进程，判断是否有指定的安全软件，并设置标记。枚举过程中，通过将进程名称进行异或计算得出一个值，并将该值与预设的值进行比较，可见此处Petya是在寻找特定名称的进程。

通过分析，我们确认Petya主要针对杀毒软件诺顿和卡巴斯基进行了反检测处理。

1、当存在NS.exe(诺顿)或ccSvcHst.exe(诺顿)进程时，不执行漏洞感染流程。

2、当存在avp.exe(卡巴斯基)进程时，不执行MBR感染流程。



**缓解措施建议**

针对Petya勒索软件，360追日团队提醒广大用户警惕防范，我们建议用户采取以下措施以保障系统安全：

1、保证系统的补丁已升级到最新，修复永恒之蓝(ms17-010）漏洞。

2、临时关闭系统的WMI服务和删除admin$共享，阻断蠕虫的横向传播方式。具体操作为，右键cmd.exe"以管理员身份运行"，输入如下命令：



```
net stop winmgmt
net share admin$ /delete
```

3、如若不幸中招，也可以采取一些措施来减小损失。

由于在感染Petya的过程中，病毒会先重启电脑加载恶意的磁盘主引导记录（MBR）来加密文件，这中间会启用一个伪造的加载界面。中招者如果能感知到重启异常，在引导界面启动系统前关机或拔掉电源，随后可以通过设置U盘或光盘第一顺序启动PE系统，使用PE系统修复MBR或者直接转移硬盘里的数据，可以在一定程度上避免文件的损失。

<br>

**总结**

Petya勒索病毒早已被安全厂商披露，而此次Petya卷土重来，肆虐欧洲大陆在于其利用了已知的OFFICE漏洞、永恒之蓝SMB漏洞、局域网感染等网络自我复制技术，使得病毒可以在短时间内呈暴发态势。另一方面，Petya木马主要通过加密硬盘驱动器主文件表（MFT），使主引导记录（MBR）不可操作，通过占用物理磁盘上的文件名、大小和位置的信息来限制对完整系统的访问，从而让电脑无法启动，相较普通勒索软件对系统更具破坏性。

自5月份WannaCry勒索病毒爆发后，中国用户已经安装了上述漏洞的补丁，同时360安全卫士具备此次黑客横向攻击的主动防御拦截技术，故而并没有为Petya勒索病毒的泛滥传播提供可乘之机。



**360追日团队（Helios Team）**

360 追日团队（Helios Team）是360公司高级威胁研究团队，从事APT攻击发现与追踪、互联网安全事件应急响应、黑客产业链挖掘和研究等工作。团队成立于2014年12月，通过整合360公司海量安全大数据，实现了威胁情报快速关联溯源，独家首次发现并追踪了三十余个APT组织及黑客团伙，大大拓宽了国内关于黑客产业的研究视野，填补了国内APT研究的空白，并为大量企业和政府机构提供安全威胁评估及解决方案输出。

已公开APT相关研究成果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01145db6017e6d3037.png)

联系方式

邮箱：360zhuiri@360.cn

微信公众号：360追日团队

扫描下方二维码关注微信公众号

[![](https://p4.ssl.qhimg.com/t016b2dd452d92d8e0f.png)](https://p4.ssl.qhimg.com/t016b2dd452d92d8e0f.png)
