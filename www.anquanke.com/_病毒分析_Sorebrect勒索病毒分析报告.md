> 原文链接: https://www.anquanke.com//post/id/86496 


# 【病毒分析】Sorebrect勒索病毒分析报告


                                阅读量   
                                **134226**
                            
                        |
                        
                                                                                    



**[![](https://p2.ssl.qhimg.com/t019168a9eaa4d674f7.png)](https://p2.ssl.qhimg.com/t019168a9eaa4d674f7.png)**

**作者：houjingyi@360CERT**



**0x00  背景介绍**



[![](https://p5.ssl.qhimg.com/t01bfdc708ff57a3c0b.png)](https://p5.ssl.qhimg.com/t01bfdc708ff57a3c0b.png)

2017年6月安全研究人员发现了一种利用AES-NI特性的名为Sorebrect的勒索病毒，它的代码和原始的AES-NI版本相比有一些显著的变化。一方面技术上它试图将恶意代码注入svchost.exe中，再进行自毁以无文件的形式躲避检测。另一方面它声称使用了NSA的溢出攻击工具（如：永恒之蓝漏洞）。

360CERT安全分析团队将在本文中对部分相关的技术进行具体分析。



**0x01  IOC**



CRC32: 907F515A

MD5: 83E824C998F321A9179EFC5C2CD0A118

SHA-1: 16B84004778505AFBCC1032D1325C9BED8679B79



**0x02  病毒详情**



在Sorebrect版本中使用的加密后缀是.aes_ni_0day和.pr0tect，早期使用AES-NI 特性的勒索病毒使用的加密文件扩展名包括： .lock，.pre_alpha，.aes和.aes_ni。

Sorebrect声称自己是特殊的“NSA EXPLOIT EDITION”，在360CERT具体分析过程中暂时还没有发现有类似于NotPetya和WannaCry使用NSA泄露的工具传播的行为，传播方式主要是感染网络中共享的文件。

接下来，360CERT对Sorebrect样本中使用的加解密、进程注入、反恢复、内网感染等技术进行一系列的分析。

**初始化加解密**

Sorebrect在程序开始运行时就使用了加解密技术，会对每个导入函数地址和固定值0x772756B1h进行异或加密保存，在调用时再与此值异或得到真正的函数地址。

[![](https://p1.ssl.qhimg.com/t016ea73d76c98594f9.png)](https://p1.ssl.qhimg.com/t016ea73d76c98594f9.png)

在一开始会先搜索被加载到内存中的PE文件起始位置。

[![](https://p2.ssl.qhimg.com/t019301a02846064988.png)](https://p2.ssl.qhimg.com/t019301a02846064988.png)

随后，开始解析kernel32的内存地址。

[![](https://p3.ssl.qhimg.com/t0196ec3e6101e606c3.png)](https://p3.ssl.qhimg.com/t0196ec3e6101e606c3.png)

进一步获取LoadLibrary函数的内存地址。 [![](https://p2.ssl.qhimg.com/t0153438ffe1079d52a.png)](https://p2.ssl.qhimg.com/t0153438ffe1079d52a.png)

根据分析，主体程序会尝试获取下列dll的地址。

[![](https://p1.ssl.qhimg.com/t010f57cc3fd8b14bee.png)](https://p1.ssl.qhimg.com/t010f57cc3fd8b14bee.png)

具体在分析过程中，sub_A0A660的三个参数，分别为动态库（dll）的地址，存放函数地址与0x772756B1h异或加密之后的值的地址，和函数名称的CRC32与0x772756B1h异或加密之后的值。

[![](https://p2.ssl.qhimg.com/t01fb9a57e52bb25738.png)](https://p2.ssl.qhimg.com/t01fb9a57e52bb25738.png)

尝试解析这些地址存放的函数地址对应的函数名称之后的效果如下所示。

之前：

[![](https://p2.ssl.qhimg.com/t01e1ffdf69c265ea5f.png)](https://p2.ssl.qhimg.com/t01e1ffdf69c265ea5f.png)

之后：

[![](https://p3.ssl.qhimg.com/t0103c0b380585ca8e2.png)](https://p3.ssl.qhimg.com/t0103c0b380585ca8e2.png)

**注入操作**

Sorebrect会试图调用DuplicateTokenEx复制一份具有system权限的进程的token，再使用CreateProcessWithTokenW创建具有system权限的svchost.exe。

[![](https://p3.ssl.qhimg.com/t016447e328fdac4c46.png)](https://p3.ssl.qhimg.com/t016447e328fdac4c46.png)

[![](https://p3.ssl.qhimg.com/t01cc1929e07bd0ab53.png)](https://p3.ssl.qhimg.com/t01cc1929e07bd0ab53.png)

如果上述过程没有成功，Sorebrect会继续调用CreateProcessW创建一个普通权限的svchost.exe。

[![](https://p3.ssl.qhimg.com/t0198bb949ca10e49a1.png)](https://p3.ssl.qhimg.com/t0198bb949ca10e49a1.png)

svchost.exe进程创建后，Sorebrect会调用WriteProcessMemory向创建的svchost.exe写入一段代码。

[![](https://p1.ssl.qhimg.com/t016dfac4e40d095da0.png)](https://p1.ssl.qhimg.com/t016dfac4e40d095da0.png)

注入代码之前：

[![](https://p0.ssl.qhimg.com/t0180c04ea0172e2441.png)](https://p0.ssl.qhimg.com/t0180c04ea0172e2441.png)

注入代码之后：

[![](https://p3.ssl.qhimg.com/t010fb2767167e0564f.png)](https://p3.ssl.qhimg.com/t010fb2767167e0564f.png)

这段代码会试图在内存中加载并执行一个文件，该文件内容与原病毒基本相同。

[![](https://p3.ssl.qhimg.com/t016d659c124793b147.png)](https://p3.ssl.qhimg.com/t016d659c124793b147.png)

主体程序接下来在内存中释放了一个dll文件，这个文件是UPX加壳的。

[![](https://p4.ssl.qhimg.com/t015b71cf9c67187b41.png)](https://p4.ssl.qhimg.com/t015b71cf9c67187b41.png)

**TOR通信**

Sorebrect主体程序还会尝试连接ipinfo.io，并以kzg2xa3nsydva3p2.onion/gate.php为参数调用前面释放的dll。该dll的功能为进行tor通信。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d634630da188c08b.png)

**[![](https://p3.ssl.qhimg.com/t01e209f1611dc08d14.png)](https://p3.ssl.qhimg.com/t01e209f1611dc08d14.png)**

**痕迹擦除**

创建一个批处理文件删除日志记录。 [![](https://p2.ssl.qhimg.com/t019075edf330c8a010.png)](https://p2.ssl.qhimg.com/t019075edf330c8a010.png)

[![](https://p5.ssl.qhimg.com/t01dfac78cc2470e05c.png)](https://p5.ssl.qhimg.com/t01dfac78cc2470e05c.png)

**对抗恢复1**

Sorebrect会尝试停止下列服务，以此来对抗可能的文件恢复。这些服务包括各种备份软件和数据库软件等等。

```
BCFMonitorService.QBFCService.QBVSS.QuickBooksDB25.LMIRfsDriver.RemoteSystemMonitorService.MSSQL$MICROSOFT##WID.dbupdate.dbupdatem.DbxSvc.MsDtsServer100.msftesql-Exchange.MSSQL$MICROSOFT##SSEE.MSSQL$PROBA.MSSQL$SBSMONITORING.MSSQL$SHAREPOINT.MSSQL$SQL2005.msftesql$SBSMONITORING.MSSQLFDLauncher.MSSQLFDLauncher$PROBA.MSSQLFDLauncher$SBSMONITORING.MSSQLFDLauncher$SHAREPOINT.MSSQLSERVER.MSSQLServerADHelper100.SQLAgent$PROBA.SQLAgent$SBSMONITORING.SQLAgent$SHAREPOINT.SQLBrowser.SQLSERVERAGENT.SQLWriter.CertPropSvc.CertSvc.DataCollectorSvc.FirebirdServerDefaultInstance.wsbexchange.MSExchangeTransportLogSearch.MSExchangeTransport.MSExchangeServiceHost.MSExchangeSearch.MSExchangeSA.MSExchangeRepl.MSExchangePop3.MSExchangeMonitoring.MSExchangeMailSubmission.MSExchangeMailboxAssistants.MSExchangeIS.MSExchangeImap4.MSExchangeFDS.MSExchangeEdgeSync.MSExchangeAntispamUpdate.MSExchangeADTopology.SPTrace.SPTimerV3.SPWriter.TeamViewer.W3SVC.W32Time.MsDtsServer.MSSQLSERVR.MSSQLServerOLAPService.zBackupAssistService.cbVSCService11.CobianBackup11.postgresql-8.4.spiceworks.QuickBooksDB23.ShadowProtectSvc.VSNAPVSS.VSS.stc_raw_agent.PleskSQLServer.MySQL56.MSExchangeRep.NAVSERVER.ZWCService.vmms.vds.sesvc.MSSQL$VEEAMSQL2008R2.SQLAgent$VEEAMSQL2008R2.Veeam Backup Catalog Data Service.Veeam Backup and Replication Service.VeeamCloudSvc.VeeamTransportSvc.VeeamCatalogSvc.VeeamDeploymentService.VeeamMountSvc.VeeamNFSSvc.FirebirdGuardianDefaultInstance.BackupExecAgentBrowser.BackupExecDeviceMediaService.DLOAdminSvcu.DLOMaintenanceSvc.bedbg.BackupExecJobEngine.BackupExecManagementService.BackupExecAgentAccelerator.BackupExecRPCService.MSExchangeADTopology.Browser.WSearch.WseComputerBackupSvc.WseEmailSvc.WseHealthSvc.WseMediaSvc.WseMgmtSvc.WseNtfSvc.WseStorageSvc.SBOClientAgent.VSS.VSNAPVSS.vmicvss.swprv.ShadowProtectSvc.SQLWriter.SQLBrowser.SQLAgent$SQLEXPRESS.MSSQL$SQLEXPRESS.MSSQL$MICROSOFT##WID.EDBSRVR.ComarchAutomatSynchronizacji.ComarchML.ComarchUpdateAgentService.RBMS_OptimaBI.RBSS_OptimaBI.ServerService.GenetecWatchdog.GenetecServer.GenetecSecurityCenterMobileServer.SQLAgent$SQLEXPRESS.SQLBrowser.SQLWriter.MSSQL$SQLEXPRESS.MSSQLServerADHelper100.MSExchangeFBA.eXchange POP3 6.0.bedbg.BackupExecRPCService.BackupExecDeviceMediaService.BackupExecAgentBrowser.BackupExecAgentAccelerator.MsDtsServer100.MSSQLFDLauncher.MSSQLSERVER.MSSQLServerADHelper100.MSSQLServerOLAPService.ReportServer.SQLBrowser.SQLSERVERAGENT.SQLWriter.WinVNC4.KAORCMP999467066507407.dashboardMD Sync.MicroMD AutoDeploy.MicroMD Connection Service.MICROMD72ONCOEMR.ONCOEMR2MICROMD7.FBSServer.FBSWorker.cbVSCService11.CobianBackup11.LogisticsServicesHost800.PRIMAVERAWindowsService.PrimaveraWS800.PrimaveraWS900.TTESCheduleServer800.DomainManagerProviderSvc.WSS_ComputerBackupProviderSvc.WSS_ComputerBackupSvc.msftesql$SBSMONITORING.msftesql-Exchange.MSSQL$ACRONIS.MSSQL$BKUPEXEC.MSSQL$MICROSOFT##SSEE.MSSQL$SBSMONITORING.MSSQLServerADHelper.MySQL.SQLBrowser.SQLWriter.MSExchangeADTopology.MSExchangeAntispamUpdate.MSExchangeEdgeSync.MSExchangeFDS.MSExchangeImap4.MSExchangeIS.MSExchangeMailboxAssistants.MSExchangeMailSubmission.MSExchangeMonitoring.MSExchangePop3.MSExchangeRepl.MSExchangeSA.MSExchangeSearch.MSExchangeServiceHost.MSExchangeTransport.MSExchangeTransportLogSearch.msftesql-Exchange.wsbexchange.Acronis VSS Provider.AcronisAgent.AcronisFS.AcronisPXE.AcrSch2Svc.AMS.MMS.MSSQL$ACRONIS.StorageNode.PleskControlPanel.PleskSQLServer.plesksrv.PopPassD.Apache2.2.Apache2.4.memcached Server.MMS.ARSM.AdobeARMservice.AcrSch2Svc.AcronisAgent.CrashPlanService.SPAdminV4.SPSearch4.SPTraceV4.SPWriterV4.Altaro.Agent.exe.Altaro.HyperV.WAN.RemoteService.exe.Altaro.SubAgent.exe.Altaro.UI.Service.exe.MELCS.MEMTAS.MEPOCS.MEPOPS.MESMTPCS.postgresql-9.5
```

[![](https://p0.ssl.qhimg.com/t018092a486a1c95976.png)](https://p0.ssl.qhimg.com/t018092a486a1c95976.png)

除了停止服务外，Sorebrect程序硬编码了一段CRC32的值，如果小写的进程名的CRC32值和硬编码的值相同则尝试终止该进程。

[![](https://p0.ssl.qhimg.com/t010c77a49441318a52.png)](https://p0.ssl.qhimg.com/t010c77a49441318a52.png)

[![](https://p0.ssl.qhimg.com/t016c78b4abec12c78c.png)](https://p0.ssl.qhimg.com/t016c78b4abec12c78c.png)



**加密操作**

Sorebrect会对主机上的文件进行加密，并在C:ProgramData目录下生成密钥，根据提示信息，受害者想要解密必须将该文件发送给攻击者。

[![](https://p4.ssl.qhimg.com/t01720cd7a28a4568ae.png)](https://p4.ssl.qhimg.com/t01720cd7a28a4568ae.png)

Sorebrect病毒使用AES-NI指令集完成加密。AES-NI是一个x86指令集架构的扩展，用于Intel和AMD微处理器，由Intel在2008年3月提出。该指令集的目的是改进应用程序使用AES执行加密和解密的速度。

[![](https://p4.ssl.qhimg.com/t01a64a825000877d79.png)](https://p4.ssl.qhimg.com/t01a64a825000877d79.png)

[![](https://p4.ssl.qhimg.com/t01d8c3288808b06b90.png)](https://p4.ssl.qhimg.com/t01d8c3288808b06b90.png)

如代码所示，将EAX寄存器设置为0之后执行CPUID指令返回的制造商标识存放在EBX，ECX和EDX寄存器中。如果既不是GenuineIntel的处理器也不是AuthenticAMD的处理器则认为该处理器不支持AES-NI指令集。将EAX寄存器设置为1之后执行CPUID指令通过ECX寄存器中的标志位进一步判断处理器是否支持AES-NI指令集。

[![](https://p3.ssl.qhimg.com/t01b18c1f6a0d60e7c4.png)](https://p3.ssl.qhimg.com/t01b18c1f6a0d60e7c4.png)

[![](https://p3.ssl.qhimg.com/t01cb192326d0a951c8.png)](https://p3.ssl.qhimg.com/t01cb192326d0a951c8.png)

**局域网感染**

Sorebrect在加密操作完成之后，会进一步探测局域网，并通过IPC$共享的方式来进行局域网内的感染。

[![](https://p5.ssl.qhimg.com/t018105b1a3fa57a94c.png)](https://p5.ssl.qhimg.com/t018105b1a3fa57a94c.png)

[![](https://p0.ssl.qhimg.com/t01e0226b0c45190615.png)](https://p0.ssl.qhimg.com/t01e0226b0c45190615.png)

设置LegalNoticeCaption和LegalNoticeText注册表项，内容分别为Microsoft Windows Security Center和Dear Owner. Bad news: your server was hacked. For more information and recommendations, write to our experts by e-mail. When you start Windows,Windows Defender works to help protect your PC by scanning for malicious or unwanted software.

系统启动时会弹出这个对话框。

[![](https://p3.ssl.qhimg.com/t01210a86fdaf61545c.png)](https://p3.ssl.qhimg.com/t01210a86fdaf61545c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ebb28cfc3dbd4d74.png)

**对抗恢复2**

删除所有卷影副本。



**0x03 防范建议**



**重要数据、文件备份**

网络犯罪分子往往使用重要和个人数据的潜在损失作为恐吓手段来强迫受害者支付赎金。因此公司和个人用户可以备份重要数据、文件以消除其影响力：至少保留三份副本，其中两个存储在不同的设备中，另一个存储在非现场或安全位置。

**保持系统补丁更新**

确保操作系统和其它应用程序安装了最新的补丁，阻止威胁将安全漏洞用作系统或网络的门户。

**安装可靠的终端安全防护软件**

在保证定期更新补丁的基础上，通过安装可靠的终端安全防护产品来进行进一步的安全防御。



**0x04 时间线**



2017-6-15趋势科技捕获到病毒并命名为Sorebrect

2017-7-7 360CERT完成对病毒的分析



**0x05 参考文档**



[http://blog.nsfocus.net/hardware-accelerate-extortion-software-xdata/](http://blog.nsfocus.net/hardware-accelerate-extortion-software-xdata/)

[https://www.cylance.com/en_us/blog/threat-spotlight-aes-ni-aka-sorebrect-ransomware.html](https://www.cylance.com/en_us/blog/threat-spotlight-aes-ni-aka-sorebrect-ransomware.html)

[https://blog.trendmicro.com/trendlabs-security-intelligence/analyzing-fileless-code-injecting-sorebrect-ransomware/](https://blog.trendmicro.com/trendlabs-security-intelligence/analyzing-fileless-code-injecting-sorebrect-ransomware/)
