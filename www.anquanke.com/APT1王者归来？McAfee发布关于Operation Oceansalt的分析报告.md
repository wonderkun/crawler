> 原文链接: https://www.anquanke.com//post/id/162575 


# APT1王者归来？McAfee发布关于Operation Oceansalt的分析报告


                                阅读量   
                                **477768**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者McAfee，文章来源：mcafee.com
                                <br>原文地址：[https://www.mcafee.com/enterprise/en-us/assets/reports/rp-operation-oceansalt.pdf](https://www.mcafee.com/enterprise/en-us/assets/reports/rp-operation-oceansalt.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01c2a21189de51230a.png)](https://p3.ssl.qhimg.com/t01c2a21189de51230a.png)



## 一、概述

McAfee高级威胁研究小组发现一个针对韩语用户的数据侦察类恶意软件。由于它与早期恶意软件Seasalt（海盐，属于早期的一个中国黑客组织）的相似性，我们将此威胁命名为Operation Oceansalt（海洋盐，或者洋盐）。Oceansalt重复使用了部分Seasalt的代码，而与活跃在2010年的Seasalt与中国黑客组织Comment Crew（评论员，即APT1）存在关联。Oceansalt主要针对韩国、美国和加拿大，该恶意软件从两个被入侵的韩国网站（目前已离线）进行分发。Oceansalt疑为APT攻击的第一阶段活动，用于收集系统信息并发送至远程控制服务器，并可以执行相关命令（指令）。目前还不清楚该恶意活动的最终目的。

### APT1卷土重来？

Comment Crew（评论员）也被称为APT1，2013年被曝光，据称是中国发起的针对美国的网络间谍活动。当时的报告曝光了该组织的内部工作细节和网络攻击能力，迫使该组织销声匿迹（也可能是改变了技术）。截至本报告之前，我们没有发现该组织的任何新攻击活动，但现在我们在针对韩国的新攻击活动中发现了它的部分代码。

我们对这些重用的代码进行了调查，发现这些源代码既没有被公开发布过，也没有在暗网市场上出售过。所以，APT1真的卷土重来了吗？我们认为这不太可能。没有确凿的证据表明这是APT1的新攻击活动，那到底攻击者是谁呢？根据我们的调查，我们提出了以下几种设想。

<!-- [if !supportLists]-->1、  <!--[endif]-->两个攻击组织之间达成了某种共享代码的协议

<!-- [if !supportLists]-->2、  <!--[endif]-->可能是原APT1的某个成员泄露了原始代码，另一个攻击组织获得了这些代码

<!-- [if !supportLists]-->3、  <!--[endif]-->攻击者故意设置一个False Flag（错误标志），以误导研究人员认为中国和朝鲜共同发起了这些攻击。

### 攻击者是说韩语的吗？

恶意文档的内容是韩文的，其主题与韩国的特定经济项目有关。这些文档看起来是独一无二的，没有在任何公开渠道上出现过。我们无法定位这些文档的来源，这意味着这些文档可能是攻击者创建的。

恶意Office文档的元数据中包含韩语的代码页（code page）。这意味着该文档包含韩语语言包，很有可能是为了确保受害者可以阅读它。我们还发现恶意文档统一使用了一个作者名字，这是先前我们分析过的针对韩国的恶意文档常用的技术之一。

[![](https://p4.ssl.qhimg.com/t0173b8b3fe089b5039.jpg)](https://p4.ssl.qhimg.com/t0173b8b3fe089b5039.jpg)

图1 恶意xls文档的代码页元数据

我们得出结论：这是一个新的恶意软件家族，攻击者主要针对韩语用户，并使用了APT1的部分源代码。此外，攻击者很可能对韩语十分了解。

### 攻击目标

研究表明初始的攻击向量是鱼叉式钓鱼攻击，通过两个恶意的韩文Excel文档下载恶意软件。根据我们的文档分析，这些目标很可能与韩国的公共基础设施项目及其财务信息有关 – 这清楚地表明攻击者的初步攻击主要针对基础设施。

第二轮恶意文档是Word文档，带有相同的元数据和作者信息。文档内容与朝韩合作基金的财务信息有关。恶意活动首次出现于2018年5月31日，出现在韩国。我们的遥测技术表明部分韩国之外的企业也遭到攻击；而到8月14日，攻击的范围扩大了，开始针对加拿大和美国的多个行业。

攻击活动在北美地区的首次出现日期尚不明确。我们没有找到针对加拿大和美国的恶意Office文档，但我们的遥测技术表明部分北美的计算机系统受到影响。针对北美企业的攻击可能只是针对韩国攻击的部分延续（因为触发检测的恶意文档屈指可数，而且它们只传播其中一个恶意软件变体）。根据我们的遥测技术，这些企业可能是投资企业、银行以及农业企业。

### 攻击目的与造成的影响

研究表明这些攻击目标会关注与韩国的公共建设支出、朝韩合作基金以及其它全球经济数据有关的文档。该恶意活动的目标可能是窃取资金。鉴于攻击者在受害者中获得的控制权限，这些攻击可能只是大规模破坏性攻击的前奏。该恶意活动的影响是巨大的：Oceansalt使得攻击者获得了目标系统及其网络的完整控制权限。如果是一个银行的内部网络，攻击者就可能获得巨额利益。

此外，其代码与先前的一个国家资助的APT组织有重叠。这种代码重用意味着该国家资助的APT组织成员与当前网络攻击活动的攻击者存在密切的联系。



## 二、恶意活动分析

该恶意活动起始于韩国，随后扩展至全球。恶意文档中的恶意软件分发链接一直保持一致性；攻击者可能是入侵了多个韩国网站来托管这些恶意代码。

### 第一波攻击：针对韩国的高等教育行业

第一波攻击中的恶意文档创建于5月18日，最后保存日期为5月28日。该韩文文档的作者是Lion，之后的文档中我们将经常看到这个名字。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0156e0f65b52d910e1.jpg)

图2 第一波攻击中的恶意文档元数据

第一波攻击中的恶意文档包含韩国姓名、物理住址和电子邮件地址的列表。这些名字属于韩国高等教育行业中的人或是各个研究院的人。该列表看起来是随机的，似乎是从政府的某个个人信息数据库中复制得到。

该恶意文档中还包含宏代码，用于从[www.[redacted].kr/admin/data/member/1/log.php](http://www.%5Bredacted%5D.kr/admin/data/member/1/log.php) 下载恶意软件，并伪装成韩国一个安全产品的名字（V3UI.exe）来执行。

### 第二波攻击：针对韩国的公共基础设施

我们的研究团队发现该恶意软件托管在一个合法的韩国网站上（属于一个音乐教师协会，与恶意文档并无任何关联）。攻击者通过一个PHP页面来完成恶意软件的分发，当用户打开2种恶意的Excel文档时，其内置的Visual Basic宏就会连接到该页面，下载和运行恶意软件。在第一波攻击发生时，韩国的一个企业将该恶意文档的样本提交给了我们。

[![](https://p5.ssl.qhimg.com/t01601301118c183b45.png)](https://p5.ssl.qhimg.com/t01601301118c183b45.png)

图3 第二波攻击中的恶意软件下载链接

Excel文档的创建者是Lion，创建日期是5月31日，正好是恶意软件被编译和托管在网站上的前一天。这些文档的内容与韩国的公共基础设施项目及其开支有关。根据我们的分析，这明确意味着攻击者的兴趣是针对与韩国这一领域有关的个人。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ef869e3a5126534c.jpg)

图4 第二波攻击中的恶意文件元数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015379a8e1777e5d84.jpg)

图5 恶意文档一：公共基础设施项目中的投资趋势

[![](https://p1.ssl.qhimg.com/t01cb53631be54f5dfe.jpg)](https://p1.ssl.qhimg.com/t01cb53631be54f5dfe.jpg)

图6 恶意文档二：公共基础设施项目中的开支

[![](https://p3.ssl.qhimg.com/t0148a24a5c83f5dd53.jpg)](https://p3.ssl.qhimg.com/t0148a24a5c83f5dd53.jpg)

图7 恶意文档三：公共项目开支报表

这一波攻击中最后一个文档的创建者仍然是Lion，创建日期是6月4日，文件名为0.<a name="OLE_LINK3"></a>온나라_상용_SW_2018<a name="OLE_LINK4"></a>년 대상_list_(20180411)_<a name="OLE_LINK5"></a>지역업체.xls。该文档伪装成韩国行政安全部Onnara的文件（该部门主要负责土地和开发）。

### 第三波攻击：朝韩合作

第三波攻击中的Word文档与Excel文档包含相同的宏代码。这些文档伪装成朝韩合作基金的财务信息，其创建时间与第二波攻击相同。此外，不管是Excel还是Word，其作者都是Lion。这一次恶意软件通过另一个韩国网站进行分发。新出现的Excel文档包含与Word文档内容有关的电话号码和联系人信息。

[![](https://p5.ssl.qhimg.com/t01316d2517573627de.png)](https://p5.ssl.qhimg.com/t01316d2517573627de.png)

图8 第三波攻击中的恶意软件分发链接

[![](https://p3.ssl.qhimg.com/t01bcdf12c793d4b4a5.jpg)](https://p3.ssl.qhimg.com/t01bcdf12c793d4b4a5.jpg)

图9 （假）朝韩合作基金的月度统计报告

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e8ad540677a0baa7.jpg)

图10 （假）朝韩合作基金的月度统计报告

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014384a6f83a7deadd.jpg)

图11 虚假的产品和合伙人信息

### 第四波攻击：针对韩国之外的目标

在韩国之外，我们发现了一小部分受到攻击的目标，疑为攻击者扩大了它的攻击范围。我们还没有发现用于下载恶意软件的恶意文档。由于攻击者在第一波和第二波攻击中使用了不同的恶意软件分发服务器，我们认为这一波攻击也有自己的分发服务器。根据McAfee的遥测数据，8月10日至14日期间，北美地区的多个行业受到攻击：
<td width="167"><pre>行业</pre></td><td width="177"><pre>国家</pre></td>
<td width="167">金融</td><td width="177">美国</td>

美国
<td width="167">医疗</td><td width="177">美国</td>

美国
<td width="167">医疗</td><td width="177">美国</td>

美国
<td width="167">电信</td><td width="177">加拿大</td>

加拿大
<td width="167">金融</td><td width="177">美国</td>

美国
<td width="167">农业和工业</td><td width="177">美国</td>

美国
<td width="167">金融</td><td width="177">美国</td>

美国
<td width="167">电信</td><td width="177">加拿大</td>

加拿大
<td width="167">金融</td><td width="177">加拿大</td>

加拿大
<td width="167">金融和技术企业</td><td width="177">美国</td>

美国
<td width="167">政府机构</td><td width="177">美国</td>

美国

图12 第四波攻击中的受害者

### 第五波攻击：针对韩国和美国

Oceansalt不仅仅只有一个样本。我们在不同的控制服务器上发现了多个不同的变体。这些变体使用了混淆技术来逃避检测。这些样本与初始Oceansalt样本几乎完全相同。第五波攻击中的样本是在7月13日至7月17日期间编译的，并由韩国和美国的企业提交给我们。
<td valign="top" width="225">哈希</td><td valign="top" width="104">编译日期</td><td valign="top" width="116">控制服务器</td>
<td valign="top" width="225">38216571e9a9364b509e52ec19fae61b</td><td valign="top" width="104">6/13/2018</td><td valign="top" width="116">172.81.132.62</td>
<td valign="top" width="225">531dee019792a089a4589c2cce3dac95</td><td valign="top" width="104">6/14/2018</td><td valign="top" width="116">211.104.160.196</td>
<td valign="top" width="225">0355C116C02B02C05D6E90A0B3DC107C</td><td valign="top" width="104">7/16/2018</td><td valign="top" width="116">27.102.112.179</td>
<td valign="top" width="225">74A50A5705E2AF736095B6B186D38DDF</td><td valign="top" width="104">7/16/2018</td><td valign="top" width="116">27.102.112.179</td>
<td valign="top" width="225">45C362F17C5DC8496E97D475562BEC4D</td><td valign="top" width="104">7/17/2018</td><td valign="top" width="116">27.102.112.179</td>
<td valign="top" width="225">C1773E9CF8265693F37DF1A39E0CBBE2</td><td valign="top" width="104">7/17/2018</td><td valign="top" width="116">27.102.112.179</td>
<td valign="top" width="225">D14DD769C7F53ACEC482347F539EFDF4</td><td valign="top" width="104">7/17/2018</td><td valign="top" width="116">27.102.112.179</td>
<td valign="top" width="225">B2F6D9A62C63F61A6B33DC6520BFCCCD</td><td valign="top" width="104">7/17/2018</td><td valign="top" width="116">27.102.112.179</td>
<td valign="top" width="225">76C8DA4147B08E902809D1E80D96FBB4</td><td valign="top" width="104">7/17/2018</td><td valign="top" width="116">27.102.112.179</td>

 

## 三、技术分析

### 下载和执行功能

<!-- [if !supportLists]-->l  <!--[endif]-->一旦使用Office打开这些恶意.xls/.doc文档，其内置的恶意宏就会连接远程服务器并下载Oceansalt

<!-- [if !supportLists]-->l  <!--[endif]-->恶意宏随后会在受感染的终端上执行Oceansalt

.xls恶意下载器的入侵指标（IoC）：
<td valign="top" width="284">IoC描述</td><td valign="top" width="284">IoC值</td>
<td valign="top" width="284">远程下载服务器</td><td valign="top" width="284">[redacted].kr<br>[redacted].kr</td>
<td valign="top" width="284">远程服务器上的Oceansalt路径</td><td valign="top" width="284">/admin/data/member/1/log[.]php<br>/gbbs/bbs/admin/log[.]php</td>
<td valign="top" width="284">受感染终端上的Oceansalt路径</td><td valign="top" width="284">%temp%SynTPHelper[.]exe<br>%temp%LMworker[.]exe</td>



[![](https://p1.ssl.qhimg.com/t0118beb007d9fc069c.jpg)](https://p1.ssl.qhimg.com/t0118beb007d9fc069c.jpg)

图13 用于下载恶意软件的部分恶意宏代码

### 控制服务器

该恶意活动使用了多个控制服务器。在6月至7月期间，我们观察到的恶意IP包括：

<!-- [if !supportLists]-->l  <!--[endif]-->172.81.132.62

<!-- [if !supportLists]-->l  <!--[endif]-->211.104.160.196

<!-- [if !supportLists]-->l  <!--[endif]-->27.102.112.179

<!-- [if !supportLists]-->l  <!--[endif]-->158.69.131.78

我们的遥测技术表明该恶意活动运营在多个国家。IP地址211.104.160.196揭示了哥斯达黎加、美国和菲律宾的感染事件。IP地址158.69.131.78揭示了美国和加拿大的感染事件。

这些服务器在8月18日至21日期间分布在多个国家。由于它们在恶意活动中分发不同的恶意软件样本，这意味着它们很可能是更大规模的隐蔽监听网络的一部分。McAfee高级威胁研究小组以前观察到过类似的攻击活动，部分入侵目标被当作中继控制服务器。



## 四、恶意软件溯源

我们对早期样本的初步调查使我们注意到一个编译于2010年的变体 – bf4f5b4ff7ed9c7275496c07f9836028。Oceansalt使用了该变体的部分代码；它们的整体代码相似度为21%。这部分被重用的代码是独一无二的，不属于任何一个公共库或公共代码，它主要提供侦察和控制功能。

该变体使用了属于APT1的域名。进一步的调查表明该样本与Seasalt的相似度达99%。Seasalt（5e0df5b28a349d46ac8cc7d9e5e61a96）据称是2010年APT1使用的恶意软件。这意味着Oceansalt重用了Seasalt的部分代码构建了一个新的恶意软件。根据对其整体技术水平的分析，Oceansalt不太可能是APT1的再次出现，这就带来了另一个问题，攻击者是如何获得Seasalt代码的呢？我们没有找到任何证据表明Seasalt的源代码在地下论坛出售或泄露过。

我们还发现几个编译于7月16日至17日的恶意软件样本，这些样本虽然经过混淆，但实际上还是同一个样本，只修改了控制服务器等少数几个地方。一些样本缺失反弹shell的功能，这表明攻击者能够访问Seasalt的源代码并进行修改和编译出不同的变体。这或许证明了这是一个由两个国家赞助的网络攻击程序之间的协作攻击行为。

### 与Seasalt代码的相似之处

Oceansalt包含部分与Seasalt相同的字符串：

<!-- [if !supportLists]-->l  <!--[endif]-->Upfileer 

<!-- [if !supportLists]-->l  <!--[endif]-->Upfileok

[![](https://p4.ssl.qhimg.com/t0103e87970e2fdf68e.jpg)](https://p4.ssl.qhimg.com/t0103e87970e2fdf68e.jpg)

图14 出现在Oceansalt中的Seasalt字符串

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018b2f6d0a58c82e36.jpg)

图15 出现在Oceansalt中的Seasalt字符串

Oceansalt和Seasalt的共享代码和函数具有高度的相似性。下面列出了它们的一些共性：

#### 命令处理程序和索引表的相似性

Oceansalt和Seasalt的命令处理程序通过相似的语义和指令编码执行相同的功能。甚至它们解析指令编码的机制也是相似的。下图中左边是Seasalt代码，右边是Oceansalt代码：

[![](https://p5.ssl.qhimg.com/t01923c99e749735d6f.jpg)](https://p5.ssl.qhimg.com/t01923c99e749735d6f.jpg)

图16 Seasalt（左）和Oceansalt（右）的命令处理程序之间的相似性

[![](https://p2.ssl.qhimg.com/t01bce203c36ba34afa.jpg)](https://p2.ssl.qhimg.com/t01bce203c36ba34afa.jpg)

图17 Seasalt（左）和Oceansalt（右）的指令索引表之间的相似性

#### 命令和功能上的相似性

Oceansalt和Seasalt的功能执行的方式是相同的，这表明它们是从同一个代码库开发的。用于表明命令执行成功还是失败的响应代码在两个恶意软件中也是完全一致的。下面是部分相似性案例：

驱动器探测功能：相似的代码签名。使用相同的代码来标记驱动器类型。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ef89b1917ee12887.jpg)

图18 Seasalt（左）和Oceansalt（右）的驱动器探测功能的相似性

<!-- [if !supportLists]-->l  <!--[endif]-->文件探测功能：获取文件信息的API和代码十分相似。发送至控制服务器的用于表明文件是否找到的响应代码也完全一致。

[![](https://p4.ssl.qhimg.com/t017c34848226c217b0.jpg)](https://p4.ssl.qhimg.com/t017c34848226c217b0.jpg)

图19 Seasalt（左）和Oceansalt（右）的命令执行功能中的相似性

<!-- [if !supportLists]-->l  <!--[endif]-->反弹shell创建功能：创建反弹shell的代码签名是相似的，并且创建的反弹shell都是基于cmd.exe

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f6bd488bcda8be81.jpg)

图20 Seasalt（左）和Oceansalt（右）的反弹shell创建功能中的相似性

### 与Seasalt代码的不同之处

Oceansalt和Seasalt的实现存在一定的不同。这证明Oceansalt不仅仅是Seasalt源代码的简单再编译，而是Seasalt的进化版本。

<!-- [if !supportLists]-->l  <!--[endif]-->编码机制的不同：Oceansalt在数据发送至服务器之前对数据进行编码和解码操作，而Seasalt则没有进行编码，直接将未加密的数据发送至服务器。

<!-- [if !supportLists]-->l  <!--[endif]-->控制服务器地址的不同：Oceansalt使用了硬编码的控制服务器地址，而Seasalt则是从其binary中解码得到控制服务器的地址。

<!-- [if !supportLists]-->l  <!--[endif]-->持久性机制的不同：Oceansalt没有任何持久性机制，这意味着它无法在受感染的终端重启后确保二次感染。Seasalt则将自己复制为C:DOCUMEN~1\java.exe并通过以下注册表项确保重启后的二次感染：

− HKLMSoftwareMicrosoftWindowscurrentVersion Run | sysinfo

根据可执行文件的头部信息，Seasalt的编译日期是2010年3月30日。Oceansalt的编译日期是2018年6月1日。在这里我们强调了编译日期的不同是因为根据前面的分析，它们之间存在高度的代码共享：

<!-- [if !supportLists]-->l  <!--[endif]-->多处一致的代码和相似的代码

<!-- [if !supportLists]-->l  <!--[endif]-->多个功能相似

<!-- [if !supportLists]-->l  <!--[endif]-->命令处理功能完全一致

<!-- [if !supportLists]-->l  <!--[endif]-->控制服务器发布和接收的命令和响应码完全相同

Oceansalt使用的反弹shell创建代码与APT1的Seasalt完全相同。不仅如此，这一反弹shell创建机制（基于管道的进程间通信）在APT1的其它恶意软件中（如WebC2-CSON和WebC2-GREENCAT）也有发现。

这些一致性促使我们认为Oceansalt是基于10年前的Seasalt开发的。Seasalt曾在APT1的报告中曝光过并没有阻碍Oceansalt开发者继续进行开发。

### Oceansalt与Seasalt的混淆机制对比

我们对Oceansalt的初始样本和Seasalt样本的混淆技术进行了全面的分析。
<td valign="top" width="256">SHA-1</td><td valign="top" width="110">编译日期</td><td valign="top" width="199">样本</td>
<td valign="top" width="256">fc121db04067cffbed04d7403c1d222d376fa7ba</td><td valign="top" width="110">7/16/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>
<td valign="top" width="256">281a13ecb674de42f2e8fdaea5e6f46a5436c685</td><td valign="top" width="110">7/17/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>
<td valign="top" width="256">1f70715e86a2fcc1437926ecfaeadc53ddce41c9</td><td valign="top" width="110">7/17/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>
<td valign="top" width="256">ec9a9d431fd69e23a5b770bf03fe0fb5a21c0c36</td><td valign="top" width="110">7/16/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>
<td valign="top" width="256">12a9faa96ba1be8a73e73be72ef1072096d964fb</td><td valign="top" width="110">7/17/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>
<td valign="top" width="256">be4fbb5a4b32db20a914cad5701f5c7ba51571b7</td><td valign="top" width="110">7/17/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>
<td valign="top" width="256">0ae167204c841bdfd3600dddf2c9c185b17ac6d4</td><td valign="top" width="110">7/17/2018</td><td valign="top" width="199">部分混淆的Oceansalt</td>



所有的部分混淆的Oceansalt样本都具有以下特征：

<!-- [if !supportLists]-->l  <!--[endif]-->编译日期在7月16日至18日之间

<!-- [if !supportLists]-->l  <!--[endif]-->包含debug语句（print logs），用于将log写入文件：C:UsersPublicVideostemp.log

<!-- [if !supportLists]-->l  <!--[endif]-->这些debug语句以时间戳开头，并在调试信息的开头包含以下关键字

− [WinMain] 

− [FraudProc] 

<!-- [if !supportLists]-->l  <!--[endif]-->连接到同一个控制服务器（IP地址为：27.102.112.179）

<!-- [if !supportLists]-->l  <!--[endif]-->尽管所有样本都没有添加额外功能（与初始Oceansalt和Seasalt相比），但部分样本缺失了反弹shell功能：
<td valign="top" width="284">部分混淆的Oceansalt样本哈希</td><td valign="top" width="284">是否包含反弹shell功能？</td>
<td valign="top" width="284">C1773E9CF8265693F37DF1A39E0CBBE2  </td><td valign="top" width="284">否</td>
<td valign="top" width="284">0355C116C02B02C05D6E90A0B3DC107C</td><td valign="top" width="284">是</td>
<td valign="top" width="284">74A50A5705E2AF736095B6B186D38DDF</td><td valign="top" width="284">是</td>
<td valign="top" width="284">45C362F17C5DC8496E97D475562BEC4D</td><td valign="top" width="284">否</td>
<td valign="top" width="284">D14DD769C7F53ACEC482347F539EFDF4</td><td valign="top" width="284">否</td>
<td valign="top" width="284">B2F6D9A62C63F61A6B33DC6520BFCCCD</td><td valign="top" width="284">是</td>
<td valign="top" width="284">76C8DA4147B08E902809D1E80D96FBB4</td><td valign="top" width="284">是</td>



### 代码共享的证据

基于我们对三类样本（Oceansalt、部分混淆的Oceansalt和Seasalt）的综合分析，我们发现了以下代码共享的证据：

<!-- [if !supportLists]-->l  <!--[endif]-->攻击者并不是简单地修改了Seasalt的控制服务器IP地址来得到Oceansalt：

<!-- [if !supportLists]-->–          <!--[endif]-->Seasalt与Oceansalt获得控制服务器IP地址的机制不同。Seasalt在binary文件的末尾获取编码过的数据，解码成以符号$分隔的tokens并获得控制服务器的信息

<!-- [if !supportLists]-->–          <!--[endif]-->Oceansalt则是在binary文件中硬编码了控制服务器IP地址和端口号的明文字符串

<!-- [if !supportLists]-->l  <!--[endif]-->一些部分混淆的Oceansalt样本缺失反弹shell功能。所有的其它功能（代码签名、响应代码等）以及命令编码都是相似的（指令编码要么完全一致，要么只偏移1）。这种程度的修改只能是在获得Seasalt源代码的基础上进行修改。

<!-- [if !supportLists]-->l  <!--[endif]-->Oceansalt中用于跟踪代码流程的debug字符串表明这些样本是在对Seasalt源码添加debug信息之后编译的：

− [WinMain]after recv cmd=%d 0Dh 0Ah 

− [WinMain]before recv 0Dh 0Ah 

− [FraudProc]Engine is still active! 0Dh 0Ah 

− [FraudPRoc]Process Restart! 0Dh 0Ah

<!-- [if !supportLists]-->l  <!--[endif]-->这些debug字符串还表明开发者在实施攻击之前进行了初步的测试，并且在没有去除调试信息的情况下进行了混淆

<!-- [if !supportLists]-->l  <!--[endif]-->Oceansalt样本（531dee019792a089a4589c2cce3dac95，编译于6月1日）包含一些可以验证是Seasalt源码编译而来的关键特征：

<!-- [if !supportLists]-->–          <!--[endif]-->缺失反弹shell功能

<!-- [if !supportLists]-->–          <!--[endif]-->缺失驱动器侦察功能

<!-- [if !supportLists]-->–          <!--[endif]-->动态加载API SHGetFileInfoA()而不是静态导入。这意味着Seasalt的源码在编译之前被修改过

[![](https://p5.ssl.qhimg.com/t01052e681980b2d2bb.jpg)](https://p5.ssl.qhimg.com/t01052e681980b2d2bb.jpg)

图21 动态加载API

 

## 五、Oceansalt的功能

Oceansalt大小为76KB，占用的磁盘空间非常小，这使其比较大的恶意软件更难被检测到。该恶意软件具有一个结构化的命令系统，用于从受害者的机器上捕获数据。我们的研究表明该恶意软件是一个第一阶段组件，可以通过它的命令下载第二/三阶段的其它恶意程序。Oceansalt的命令系统还允许攻击者在受害者的机器上执行多种恶意行为。

#### 初步侦察

Oceansalt在开始时会尝试连接到控制服务器158.69.131.78:8080。一旦连接成功，该恶意软件就会将感染终端的以下信息发送至服务器：

<!-- [if !supportLists]-->l  <!--[endif]-->IP地址

<!-- [if !supportLists]-->l  <!--[endif]-->计算机名称

<!-- [if !supportLists]-->l  <!--[endif]-->恶意软件的文件路径

这些数据在发送至服务器之前将每一个字节都进行了一个NOT编码操作（取反）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb4657b8a698e2ef.jpg)

图22 Oceansalt从感染终端收集的初始数据

[![](https://p0.ssl.qhimg.com/t0147b4be2b273a3cd2.jpg)](https://p0.ssl.qhimg.com/t0147b4be2b273a3cd2.jpg)

图23 Oceansalt的控制服务器连接功能

#### 命令处理功能

Oceansalt具有12条命令。这些命令分别用0x0到0xB（0到11）表示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f7eb92275bfe9c80.jpg)

图24 命令索引表（即Oceansalt的功能列表）

[![](https://p0.ssl.qhimg.com/t0117f15b09b9a670e6.jpg)](https://p0.ssl.qhimg.com/t0117f15b09b9a670e6.jpg)

图25 Oceansalt的命令执行功能

##### 0x0: 驱动器探测

控制服务器向Oceansalt发送此命令以获得感染终端的驱动器信息。信息的格式为：

#&lt;Drive _ letter&gt;:&lt;Drive _ type&gt;&lt;Drive _ letter&gt;:&lt;Drive _ type&gt;…#
<td valign="top" width="284">标签</td><td valign="top" width="284">描述</td>
<td valign="top" width="284">&lt;Drive_letter&gt;</td><td valign="top" width="284">A、B、C、D、E等，系统上的逻辑驱动器</td>
<td valign="top" width="284">&lt;Drive_type&gt;</td><td valign="top" width="284">0 = DRIVE_REMOVABLE 1 = DRIVE_FIXED 2 = DRIVE_CDROM 3 = DRIVE_REMOTE</td>

2 = DRIVE_CDROM 



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f850444ebb575bd9.jpg)

图26 Oceansalt收集的驱动器信息

##### 0x1: 文件探测

将指定文件或文件夹（由控制服务器指定）的以下信息发送至控制服务器：

<!-- [if !supportLists]-->l  <!--[endif]-->文件名

<!-- [if !supportLists]-->l  <!--[endif]-->文件类型，例如是文件还是文件夹

<!-- [if !supportLists]-->l  <!--[endif]-->如果定位到文件，则发送OK

<!-- [if !supportLists]-->l  <!--[endif]-->文件创建时间，格式为&lt;YYYY-mm-DD HH:MM:SS&gt;

##### 0x2: 命令执行

通过WinExec()执行命令。命令内容和命令号由控制服务器提供。例如：

&lt;DWORD （命令号）&gt;&lt;（命令内容）&gt; 02 00 00 00 C:Windowssystem32calc.exe

该命令是静默执行的（使用WinExec()的SW_HIDE选项）。

[![](https://p2.ssl.qhimg.com/t01ea3fe70ed8dfc058.jpg)](https://p2.ssl.qhimg.com/t01ea3fe70ed8dfc058.jpg)

图27 Oceansalt的命令执行功能

##### 0x3: 文件删除

<!-- [if !supportLists]-->l  <!--[endif]-->从硬盘上删除控制服务器指定的文件

<!-- [if !supportLists]-->l  <!--[endif]-->命令执行成功后，向控制服务器发送一个ASCII码的0

<!-- [if !supportLists]-->l  <!--[endif]-->命令执行失败后，向控制服务器发送一个ASCII码的1

##### 0x4: 文件写入

<!-- [if !supportLists]-->l  <!--[endif]-->在指定路径下创建一个文件，并写入控制服务器提供的内容

<!-- [if !supportLists]-->l  <!--[endif]-->如果文件写入操作成功，向控制服务器发送关键字upfileok

<!-- [if !supportLists]-->l  <!--[endif]-->如果文件写入操作失败，向控制服务器发送关键字upfileer

[![](https://p2.ssl.qhimg.com/t01a48bedfcc776440f.jpg)](https://p2.ssl.qhimg.com/t01a48bedfcc776440f.jpg)

图28 Oceansalt的文件写入功能

##### 0x5: 文件读取

（被研究人员吃了）

##### 0x6: 进程探测

<!-- [if !supportLists]-->l  <!--[endif]-->向控制服务器发送感染终端上所有运行进程的名称和ID列表

<!-- [if !supportLists]-->l  <!--[endif]-->这些数据是通过单独的数据包发送的，就是说，一个进程一个数据包

[![](https://p2.ssl.qhimg.com/t01b9b189fc20efcc83.jpg)](https://p2.ssl.qhimg.com/t01b9b189fc20efcc83.jpg)

图29 Oceansalt的进程探测功能

##### 0x7: 杀死进程

<!-- [if !supportLists]-->l  <!--[endif]-->通过指定的ID杀死进程

##### 0x8: 创建反弹shell

<!-- [if !supportLists]-->l  <!--[endif]-->通过Windows管道创建从感染终端到控制服务器的反弹shell

<!-- [if !supportLists]-->l  <!--[endif]-->该反弹shell基于cmd.exe，可用于实施更多恶意操作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ea2e73f0d032fc57.jpg)

图30 Oceansalt的反弹shell创建功能

##### 0x9: 操作反弹shell

<!-- [if !supportLists]-->l  <!--[endif]-->操作前一条命令创建的反弹shell

<!-- [if !supportLists]-->l  <!--[endif]-->控制服务器发送的命令将由感染终端上的cmd.exe执行

<!-- [if !supportLists]-->l  <!--[endif]-->命令执行完毕后，通过管道从cmd.exe读取输出并发送至控制服务器

##### 0XA: 终止反弹shell

<!-- [if !supportLists]-->l  <!--[endif]-->关闭进程间通信的管道句柄，终止反弹shell

##### 0XB: 连接测试

<!-- [if !supportLists]-->l  <!--[endif]-->通过接收控制服务器发送的7个字节的数据并发送回控制服务器来测试数据接收和发送功能是否正常

持久性

<!-- [if !supportLists]-->l  <!--[endif]-->Oceansalt没有任何持久性机制，无法确保系统重启后继续运行

<!-- [if !supportLists]-->l  <!--[endif]-->这意味着感染链上的其它组件可能会提供此功能



## 六、结论

根据McAfee高级威胁研究小组的分析，我们将这个全球威胁命名为Operation Oceansalt。该恶意活动使用与APT1在2010年使用的工具有关的新恶意软件，主要针对韩国等国家。

我们的研究表明APT1的恶意软件以不同的形式部分存活在另一个APT组织针对韩国的恶意活动中。这一研究结果验证了不同的攻击者（包括国家资助的攻击者）是如何进行合作的。



## 七、入侵指标（IoC）

### McAfee检测到的恶意样本

■ Generic.dx!tjz 

■ RDN/Generic.grp 

■ RDN/Generic.ole 

■ RDN/Generic.grp (trojan) 

■ RDN/Trojan-FQBD 

■ <a name="OLE_LINK20"></a>RDN/Generic.RP

### IP 地址

■ 158.69.131.78 

■ 172.81.132.62 

■ 27.102.112.179 

■ 211.104.160.196

### 哈希

■ fc121db04067cffbed04d7403c1d222d376fa7ba 

■ 832d5e6ebd9808279ee3e59ba4b5b0e884b859a5 

■ be4fbb5a4b32db20a914cad5701f5c7ba51571b7 

■ 1f70715e86a2fcc1437926ecfaeadc53ddce41c9 

■ dd3fb2750da3e8fc889cd1611117b02d49cf17f7 

■ 583879cfaf735fa446be5bfcbcc9e580bf542c8c 

■ ec9a9d431fd69e23a5b770bf03fe0fb5a21c0c36 

■ d72bc671583801c3c65ac1a96bb75c6026e06a73 

■ e5c6229825f11d5a5749d3f2fe7acbe074cba77c 

■ 9fe4bfdd258ecedb676b9de4e23b86b1695c4e1e 

■ 281a13ecb674de42f2e8fdaea5e6f46a5436c685 

■ 42192bb852d696d55da25b9178536de6365f0e68 

■ 12a9faa96ba1be8a73e73be72ef1072096d964fb 

■ 0ae167204c841bdfd3600dddf2c9c185b17ac6d4

 

## 八、额外信息

#### Oceansalt与Seasalt的代码可视化对比：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011f1750d3d40d9fe9.png)

图31 Oceansalt，2018

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017f74c452b1db0bc6.png)

图32 Seasalt，2010
