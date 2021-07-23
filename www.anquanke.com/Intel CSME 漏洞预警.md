> 原文链接: https://www.anquanke.com//post/id/159597 


# Intel CSME 漏洞预警


                                阅读量   
                                **181933**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0105d8df5be16005e1.png)](https://p1.ssl.qhimg.com/t0105d8df5be16005e1.png)



## 0x00 漏洞背景

英特尔公布：在英特尔 CSME，英特尔服务器平台服务和英特尔可信执行引擎固件中潜在的安全漏洞会允许信息泄漏，英特尔正在发布英特尔 CSME，英特尔服务器平台服务和英特尔可信执行引擎更新，以缓解此潜在漏洞。

360-CERT团队经过评估，认为漏洞风险等级高危，建议用户参照相关修复建议进行防御。



## 0x01 漏洞细节

CVE ID: CVE-2018-3655

描述：漏洞存在于11.21.55版本之前的英特尔CSME中的子系统，4.0版本之前的英特尔服务器平台服务和3.1.55版本之前的英特尔可信执行引擎固件中，可能允许未经身份验证的用户通过物理访问来修改或泄漏信息。

CVSS Base Score: 7.3 High

CVSS Vector: CVSS:3.0/AV:P/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N

具有物理访问权限的未经身份验证的用户可以：

•绕过英特尔CSME 反重放保护，可能允许暴力攻击来获取存储在英特尔CSME内的信息。

•获得未经授权访问英特尔MEBX的密码。

•篡改英特尔CSME文件系统目录的完整性或服务器平台服务和可信执行环境（英特尔TXT）数据文件。

INTEL-SA-00086中描述的缓解措施无法防止此问题，因为对系统具有物理访问权限的用户可能能够回滚到受CVE-2017-5705，CVE-2017-5706和CVE-2017-5707影响的早期英特尔CSME固件。



## 0x02 影响范围

此漏洞影响英特尔CSME固件版本：11.0至11.8.50， 11.10至11.11.50， 11.20至11.21.51。 英特尔服务器平台服务固件版本：4.0（仅限Purley和Bakerville）。 英特尔TXE版本：3.0到3.1.50。

Intel CSME:

|更新的英特尔CSME固件版本|替代英特尔CSME固件版本
|------
|11.8.55|11.8.50.3399
|11.11.55|11.11.50.1402
|11.21.55|11.21.50.1400

英特尔服务平台服务：

|更新的SPS固件版本|替代SPS固件版本
|------
|SPS_SoC-A_04.00.04.177.0|SPS_SoC-A_04.00.04.172.0
|SPS_SoC-X_04.00.04.077.0|SPS_SoC-X_04.00.04.057.0
|SPS_E5_04.00.04.381.0|SPS_E5_04.00.04.340.0

英特尔可信执行引擎（TXE）：

|更新了TXE固件版本|替代TXE固件版本
|------
|3.1.55|3.1.50.2222

不受影响范围： 英特尔CSME固件11.0版本之前的版本 。 英特尔服务器平台服务4.0以前版本。 TXE 3.0以前版本。 英特尔CSME固件版本11.8.55 ， 11.11.55 ， 11.21.55 版本。 英特尔服务器平台服务5.0及更高版本。 TXE 3.1.55或更高版本。



## 0x03 修复建议

请英特尔CSME，英特尔服务器平台服务和英特尔可信执行引擎（TXE）的用户更新最新补丁。



## 0x04 时间线

2018-09-11 英特尔漏洞披露

2018-09-12 360CERT发布预警通告



## 0x05 参考链接
1. [https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00125.html](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00125.html)
1. [https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00086.html](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00086.html)