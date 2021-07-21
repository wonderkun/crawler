> 原文链接: https://www.anquanke.com//post/id/94179 


# 360：处理器Meltdown与Spectre漏洞修复简要指南


                                阅读量   
                                **118490**
                            
                        |
                        
                                                                                    



报告下载:[ 360： 处理器Meltdown与Spectre漏洞修复简要指南.pdf](https://cert.360.cn/static/files/360%EF%BC%9A%20%E5%A4%84%E7%90%86%E5%99%A8Meltdown%E4%B8%8ESpectre%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D%E7%AE%80%E8%A6%81%E6%8C%87%E5%8D%97.pdf)

## 0x00 概述

2018年1月4日，Jann Horn等安全研究者披露了”Meltdown”(CVE-2017-5754)和”Spectre”(CVE-2017-5753 &amp; CVE-2017-5715)两组CPU特性漏洞。

据悉，漏洞会造成CPU运作机制上的信息泄露，低权级的攻击者可以通过漏洞来远程泄露用户信息或本地泄露更高权级的内存信息。

实际攻击场景中，攻击者在一定条件下可以做到，
- 泄露出本地操作系统底层运作信息，密钥信息等;
- 通过获取泄露的信息，可以绕过内核(Kernel), 虚拟机超级管理器(HyperVisor)的隔离防护;
- 云服务中，可能可以泄露到其它租户隐私信息；
- 通过浏览器泄露受害者的帐号，密码，内容，邮箱, cookie等用户隐私信息；
目前相关的平台，厂商，软件提供商都在积极应对该系列漏洞，部分厂商提供了解决方案。

经过360安全团队评估，”Meltdown”和”Spectre”漏洞影响重要，**修复流程较复杂，建议相关企业/用户在充分了解补丁风险的基础上，作好相关的修复评估工作**。

## 0x01 漏洞影响面

**影响面**

漏洞风险等级重要，影响广泛：
- 近20年的Intel, AMD,　Qualcomm厂家和其它ARM的处理器受到影响；
- 因为此次CPU漏洞的特殊性，包括Linux, Windows, OSX, iOS, Android等在内的操作系统平台参与了修复；
- 360安全浏览器, Firefox, Chrome, Edge等浏览器也发布了相关的安全公告和缓解方案；
**漏洞编号**
<li>Meltdown
<ul>
- CVE-2017-5754- CVE-2017-5715
- CVE-2017-5753
## 0x02 漏洞信息

注：　本段文字中直接引用了相关安全公告，如有异议请联系cert@360.cn。

现代处理器（CPU）的运作机制中存在两个用于加速执行的特性，推测执行（Speculative Execution）和间接分支预测（Indirect Branch Prediction)。

表面上看，处理器是依次顺序执行既定的处理器指令。但是，现代处理器为了更好利用处理器资源，已经开始启用并行执行，这个技术已经应用了20年左右(1995年开始)。假设，基于猜测或概率的角度，在当前的指令或分支还未执行完成前就开始执行可能会被执行的指令或分支，会发生什么？如果猜对了，直接使用，CPU执行加速了。如果猜测不正确，则取消操作并恢复到原来的现场（寄存器，内存等），结果会被忽略。整个过程过程并不会比没有猜测的时候慢，即CPU的推测执行（Speculative Execution）技术。

不幸的是，尽管架构状态被回滚了，仍然有些副作用，比如TLB或缓存状态并没有被回滚。这些副作用随后可以被黑客通过旁道攻击(Side Channel Attack)的方式获取到缓存的内容。如果攻击者能触发推测执行去访问指定的敏感数据区域的话，就可能可以读取到更高特权级的敏感数据。

