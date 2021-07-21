> 原文链接: https://www.anquanke.com//post/id/145003 


# DEFCON CHINA议题解读 | windows10代码安全机制


                                阅读量   
                                **125023**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01b019ae56431acbe3.jpg)](https://p1.ssl.qhimg.com/t01b019ae56431acbe3.jpg)

吃人@dmzlab

## 演讲者

丁川达，2014 年加入腾讯，现任腾讯玄武实验室工程师，主要从事 Windows 平台安全研究。CanSecWest 2016 会议演讲者。

曾从事软件开发相关工作，对于因研发管理问题和开发人员安全意识欠缺而导致的各类漏洞有深入了解。



## 会议议程
- 代码完整性保护
- 执行保护
- 任意代码保护
- 应用程序保护
### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E8%80%85%E5%A6%82%E4%BD%95%E6%94%BB%E5%87%BB%E6%B5%8F%E8%A7%88%E5%99%A8"></a>攻击者如何攻击浏览器

典型的网络浏览器漏洞利用链由三部分组成：

远程代码执行（RCE）漏洞的利用。<br>
特权提升漏洞（EOP）漏洞的利用，用于提权并逃离沙箱。<br>
利用获得的权限来实现攻击者目标的有效载荷（例如勒索软件，植入，侦察等）。<br>
这些攻击的模块化设计，使攻击者能够根据目标选择不同的RCE，EOP和有效载荷组合。因此，现代攻击无处不在地依靠执行任意本地代码来运行其利用的第二阶段和第三阶段。

### <a class="reference-link" name="%E7%BC%93%E8%A7%A3%E4%BB%BB%E6%84%8F%E5%8E%9F%E7%94%9F%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>缓解任意原生代码执行

大多数现代浏览器攻击尝试将内存安全漏洞转化为在目标设备上运行任意本机代码的方法。这种技术非常普遍，因为它为攻击者提供了最简单快捷的途径，使他们能够灵活而均匀地对每个阶段进行阶段化攻击。对于防御来说，防止任意代码执行是及其易用的，因为它可以在不需要事先知道漏洞的情况下大幅限制攻击者的自由范围。为此，Windows 10创作者更新中的Microsoft Edge利用代码完整性保护（CIG）和任意代码保护（ACG）来帮助防御现代Web浏览器攻击。



## Windows10防御机制

#### <a class="reference-link" name="WDEG"></a>WDEG

微软于2017年10月17日正式发布了Windows 10的新版本Fall Creators Update（RS3）。<br>
在此次更新中，微软将其工具集EMET（The Enhanced Mitigation Experience Toolkit）的功能集成到操作系统中，推出了WDEG（Windows Defender Exploit Guard）。

WDEG主要实现以下四项功能：

1.攻击防护（Exploit protection）<br>
通过应用缓解技术来阻止攻击者利用漏洞，可以应用于指定的程序或者系统中所有的程序。

2.攻击面减少（Attack surface reduction）<br>
通过设置智能规则来减少潜在的攻击面，以阻止基于Office应用、脚本、邮件等的攻击。

3.网络保护（Network protection）<br>
扩展Windows Defender SmartScreen的范围，为所有网络相关的操作提供基于信任的防护。

4.受控制文件夹的访问（Controlled folder access）<br>
协助保护系统中的重要文件，使其不会被恶意软件（尤其是加密文件的勒索软件）修改。

User Mode API Hook：<br>
分配/执行/启用执行位的内存区域<br>
创建进程/线程<br>
创建文件/文件映射<br>
获取模块/函数地址

```
export address filter + modules
mshtml.dll
flash*.ocx
jscript*.dll
vbscript.dll
vgx.dll
mozjs.dll
xul.dll
acrord32.dll
acrofx32.dll
acroform.api
```

局限性：<br>
在很大程度上与emet 5.x相同，但也有类似的弱点<br>
User Mode hooks可以被绕过<br>
增加了恶意代码执行的难度但并不能完全阻止。

#### <a class="reference-link" name="CIG%EF%BC%9A%E5%8F%AA%E5%85%81%E8%AE%B8%E5%8A%A0%E8%BD%BD%E6%AD%A3%E7%A1%AE%E7%AD%BE%E5%90%8D%E7%9A%84images"></a>CIG：只允许加载正确签名的images

攻击者在攻击进程中加载images通过以下方式：在进程中加载dll和创建子进程。win10 TH2 推出了两种解决办法防止上述攻击：进程签名策略（process signature policy），子进程策略（child process policy）。

##### <a class="reference-link" name="Process%20Signature%20Policy"></a>Process Signature Policy

[![](https://p4.ssl.qhimg.com/t01fb2dba2830ce9a69.png)](https://p4.ssl.qhimg.com/t01fb2dba2830ce9a69.png)

##### <a class="reference-link" name="Child%20Process%20Policy"></a>Child Process Policy

[![](https://p3.ssl.qhimg.com/t0190363612cddc1599.png)](https://p3.ssl.qhimg.com/t0190363612cddc1599.png)<br>
从Windows 10 1511更新开始，Edge首次启用了CIG并做出了额外的改进来帮助加强CIG：防止子进程创建，由于UMCI策略是按每个进程应用的，因此防止攻击者产生具有较弱或不存在的UMCI策略的新进程也很重要。在Windows 10 1607中，Edge为内容流程启用了无子进程缓解策略，以确保无法创建子进程。

此策略目前作为内容处理令牌的属性强制执行，以确保阻止直接（例如调用WinExec）和间接（例如，进程外COM服务器）进程的启动。

更快地启用CIG策略（Windows 10 Creators更新）：UMCI策略的启用已移至流程创建时间，而不是流程初始化期间。通过消除将不正确签名的DLL本地注入内容进程的进程启动时间差进一步提高可靠性。这是通过利用 UpdateProcThreadAttribute API为正在启动的进程指定代码签名策略来实现的。

局限性：攻击者可以使用自定义加载器加载shellcode来完成攻击，虽然有一定难度但是仍然可以绕过。

#### <a class="reference-link" name="ACG:%E4%BB%A3%E7%A0%81%E4%B8%8D%E8%83%BD%E5%8A%A8%E6%80%81%E7%94%9F%E6%88%90%E6%88%96%E4%BF%AE%E6%94%B9"></a>ACG:代码不能动态生成或修改

尽管CIG提供了强有力的保证，只有经过正确签名的DLL才能从磁盘加载，但在映射到内存或动态生成的代码页后，它不能保证代码页的状态。这意味着即使启用了CIG，攻击者也可以通过创建新代码页或修改现有代码页来加载恶意代码。实际上，大多数现代Web浏览器攻击最终都依赖于调用VirtualAlloc或VirtualProtect等API来完成此操作。一旦攻击者创建了新的代码页，他们就会将其本地代码有效载荷复制到内存中并执行它。

ACG在Windows 10 RS2中被采用。大多数攻击都是通过利用分配或修改可执行内存完成。ACG限制了受攻击的进程中的攻击者能力：阻止创建可执行内存，阻止修改现有的可执行内存，防止映射wx section。启用ACG后，Windows内核将通过强制执行以下策略来防止进程在内存中创建和修改代码页：代码页是不可变的，现有的代码页不能写入，这是基于在内存管理器中进行额外检查来强制执行的，以防止代码页变得可写或被流程本身修改。例如，不再可以使用VirtualProtect将代码页变为PAGE_EXECUTE_READWRITE。无法创建新的未签名代码页。不可使用VirtualAlloc来创建新的PAGE_EXECUTE_READWRITE代码页。

结合使用时，ACG和CIG施加的限制可确保进程只能将已签名的代码页直接映射到内存中。

局限性：OOP JIT需要生成动态代码，若要同时工作，将增加设计的复杂性，并且攻击者可以通过JIT和OOP生成恶意代码。

#### <a class="reference-link" name="JIT"></a>JIT

现代Web浏览器通过将JavaScript和其他更高级别的语言转换为本地代码实现了卓越的性能。因此，它们固有地依赖于在内容过程中生成一定数量的未签名本机代码的能力。JIT功能移入了一个单独的进程，该进程在其独立的沙盒中运行。JIT流程负责将JavaScript编译为本地代码并将其映射到请求的内容流程中。通过这种方式，决不允许直接映射或修改自己的JIT代码页。<br>[![](https://p1.ssl.qhimg.com/t019e5502bb55e83a47.png)](https://p1.ssl.qhimg.com/t019e5502bb55e83a47.png)

#### <a class="reference-link" name="Device%20Guard%20Policy"></a>Device Guard Policy

#### <a class="reference-link" name="%E5%B7%A5%E4%BD%9C%E5%8E%9F%E7%90%86"></a>工作原理

Device Guard 将 Windows 10 企业版操作系统限制为仅运行由受信任的签署人签名的代码，如代码完整性策略通过特定硬件和安全配置所定义，其中包括：

用户模式代码完整性 (UMCI)

新内核代码完整性规则（包括新的 Windows 硬件质量实验室 (WHQL) 签名约束）

带有数据库 (db/dbx) 限制的安全启动

基于虚拟化的安全，用于帮助保护系统内存和内核模式应用与驱动程序免受可能的篡改。

Device Guard 适用于映像生成过程，因此你可以为支持的设备启用基于虚拟化的安全功能、配置代码完整性策略并设置 Windows 10 企业版所需的任何其他操作系统设置。此后，Device Guard 可帮助你保护设备：

安全启动 Windows 启动组件后，Windows 10 企业版可以启动基于 Hyper-V 虚拟化的安全服务，包括内核模式代码完整性。这些服务通过防止恶意软件在启动过程早期运行或在启动后在内核中运行，帮助保护系统核心（内核）、特权驱动程序和系统防护（例如反恶意软件解决方案）。



## 参考链接

[https://hk.saowen.com/a/c349626fb50ebd1cba721ce30b81ea4428f958fb5e3ae6dc24dad321254f11b8](https://hk.saowen.com/a/c349626fb50ebd1cba721ce30b81ea4428f958fb5e3ae6dc24dad321254f11b8)
