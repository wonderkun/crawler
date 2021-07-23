> 原文链接: https://www.anquanke.com//post/id/90992 


# 攻击者部署ICS攻击框架“Triton”导致关键基础设施中断服务（下）


                                阅读量   
                                **84026**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Blake Johnson, Dan Caban, Marina Krotofil, Dan Scali, Nathan Brubaker, Christopher Glyer，文章来源：fireeye.com
                                <br>原文地址：[https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html](https://www.fireeye.com/blog/threat-research/2017/12/attackers-deploy-new-ics-attack-framework-triton.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/dm/1024_672_/t01bd2ebd861a9d7ba5.jpg)](https://p4.ssl.qhimg.com/dm/1024_672_/t01bd2ebd861a9d7ba5.jpg)

> 本文是Fireeye针对一次工业安全系统攻击事件的分析，本文是该文章的上下部分，主要介绍了威胁模型、攻击场景以及技术分析。

## 传送门

[攻击者部署ICS攻击框架“Triton”导致关键基础设施中断服务（上）](https://www.anquanke.com/post/id/91002)



## 五、安全仪表系统威胁模型及攻击场景

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016851b75feb91ba90.jpg)

图2. 网络安全及控制安全的时间关系图

针对ICS的破坏性攻击活动的生命周期与其他类型的网络攻击类似，但其中存在几个关键的区别点。首先，攻击者的任务是破坏正常业务流程，而不是窃取数据。其次，攻击者必须事先侦察OT信息，具备足够多的专业知识才能理解如何控制工业生产流程并成功操纵该流程。

图2表示的是工业流程控制环境中网络安全及安全控制之间的关系。即使网络安全防护措施失效，安全控制也可以防止出现物理损害后果。为了能让攻击活动造成最大程度的物理损坏，网络攻击者还需要绕过安全控制机制。

成功搞定SIS后，攻击者可以通过各种方式发起后续攻击活动，SIS威胁模型如下所示：

**攻击选项1：**使用SIS关闭生产流程。

场景：攻击者可以重新编程SIS业务逻辑，关闭实际上处于安全状态的某个生产流程。换句话说，攻击者可以让SIS出现误报。

后果：由于生产流程停滞，工厂重启该流程的程序非常复杂，因此会带来资金损失。

**攻击选项2：**重新编程SIS以允许不安全状态存在

场景：攻击者可以重新编程SIS业务逻辑，允许不安全状态持续存在。

后果：由于SIS无法正常发挥作用，导致安全风险提高，容易造成物理损坏后果（如对生产设备、产品、生产环境以及人身安全带来影响）。

**攻击选项3：**重新编程SIS以允许不安全状态存在，同时使用DCS来创建不安全的状态或危险状态。

场景：攻击者可以使用DCS来操控生产流程，将其置于不安全状态中，同时阻止SIS正常发挥作用。

后果：会影响人身安全、生产环境安全，也会对生产设备造成损坏，损坏程度取决于生产流程所受的物理限制条件以及工厂整体设计方案。



## 六、攻击意图分析

我们有一定的把握认为攻击者的长期目标是研发能够导致物理损坏后果的攻击能力。之所以得出这个结论，原因是攻击者最初在搞定DCS并站稳脚跟后，他们本可以操控生产流程或者关闭整个工厂，然而他们却选择继续攻击SIS系统。一旦搞定DCS以及SIS系统，攻击者就可以实施攻击行为，在工厂的物理及机械限制条件内造成最大程度的损坏。

一旦进入SIS网络后，攻击者开始使用事先生成的TRITON攻击框架，通过TriStation协议与SIS控制器进行交互。攻击者本来可以发出挂起命令关闭某个生产流程，也可以向SIS控制器中上传漏洞代码导致SIS控制器故障，然而，他们选择在一段时间内进行多次尝试，意图是在目标环境中开发并使用SIS控制器的功能控制逻辑。虽然攻击脚本中某些检查条件没有通过，最终导致攻击者无法顺利完成攻击意图，但他们仍在坚持不懈地努力尝试这一过程。这表明攻击者希望造成某些特定后果，而不单单是关闭某个生产流程那么简单。

值得注意的是，我们曾多次在攻击活动中观察到攻击者曾长期入侵过ICS，但他们并没有破坏或禁用运营流程。比如，俄罗斯攻击者（如沙虫组织）对西方国家ICS的入侵行为曾持续多年，但期间他们并没有中断生产流程。



## 七、恶意软件功能摘要

TRITON攻击工具包含许多功能，其中包括读写程序、读写单个函数以及查询SIS控制器状态功能。然而，`trilog.exe`样本中只用到了其中一些功能（攻击者并没有充分使用TRITON的所有侦察功能）。

TRITON恶意软件可以与Triconex SIS控制器通信（比如，可以发送诸如**halt**之类的特定命令或者读取内存数据），使用攻击者定义的载荷远程编程控制器逻辑。在Mandiant分析的TRITON样本中，攻击者将一个额外程序添加到Triconex控制器的执行表中。该样本没有修改合法的原始程序，希望控制器能继续保持正常工作状态，不出现故障或异常现象。如果控制器出现故障，TRITON会尝试让控制器返回运行状态。如果控制器没有在预期时间内回到运行状态，该样本会使用无效数据覆盖恶意程序，掩盖其攻击行为。



## 八、建议

如果资产方想防御此类攻击事件，他们应该考虑部署如下控制机制：

1、如果技术上可以实现，应该将安全系统网络与生产流程控制及信息系统网络相互隔离。能够编程SIS控制器的工程工作站不应该与任何DCS流程控制或信息系统处于同一个网络中。

2、有些硬件设施可以通过物理控制功能，实现对控制器的安全编程，资产方应该部署这类硬件设施。这些硬件设施通常采用由实体钥匙控制的功能切换模式。对于Triconex控制器而言，只有在事先规划的编程任务期间，才能将钥匙拧到`PROGRAM`模式。

3、切换为关键状态时，需要采用切实有效的状态切换管理机制，同时要定期审核当前的关键状态。

4、任何程序如果需要依赖SIS提供的数据，请务必使用单向网关，不要使用双向网关。

5、如果服务器或工作站终端可以通过TCP/IP协议访问SIS系统，请使用严格的访问控制及应用程序白名单机制。

6、监控ICS网络流量，特别注意不在预期内的通信流量以及其他异常行为。

[![](https://p4.ssl.qhimg.com/t01f390570380022cee.png)](https://p4.ssl.qhimg.com/t01f390570380022cee.png)

图3. Triconex钥匙开关（[原图](https://images-na.ssl-images-amazon.com/images/I/41jr93jKzML._SX466_.jpg)



## 九、附录：技术分析

[![](https://p5.ssl.qhimg.com/t01b0e13e24db7a3398.jpg)](https://p5.ssl.qhimg.com/t01b0e13e24db7a3398.jpg)

图4. TRITON架构及攻击场景

攻击者将TRITON部署在运行着微软Windows操作系统的SIS工程工作站上，并将该恶意软件名字伪装成合法的Triconex Trilog应用程序。合法的Trilog程序用来检查日志，属于TriStation应用程序集中的一个程序。这款恶意软件原来为python脚本，通过Py2EXE编译成二进制程序，需要依赖包含标准开源Python库的一个zip文件，也需要依赖攻击者开发的Triconex攻击框架，以便与Triconex控制器交互。除了可执行文件之外，攻击者还使用了两个二进制文件，分别为`inject.bin`（恶意函数代码）以及`imain.bin`（恶意控制逻辑），这两个文件为控制器的载荷文件。这些文件名被硬编码在经过Py2EXE编译的python脚本中。

`Trilog.exe`可以接受来自命令行的1个参数，该参数为目标Triconex设备的单个IP地址。恶意软件并没有利用TRITON底层库支持的Triconex设备发现功能，相反，为了探测环境中的所有目标控制器，恶意软件需要多次调用`trilog.exe`，每次调用针对一个IP地址。`trilog.exe`执行后会检查控制器的状态，然后使用TriStation协议读取公开的配置信息。如果控制器处于运行状态，`trilog.exe`会编码两个载荷文件（即`inject.bin`以及`imain.bin`），将这两个载荷文件传递给通信库，以便将其添加到控制器的程序内存及执行表中。

载荷文件插入Triconex控制器的内存后，攻击脚本开始执行倒计时流程，定期检查控制器的状态。如果检测到错误状态，通信库中的**SafeAppendProgramMod**方法会尝试重置控制器，使用TriStation协议命令将控制器恢复为上一个状态。如果恢复失败，`trilog.exe`会尝试将一个小型的“傀儡”程序写入内存中。我们认为这是一种反取证技术，目的是用来隐藏Triconex控制器上攻击者使用过的攻击代码。

Mandiant与资产方通力合作，在实验室环境中使用真实有效的Triconex控制器来运行`trilog.exe`，随后发现了恶意软件中存在一个条件检查过程，检查过程会阻止载荷文件持续驻留在目标环境中。经Mandiant确认，如果修改攻击脚本，移除这个检查过程，那么载荷文件就会驻留在控制器内存中，并且控制器可以继续保持运行状态。

TRITON实现了TriStation协议，该协议也是合法TriStation应用程序所使用的协议，用来对控制器进行配置。

攻击者创建了名为**TsHi的**一个高级接口，通过该接口，攻击者可以使用TRITON框架构建攻击脚本。该接口提供了侦察及攻击功能。这些功能可以接受用户输入的二进制数据，经过代码签名检查及校验和检查后，再将这些数据传递给底层库进一步序列化处理，以便在网络上传输。

攻击者还构建了名为**TsBase**的一个模块，该模块包含可以被**TsHi**调用的一些函数，可以将攻击者的攻击意图转化为正确的TriStation协议功能代码。对于某些特定功能而言，该模块还可以将数据打包、填充，以转换成正确的格式。

此外，攻击者还使用了另一个模块，名为**TsLow**，该模块实现了TriStation UDP总线（wire）协议。`TsBase`库主要依赖的是`ts_exec`方法。`ts_exec`方法接受功能代码以及预期的响应代码，序列化命令载荷后使用UDP进行传输。收到控制器返回的响应数据后，该方法会检查响应数据是否与预期值相匹配，如果匹配则返回相应的数据结构，否则返回一个**False**对象。

**TsLow**还提供了一个connect方法，用来检查与目标控制器的通连关系。如果调用该方法时没有使用任何参数作为目标地址，则该方法会运行detect_ip这个函数来发现设备。该方法的工作原理是使用IP广播，实现TriStation协议上的“ping”消息，以查找经过当前路由器可达的控制器。



## 十、IOC

|**文件名**|**哈希值**
|------
|trilog.exe|MD5: 6c39c3f4a08d3d78f2eb973a94bd7718SHA-256:e8542c07b2af63ee7e72ce5d97d91036c5da56e2b091aa2afe737b224305d230
|imain.bin|MD5: 437f135ba179959a580412e564d3107fSHA-256:08c34c6ac9186b61d9f29a77ef5e618067e0bc9fe85cab1ad25dc6049c376949
|inject.bin|MD5: 0544d425c7555dc4e9d76b571f31f500SHA-256:5fc4b0076eac7aa7815302b0c3158076e3569086c4c6aa2f71cd258238440d14
|library.zip|MD5: 0face841f7b2953e7c29c064d6886523SHA-256:bef59b9a3e00a14956e0cd4a1f3e7524448cbe5d3cc1295d95a15b83a3579c59
|TS_cnames.pyc|MD5: e98f4f3505f05bf90e17554fbc97bba9SHA-256:2c1d3d0a9c6f76726994b88589219cb8d9c39dd9924bc8d2d02bf41d955fe326
|TsBase.pyc|MD5: 288166952f934146be172f6353e9a1f5SHA-256:1a2ab4df156ccd685f795baee7df49f8e701f271d3e5676b507112e30ce03c42
|TsHi.pyc|MD5: 27c69aa39024d21ea109cc9c9d944a04SHA-256:758598370c3b84c6fbb452e3d7119f700f970ed566171e879d3cb41102154272
|TsLow.pyc|MD5: f6b3a73c8c87506acda430671360ce15SHA-256:5c776a33568f4c16fee7140c249c0d2b1e0798a96c7a01bfd2d5684e58c9bb32
|sh.pyc|MD5: 8b675db417cc8b23f4c43f3de5c83438SHA-256:c96ed56bf7ee85a4398cc43a98b4db86d3da311c619f17c8540ae424ca6546e1



## 十一、检测规则

```
rule TRITON_ICS_FRAMEWORK
`{`
      meta:
          author = "nicholas.carr @itsreallynick"
          md5 = "0face841f7b2953e7c29c064d6886523"
          description = "TRITON framework recovered during Mandiant ICS incident response"
      strings:
          $python_compiled = ".pyc" nocase ascii wide
          $python_module_01 = "__module__" nocase ascii wide
          $python_module_02 = "&lt;module&gt;" nocase ascii wide
          $python_script_01 = "import Ts" nocase ascii wide
          $python_script_02 = "def ts_" nocase ascii wide  

          $py_cnames_01 = "TS_cnames.py" nocase ascii wide
          $py_cnames_02 = "TRICON" nocase ascii wide
          $py_cnames_03 = "TriStation " nocase ascii wide
          $py_cnames_04 = " chassis " nocase ascii wide  

          $py_tslibs_01 = "GetCpStatus" nocase ascii wide
          $py_tslibs_02 = "ts_" ascii wide
          $py_tslibs_03 = " sequence" nocase ascii wide
          $py_tslibs_04 = /import Ts(Hi|Low|Base)[^:alpha:]/ nocase ascii wide
          $py_tslibs_05 = /modules?version/ nocase ascii wide
          $py_tslibs_06 = "bad " nocase ascii wide
          $py_tslibs_07 = "prog_cnt" nocase ascii wide  

          $py_tsbase_01 = "TsBase.py" nocase ascii wide
          $py_tsbase_02 = ".TsBase(" nocase ascii wide 

          $py_tshi_01 = "TsHi.py" nocase ascii wide
          $py_tshi_02 = "keystate" nocase ascii wide
          $py_tshi_03 = "GetProjectInfo" nocase ascii wide
          $py_tshi_04 = "GetProgramTable" nocase ascii wide
          $py_tshi_05 = "SafeAppendProgramMod" nocase ascii wide
          $py_tshi_06 = ".TsHi(" ascii nocase wide  

          $py_tslow_01 = "TsLow.py" nocase ascii wide
          $py_tslow_02 = "print_last_error" ascii nocase wide
          $py_tslow_03 = ".TsLow(" ascii nocase wide
          $py_tslow_04 = "tcm_" ascii wide
          $py_tslow_05 = " TCM found" nocase ascii wide  

          $py_crc_01 = "crc.pyc" nocase ascii wide
          $py_crc_02 = "CRC16_MODBUS" ascii wide
          $py_crc_03 = "Kotov Alaxander" nocase ascii wide
          $py_crc_04 = "CRC_CCITT_XMODEM" ascii wide
          $py_crc_05 = "crc16ret" ascii wide
          $py_crc_06 = "CRC16_CCITT_x1D0F" ascii wide
          $py_crc_07 = /CRC16_CCITT[^_]/ ascii wide  

          $py_sh_01 = "sh.pyc" nocase ascii wide  

          $py_keyword_01 = " FAILURE" ascii wide
          $py_keyword_02 = "symbol table" nocase ascii wide  

          $py_TRIDENT_01 = "inject.bin" ascii nocase wide
          $py_TRIDENT_02 = "imain.bin" ascii nocase wide  

      condition:
          2 of ($python_*) and 7 of ($py_*) and filesize &lt; 3MB
`}`
```