此外，猜测过程是可以被“污染”的，攻击者可以构造出类似ROP攻击的逻辑去影响推测过程。根据作者提供的思路，主要有三种场景：
1. “边界检查绕过”：通过污染分支预测，来绕过kernel或hypervisor的内存对象边界检测。比如，攻击者可以对高权级的代码段，或虚拟环境中hypercall，通过构造的恶意代码来触发有越界的数据下标，造成越界访问。
1. “分支目标注入”： 污染分支预测。抽象模型比较好的代码往往带有间接函数指针调用的情况，CPU在处理时需要会进行必要的内存访问，这个过程有点慢，所以CPU会预测分支。攻击者可以通过类似的ROP的方式来进行信息泄露。
1. “流氓数据加载”：部分CPU上，为了速度并不是每次都对指令作权限检查的，检查的条件存在一定的缺陷；
实际攻击场景中，攻击者在一定条件下可以做到，
- 泄露出本地操作系统底层运作信息，秘钥信息等;
- 通过获取泄露的信息，可以绕过内核(Kernel), 虚拟机超级管理器(HyperVisor)的隔离防护;
- 云服务中，可以泄露到其它租户隐私信息；
- 通过浏览器泄露受害者的帐号，密码，内容，邮箱, cookie等用户隐私信息；
360CERT和360GearTeam对漏洞进行了研究性质的尝试。在Linux+Docker的环境下进行的攻击演示，通过利用Meltdown或Spectre漏洞，模拟在独立的Docker容器A对同一个宿主中的Docker容器B进行敏感数据（密码）窃取的尝试。

声明：本试验是360CERT针对CPU的Meltdown和Spectre漏洞作的一个研究性测试，实际的Docker攻击利用场景中需要满足特殊和较严苛的限制条件。



