
# 侧信道攻击研究——PADDING ORACLE


                                阅读量   
                                **341787**
                            
                        |
                        
                                                                                                                                    ![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/203808/t01c9209b1a44e27d84.jpg)](./img/203808/t01c9209b1a44e27d84.jpg)



## 一. 引言

大家好，我是来自银基安全实验室的Cure，本次为大家带来的是Padding Oracle攻击的相关介绍与实践。

随着Web服务的日益流行，Web数据的安全传输愈发引起业界重视。HTTPS协议的常见实现经历了从SSL到TLS的变化，目前，使用最广泛的TLS协议为TLS 1.2，为各个浏览器普遍支持，而最新TLS 1.3协议，更是在TLS 1.2的基础上简化了交互流程，提高了性能。

然而，目前的许多Web网站，出于种种原因，仍然采用着古老的HTTP协议。HTTP协议对传输的数据不作保护。为了避免诸如密码等敏感信息在网络上直接传输而导致被中间人截获，网站的开发者常常自己实现一套加密机制，典型地有DES、AES等。

相对于经历了长足发展的TLS协议而言，自实现的安全协议往往存在着一定程度的疏漏，为使用者带来安全隐患。攻击DES、AES的方法有很多，Padding Oracle是其中一个，如果该攻击使用得当，可以在不获取key的情况下，达到解密密文和加密明文的能力，在特定场景下能够窃取用户隐私，甚至用于网站提权。

本文仅从Padding Oracle这一侧面入手，探索其基本原理并结合实例进行讲解。文章后续包括以下章节：第二章介绍Padding Oracle的攻击方法；第三章以泛化Web网站为例，阐述通过该攻击获取admin权限的具体流程；第四章尝试性的给相应的漏洞修补方案，使前述攻击失效；第五章使用Timing侧信道作为辅助，再次使能Padding Oracle；第六章讨论Padding Oracle的一些杜绝方式，并提倡使用在安全敏感的网络服务中使能TLS。

希望本文提供的技术探索与实例，能够起到抛转引玉的作用，同时，也为初学者提供些许思路与参考。



## 二. Padding Oracle原理

Oracle Padding是一种通过对DES、AES等block加解密算法的Padding进行调控，根据解密过程是否正常，结合调控内容进行攻击，在无需知道key的前提下达成解密密文或加密明文的效果。下面对其原理进行阐述。



### 2.1 Padding

DES、AES等block cipher加解密算法要求输入内容的长度为block size的整数倍。在加密过程中，若原始数据长度不符合该要求，则在其后添加padding部分以进行补足，在解密过程中，则在解密结果的末尾对padding部分进行移除。

常见的padding方案有PKCS5和PKCS7等，以PKCS5为例，其block size固定为8，padding方案如下：

① 若加密对象的长度是8字节的倍数，则在其后填充8个字节，每个字节内容均为0x08。

② 若加密对象的长度不是8字节的倍数，则在其后补充n个字节（1&lt;=n&lt;=7）使之成为8字节的倍数，每个字节的内容均为n。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011eb778fbff8a4412.png)

### 2.2 AES CBC加密流程

AES CBC的加密流程如下图所示。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010b1e8716a25017b4.png)



其中，plaintext是添加padding后的明文，Initialization Vector称初始化向量IV，由加密算法的调用者提供。

加密流程如下：

① 整个plaintext按照block size拆分为多个组。

② 第一组与IV进行异或运算，运算结果结合加密密钥key经过复杂运算得到第一组ciphertext。

③ 第一组ciphertext作为新的IV，与第二组plaintext进行异或运算，其结果结合加密密钥key经过复杂运算得到第二组ciphertext。

④ 第二组ciphertext作为新的IV，与第三组plaintext进行异或运算，其结果结合加密密钥key经过复杂运算得到第三组ciphertext。

⑤ .依此类推…，直至得到组后一组ciphertext。

⑥ 各组ciphertext组合结果即完整ciphertext，也是加密结果，其长度为block大小的倍数。



### 2.3 AES CBC解密流程

AES的解密过程是加密过程的逆运算，该逆运算与加密过程构成分组对应，具体流程如下图所示。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e7619e9a00049584.png)





其中，解密算法按照如下流程进行：

① ciphertext被按照block size进行分组。

