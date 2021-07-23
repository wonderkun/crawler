> 原文链接: https://www.anquanke.com//post/id/86912 


# 【漏洞预警】SambaBleed：Samba信息泄露漏洞（CVE–2017–12163）预警


                                阅读量   
                                **100794**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01db83218e4390d93c.png)](https://p1.ssl.qhimg.com/t01db83218e4390d93c.png)



**0x00 事件描述**



Samba作为Linux和UNIX系统上实现SMB协议的一个免费软件，在*nix领域有很广泛的应用场景。

日前，360 Gear Team的安全研究员(连一汉,胡智斌)发现Samba SMB1协议存在安全缺陷，**攻击者在拥有Samba账户写入权限的情况下，可以远程泄露目标Samba服务器的内存信息，影响Samba全版本**，漏洞编号为**CVE-2017-12163**。之后，Samba和Google团队提供了修复方案。

据悉，该漏洞被称为**SambaBleed漏洞**。

360CERT建议使用Samba软件的用户尽快进行安全更新。



**0x01 事件影响面**



**影响等级**

**漏洞风险等级较高，影响范围较广**

**影响版本**

Samba全版本

**修复版本**

Samba 4.6.8, 4.5.14 和 4.4.16



**0x02 漏洞细节**



在SMB1协议中，用户写请求的范围没有被严格检查，超过用户已发送的数据大小，从而导致服务器的内存信息被写入文件，但是并不能控制哪些内存信息被写入。官方提供的补丁在写入之前加了请求写入数据大小的判断，从而防御该漏洞。

泄露的内存信息:

[![](https://p4.ssl.qhimg.com/t01984bcd0e9b6ac675.jpg)](https://p4.ssl.qhimg.com/t01984bcd0e9b6ac675.jpg)



**0x03 修复方案**



1、Samba 4.6.7, 4.5.13和4.4.15版本已提供官方补丁，强烈建议所有受影响用户，及时更新官方补丁，或者更新到已修复版本。

补丁地址：[https://www.samba.org/samba/history/security.html](https://www.samba.org/samba/history/security.html)

2、强制使用SMB2协议，在smb.conf的[global]里设置”**server min protocol = SMB2_02**“，并重启smbd。



**0x04 时间线**



2017-09-20 官方发布Samba 4.6.7, 4.5.13和4.4.15版本更新

2017-09-22 360CERT发布预警通告



**0x05 参考资料**



[https://www.samba.org/samba/security/CVE-2017-12163.html](https://www.samba.org/samba/security/CVE-2017-12163.html)
