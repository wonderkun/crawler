> 原文链接: https://www.anquanke.com//post/id/151220 


# openssl基本密码学操作


                                阅读量   
                                **142139**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01ed932fa23a879b87.jpg)](https://p2.ssl.qhimg.com/t01ed932fa23a879b87.jpg)

本文简述了如何使用OpenSSL实现前述密码算法。



## openssl的基本检查

使用以下命令检测版本，-a可以提供完整数据。

`openssl version

openssl version -a`

### <a class="reference-link" name="speed%20test"></a>speed test

speed测试是openssl跑一下不同算法在你机器上的实际执行速度，这项测试在openssl中是一项非常有指导意义的测试。一方面，他给出了你选择算法的依据，通过实际数据告诉你每个算法能跑多快；另一方面，他可以用来评估不同硬件对算法的加速能力。如果仅仅是给出了选择算法的能力，我们可以得到一个一般性结论，例如chacha20比AES快，但实际上很多CPU带有AESNI指令集，这种情况下AES的执行速度反而会更高。所以运行性能是和执行平台紧密相关的。关于这部分，可以参考Intel对OpenSSL的性能优化（[https://software.intel.com/en-us/articles/improving-openssl-performance](https://software.intel.com/en-us/articles/improving-openssl-performance) ）。

具体的测试方法是openssl speed。后面可以跟算法，只测试特定的算法集。我这里跑了一遍全集，挑几个重点算法说一下性能吧。

<a class="reference-link" name="hash%E7%AE%97%E6%B3%95"></a>**hash算法**
1. sha256，标杆性hash算法，64字节小数据140M/s，8k大数据353M/s。sha512，170/470。hash算法的内部状态越长，在连续计算时的速度越快；
1. sha1，251/768；
1. md5，243/575(你没看错，md5比sha1还慢)；
1. rmd160比sha256还慢，whirlpool比sha256慢，最快的是ghash，小数据4222/9732，但是奇怪的是笔者未查到这是什么算法(openssl list -digest-algorithms的输出里没有)；
1. 最合适的算法，应该就是sha-512/256了吧。很安全，速度比sha256快，长度也不算太长，还能防御LEA(Length extension attack)。
<a class="reference-link" name="%E5%AF%B9%E7%A7%B0%E7%AE%97%E6%B3%95"></a>**对称算法**
1. aes-128-cbc，标杆算法，120/125(M/s)，aes-192，93/103，aes-256，86/88，aes的内部状态越长，在连续计算时的速度越慢，这点和hash正好相反；
1. camellia128，138/167，camellia192，110/128，camellia256，109/124，这是一种大批量数据计算非常优越的算法，AES在计算大批量时性能上升并不快；
1. des比aes慢的多，只有66M/s，3DES更慢，只有25M/s；
1. 没有chacha20；
1. 不考虑chacha20的情况下，最好的算法应该是camellia128，当然，工业标杆是aes-128-cbc。
<a class="reference-link" name="%E9%9D%9E%E5%AF%B9%E7%A7%B0%E7%AE%97%E6%B3%95"></a>**非对称算法**
1. rsa 1024/2048/3072/4096的sign效率分别是8698/1351/453/206(个/s)，verify效率分别是131847/46297/22970/13415，rsa也是随着内部状态上升效率下降的，而且下降非常快，而且verify效率远高于sign；
1. dsa 1024/2048的sign效率分别是9836/3280，verify的效率分别是10584/3616；
1. ecdsa 192/224/256/384的sign效率分别是12696/12672/21016/4383，verify效率分别是3200/5630/9994/1019，能很明显看出来，sign效率比verify高，256位的时候由于某种效应性能达峰，后续直接断崖下跌；
1. ecdh 192/224/256/384的效率为3642/8339/15094/1183，同样能看出这种效应；
1. rsa和ecc不具有互换性，rsa参数选择建议2048，ecc参数选择建议256。
### <a class="reference-link" name="%E5%AF%B9%E7%A7%B0%E5%8A%A0%E8%A7%A3%E5%AF%86"></a>对称加解密

openssl支持多种对称加密算法，可以直接对文件加解密，在使用前，我们首先列出系统上支持的算法。

openssl enc -ciphers

输出很复杂，不列举，我们直接讲我的机器上分析后的结果。
1. 第一段是密码算法，在我这里，支持以下算法：aes, bf, blowfish, camellia, cast, chacha20, des, des3, desx, id(ea), rc2, rc4, seed；
1. 最后一段有可能是模式，在我这里，支持以下模式：ECB，CBC，CFB，OFB，CNT。其中CFB，OFB和CTR(CNT)是可流式的，其余都是块式的，关于加密模式，可以看这篇；
1. 在enc的manpages （[https://www.openssl.org/docs/manmaster/man1/enc.html](https://www.openssl.org/docs/manmaster/man1/enc.html) ）里明确说了，enc不支持CCM或是GCM这类的authenticated encryption，推荐是使用CMS；
例如我们使用比较流行的chacha20来加密一个文件src，里面可以随便写一句话。

openssl enc -chacha20 &lt; src &gt; dst

注意dst应该会比src大。因为默认情况下，openssl会为密码加一个salt，然后把salt保存到加密结果上去，再从passwd+salt里推导出key和IV（默认sha256）。默认的salt为8bytes，合64bits，key为32bytes，合256bits，IV为16bytes，合128bits。具体情况可以用openssl enc -P -chacha20来打印。

另一点让我比较惊讶的就是，chacha20是一种流式算法。如果你采用-aes-128-ecb的话（这是一种典型的块式算法，已经研究的比较透彻了），输出是长度对16对整加16字节，而chacha20的输出纯粹比输入长16个字节。我觉得很好奇，于是就找了这个源码 （[https://gist.github.com/cathalgarvey/0ce7dbae2aa9e3984adc](https://gist.github.com/cathalgarvey/0ce7dbae2aa9e3984adc) ）研究了下。

算法的核心状态机是一个64字节的数组，第一个分组16字节填充固定数据，第二个分组32字节填充key，第三个分组8字节填充nonce，最后8字节填充IV。然后通过一个变形算法，把这个核心状态变成一个out数组，再XOR到目标数据上去。每次输出一个out数组，nonce都会自动增长。

如果他的算法没错的话，chacha20非但是一个流式算法，而且主体算法就是CTR的变形。那么chacha20就会有CTR的几个特性，例如明文-密文对应，加密-解密过程是同一个。而且如果每次nonce不变的话，对CPA的抵抗会有问题。(公司里有个场景正好是这种nonce不能变的)

另外，这个加密过程有几个细节。一个是可以用-a或者-base64开关来获得一个纯文本的结果（当然，代价就是增加空间消耗）。第二个是可以用-k来指定密码，用-kfile来指定密码文件，而不是现场输入。当然，这样做的代价就是可能会记入command history，或者有磁盘记录。最后一个是-z，可以在加密前先做一遍压缩。

相应的，解密指令就是openssl enc -d -chacha20 &lt; dst

另外，openssl还提供了以算法为基础的写法。例如chacha20的加密指令也可以写成这样。openssl chacha20 &lt; src &gt; dst

大家举一反三，此处不在赘述。

### <a class="reference-link" name="%E6%91%98%E8%A6%81%E7%94%9F%E6%88%90"></a>摘要生成

先说一句，本章一般人不需要阅读，性子急的朋友请先看最后一段。

openssl用于摘要的方法主要是dgst。首先老规矩，我们先看有哪些摘要算法。

openssl list -digest-commands

在贝壳这里的机器上，算法基本有这么几类。blake2，gost，md4，md5，rmd160，sha1，sha2。不用说，md4/5，sha1都是不安全的。我查了一下，gost和原生ripemd也是不安全的。blake2，ripemd160，sha2还是安全的。所以推荐算法是blake2，sha2。具体来说算法就是blake2b512，blake2s256，sha224，sha256，sha384，sha512，第一选择是sha256。很可惜，没有sha-512/256。

然后我们就可以用来算hash了。例如

openssl sha256 &lt; src

可以看到输出了吧。

OK，下面要说一个悲伤的事实。为什么我们没听说过人家用这个功能呢？因为linux的coreutils里面，有md5sum和sha256sum。我查了一下，支持blake2，CRC，md5，sha1，sha224，sha256，sha384，sha512。上面数的各种推荐算法，还有最常用的MD5，你都能直接用。不用苦逼的用openssl拼。

所以这一章，其实是废话来着。



## RSA的生成和使用

RSA支持的功能比较全面，加解密，签署验证，还有验证还原操作。可以说是用途最广的一个算法族。

### <a class="reference-link" name="%E5%85%AC%E7%A7%81%E9%92%A5%E5%AF%B9%E7%9A%84%E7%94%9F%E6%88%90%E5%92%8C%E7%AE%A1%E7%90%86"></a>公私钥对的生成和管理

<a class="reference-link" name="%E7%94%9F%E6%88%90%E5%AF%86%E9%92%A5"></a>**生成密钥**

openssl genrsa 2048 &gt; rsa.key

在openssl里，in和out经常和stdin和stdout有相同的含义，两者经常可以互换使用。例如上面指令，其实也可以写成openssl genrsa 2048 -out rsa.key，但是如果用stdout写出，会使得openssl无法控制权限（毕竟它不知道你要写文件）。所以，这样生成的密钥，权限为其他人可读。常规请用-out写出，比较安全。

<a class="reference-link" name="%E6%9F%A5%E7%9C%8B%E5%AF%86%E9%92%A5"></a>**查看密钥**

openssl rsa -text -in rsa.key

可以看到很多数据，modulus，publicExponent，privateExponent，prime1，prime2，exponent1，exponent2，coefficient。具体意义可以在这里查看（[https://stackoverflow.com/questions/5244129/use-rsa-private-key-to-generate-public-key](https://stackoverflow.com/questions/5244129/use-rsa-private-key-to-generate-public-key) ）。

可以注意到，除了最基本的p=prime1，q=prime2，n=modulus，e=publicExponent，d=privateExponent外，openssl还额外保存了三个数，exponent1=d mod (p-1)，exponent2=d mod (q-1)，coefficient=(inverse of q) mod p，为啥我也不明白。关于prime1，prime2的详细解释，请看这篇。

<a class="reference-link" name="%E5%88%86%E7%A6%BB%E5%85%AC%E9%92%A5"></a>**分离公钥**

openssl rsa -pubout &lt; rsa.key &gt; rsa.pub

分离之后可以查看

openssl rsa -text -pubin -in rsa.pub

可以看到，只有modulus和publicExponent了。

另外，你可以把key加密或解密（很多场合下会用到）。方法如下：

openssl rsa -aes128 &lt; rsa.key &gt; rsa.enc

openssl rsa &lt; rsa.enc &gt; rsa.key

很多教程里会告诉你用-des或-3des，根据密码学常识你就知道，这是错的。idea也建议不要用，因此推荐用aes(优先)或者camellia。

### <a class="reference-link" name="%E5%8A%A0%E8%A7%A3%E5%AF%86"></a>加解密

<a class="reference-link" name="%E6%95%B0%E6%8D%AE%E5%8A%A0%E5%AF%86"></a>**数据加密**

openssl rsautl -encrypt -pubin -inkey rsa.pub &lt; src &gt; dst

注意输出长度和位数相等（这里是2048）。

<a class="reference-link" name="%E6%95%B0%E6%8D%AE%E8%A7%A3%E5%AF%86"></a>**数据解密**

openssl rsautl -decrypt -inkey rsa.key &lt; dst &gt; src.new

diff src src.new

注意公钥加密私钥解密。

### <a class="reference-link" name="%E7%AD%BE%E7%BD%B2%E9%AA%8C%E8%AF%81"></a>签署验证

<a class="reference-link" name="%E6%95%B0%E6%8D%AE%E7%AD%BE%E7%BD%B2"></a>**数据签署**

openssl rsautl -sign -inkey rsa.key &lt; src &gt; dst

注意输出长度和位数相等（这里是2048）。

数据验证有多种方法，第一种是直接用rsautl

openssl rsautl -verify -pubin -inkey rsa.pub &lt; dst &gt; src.new

diff src src.new

注意私钥签署公钥验证。

另一种是用pkeyutl，注意这里有两种效果。

openssl pkeyutl -verify -pubin -inkey rsa.pub -sigfile sig &lt; src

openssl pkeyutl -verifyrecover -pubin -inkey rsa.pub &lt; sig

这里就是RSA系列sign算法比较特殊的地方。一般的sign都是验证sig和src是否具有对应关系，RSA的verify直接能解出原始数据来，这也算某种意义上的“验证了对应关系”。所以rsautl的verify，在pkeyutl的通配模式里，其实是verifyrecover。

### <a class="reference-link" name="ECC%E7%9A%84%E7%94%9F%E6%88%90%E5%92%8C%E4%BD%BF%E7%94%A8"></a>ECC的生成和使用

ECC支持签署，验证和derivation。其中签署用的是ECDSA算法（很遗憾，不是EdDSA），Kx用的是ECDH。

<a class="reference-link" name="%E5%85%AC%E7%A7%81%E9%92%A5%E5%AF%B9%E7%9A%84%E7%94%9F%E6%88%90%E5%92%8C%E7%AE%A1%E7%90%86"></a>**公私钥对的生成和管理**

ECC的生成比较特殊。在ECC里，你不止要设定一个长度，而是要选择一条曲线，因此第一步，需要列出所有支持的曲线。

openssl ecparam -list_curves

我这里的数据很长，具体不列了。但是可以看出几个特点：

不支持25519曲线；某几条曲线不支持ECDSA。

随后，你可以选择一个曲线来生成密钥。例如我们选择secp256r1。

openssl ecparam -genkey -name secp256r1 &gt; ecc.key

查看密钥

openssl ec -text &lt; ecc.key

可以看到，ECC的数据就要比RSA简单的多，只有一个priv和一个pub。其余主要是说你用了什么曲线。

分离公钥并查看

openssl ec -pubout &lt; ecc.key &gt; ecc.pub

openssl ec -text -pubin &lt; ecc.pub

其实很多同学看出来了，openssl在处理ECC时和RSA的参数基本是类似的，只是ec和rsa指令的区别而已。对于已经生成好的key而言，我们可以抽离具体的key算法，用一个比较通用的办法来处理公钥提取问题。

openssl pkey -pubout &lt; ecc.key &gt; ecc.pub

pkey指令也可以用于其他方面，例如加解密。具体就不赘述了。

<a class="reference-link" name="%E7%AD%BE%E7%BD%B2%E5%92%8C%E9%AA%8C%E8%AF%81"></a>**签署和验证**

ECC的签署和验证就要借助于pkey指令了，具体来说，是pkeyutl指令。注意，这里的形态和RSA的形态不一样。

openssl pkeyutl -sign -inkey ecc.key &lt; src &gt; sig

openssl pkeyutl -verify -pubin -inkey ecc.pub -sigfile sig &lt; src

这里无法直接解出原始数据，只能验证得到是否正确的结果。ECC是不支持verifyrecover的。

<a class="reference-link" name="derivation"></a>**derivation**

我们先假定你生成了两对key和pub，随后你可以用这两对key和pub推导出一个双方共同的秘密。

openssl pkeyutl -derive -inkey ecc1.key -peerkey ecc2.pub

我们可以看到，这么生成出来的数据是一堆乱码。所以加上hexdump让输出比较可读。

openssl pkeyutl -derive -inkey ecc1.key -peerkey ecc2.pub -hexdump

我们也可以换一个顺序来生成。

openssl pkeyutl -derive -inkey ecc2.key -peerkey ecc1.pub -hexdump

可以看到，结果并没有差别。

key derivation的时候，双方互相给对方发一个pub。随后利用对方的pub和自己的priv计算出一个共享的s。攻击者虽然有双方的pub，然而无法得到s。当然，如我们在这里说过，Mallory永远可以通过拦截pub的发送过程来发出攻击。



## DH的生成和使用

### <a class="reference-link" name="%E7%A7%81%E9%92%A5%E7%94%9F%E6%88%90"></a>私钥生成

生成dh私钥

openssl dhparam -outform PEM -out dhparam.pem 1024

查看私钥

openssl dhparam -in dhparam.pem -text

注意，双方的p和g都是现场约定的，公钥A可以很快计算生成，因此都无需保存。

DH的私钥一般不用于加密和签署（你看，他连公钥都没有）。DH是一个Kx算法，因此DH的私钥只用于derivation操作。

### <a class="reference-link" name="derivation"></a>derivation

根据pkeyutl的manpage （[https://www.openssl.org/docs/manmaster/man1/pkeyutl.html](https://www.openssl.org/docs/manmaster/man1/pkeyutl.html) ），dh的私钥应当支持derivation操作。然而杯具的是，我实际测试openssl pkeyutl -derive -inkey dhparam1.pem -peerkey dhparam2.pem无法执行，不知道是不是因为dhparam都是priv的缘故。但是dhparam里确实没有生成公钥的参数。

无论如何，在nginx里，dhparam是一个重要参数。如果你使用默认的dhparam，会被警告不安全。



## DSA的生成和使用

首先，DSA只支持签署和验证。

### <a class="reference-link" name="%E5%85%AC%E7%A7%81%E9%92%A5%E5%AF%B9%E7%9A%84%E7%94%9F%E6%88%90"></a>公私钥对的生成

和RSA非常像，但是有点区别。

openssl dsaparam -genkey 2048 &gt; dsa.key

另外注意，dsaparam参数是不支持加密的。如果要加密，需要写成这个样子。

openssl dsaparam -genkey 2048 | openssl dsa -aes128 &gt; dsa.key

同类，如果要读取内容的话，可以这么做。

openssl dsa -text &lt; dsa.key

剥离公钥这么做。

openssl dsa -pubout &lt; dsa.key &gt; dsa.pub

我们把公钥和私钥分别打出来，可以发现，公钥的要素是pub，P，Q，G。私钥多一项priv。

### <a class="reference-link" name="%E7%AD%BE%E7%BD%B2%E9%AA%8C%E8%AF%81"></a>签署验证

这是另一个奇怪的地方。根据pkeyutl的manpage （[https://www.openssl.org/docs/manmaster/man1/pkeyutl.html](https://www.openssl.org/docs/manmaster/man1/pkeyutl.html) ），DSA的key支持sign(而且只支持sign)。可是我在实验openssl pkeyutl -sign -in src -inkey dsa.key -out sig的时候，又失败了。这个例子是直接抄的manpage，错误提示是Public Key operation error。如果有朋友知道为什么，欢迎沟通交流。

审核人：yiwang   编辑：边边
