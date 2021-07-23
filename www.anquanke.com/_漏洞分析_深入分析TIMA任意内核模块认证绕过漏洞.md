> 原文链接: https://www.anquanke.com//post/id/85316 


# 【漏洞分析】深入分析TIMA任意内核模块认证绕过漏洞


                                阅读量   
                                **82003**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：bugs.chromium.org
                                <br>原文地址：[https://bugs.chromium.org/p/project-zero/issues/detail?id=960](https://bugs.chromium.org/p/project-zero/issues/detail?id=960)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t014705f7f0b125156e.jpg)](https://p2.ssl.qhimg.com/t014705f7f0b125156e.jpg)



**翻译：**[**shan66******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：140RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

<br>

**前言**

为了确保Android设备中Linux内核的完整性，三星推出了一个名为“lkmauth”的功能。该功能的最初目的是，确保只有三星核准的那些内核模块才可以加载到Linux内核中。

<br>

**TIMA任意内核模块认证绕过漏洞分析**

每当内核尝试载入内核模块时，系统就会用到“lkmauth”功能。在加载内核模块之前，内核首先会加载“lkmauth”的trustlet，并发送一个请求，来验证模块的完整性。

由于三星设备使用了两个不同的TEE，所以对于每个TEE都单独实现了相应的“lkmauth”功能。

在使用QSEE TEE（它使用了内核配置TIMA_ON_QSEE）的设备上，使用“tima_lkmauth”的trustlet来验证待加载的内核模块的完整性。当然，这个trustlet本身是相当简单的——它提供了一个硬编码的列表，来保存所有“可允许”的内核模块的SHA1哈希值。如果当前待加载的内核模块的SHA1没有出现在硬编码的列表中，那么它就会被拒绝。

对于使用MobiCore TEE（使用内核配置TIMA_ON_MC20）的设备而言，它们会通过“ffffffff00000000000000000000000b.tlbin”trustlet来验证待加载内核模块的完整性。然而，在这种情况下，其流程会稍微有点复杂，下面简单介绍加载模块的具体步骤：

1. [如果trustlet尚未加载]：加载trustlet。

2. [如果已批准的哈希值列表尚未加载]：向trustlet发送请求，以便加载已批准的SHA1哈希签名列表。

3. 将存放内核模块的缓冲区传递给trustlet进行验证。如果该内核模块的SHA1哈希值不在先前加载的已批准哈希值列表中，则会被拒绝。

已经批准的模块的哈希值组成的列表，将作为设备固件的一部分，存储在文件“/system/lkm_sec_info”中。该文件的结构如下所示： 

```
&lt;LIST_OF_APPROVED_SHA1_HASHES&gt; || &lt;RSA-SHA1(LIST_OF_APPROVED_HASHES)&gt;
```

RSA签名本身会使用PKCS＃1 v1.5进行填充，其中BT = 1，PS是0xFF字节的常量字符串。

用于验证签名的公钥，我们可以通过静态分析方法从trustlet中找到。在trustlet的自身代码中，2048位的模数（N）是以反向字节顺序硬编码的形式存在的。经验证，在许多不同的设备和版本（如GT-I9300、SM-P600、SM-G925V等）中，都使用了相同的常量模量。这个模数本身是

```
23115949866714941391353337177289175219285878274139282906616665210063884406381659531323213685988661310147714551519208211866717752764819593136041821730036424774768373518089158559738346399417711215445691103520271683108620470478217421253901045241463596145712323679479119182170178158376677146612087823704797563128645982031650495998390419939015769566125776929249878666421780560391442439477189264423758971325406632562977618217815844688082799802924540355522191958147326121713251815752299744182840538928330568160188518794896256711464745438125835732128172016078553039694575936536720388879378619731459541542508235684590815108447
```

这里使用的公钥指数为3。

发送到trustlet的请求缓冲区具有以下结构： 



```
/* Message types for the lkmauth command */
typedef struct lkmauth_hash_s `{`
uint32_t cmd_id;
uint32_t hash_buf_start;/* starting address of buf for ko hashes */
uint32_t hash_buf_len;/* length of hash buf, should be multiples of 20 bytes */
uint8_t ko_num;/* total number ko */
`}` __attribute__ ((packed)) lkmauth_hash_t;
```

通过对trustlet中处理这个命令的代码进行逆向工程，得到了处理函数高级逻辑代码，具体如下所示： 



```
int load_hash_list(char* hash_buf_start, uint32_t hash_buf_len, uint8_t ko_num) `{`
  //Checking the signature of the hash buffer, without the length of the
  //public modulus (256 bytes = 2048 bits)
  uint32_t hash_list_length = hash_buf_len - 256;
  char* rsa_signature_blob = hash_buf_start + hash_list_length;
  if (verify_rsa_signature(hash_buf_start, hash_list_length, rsa_signature_blob))
    return SIGNATURE_VERIFICATION_FAILURE;
  //Copying in the verified hashes into the trustlet
  //SHA1 hashes are 20 bytes long (160 bits) each
  //The maximal number of copied hashes is 0x23
  //g_hash_list is a list in the BSS section of the trustlet
  //g_num_hashes is also in the BSS section of the trustlet
  uint8_t i;
  for (i=0; i&lt;ko_num &amp;&amp; i&lt;0x23; i++) `{`
    memcpy(g_hash_list + i*20, hash_buf_start + i*20, 20);
  `}`
  g_num_hashes = i;
  return SUCCESS;
`}`
```

问题在于，上述代码包含了一个逻辑缺陷：没有对“ko_num”字段进行相应的验证，以确保其匹配哈希值列表的实际长度。这意味着攻击者能够欺骗trustlet来加载额外的“允许哈希值”，即使它们不是已经签名的blob的一部分。为此，可以在提供与哈希值列表的原始长度匹配的"hash_buf_len"的时候，通过提供一个大于实际哈希值数量的“ko_num”字段来达到这一目的。然后，攻击者可以在缓冲器中的签名blob之后提供任意的SHA1哈希值，从而导致这些额外的哈希值也会被复制到已经批准的可信哈希值列表中。

下面给出此类攻击的一个具体例子： 



```
hash_buf_start = &lt;ORIGINAL_SIGNED_HASH_LIST&gt; ||
                   &lt;RSA-SHA1(ORIGINAL_SIGNED_HASH_LIST)&gt; ||
                   &lt;4 GARBAGE BYTES&gt; ||
                   &lt;ATTACKER_CONTROLLED_SHA1_HASH&gt;
  hash_buf_len = len(&lt;ORIGINAL_SIGNED_HASH_LIST&gt;) +
                 len(&lt;RSA-SHA1(ORIGINAL_SIGNED_HASH_LIST)&gt;)
  ko_num = (&lt;ORIGINAL_SIGNED_HASH_LIST&gt;/20) + ceil(256/20) + 1
```

由于“/system/lkm_sec_info”中的原始哈希值列表长度总是很短（例如从来不超过8）的，因此表达式（（&lt;ORIGINAL_SIGNED_HASH_LIST&gt; / 20）+ ceil（256/20）+1）的值永远不会大于22。但是它仍然小于0x23（35）个哈希值的硬编码下限，这意味着上面的代码能够正常执行所提供的命令。此后，已批准的哈希值列表将会变成如下所示的结构： 



```
original_approved_hash_1
original_approved_hash_2
...
original_approved_hash_n
bytes_00_to_20_of_rsa_signature
bytes_20_to_40_of_rsa_signature
...
bytes_240_to_256_of_rsa_signature || 4_garbage_bytes
attacker_controlled_sha1_hash
```

实际上，这就将攻击者控制的SHA1哈希值插入到了已批准的哈希值列表中，从而成功绕过了签名验证。

该漏洞的一种利用方法是，控制一个可以加载内核模块的进程，然后将感染的哈希值列表请求发送给trustlet。例如，“system_server”进程就具有这种能力，同时还能够加载trustlet，并与之进行通信（我们已经在SM-G925V的默认SELinux策略中进行了相应的验证）： 



```
allow system_server mobicore-user_device : chr_file `{` ioctl read write getattr lock append open `}` ; 
allow system_server mobicoredaemon : unix_stream_socket connectto ; 
allow system_server mobicore_device : chr_file `{` ioctl read write getattr lock append open `}` ;
```

将受感染的哈希值列表加载到trustlet之后，攻击者就可以尝试加载与刚才插入到列表中的SHA1哈希值相匹配的内核模块了。需要注意的是，加载模块的第一次尝试将会失败，因为内核将尝试加载已批准的哈希值列表本身，但是trustlet将检测到此情况并返回错误代码RET_TL_TIMA_LKMAUTH_HASH_LOADED。这样的话，内核会做一个标记，指出列表已经加载好了——也就是说，下一次加载模块的时候，就不会重新加载这个列表了： 



```
...
else if (krsp-&gt;ret == RET_TL_TIMA_LKMAUTH_HASH_LOADED) `{`
  pr_info("TIMA: lkmauth--lkm_sec_info already loadedn");
  ret = RET_LKMAUTH_FAIL;
  lkm_sec_info_loaded = 1;
`}`
...
```

之后，第二次尝试加载已经感染的模块的时候，就会成功了，因为它的哈希值已经位于已批准的哈希值列表中了。