[![](https://p5.ssl.qhimg.com/dm/1024_645_/t014f5fe73560488e10.png)](https://p5.ssl.qhimg.com/dm/1024_645_/t014f5fe73560488e10.png)

目前几大系统厂商各自在操作系统内核中引入了KPTI的技术，旨在和用户态的页表隔离，解决”Meltdown”漏洞问题。但根据相关测试信息显示，修复补丁可能带来5%到30%性能上的损失，其中个人终端用户基本感觉不到，部分服务器的IO场景可能造成较大的性能损耗。

针对”Spectre”漏洞，相关操作系统厂商和芯片厂商积极配合，通过微码固件更新和操作系统更新的方式进行解决。

## 0x03 安全建议

**360CERT建议相关企业/用户务必在充分了解相关风险的基础上作好相关修复评估工作:**
1. “Meltdown”和”Spectre”漏洞修复流程相对复杂，部分平台上暂时没有统一的修复工具；
1. 芯片厂商（如：Intel）的微码固件补丁需要通过所在硬件OEM厂商获取（如：Dell，联想等）；
1. 可能会有部分软件不兼容问题（如Windows平台下的部分杀毒软件等）；
1. 在云平台或特定应用场景中可能造成较大幅度的性能损失，升级前请充分了解相关信息；
具体评估和修复工作，可以参考以下建议和相关厂商的安全公告：

### Intel的缓解建议

Intel已经和产业界联合，包括其它处理器厂商和软件厂商开发者，来缓解之前提到的三种攻击类型。缓解策略主要聚焦在适配市面产品和部分在研产品。缓解策略除了解决漏洞本身之外，还需要兼顾到性能影响，实施复杂度等方面。

启用处理器已有的安全特性（如 Supervisor-Mode Execution Protection 和 Execute Disable Bit ）可以有效提高攻击门槛。这部分的相关信息可以参阅Intel的相关资料。

Intel一直在与操作系统厂商，虚拟化厂商，其它相关软件开发者进行合作，协同缓解这些攻击。作为我们的常规研发流程，Intel会积极保证处理器的性能。

来源：

```
https://newsroom.intel.com/wp-content/uploads/sites/11/2018/01/Intel-Analysis-of-Speculative-Execution-Side-Channels.pdf
```

### PC终端用户

PC终端用户，建议用户根据各个平台进行如下对应操作：

##### 微软Windows

修复步骤如下：
<li>
<ol>
- 更新对应的浏览器，缓解”Spectre”漏洞攻击；
</ol>
</li><th bgcolor="yellow" width="20%,">浏览器</th><th bgcolor="yellow" width="60%">缓解措施</th>
|360安全浏览器|升级360安全浏览器到9.1及以上版本
|Firefox|升级Firefox到57.0.4及以上版本
|Chrome|1. 在地址栏中，输入 chrome://flags/#enable-site-per-process，然后按 Enter 键。<br>2.点击“Strict site isolation”旁边的启用。(如果系统没有显示“Strict site isolation”，请更新 Chrome。)。<br>3. 点击立即重新启动
|Edge/IE|补丁集成于Windows补丁中，请参考“更新Windows补丁”
<li>
<ol>
- 更新芯片厂商的微码补丁
</ol>
</li><th bgcolor="yellow" width="20%,">芯片厂商</th><th bgcolor="yellow" width="60%">微码补丁地址</th>
|Intel|微码补丁发布流程较复杂，请关注并通过OEM提供商渠道更新（如戴尔,联想，惠普等）。

如：

[![](https://p2.ssl.qhimg.com/t012f2fe09b15d9b2d7.png)](https://p2.ssl.qhimg.com/t012f2fe09b15d9b2d7.png)
<li>
<ol>
- 更新Windows补丁
</ol>
</li>
用户可直接下载360安全卫士CPU漏洞免疫工具进行更新： **[http://down.360safe.com/cpuleak_scan.exe](http://down.360safe.com/cpuleak_scan.exe)**

**注意：根据微软提供的信息，依然存在部分不兼容（如杀毒软件，部分AMD的CPU）的风险，请充分了解风险后再选择是否更新：**
- [https://support.microsoft.com/en-us/help/4073119/windows-client-guidance-for-it-pros-to-protect-against-speculative-exe](https://support.microsoft.com/en-us/help/4073119/windows-client-guidance-for-it-pros-to-protect-against-speculative-exe)
### 苹果OSX

苹果在Mac OSX High Sierra 10.13.2 及更高版本修复了Meltdown和Spectre漏洞，请直接升级。

### Android &amp; iOS

苹果在iOS 11.2.2及更高版本修复了Spectre漏洞；

Android产品将于近期更新，尽请留意。

### IDC/云系统管理员

目前部分IDC/云基础架构厂商已经提供了初步解决方案，但是由于补丁带来的风险和性能损耗暂时没有明确，权威的结论。

**请系统管理员尽量做到：**
1. 积极联系相关的上游了解相关的风险和解决方案，协同制定解决方案；
1. 需要重点关注补丁带来风险和性能损耗评估；
1. 从宏观和微观层面，制定完善，可行的修复和测试流程方案；
1. 涉及到的微码固件补丁请联系硬件OEM厂商，协同修复，测试，评估；
以下是相关厂商提供的解决方案：

**Linux-Redhat/CentOS发行版**

Redhat提供了一份产品的修复状态清单，建议用户参照该清单进行更新。具体用户可以参考：
- [https://access.redhat.com/security/vulnerabilities/speculativeexecution](https://access.redhat.com/security/vulnerabilities/speculativeexecution)
- [https://access.redhat.com/articles/3311301#page-table-isolation-pti-6](https://access.redhat.com/articles/3311301#page-table-isolation-pti-6)
鉴于更新完补丁后，在部分应用场景下会造成性能下降，RedHat方面提供了运行时的解决方案：
- [https://access.redhat.com/articles/3311301#page-table-isolation-pti-6](https://access.redhat.com/articles/3311301#page-table-isolation-pti-6)
用户可以通过以下命令临时关闭或部分KPTI，Indirect Branch Restricted Speculation (ibrs)，Indirect Branch Prediction Barriers (ibpb) 等安全特性。

```
# echo 0 &gt; /sys/kernel/debug/x86/pti_enabled
# echo 0 &gt; /sys/kernel/debug/x86/ibpb_enabled
# echo 0 &gt; /sys/kernel/debug/x86/ibrs_enabled
```

该特性需要使用debugfs 文件系统被挂在，RHEL 7默认开启了。 在RHEL 6中可以通过以下命令开启：

```
# mount -t debugfs nodev /sys/kernel/debug
```

用户可以通过以下命令查看当前安全特性的开启状态：

```
# cat /sys/kernel/debug/x86/pti_enabled
# cat /sys/kernel/debug/x86/ibpb_enabled
# cat /sys/kernel/debug/x86/ibrs_enabled
```

Intel芯片在修复前默认如下：

```
pti 1 ibrs 1 ibpb 1 -&gt; fix variant#1 #2 #3
pti 1 ibrs 0 ibpb 0 -&gt; fix variant#1 #3 (for older Intel systems with no microcode update available)
```

Intel芯片在修复后默认如下：

```
pti 0 ibrs 0 ibpb 2 -&gt; fix variant #1 #2 if the microcode update is applied
pti 0 ibrs 2 ibpb 1 -&gt; fix variant #1 #2 on older processors that can disable indirect branch prediction without microcode updates
```

在没有微码固件补丁升级的情况下：

```
# cat /sys/kernel/debug/x86/pti_enabled
1
# cat /sys/kernel/debug/x86/ibpb_enabled
0
# cat /sys/kernel/debug/x86/ibrs_enabled
0
```

注：Redhat等厂商并不直接提供芯片厂商的微码，需要用户到相关的硬件OEM厂商进行咨询获取。

### **Linux-Ubuntu发行版**

目前Ubuntu只完成对Meltdown(CVE-2017-5754)漏洞在 x86_64　平台上的更新。

请关注Ubuntu的更新链接：
- [https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/SpectreAndMeltdown](https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/SpectreAndMeltdown)
### **Linux-Debian发行版**

目前Debian完成了Meltdown(CVE-2017-5754)漏洞的修复。

关于　CVE-2017-5715　和　CVE-2017-5753　请关注Debian的更新链接：
- [https://security-tracker.debian.org/tracker/CVE-2017-5753](https://security-tracker.debian.org/tracker/CVE-2017-5753)
- [https://security-tracker.debian.org/tracker/CVE-2017-5715](https://security-tracker.debian.org/tracker/CVE-2017-5715)
### **微软Windows Server**

建议用户开启系统自动更新功能，进行补丁补丁安装。

**根据微软提供的信息，依然存在部分软件不兼容（如杀毒软件）的风险，请充分了解风险后再选择是否更新。**

更多信息请查看：
- [https://support.microsoft.com/en-us/help/4073119/windows-client-guidance-for-it-pros-to-protect-against-speculative-exe](https://support.microsoft.com/en-us/help/4073119/windows-client-guidance-for-it-pros-to-protect-against-speculative-exe)
### **Xen虚拟化**

目前Xen团队针对Meltdown，Spectre漏洞的修复工作依然在进行中，请关注Xen的更新链接：
- [http://xenbits.xen.org/xsa/advisory-254.html](http://xenbits.xen.org/xsa/advisory-254.html)
**目前Xen暂时没有性能损耗方面的明确评估，请谨慎更新。**

### **QEMU-KVM虚拟化**

QEMU官方建议通过更新guest和host操作系统的补丁来修复Meltdown漏洞，并表示Meltdown漏洞不会造成guest到host的信息窃取。

针对Spectre的变种CVE-2017-5715，QEMU方面正在等待KVM更新后再修复，目前KVM在进行相关补丁整合。**需要注意的是，热迁移不能解决CVE-2017-5715漏洞，KVM需要把cpu的新特性expose到guest内核使用，所以guest需要重启。**

相关信息请查阅：
- [https://www.qemu.org/2018/01/04/spectre/](https://www.qemu.org/2018/01/04/spectre/)
- [https://marc.info/?l=kvm&amp;m=151543506500957&amp;w=2](https://marc.info/?l=kvm&amp;m=151543506500957&amp;w=2)
### 云平台租户

360CERT建议云平台用户，
1. 关注所在云厂商的安全公告，配合相关云厂商做好漏洞补丁修复工作；
1. 充分了解和注意补丁带来的风险和性能损耗方面的指标；
1. 更新前可以考虑使用相关快照或备份功能；
## 0x04 FAQ 常见问题
<li>问题： Meltdown和Spectre漏洞具体技术影响。 比如利用这两个漏洞发动攻击是否容易，什么条件下触发，危害多大？回答： Meltdown和Spectre漏洞在一定的条件下都可以触发，例如通过本地环境,浏览器环境， Xen/QEMU-KVM中恶意租户Guset的场景来触发和攻击，虽然目前尚未发现公开的攻击代码，但能够对用户造成帐号， 密码， 内容， 邮箱, cookie等隐私信息泄露潜在危害。从以往情况看，在漏洞暴露后一定时间内，就可能出现可利用的攻击代码。对此，我们需要保持高度警惕。Meltdown漏洞主要作用于本地环境，可用于越权读内核内存。Spectre由于不会触发trap，可以用于浏览器攻击，以及虚拟机guest/host攻击，及其它存在代码注入（如即时编译JIT）程序的潜在攻击。具体技术情况需如下：<br><table><tbody>
<tr>
<th bgcolor="yellow" width="5%,">类型</th>
<th bgcolor="yellow" width="10%,">利用难度</th>
<th bgcolor="yellow" width="10%,">本地环境触发</th>
<th bgcolor="yellow" width="10%">浏览器触发</th>
<th bgcolor="yellow" width="15%,">内核数据泄露</th>
<th bgcolor="yellow" width="15%">虚拟化Guest内核攻击</th>
<th bgcolor="yellow" width="15%">虚拟化Host/HyperVisor攻击</th>
<th bgcolor="yellow" width="15%">其它JIT程序潜在攻击</th>
</tr>
<tr>
<td bgcolor="yellow">Meltdown</td>
|较难
|是
|否
|是
|是
|部分场景可用
|否
</tr>
<tr>
<td bgcolor="yellow">Spectre</td>
|较难
|是
|是
|是
|是
|部分场景可用
|是
</tr>
</tbody></table>
</li>
1. 问题：当前对漏洞的处置情况到底怎么样了，业界解决情况如何，有没有比较完善的解决方案。目前能解决到什么程度，怎么才能彻底解决？回答：目前大部分的个人终端操作系统（如Windows, MacOS, iOS, Android）都可以通过直接的渠道进行更新解决，其中Windows平台存在部分杀毒软件不兼容风险。针对IDC或云厂商相关的系统管理员，除了还需要再继续评估补丁的兼容性风险外，更需要再进一步评估补丁可能带来的较大幅度的性能损耗，目前芯片厂商也在积极和大型IDC，云服务提供商协同制定更完善的解决方案。
1. 360CERT建议该怎么解决，后续该怎么做？回答：360CERT建议，一方面，PC/手机的个人用户可以直接通过操作系统厂商或第三方安全厂商提供的补丁来解决。另一方面，针对补丁给企业带来修复难题，大型IDC/企业/云厂商，芯片厂商，操作系统厂商，信息安全公司要协同起来，在补丁方案，补丁风险评估，补丁导致的性能损耗评估，综合补丁标准方案，一体化补丁等方面形成合力，在保证业务稳定的情况下逐步或分阶段推进补丁的修复工作。
## 0x05 时间线

2018-01-04 Google的Jann Horn发布漏洞信息

2018-01-04 360安全团队发布预警通告

2018-01-09 360安全团队更新预警通告为版本2

## 0x06 相关安全公告
<li>Intel
<ul>
- [https://newsroom.intel.com/news/intel-responds-to-security-research-findings/](https://newsroom.intel.com/news/intel-responds-to-security-research-findings/)
- [https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00088&amp;languageid=en-fr](https://security-center.intel.com/advisory.aspx?intelid=INTEL-SA-00088&amp;languageid=en-fr)
- [https://www.intel.com/content/www/us/en/architecture-and-technology/facts-about-side-channel-analysis-and-intel-products.html](https://www.intel.com/content/www/us/en/architecture-and-technology/facts-about-side-channel-analysis-and-intel-products.html)- [https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV180002](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/ADV180002)
- [https://support.microsoft.com/en-us/help/4073119/windows-client-guidance-for-it-pros-to-protect-against-speculative-exe](https://support.microsoft.com/en-us/help/4073119/windows-client-guidance-for-it-pros-to-protect-against-speculative-exe)- [https://support.lenovo.com/us/zh/solutions/len-18282](https://support.lenovo.com/us/zh/solutions/len-18282)- [http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20180106-01-cpu-en](http://www.huawei.com/en/psirt/security-advisories/huawei-sa-20180106-01-cpu-en)- [https://aws.amazon.com/de/security/security-bulletins/AWS-2018-013/](https://aws.amazon.com/de/security/security-bulletins/AWS-2018-013/)- [https://developer.arm.com/support/security-update](https://developer.arm.com/support/security-update)- [https://googleprojectzero.blogspot.co.at/2018/01/reading-privileged-memory-with-side.html](https://googleprojectzero.blogspot.co.at/2018/01/reading-privileged-memory-with-side.html)
- [https://www.chromium.org/Home/chromium-security/ssca](https://www.chromium.org/Home/chromium-security/ssca)
- [https://security.googleblog.com/2018/01/todays-cpu-vulnerability-what-you-need.html](https://security.googleblog.com/2018/01/todays-cpu-vulnerability-what-you-need.html)- [http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-5715](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-5715)
- [http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-5753](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-5753)
- [http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-5754](http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-5754)- [https://access.redhat.com/security/vulnerabilities/speculativeexecution](https://access.redhat.com/security/vulnerabilities/speculativeexecution)
- [https://access.redhat.com/articles/3311301#page-table-isolation-pti-6](https://access.redhat.com/articles/3311301#page-table-isolation-pti-6)- [https://support.apple.com/en-us/HT208394](https://support.apple.com/en-us/HT208394)- [http://xenbits.xen.org/xsa/advisory-254.html](http://xenbits.xen.org/xsa/advisory-254.html)- [https://blog.mozilla.org/security/2018/01/03/mitigations-landing-new-class-timing-attack/](https://blog.mozilla.org/security/2018/01/03/mitigations-landing-new-class-timing-attack/)- [https://www.vmware.com/us/security/advisories/VMSA-2018-0002.html](https://www.vmware.com/us/security/advisories/VMSA-2018-0002.html)- [https://www.amd.com/en/corporate/speculative-execution](https://www.amd.com/en/corporate/speculative-execution)- [https://www.suse.com/support/kb/doc/?id=7022512](https://www.suse.com/support/kb/doc/?id=7022512)- [https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/SpectreAndMeltdown](https://wiki.ubuntu.com/SecurityTeam/KnowledgeBase/SpectreAndMeltdown)- [https://marc.info/?l=kvm&amp;m=151543506500957&amp;w=2](https://marc.info/?l=kvm&amp;m=151543506500957&amp;w=2)
- [https://www.qemu.org/2018/01/04/spectre/](https://www.qemu.org/2018/01/04/spectre/)- [https://meltdownattack.com/meltdown.pdf](https://meltdownattack.com/meltdown.pdf)
- [https://spectreattack.com/spectre.pdf](https://spectreattack.com/spectre.pdf)
- [https://googleprojectzero.blogspot.co.uk/2018/01/reading-privileged-memory-with-side.html](https://googleprojectzero.blogspot.co.uk/2018/01/reading-privileged-memory-with-side.html)- [http://down.360safe.com/cpuleak_scan.exe](http://down.360safe.com/cpuleak_scan.exe)