② 倒数第一组ciphertext结合key按照复杂算法进行解密，其结果与相应IV（倒数第二组ciphertext，与加密过程呼应）进行异或，得到倒数第一组plaintext。检测该组plaintext的padding是否合法。若非法，则解密失败，返回相应失败。

③ 倒数第二组ciphertext结合key按照复杂算法进行解密，其结果与相应IV（倒数第三组ciphertext，与加密过程呼应）异或，得到倒数第二组plaintext。

④ 倒数第三组ciphertext结合key按照复杂算法进行解密，其结果与相应IV（倒数第四组ciphertext，与加密过程呼应）异或，得到倒数第三组plaintext。

⑤ 依此类推…，直至得到第一组plaintext。

⑥ 各组plaintext合并完整plaintext，该plaintext末尾带有padding，读取其中最后一个字节的内容可以获得padding长度，从完整plaintext的末尾截取该长度后，得到的数据即解密结果。



### 2.4 Padding Oracle攻击原理

Oracle Padding攻击指的是，在已知密文、IV，能够触发解密，且能够区分解密失败和解密成功的情况下，无需得知key而做到解密密文或加密明文。下面对其原理进行介绍。

如图为原始密文中末尾block的解密环节，其中，cleartext与plaintext同义。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b3717b0142d6a1d4.png)



图中，C15由上一个block中的E7与I15异或得出。其中，I15是末尾block的块解密结果。类似地，有，C14 = I14 ^ E6，C13 = I13 ^ E5，C12 = I12 ^ E4，…

如果我们从0x00~0xFF爆破式地改变E7的值，大多数情况，会使得plaintext包含一个非法的padding；但其中，存在这样一种情形，即C15为0x01，此时plaintext具有合法的padding。

通过改变E7，我们能够将C15强制变为0x01，该情形可以由padding的合法性筛选得出。而此时，有，I15 ^ E`7 = 0x01，推出 I15 = 0x01 ^ E`7。

进一步，能够计算出原始C15 ：C15 = E7 ^ I15 = E7 ^ 0x01 ^ E`7。

一旦取得了C15，就可以继续爆破C14。具体地，首先通过调整E7，使C15为0x02，再通过由0x00~0xFF遍历E6，使得C14 C15为0x02 0x02，该情形同样可以由padding的合法性筛选得出。而此时，有，I14 ^ E`6 = 0x02，推出I14 = 0x02 ^ E`6。

进一步，能够计算出原始C14：C14 = E6 ^ I14 = E6 ^ 0x02 ^ E`6。

依此类推，能够获得全部原始C8~C14，即末尾block的明文。

使用Padding Oracle进行密文解密：假设原始密文由block&lt;1~n&gt;构成，分别对以block&lt;n-1~n&gt;、block&lt;n-2~n-1&gt;、…、block&lt;1~2&gt;，block&lt;iv, 1&gt;使用上述方法，即获得全部明文。若iv未知，则只能获取block n~2的明文，但仍起到了控制未知数据量的效用。

使用Padding Oracle进行明文加密：从block n到block 1方向，调整E系列，方式同上，使C系列呈现为带有合法padding的目标明文。由于这样构造出的iv与原始iv不同，故构造密文解密所得与目标明文无法做到完全一致，但对于特定攻击场景仍有意义。



## 三. 针对泛化Web应用的攻击实施

本章首先给出一个泛化的Web网站，进而以该网站为例，介绍使用Padding Oracle对其实施攻击的方法。



### 3.1 泛化Web应用

本章所涉及的泛化的Web网站采集自PentesterLab，有如下特征：

① 允许注册、登录；

② 具有admin账户，但密码未知。

如图为使用注册并使用frog账户登录时的效果。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bc6ce7ed7b1bb84f.png)

### 3.2 攻击实施

通过观察容易发现，在执行过一次登录后，对该网站相应页面的访问不再需要输入密码，推测Web应用使用了cookie。

通过监测网络得知，携带的cookie示例如下。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0178e432b3a6fb8921.png)



任意更改cookie中auth字符串的值，发送请求，收到报错如下图。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017d1d3a5bf81c7070.png)



由此，推测网站对cookie进行基于AES、DES等带有padding的算法进行解密，而padding的合法与非法是能够通过返回字符串的内容进行区分的。

