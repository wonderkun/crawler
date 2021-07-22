> 原文链接: https://www.anquanke.com//post/id/182699 


# 【缺陷周话】第44期：Spring Boot 配置错误：不安全的 Actuator


                                阅读量   
                                **178055**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)](https://p4.ssl.qhimg.com/t01649690fcb193fd32.jpg)



## 1、Spring Boot 配置错误：不安全的 Actuator

Spring Boot Actuator 是针对 Spring Boot 应用监控和管理而建立的一个模块，用于对 Spring Boot 应用的健康检查、审计、收集应用的运行状况和 HTTP 追踪等。Spring Boot Actuator 中包含了许多内置端点用于显示应用程序的监控信息，当 Spring Boot Actuator 配置不当时，攻击者可以通过访问默认的内置端点轻易获得应用程序的敏感信息。本文以JAVA语言源代码为例，分析“Spring Boot配置错误：不安全的Actuator”缺陷产生的原因以及修复方法。



## 2、“Spring Boot 配置错误：不安全的 Actuator”的危害

在 Actuator 启用的情况下，如果没有做好相关权限控制，攻击者可以通过访问默认的执行器端点来获取应用系统中的监控信息。部分内置端点描述如下：

<th width="160">ID</th><th width="350">描述</th>
|------
<td width="139">auditevents</td><td width="347">显示应用暴露的审计事件 (比如认证进入、订单失败)</td>
<td width="139">info</td><td width="347">显示应用的基本信息</td>
<td width="139">env</td><td width="347">显示全部环境属性</td>
<td width="139">health</td><td width="347">报告应用程序的健康指标，这些值由HealthIndicator的实现类提供</td>
<td width="139">loggers</td><td width="347">显示和修改配置的loggers</td>
<td width="139">mappings</td><td width="347">描述全部的URI路径，以及它们和控制器(包含Actuator端点)的映射关系</td>
<td width="139">shutdown</td><td width="346">关闭应用程序，要求endpoints.shutdown.enabled设置为true</td>
<td width="139">trace</td><td width="346">提供基本的 HTTP 请求跟踪信息（时间戳、HTTP 头等）</td>

示例源于 WebGoat-8.0.0.M25 (https://www.owasp.org/index.php/Category:OWASP_WebGoat_Project)，源文件名：application.properties。

### 3.1 缺陷代码

[![](https://p0.ssl.qhimg.com/t017a38824cb645732e.png)](https://p0.ssl.qhimg.com/t017a38824cb645732e.png)

上述配置是对内置端点 trace 进行授权配置，设置为 false，是指不需要授权就可以访问内置端点 trace。访问内置端点trace时不需要特别授权，攻击者可以轻易获得应用基本的 HTTP 请求信息（时间戳、HTTP 头等），还有用户 token、cookie 字段。

使用代码卫士对上述示例代码进行检测，可以检出“Spring Boot配置错误：不安全的Actuator”缺陷，显示等级为中。在代码行第19行报出缺陷，如图1所示：

[![](https://p0.ssl.qhimg.com/t01657ad4187d551cdd.png)](https://p0.ssl.qhimg.com/t01657ad4187d551cdd.png)

图1：“Spring Boot 配置错误：不安全的 Actuator”检测示例

### 3.2 修复代码

[![](https://p0.ssl.qhimg.com/t012b9c8fcba7fdfa6d.png)](https://p0.ssl.qhimg.com/t012b9c8fcba7fdfa6d.png)

在上述修复代码中，将内置端点trace 进行授权配置为 true，保证访问内置端点 trace 是经过授权的。

使用代码卫士对修复后的代码进行检测，可以看到已不存在“SpringBoot配置错误：不安全的Actuator”缺陷。如图2所示：

[![](https://p1.ssl.qhimg.com/t01bacbc7f191def3d2.png)](https://p1.ssl.qhimg.com/t01bacbc7f191def3d2.png)

图2：修复后检测结果



## 4、如何避免“Spring Boot 配置错误：不安全的 Actuator”

Spring Boot 也提供了安全限制功能。比如要禁用 trace 端点，则可设置如下：

如果只想打开一两个接口，那就先禁用全部接口，然后启用需要的接口：

另外也可以引入 spring-boot-starter-security 依赖并自定义配置
