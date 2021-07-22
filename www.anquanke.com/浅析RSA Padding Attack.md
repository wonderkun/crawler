> 原文链接: https://www.anquanke.com//post/id/158944 


# 浅析RSA Padding Attack


                                阅读量   
                                **232499**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0129f7f5a99268bd88.jpg)](https://p0.ssl.qhimg.com/t0129f7f5a99268bd88.jpg)

## 前言

近日在复盘一些Crypto的题目，做到了N1CTF的一道rsapadding，进行了一些拓展，于是进行了一些分析记录，有了这篇文章



## 题目分析

题目已开源在

```
https://github.com/Nu1LCTF/n1ctf-2018/tree/master/source/crypto/rsapadding
```

主要代码为

```
m = '*****************'
n = 21727106551797231400330796721401157037131178503238742210927927256416073956351568958100038047053002307191569558524956627892618119799679572039939819410371609015002302388267502253326720505214690802942662248282638776986759094777991439524946955458393011802700815763494042802326575866088840712980094975335414387283865492939790773300256234946983831571957038601270911425008907130353723909371646714722730577923843205527739734035515152341673364211058969041089741946974118237091455770042750971424415176552479618605177552145594339271192853653120859740022742221562438237923294609436512995857399568803043924319953346241964071252941
e = 3
welcom()
if cmd():
    f = open("/root/crypto/file.py")
    print(f.read())
    return
mm = bytes_to_long(m)
assert pow(mm, e) != pow(mm, e, n)
sys.stdout.write("Please give me a padding: ")
padding = input().strip()
padding = int(sha256(padding.encode()).hexdigest(),16)
c = pow(mm+padding, e, n)
print("Your Ciphertext is: %s"%c)
```

意思很简单<br>
1.pow(mm, e) != pow(mm, e, n)<br>
2.输入一个值<br>
3.将输入的值sha256，记做padding<br>
4.利用rsa加密m+padding<br>
值得注意的是，e=3，padding可控<br>
那么我们拥有的条件只有

```
n,e,c,padding
```

所以这里的攻击肯定是要从可控的padding入手了



## 初步推导

我们可以随便构造一对已知padding的密文，得到<br><br>[![](https://p0.ssl.qhimg.com/t01a17c1e5481d745b3.png)](https://p0.ssl.qhimg.com/t01a17c1e5481d745b3.png)<br><br>
此时，我们可以设<br><br>[![](https://p1.ssl.qhimg.com/t017a36793ac335d19e.png)](https://p1.ssl.qhimg.com/t017a36793ac335d19e.png)<br><br>
利用这两个式子，我们可以得到如下线性关系<br><br>[![](https://p2.ssl.qhimg.com/t018ae5e413a4113865.png)](https://p2.ssl.qhimg.com/t018ae5e413a4113865.png)<br><br>
即方程形式为<br><br>[![](https://p4.ssl.qhimg.com/t01d7adda10243b748c.png)](https://p4.ssl.qhimg.com/t01d7adda10243b748c.png)<br><br>
其中<br><br>[![](https://p3.ssl.qhimg.com/t01f72c6a4d719b6fba.png)](https://p3.ssl.qhimg.com/t01f72c6a4d719b6fba.png)<br><br>
即<br><br>[![](https://p0.ssl.qhimg.com/t012551219878a1faf3.png)](https://p0.ssl.qhimg.com/t012551219878a1faf3.png)<br><br>
我们有<br><br>[![](https://p3.ssl.qhimg.com/t011a5591666a5239bf.png)](https://p3.ssl.qhimg.com/t011a5591666a5239bf.png)<br><br>
我们知道<br><br>[![](https://p5.ssl.qhimg.com/t0190ee12d0ab122798.png)](https://p5.ssl.qhimg.com/t0190ee12d0ab122798.png)<br><br>
那么将其带入得到<br><br>[![](https://p4.ssl.qhimg.com/t0104f7ddd0468ab957.png)](https://p4.ssl.qhimg.com/t0104f7ddd0468ab957.png)<br><br>
我们将c1展开得到<br><br>[![](https://p2.ssl.qhimg.com/t01a8d538c73f44a94e.png)](https://p2.ssl.qhimg.com/t01a8d538c73f44a94e.png)<br><br>
我们将这个式子带入得到<br><br>[![](https://p0.ssl.qhimg.com/t01f8beba6fa24abf75.png)](https://p0.ssl.qhimg.com/t01f8beba6fa24abf75.png)<br><br>
于是便一筹莫展



## 可求证明

上述的推导我们漏了一个非常重要的信息<br><br>[![](https://p0.ssl.qhimg.com/t01c269303c5b02ce60.png)](https://p0.ssl.qhimg.com/t01c269303c5b02ce60.png)<br><br>
那么不难发现<br><br>[![](https://p5.ssl.qhimg.com/t011ca627776fc55ead.png)](https://p5.ssl.qhimg.com/t011ca627776fc55ead.png)<br>
同理，我们还可以构造方程<br><br>[![](https://p2.ssl.qhimg.com/t010a5a920ba193e3b0.png)](https://p2.ssl.qhimg.com/t010a5a920ba193e3b0.png)<br><br>
如此一来，我们可以得到<br><br>[![](https://p5.ssl.qhimg.com/t014d545d86c4d6e91d.png)](https://p5.ssl.qhimg.com/t014d545d86c4d6e91d.png)<br><br>
是下列方程组的一个解<br><br>[![](https://p4.ssl.qhimg.com/t01c77a49c79c81f40a.png)](https://p4.ssl.qhimg.com/t01c77a49c79c81f40a.png)<br><br>
那么一定可以有<br><br>[![](https://p1.ssl.qhimg.com/t01f8df2af1d71983a4.png)](https://p1.ssl.qhimg.com/t01f8df2af1d71983a4.png)<br><br>
可以被写成<br><br>[![](https://p2.ssl.qhimg.com/t019f23785002bfdc70.png)](https://p2.ssl.qhimg.com/t019f23785002bfdc70.png)<br><br>
如此一来，只要<br><br>[![](https://p2.ssl.qhimg.com/t01a66e61e15f546369.png)](https://p2.ssl.qhimg.com/t01a66e61e15f546369.png)<br><br>
我们由e=3可以得知<br><br>[![](https://p2.ssl.qhimg.com/t013b940e70073f61d6.png)](https://p2.ssl.qhimg.com/t013b940e70073f61d6.png)<br><br>
只有唯一解，所以k1和k2必互素，所以这里是M2一定是可求的



## Related Message Attack

前面做了这么多证明铺垫，最后当然要祭出大招，即求解方法<br>
这里的攻击是有方法名称的，即Related Message Attack<br>
在e=3的情况下，我们可以利用rsa padding得到明文<br>
根据之前第一步的推导，我们得到了<br><br>[![](https://p1.ssl.qhimg.com/t017a1fa69ecd8d3e56.png)](https://p1.ssl.qhimg.com/t017a1fa69ecd8d3e56.png)<br><br>
我们将式子变形为<br><br>[![](https://p0.ssl.qhimg.com/t019f5185d97f829e69.png)](https://p0.ssl.qhimg.com/t019f5185d97f829e69.png)<br><br>
移项得到<br><br>[![](https://p2.ssl.qhimg.com/t01a35a7e58a345ca76.png)](https://p2.ssl.qhimg.com/t01a35a7e58a345ca76.png)<br><br>
根据立方差公式，我们又有<br><br>[![](https://p3.ssl.qhimg.com/t0170233bff04ec16d1.png)](https://p3.ssl.qhimg.com/t0170233bff04ec16d1.png)<br><br>
联立<br><br>[![](https://p0.ssl.qhimg.com/t014510d861bea58899.png)](https://p0.ssl.qhimg.com/t014510d861bea58899.png)<br><br>
我们将式子1左右同乘`aM2-b`，将式子2左右同乘`3b`<br>
然后即可得到如下式子<br><br>[![](https://p2.ssl.qhimg.com/t015e04908d4fc8781e.png)](https://p2.ssl.qhimg.com/t015e04908d4fc8781e.png)<br><br>
我们再把c2带入得到<br><br>[![](https://p1.ssl.qhimg.com/t0111cbebc8906c87d1.png)](https://p1.ssl.qhimg.com/t0111cbebc8906c87d1.png)<br><br>
则最后可以有<br><br>[![](https://p4.ssl.qhimg.com/t01bf958131723a742c.png)](https://p4.ssl.qhimg.com/t01bf958131723a742c.png)<br><br>
即可求得M2<br>
而我们知道<br><br>[![](https://p2.ssl.qhimg.com/t018709a0a388a150c6.png)](https://p2.ssl.qhimg.com/t018709a0a388a150c6.png)<br><br>
所以最后有<br><br>[![](https://p1.ssl.qhimg.com/t01ee8b636352ed1af6.png)](https://p1.ssl.qhimg.com/t01ee8b636352ed1af6.png)<br><br>
注意，这里的分式不是除法，是逆元



## payload

既然推导出了公式，写脚本即可

```
def getM2(a,b,c1,c2,n):
    a3 = pow(a,3,n)
    b3 = pow(b,3,n)
    first = c1-a3*c2+2*b3
    first = first % n
    second = 3*b*(a3*c2-b3)
    second = second % n
    third = second*gmpy2.invert(first,n)
    third = third % n
    fourth = (third+b)*gmpy2.invert(a,n)
    return fourth % n
m = getM2(a,b,c1,c2,n)-padding2
print libnum.n2s(m)
```



## Coppersmith’s short-pad attack

上述情况是e=3时候，我们可以根据<br><br>[![](https://p0.ssl.qhimg.com/t01bc055b31f2ace779.png)](https://p0.ssl.qhimg.com/t01bc055b31f2ace779.png)<br><br>
推导出m<br>
那么当e不是3的时候怎么办呢？<br>
这里稍作拓展，我们可以用Coppersmith’s short-pad attack，即padding过短引起的攻击<br>
脚本如下

```
https://github.com/ValarDragon/CTF-Crypto/blob/master/RSA/FranklinReiter.sage
```



## 后记

根据这一次学习，不难发现在存在padding的情况下，rsa也存在各种风险：<br>
1.若e=3，则可以利用Related Message Attack<br>
2.若e不为3，但padding过短，则可以利用Coppersmith’s short-pad attack