基于这一点，利用padBuster工具（原理同2.1所述）对auth字符串进行解密，得出其末尾两个block的明文为user=frog。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016707e114ce02cd81.png)



由于iv未知，完整的明文并不可得，但这已经足够我们进行大胆猜测：对于cookie，网站会进行解密，并提取“user=”后面的内容作为当前用户。

进一步，利用padBuster工具（原理同2.1所述），构造密文，使明文含有“user=admin”字符串，得到auth内容示例。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01afab1d38b8c51b1d.png)



向网站发送修改auth为上图字符串的数据包，成功以admin身份登入，达成提权。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f8254f90a1575bce.png)

## 四. 漏洞修复

由于2.2中Padding Oracle攻击实施的关键在于，能够区分解密过程padding是否合法。具体地，当padding非法，则返回“Invalid padding”文字，若padding合法而只是解密内容不符合期许，则报错User not found。

由此，提出漏洞修复方案：令这两种情况的信息输出完全相同。

对于padding非法情况，修改如下图。

[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f544156984a7bcca.png)



对于padding合法但解密内容不符合预期的情况，修改如下图。

[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e2f1d1cb1a6897cb.png)



此时，继续使用padBuster工具按照2.2所述方法进行攻击，会发生失败。



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0160c31878b6aba9d4.png)



由于工具无法区分解密过程中padding合法与非法的情形，故无法实施Padding Oracle攻击。故而，漏洞修复生效。



## 五. 结合Timing侧信道再次攻击

本章以Timing侧信道攻击作为辅助，重新使能解密失败和解密成功两种情形的判别，进而重新使能基于Padding Oracle的Web应用提权。

### 5.1 Timing侧信道简介

所谓Timing侧信道，利用的被攻击对象在不同行为流程下的执行时间的差异，推断被攻击对象的实现细节。以下概念性简介引自我的另一篇文章《侧信道攻击研究 – TIMING》。

假设Web 网站采用了如下代码：

[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015c0049967fbd5d91.png)



其逻辑可以简要归纳为：

① 若用户名不存在，则登录失败；

② 若用户名存在但密码不正确，则登录失败；

③ 只有当用户名和密码都正确，才返回成功。

其中，逻辑①的道理在于，当发生基于字典的爆破攻击时，由于涉及的查表列数只有1列，能够一定程度上减小服务器的开销。同时，由于逻辑①和逻辑②返回的信息字符串完全相同，避免了攻击者根据该信息判断出用户名是否存在，而进行后续针对性的爆破。

然而，看似缜密的设计仍然能够受到Timing侧信道的有效攻击。具体攻击方式如下：

① 攻击者从本地提交post请求，其中，变化username，而保持password为任意固定值，例如“123456”。

② 攻击者统计每次从发出请求起到受到服务器回执所耗费的时间，对于同一组用户名和密码，也可以通过测量多次取平均值、中值等方法消除网络延迟引入的时间抖动

③ 对于统计时间较长的请求，认为其所对应的用户名是存在的。

④ 基于存在的用户名，进一步发动针对性的爆破。

本例中，Timing侧信道的立足点在于用户名是否存在所引入的访问时间的差异。具体地，若用户名不存在，则网站服务器仅执行逻辑①的相关判断，所耗费时间较短；若用户名存在，则网站服务器还需额外执行逻辑②的判断（即使密码错误），所耗费时间较长。由此，虽然用户名存在与否对返回的信息字符串并无影响，但攻击者可以从时间入手，推断出真正存在的用户名。



### 5.2辅助攻击的思路

实施Timing侧信道攻击的要点在于，找到被攻击对象在不同行为流程下执行时间的差异。即便处于一个纯粹的旁观者位置，经过简单的使用，也容易推测，网站的实现流程如下图所示。

[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013848bcd5a4057f4f.png)



显然，解密失败时，对应的是一个时间较短的执行过程，而解密成功时，即便解出的信息有问题，由于涉及数据库访问的I/O行为，是一个耗时较多的过程。基于此差异，虽然解密成功或失败返回的文字信息完全相同，但还是可以通过Timing侧信道进行判别。举例而言，当遍历0x01~0xFF调整单个字节时，第三章的方法是基于返回的内容筛选出padding合法的情形，而基于Timing侧信道，我们认为，耗时最长的情形的padding是合法的。一旦能够判定哪些情形的padding是合法的，使用与第三章相同的方式即可进一步完成对于泛化Web应用的攻击。



