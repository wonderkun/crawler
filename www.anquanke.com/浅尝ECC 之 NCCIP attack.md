> 原文链接: https://www.anquanke.com//post/id/204397 


# 浅尝ECC 之 NCCIP attack


                                阅读量   
                                **267391**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t017bc8e3180e115678.jpg)](https://p3.ssl.qhimg.com/t017bc8e3180e115678.jpg)



## 前言

​ 在刚结束的De1CTF中，遇到了自己不怎么常见的有关ECC问题的一道密码学的题目。由于自己之前没怎么接触过，再加上走了点弯路，自己肝了快一天才把这题做出来。做出来后觉得这个问题也挺有意思的，于是记此文章以记录，若有不当之处，还请大佬们斧正。



## De1CTF – ECDH

[赛题附件](https://github.com/JayxV/JayxV.github.io/blob/master/2020/05/05/NCCIP/ECDH.zip)在这里，然后审计代码之后，可以把这个问题概括为：
1. 题目用的是标准曲线：y^2 ≡ x^3 +ax + b (mod p)，并提供a,b,p
1. 函数 Exchange：ECDH问题，生成共享密钥时你提供一个点P，他会用自己的私钥，secret*P生成协商密钥key
1. 函数 Encrypt：用key加密你的输入，加密方式为将key的x和y拼接后于输入简单异或
1. 函数 Backdoor：输入服务端secret值，返回flag
整体流程算是一个标准的ECDH，但在标准的ECDH中，一方应该是无法计算出另一方的私钥的，否则这个算法就GG了。而这一题的漏洞就在于，在密钥交换的过程中，服务端并没有检查你提供的点是否在规定好的曲线上。所以这里的攻击方式就是”No Correctness Check for Input Points” (NCCIP) attacks。

由有限域上椭圆曲线上整数点的加法计算式：

设：已知曲线 y^2 ≡ x^3 +ax + b (mod p) 和 P(x1,y1) 和 Q(x2,y2) ，我们计算R(x3,y3) = P + Q

x3 ≡ k2-x1 – x2 (mod p)

y3 ≡ k(x1-x3) – y1 (mod p)

若P = Q 则 k = (3*x2+a)/(2y1) mod p

若P ≠ Q，则k = (y2-y1)/(x2-x1) mod p

曲线的阶与b值有关，但是我们发现，在整个加法、乘法（从加法引申到乘法是一件极其自然的事）计算的过程中，点R却与曲线的b值无关，所以，如果更改b的值，生成一条新的曲线，且这个曲线的阶有一个很小的因子，比如只有7，那么这个曲线上一定会有阶为7的点。如果我们将这个点传给服务端。而服务端没有检查我们这个点的合法性，直接拿来计算生成key，会产生怎么样的后果呢？

我们假设点P的阶为7，即 7*P = O∞，再设secret值为31

那么服务端就会计算31*P ≡ 3P

由于阶很小，我们可以遍历得到 key = 3P，等价于，我们知道了secret % 7 = 3

所以，我们只要多找这么几个低阶点，多得到几条这样的同余式，最后利用CRT就可以恢复secret了。

【呃，再简要说明一下我们的操作叭，我们更改了b的值，造了一条新的曲线，并且在上面找了一个低阶点。而这个点拿去服务端运算，运算只需要这个点的x坐标，y坐标和曲线的a值，所以可以理解为，因为服务端没有检查输入点的合法性，导致，服务端用的曲线被我们窜改了。】

### <a class="reference-link" name="step1-%E6%89%BE%E5%88%B0%E6%9C%89%E4%BD%8E%E9%98%B6%E7%82%B9%E7%9A%84%E6%9B%B2%E7%BA%BF"></a>step1-找到有低阶点的曲线

​ 我们要找到低阶点，我们就先要找到一条阶有小因子的曲线。

​ 由于sympy分解大数速度似乎有点慢，于是我们直接更改b的值，生成一条新的曲线，然后计算、再去[在线平台](http://www.factordb.com/)分解这条曲线的阶，看看是否有小因子。

​ 有一条曲线，但是上面的生成元点怎么找呢？这里我们改一改，先确定一个点，然后再去确定b值从而确定曲线，然后去计算、分解这个点的阶。

```
x = 0xb55c08d92cd878a3ad444a3627a52764f5a402f4a86ef700271cb17edfa739ca
y = 20
q = 0xdd7860f2c4afe6d96059766ddd2b52f7bb1ab0fce779a36f723d50339ab25bbd
a = 0x4cee8d95bb3f64db7d53b078ba3a904557425e2a6d91c5dfbf4c564a3f3619fa

for _ in range(60):
    y+=1
    b = (y**2 - x**3- a*x)%q
    ecc = EllipticCurve(GF(q), [a,b])
    G = ecc(x,y)
    print(y)
    print(G.order())
```

### <a class="reference-link" name="step2-%E6%89%BE%E5%88%B0%E4%BD%8E%E9%98%B6%E7%82%B9"></a>step2-找到低阶点

有一条阶有小因子的线了，有上面的一个点G，且知道它的阶了，低阶点怎么找呢？

这里有一个很简单的道理，我们知道，77，可以等于7乘以11，也可以等于11乘以7。所以，如果我们这个点G的阶是77，那么，7*P的阶就是11，11*P的阶就是7了。

这里，我们通过上面的脚本得到一个阶为2 * 3 * 5^2 * 83 * 13313 * 45413 *6654245328558174325218919079449691616264872121315671061356825923的点G，从而我们可以得到阶分别为2，3，5，83，13313的点（后面的就不要了，阶太大，之后遍历耗时也太长了，大概一万左右的是我们可以接受的。）

下面的脚本就可以得到一个阶为83的点P

```
x = 0xb55c08d92cd878a3ad444a3627a52764f5a402f4a86ef700271cb17edfa739ca
q = 0xdd7860f2c4afe6d96059766ddd2b52f7bb1ab0fce779a36f723d50339ab25bbd
a = 0x4cee8d95bb3f64db7d53b078ba3a904557425e2a6d91c5dfbf4c564a3f3619fa
y = 314

b = (y^2 - x^3- a*x)%q
ecc = EllipticCurve(GF(q), [a,b])
G = ecc(x,y)
print(G  * 2 * 3 * 5^2  * 13313 * 45413 *6654245328558174325218919079449691616264872121315671061356825923)
```

### <a class="reference-link" name="step3-%E8%AE%A1%E7%AE%97%E5%8D%8F%E5%95%86%E5%AF%86%E9%92%A5"></a>step3-计算协商密钥

我们将这个点P当做我们的公钥传给服务端，他会用secret*P 计算协商密钥key

需要说明的是，由于我们破坏了规则，导致服务端的公钥已经不能用了，况且，其实我们自己也不知道自己的私钥是啥。所以这个协商密钥我们还得利用加密函数来获取。

具体操作见下面交互脚本

```
sh.recvuntil("choice:n")
sh.sendline("Encrypt")
sh.recvuntil("hex):n")
mess = "a"*512
sh.sendline(mess)
sh.recvuntil("The result is:n")
res = sh.recvuntil("n")[:-1]
key = int(mess,16)^int(res,16)
x , y = key &gt;&gt; q.bit_length() , key &amp; ((1 &lt;&lt; q.bit_length()) - 1)
G = (x,y)
```

由于q是256位的，所以key是512位，所以我们传个512位的明文过去。然后异或回来，分离一下，我们就可以得到secret*P这个点了。

### <a class="reference-link" name="step4-%E8%AE%A1%E7%AE%97secret%E7%9A%84%E4%B8%80%E4%B8%AA%E5%89%A9%E4%BD%99"></a>step4-计算secret的一个剩余

知道key了，我们就可以遍历计算secret关于这个低阶的剩余了

```
G = (x,y)    #key
Q = (int(each[0]),int(each[1]))        #我们找到的低阶点Q
for i in range(1,int(each[2])):
    if mul(i,Q) == G:
        reslist.append(i)    #secret的剩余
        N.append(int(each[2]));print (i,int(each[2]))     #secret的剩余对应的阶
        break
```

### <a class="reference-link" name="step5-%E5%88%A9%E7%94%A8CRT%E8%AE%A1%E7%AE%97secret"></a>step5-利用CRT计算secret

```
def CRT(mi, ai):
    M = reduce(lambda x, y: x * y, mi)
    ai_ti_Mi = [a * (M / m) * inverse(M / m, m) for (m, a) in zip(mi, ai)]
    return reduce(lambda x, y: x + y, ai_ti_Mi) % M

secret = CRT(N, reslist)
```

完整exp放在[这里](https://github.com/JayxV/JayxV.github.io/blob/master/2020/05/05/NCCIP/ECDH-exp.zip)了。



## 总结

个人认为，NCCIP问题主要还是因为服务端的曲线被窜改为阶有小因子的不安全的曲线，从而造成了私钥部分信息的泄露。通过这个问题，自己对ECC也有了更进一步的认识。
