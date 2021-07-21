> 原文链接: https://www.anquanke.com//post/id/153373 


# 如何攻击智能汽车远程启动系统（Part 1）


                                阅读量   
                                **121071**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：versprite.com
                                <br>原文地址：[https://versprite.com/blog/hacking-remote-start-system/](https://versprite.com/blog/hacking-remote-start-system/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ca56ebc03afbef5d.jpg)](https://p4.ssl.qhimg.com/t01ca56ebc03afbef5d.jpg)

## 一、前言

关于汽车安全方面的研究趋势始于2010年，到目前为止，研究人员已经在汽车中发现了多个严重安全问题。

黑客们经常向公众展示他们有能力远程跟踪、窃取和控制未经改装的各种汽车的能力，在大多数情况下，厂商可以向受影响的汽车软件推送远程更新来修复这些问题，但很少有人去关注修复[严重漏洞](https://versprite.com/tag/security-vulnerabilities/)的具体过程。



## 二、远程启动系统

汽车远程启动器是一种现成系统，可以安装在汽车上，实现引擎远程启动或者无钥匙启动等高级功能。尽管这些设备的确能够带来便利，但想顺利安装安全更新可能是非常困难的事情。虽然有些汽车提供无线更新功能，但有几款车型需要物理访问才能更新固件，这样就存在安全威胁无法及时修复的风险。

此外，这些产品通常都需要专业水平才能安装，使设备对驾驶员透明。由于我们没有在已有的汽车安全研究领域中发现关于这类产品的内容，因此我们决定自己研究这些产品。

传统意义上，远程启动系统由车钥匙（key fob）来控制，但现在越来越多的厂商提供了智能手机控制方案。我们的研究表明，汽车远程启动移动解决方案的行业领先者为**VOXX International**以及**Directed Electronics**，这两家厂商都管理着多个品牌。这些厂商所提供的远程启动产品主要支持蓝牙或者无线蜂窝网络通信协议。

我们认为，从优秀的汽车盗窃者来看，这种启用了蓝牙功能的隔离攻击环境非常具有吸引力。

经过一番考虑，我们将目光投向了VOXX International的**CarLinkBT**远程启动模块。CarLinkBT允许驾驶员通过智能手机远程锁定、解锁、打开行李箱以及启动汽车，非常方便。

CarLinkBT移动应用通过蓝牙低功耗（Bluetooth Low Energy，BLE）协议与[**Carlink ASCLBT**](http://www.carlinkusa.com/ASCLBT/)远程启动模块通信。为了准确理解移动应用如何控制远程启动模块，我们从[APKPure.com](https://apkpure.com/carlinkbt-basic/com.carlinkbtbasic)上下载了CarLinkBT安卓APK安装文件进行进一步分析。



## 三、APK逆向分析

APK（Android Package）是一种归档文件格式，包含应用代码及应用资源，[Android操作系统](https://versprite.com/tag/android-mobile-security/)使用APK来安装应用，我们可以通过分析APK文件理解应用工作流程。

APK中有个**classes.dex**文件，该文件包含类定义以及应用字节码（bytecode）。为了便于分析，我们首先使用了[dex2jar](https://github.com/pxb1988/dex2jar)将应用转换为JAR文件。

接着我们使用[Bytecode Viewer](https://github.com/Konloch/bytecode-viewer)来反编译应用的字节码。我们感兴趣的是应用如何连接CarLinkBT远程启动模块并与之通信，因此我们专门搜索了与BLE有关的那些类，然后就发现了**BLEUtilities**这个类。

BLEUtilities类定义了如下公开方法，应用会使用这些方法来管理与CarLinkBT远程启动模块的连接：

[![](https://p3.ssl.qhimg.com/t016538f865fbb0e44f.png)](https://p3.ssl.qhimg.com/t016538f865fbb0e44f.png)

图1. BLEUtilities的公开方法

当创建BLEUtilities实例时，应用会调用scanLeDevice()，开始扫描CarLinkBT模块。在Anddroid API的[BluetoothAdapter](https://developer.android.com/reference/android/bluetooth/BluetoothAdapter)类中，与BLE扫描有关的有多个方法，scanLeDevice()是这几种方法的封装函数。如果探测到CarLinkBT模块，那么onLeScan回调方法就会停止扫描新设备，然后调用connectToDevice()，尝试与设备的GATT服务器建立新连接。

[![](https://p4.ssl.qhimg.com/t01e0a37b02fb989690.png)](https://p4.ssl.qhimg.com/t01e0a37b02fb989690.png)

图2. scanLeDevice()代码片段



## 四、BLE GATT

GATT的全称为[Generic Attribute Profile](https://www.bluetooth.com/specifications/gatt/generic-attributes-overview)（通用属性配置文件），该规范可以定义BLE设备如何通过GATT服务器提供的分层数据结构进行通信。

在数据结构的顶层为GATT配置文件，其中包含一个或多个GATT服务。GATT服务由通用唯一标识符（UUID）标识，由GATT属性（characteristic）所组成。

GATT characteristic同样由UUID标识，包含characteristic值、一组characteristic属性以及可选的characteristic描述符所组成。与GATT服务器建立连接后，客户端可以根据访问权限来读取或者写入characteristic。

Android API的[BluetoothDevice](https://developer.android.com/reference/android/bluetooth/BluetoothDevice)类包含名为connectGatt()的一个方法，该方法可以与由BLE设备托管的GATT服务器建立连接，返回一个新的[BluetoothGatt](https://developer.android.com/reference/android/bluetooth/BluetoothGatt)实例。CarLinkBT应用的BLEUtilities类包含名为mGatt的一个公开的BluetoothGatt对象，该类中把这个对象当成GATT客户端来使用。

connectToDevice()方法负责调用connectGatt()来生成与CarLinkBT模块对应的mGatt以及BluetoothGatt实例。GATT连接成功建立后，应用可能会使用writeCommandToDevice()方法将命令发送至GATT服务器，控制远程启动模块。

[![](https://p4.ssl.qhimg.com/t012ded002f73181b79.png)](https://p4.ssl.qhimg.com/t012ded002f73181b79.png)

图3. connectToDevice()代码片段

writeCommandToDevice()方法中包含几个初步检查过程。一是如果未启用GATT通知，则会调用enableNotifications()方法。客户端可以通过两种方法利用characteristic值与GATT服务器通信，一种是Notification（通知），另一种是Indication（指示）。

与Indication不一样，Notification不需要客户端的确认，因此允许使用无连接形式的通信。Notification默认情况下并没有处于启用状态，因此必须由GATT客户端启用。



## 五、理解UART服务

前面提到过，GATT组件可以通过UUID值来识别。UUID实例在BLEUtilities类中定义：

[![](https://p5.ssl.qhimg.com/t01eac1dc3f59912193.png)](https://p5.ssl.qhimg.com/t01eac1dc3f59912193.png)

图4. Nordic UART UUID

分析这些UUID后，我们发现它们对应的是[Nordic UART服务](https://infocenter.nordicsemi.com/index.jsp?topic=%2Fcom.nordic.infocenter.sdk52.v0.9.2%2Fble_sdk_app_nus_eval.html)。UART的全称为Universal asynchronous receiver-transmitter（通用异步收发传输器），支持两个设备之间的串行通信。UART_SERVICE_UUID对应的是UART服务。

在访问服务的底层characteristic之前，必须获取该服务的引用。程序可以调用BluetoothGattService实例的getService()方法完成这个任务。

[![](https://p4.ssl.qhimg.com/t01ef24a6a11c47a8d8.png)](https://p4.ssl.qhimg.com/t01ef24a6a11c47a8d8.png)

图5. 调用getService()方法

UART_WRITE_UUID对应的是服务的RX characteristic，UART_NOTIFICATION_UUID对应的是TX characteristic。getService()返回的BluetoothGattService实例必须调用getCharacteristic()方法才能访问TX以及RX characteristic。

[![](https://p1.ssl.qhimg.com/t01c143a49ba53cb8d8.png)](https://p1.ssl.qhimg.com/t01c143a49ba53cb8d8.png)

图6. 调用getCharacteristic()

最后，UART_NOTIFICATION_DESCRIPTOR为对应TX Characteristic的客户端属性配置描述符（Client Characteristic Configuration Descriptor，CCCD）。该描述符的bit字段值用来启用或者禁用与characteristic关联的Notification以及Indicator。

应用调用getDescriptor()方法来获取与CCCD对应的BluetoothGattDescriptor实例，然后调用writeDescriptor()启用服务的TX characteristic的notification。对于每个characteristic实例，应用会调用setCharacteristicNotification()方法，通知GATT客户端监听来自GATT服务的Notification。

[![](https://p5.ssl.qhimg.com/t01382e0c3ba7fbcc6d.png)](https://p5.ssl.qhimg.com/t01382e0c3ba7fbcc6d.png)

图7. 调用getDescriptor()



## 六、XXTEA加密密钥生成

启用设备的Notification后，writeCommandToDevice()会做第二个检查，如果设置了currentXXTeaKey，则会调用resendDynamicKey()方法。currentXXTeaKey是一个全局字节数组，包含与Nordic UART服务加密通信中所需使用的XXTEA密钥。XXTEA为使用128位密钥的分组密码，实现上相对轻量级一些。

CarLinkBT应用中包含一个XXTEA类，其中包含加密、解密、数组操作以及数据类型转换的相关方法。XXTEA类同样包含名为generateRandomKey()的一个方法，可以用于生成随机的128位（或16字节）XXTEA密钥。比如，我们可以在resendDynamicKey()中看到，generateRandomKey()返回的密钥会作为参数传递给writeDynamicKey()。

[![](https://p5.ssl.qhimg.com/t01c1d899eeb50e8562.png)](https://p5.ssl.qhimg.com/t01c1d899eeb50e8562.png)

图8. resendDynamicKey()代码片段

writeDynamicKey()方法负责使用新的加密密钥更新Nordic UART服务。具体方法是将加密密钥消息写入服务的RX characteristic（UART_WRITE_UUID）中。密钥消息为一个20字节数组，包含随机生成的XXTEA密钥，前缀为“1”、“37”、“-7”以及消息ID值的最低有效字节。

[![](https://p1.ssl.qhimg.com/t018716689401da29d0.png)](https://p1.ssl.qhimg.com/t018716689401da29d0.png)

图9. 构造密钥消息

在写入服务的RX characteristic之前，密钥消息会经过默认加密密钥的加密处理，默认加密密钥在XXTEA类中计算。成功写入加密消息后，currentXXTeaKey会更新为新的密钥值。

[![](https://p5.ssl.qhimg.com/t01171a90da16f8f92f.png)](https://p5.ssl.qhimg.com/t01171a90da16f8f92f.png)

图10. 默认的XXTEA密钥

经过writeCommandToDevice()中的第二次检查后，应用会继续构造需要写入服务RX characteristic的一则命令消息。命令消息是一个8字节数组，其前4个字节来自于当前的系统时间。

[![](https://p2.ssl.qhimg.com/t01ec521d0498687746.png)](https://p2.ssl.qhimg.com/t01ec521d0498687746.png)

图11. 构造命令消息

命令消息的第5个字节为消息ID的最低有效字节位。第6个字节包含pendingCommand的值，对应的具体值如下所示：

[![](https://p2.ssl.qhimg.com/t0143ed234e00edd887.png)](https://p2.ssl.qhimg.com/t0143ed234e00edd887.png)

图12. CarLink UART命令

命令消息的末尾为“55”及“-66”。命令消息构建完毕后，会使用当前的XXTEA秘密要进行加密。然而，如果currentXXTeaKey为空（null），则会使用默认的XXTEA密钥进行加密。这个处理逻辑表明使用新的XXTEA密钥来更新设备只是一个可选项。在此之后，加密的命令消息会写入RX characteristic，由CarLinkBT模块进行处理。

[![](https://p0.ssl.qhimg.com/t017ed3b8d3ab394fa3.png)](https://p0.ssl.qhimg.com/t017ed3b8d3ab394fa3.png)

图13. 加密命令消息



## 七、总结

现在我们已经理解应用BLE操作的工作流程，再总结一下，可以分为以下几个步骤：

1、scanLeDevice()扫描CarLinkBT模块，然后调用connectToDevice()；

2、connectToDevice()调用connectGatt()，将返回的实例赋予mGatt；

3、writeCommandToDevice()调用enableNotifications()来启用Notification；

4、writeCommandToDevice()调用resendDynamicKey()来配置新的XXTEA密钥；

5、writeCommandToDevice()生成命令消息，然后使用当前的XXTEA密钥来加密消息；

6、writeCommandToDevice()将加密消息写入服务的RX characteristic中；

7、CarLinkBT远程启动模块处理此命令消息，然后返回相应数据。

这里需要重点注意的是，客户端会负责加密密钥的生成及管理，这意味着恶意的BLE客户端应该能够模仿应用程序，向CarLinkBT远程启动模块发送命令。

在Part 2中，我们会重点关注动态分析结果，进一步确认我们的发现，理解CarLinkBT设备在实际环境中如何运行，欢迎大家继续关注。