### 5.3 辅助攻击的实施

辅助攻击的实施通过修改padBuster实现，且只需将基于网站返回信息字符串的判定改为基于网站对请求的处理时间进行判定即可。然而，站在网站用户的立场上，如何合理地获取请求的处理时间是实施攻击的难点。这一难点的解决用到如下四个技巧。

**1）间接测量处理时间**

通过测量自发出请求至收到网站回执的时间，来反应网站对请求的处理时间。，

**2）通过多次测量减少误差**

对于同一请求，实施多次测量，通过计算时间和减少偶尔性引发的误差。

**3）通过交错测量减少误差**

当自0x01~0xFF调整cookie的某一byte时，基于不同数值的测量并不分别多次进行，而是交替进行多次。即化AAAABBBB为ABABABAB。

**4）通过局部取样减少误差**

当某一byte值的多次测量数据进行求和时，并不使用全部数据，而是使用全部数据排序后位于5%~10%大小区间的这部分。

对于1），诚然，自发送请求到收到回执的时间 = 网络传输时间 + 请求处理时间。然而，网络传输时间与网络状态有关，存在抖动，且抖动大小的量级不亚于执行时间的量级，这为时间的测量引入了较大的不稳定性；而且，请求处理时间与当前服务器中所执行任务的数量，服务本身的忙碌程度等有关，也会为时间的测量引入不稳定性。为此，需要引入多次测量，即2）。然而，AAAABBBB式的测量难以切实减小该误差，因为A和B的测量仍可能处于相差较多的大环境，而ABABABABAB能够减小误差的原因在于，每一轮测量（AB）中，A和B所处的测试环境相对来说是十分接近的，故而，引入了3）。进一步地，考虑到多次测量中，极端值误差较大，较好的方式是取位于中间的一部分参与计算，经验表明，5%~10%效果较好。

基于前述理论，修改代码并重新实施Padding Oracle攻击，能够成功提权，效果如下。



**1）解密密文**



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b4fca4f9648cb4b7.png)



图中，多次出现的小数是多次执行的时间和，单位是微秒；紧随其后的整数是相应字节的调整值，如前所述，该值对应padding合法的情形。



**2）加密明文**



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f08e1e6f3c846b45.png)



图中数字的含义与解密密文的情形相同。



**3）提权成功**



[![](./img/203808/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ebeb4d57c75c37b6.png)

其中，使用的cookie中，auth的内容即加密明文所得的密文字符串。



## 六. Padding Oracle的反思

Padding Oracle所依赖有几下几点：

① 攻击者能够反复访问被攻击对象并触发解密流程。

② 攻击者能够区分解密失败与解密成功这两种情形。

第四章的方法不能彻底杜绝Padding Oracle的攻击，其本质在于，虽然从文字信息上杜绝了对解密失败与解密成功的判别，但并没有杜绝从时间上对两种情形的判别。

基于此，一种思路是，无论解密成功与否，都添加相关的数据库流程，另一个思路是，添加相关的hash，例如，在AES CBC的基础上引入HMAC，使得任何基于密文请求内容的调整，都由于校验失败而直接返回，这样一来，很大程度地减小了差异的可能性。

上述思路在TLS 1.2+中已经全面实现，而另一方面，由于TLS对于不同用户的不同连接，key是动态生成的，也很大程度地消除了自实现安全算法中单一key的隐患。

本文以Padding Oracle为切入点，讨论了常见自实现安全算法与自实现防御手段的局限性。与业界普遍认同的观点相同，本文提倡Web服务在安全敏感的传输场景下使用基于新版的TLS的HTTPS协议，以更好地为用户与服务的信息安全提供保障。



## 参考文献

[1] [https://en.wikipedia.org/wiki/Padding_oracle_attack](https://en.wikipedia.org/wiki/Padding_oracle_attack)

[2] [https://pentesterlab.com/exercises/padding_oracle/course](https://pentesterlab.com/exercises/padding_oracle/course)

[3] Mayer J S D, Sandin J. Time trial: Racing towards practical remote timing attacks[J]. Black Hat US Briefings, 2014.
