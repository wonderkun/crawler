
# Nexus Repository Manager 漏洞分析


                                阅读量   
                                **439327**
                            
                        |
                        
                                                                                    



[![](./img/202867/t01eefd46052f30f7e9.png)](./img/202867/t01eefd46052f30f7e9.png)



author：r4v3zn@白帽汇安全研究院

## 前言

3 月 31 日 Nexus Repository Manager 官方发布了 `CVE-2020-10199` `CVE-2020-10204` 的漏洞通告信息，两个漏洞均是由 [Github Secutiry Lab](https://securitylab.github.com/) 的是 <a>@pwntester</a> 发现的。

Nexus Repository 是一个开源的仓库管理系统，在安装、配置、使用简单的基础上提供了更加丰富的功能。



## 漏洞概述

`CVE-2020-10199` 和 `CVE-2020-10204` 主要是由于可执行恶意 `EL表达式` 导致的。



### <a class="reference-link" name="CVE-2020-10199"></a>CVE-2020-10199

该漏洞的最终触发是通过给 `HelperBean` 的 `message` 进行 `EL表达式` 注入。

#### <a class="reference-link" name="%E5%BD%B1%E5%93%8D%E8%8C%83%E5%9B%B4"></a>影响范围

Nexus Repository Manager 3.x OSS / Pro &lt;= 3.21.1

### <a class="reference-link" name="CVE-2020-10204"></a>CVE-2020-10204

漏洞触发的主要原因是在<br>`org.sonatype.nexus.security.privilege.PrivilegesExistValidator` 或 `org.sonatype.nexus.security.role.RolesExistValidator` 类中，会对不存在的 `privilege` 或 `role` 抛出错误，而在错误信息抛出的时候，会存在一个 `EL表达式` 的渲染，会提取其中的el表达式并执行，从而造成 `EL表达式` 注入。

#### <a class="reference-link" name="%E5%BD%B1%E5%93%8D%E8%8C%83%E5%9B%B4"></a>影响范围

Nexus Repository Manager 3.x OSS / Pro &lt;= 3.21.1



## 调试

下载 Docker 镜像：

```
docker pull sonatype/nexus3:3.21.1
```

创建 nexus 数据存储目录：

```
mkdir /your-dir/nexus-data
```

运行 Docker 镜像，并且开启调试端口，其中 8081 为 web 访问端口，5050 端口为远程调试端口：

```
docker run -d --rm -p 8081:8081 -p 5050:5050 --name nexus -v /your-dir/nexus-data:/nexus-data -e INSTALL4J_ADD_VM_PARAMS="-Xms2g -Xmx2g -XX:MaxDirectMemorySize=3g  -Djava.util.prefs.userRoot=/nexus-data -agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=5050" sonatype/nexus3:3.21.1
```

下载 Nexus 源码，并且切换至 `3.21.0-05` 分支：

```
git clone https://github.com/sonatype/nexus-public.git
git checkout -b release-3.21.0-05 origin/release-3.21.0-05
```

IDEA 导入项目并且配置远程调试信息：

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_646_/t0119fc1bb44dfad779.png)



## 分析

### <a class="reference-link" name="CVE-2020-10199"></a>CVE-2020-10199

该漏洞主要是因为 `HelperBean` 的 `message` 并做 EL表达式过滤，导致出现 RCE 漏洞。根据作者作者描述，作者发现如果可控的数据进入到 `createViolation` 函数将会调用 `buildConstraintViolationWithTemplate` 执行EL表达式，在 `org.sonatype.nexus.repository.rest.api.AbstractGroupRepositoriesApiResource#validateGroupMembers:97` 中 `createViolation` 会调用执行。

```
private void validateGroupMembers(T request) {
  String groupFormat = request.getFormat();
  Set&lt;ConstraintViolation&lt;?&gt;&gt; violations = Sets.newHashSet();
  Collection&lt;String&gt; memberNames = request.getGroup().getMemberNames();
  for (String repositoryName : memberNames) {
    Repository repository = repositoryManager.get(repositoryName);
    if (nonNull(repository)) {
      String memberFormat = repository.getFormat().getValue();
      if (!memberFormat.equals(groupFormat)) {
        violations.add(constraintViolationFactory.createViolation("memberNames",
            "Member repository format does not match group repository format: " + repositoryName));
      }
    }
    else {
      violations.add(constraintViolationFactory.createViolation("memberNames",
          "Member repository does not exist: " + repositoryName));
    }
  }
  maybePropagate(violations, log);
}
```

其中 `GolangGroupRepositoriesApiResource` 继承 `AbstractGroupRepositoriesApiResource` 符合，在执行 `createRepository` 或 `updateRepository` 会利用到 `validateGroupMembers` 从而触发漏洞：

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_553_/t01256d0c066abf7c46.png)

其中 `[@path](https://github.com/path)` 为请求路径，通过变量拼接可以得出完整的路径为 `beta/repositories/go/group` 也可以通过 `Java Enterprise` 可以看到请求路径为 `beta/repositories/go/group`。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_576_/t011d91cdf2b90bc9b5.jpg)

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_522_/t012d27172d1fd096e0.png)

通过查看 swagger 可以看到请求的 Base URL 为 `/service/rest/` ，最后得出请求的完整链接为 `/service/rest/beta/repositories/go/group`。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_504_/t0145832f4aa216166a.png)

最后发起请求执行命令：

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_350_/t01586694475a776107.png)

#### <a class="reference-link" name="memberNames%E5%8F%82%E6%95%B0%E4%B8%BA%E4%BB%80%E4%B9%88%20String%20%E9%9C%80%E8%A6%81%E5%8F%98%E6%88%90%20Array"></a>memberNames参数为什么 String 需要变成 Array

可以看到请求的参数为 `GolangGroupRepositoryApiRequest` 类，该类中请求的参数 `group` 类型为 `GroupAttributes`。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_463_/t0130618d8f40ad115e.png)

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_752_/t01cd6d54df56bd97ae.png)

可以看到在 `GroupAttributes` 构造方法中需要一个参数名称为 `memberNames` 属性，该属性的类型为<br>`Collection&lt;String&gt;`。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_451_/t012f661c8c3143ead2.png)

通过查看 `Collection` 的继承链可以看到在有 `List`、`Set`、`Queue` 等继承，也就是说在请求的参数为其中继承某一个类型就可以实现。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/998_1024_/t01bf5a8cbcadfed685.png)

回到正题，为什么 `String` 类型的不行，查看 `String` 类，源代码可以看到 `String` 并未继承 `Collection` 所以无法正常使用。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_732_/t013911fa4753efe315.png)

### <a class="reference-link" name="CVE-2020-10204"></a>CVE-2020-10204

CVE-2020-10204 为 [`CVE-2018-16621`](https://github.com/Cryin/Paper/blob/master/CVE-2018-16621%20Nexus%20Repository%20Manager3%20%E4%BB%BB%E6%84%8FEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5.md) 的绕过，官方在修复的漏洞采用的方案是新增 `org.sonatype.nexus.common.template.EscapeHelper.stripJavaEl:81` 对用户输入roles参数进行过滤，正则匹配的结果是将‘${’替换为‘{ ’，从而防止EL表达式注入，代码片段如下：

```
/**
   * Strip java el start token from a string
   * @since 3.14
   */
  public String stripJavaEl(final String value) {
    if (value != null) {
      return value.replaceAll("\$+\{", "{");
    }
    return null;
  }
```

漏洞触发主要是由于 `org.sonatype.nexus.security.privilege.PrivilegesExistValidator` 和 `org.sonatype.nexus.security.role.RolesExistValidator` 类中，会将没有找到的 privilege 或 role 放入错误模板中，而在错误模板在渲染的时候会提取其中的`EL表达式`并执行。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_757_/t01509d72998a6fe91f.png)

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_965_/t01f97ad5230bd5c15d.png)

最后发起请求执行命令：

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_439_/t015d3dbafdaf50613c.png)

### <a class="reference-link" name="EL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%89%A7%E8%A1%8C%E6%B5%81%E7%A8%8B"></a>EL表达式执行流程

进入 `EL表达式` 流程之后会通过`org.hibernate.validator.internal.engine.constraintvalidation.ConstraintTree#validateConstraints` 进行校验表达式，然后通过 `addConstraintFailure` 进行添加 `validationContext`。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_414_/t01e7cd7580dd6ae0ba.png)

跟进 `addConstraintFailure` 之后可以看到 `messageTemplate` 为我们提交的 `EL表达式` 信息，然后通过 `this.interpolate` 进行执行该表达式。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_301_/t01ae04d8ca3fcf374b.png)

跟进 `this.interpolate` 可以看到通过 `this.validatorScopedContext.getMessageInterpolator().interpolate(messageTemplate, context);` 进行执行，其中 `messageTemplate` 参数为我们提交的 `EL表达式` 。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_215_/t01c5b2f09b22cbe921.png)

跟进 `org.hibernate.validator.messageinterpolation.AbstractMessageInterpolator#interpolate` 之后，将提交的 `EL表达式` 作为参数交由 `this.interpolateMessage(message, context, this.defaultLocale);` 处理。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_468_/t010e1bfd1a0c735fee.png)

继续跟进 `org.hibernate.validator.messageinterpolation.AbstractMessageInterpolator#interpolateMessage` 然后通过 `this.interpolateExpression` 进行针对表达式进行处理，然后将处理结果赋值给 `resolvedMessage`，并且作为参数再次处理表达式。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_436_/t010e88e1936a7234c1.png)

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_200_/t01c55ad8f7bc5ec6ea.png)

此时执行的代码为 `this.interpolateExpression(new TokenIterator(this.getParameterTokens(resolvedMessage, this.tokenizedELMessages, InterpolationTermType.EL)), context, locale);` 跟进代码可以看到 `isEL=True`，然后通过 `this.interpolate` 处理。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_538_/t0107861ba536c8d0bb.png)

跟进 `org.hibernate.validator.messageinterpolation.ResourceBundleMessageInterpolator#interpolate:83` 可以看到已经将我们提交的 `EL表达式` 实例化为 EL 类型对象。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_406_/t016099c691b988b917.png)

最后通过 `org.hibernate.validator.internal.engine.messageinterpolation.ElTermResolver#interpolate` 方法中的 `resolvedExpression = (String)valueExpression.getValue(elContext);` 进行执行表达式，然后将执行结果转换为 `String` 类型结果内容进行响应。

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_525_/t0140dde980f1a1ad9f.png)

以下为整个的调用链条：

[![](./img/202867/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_684_/t014d65e8d9e48458e0.png)



## 修复

升级至最新版本或 Nexus Repository Manager 3.x OSS / Pro &gt; 3.21.1



## 参考
- [GHSL-2020-011: Remote Code Execution – JavaEL Injection (low privileged accounts) in Nexus Repository Manager](https://securitylab.github.com/advisories/GHSL-2020-011-nxrm-sonatype)
- [CVE-2020-10204/CVE-2020-10199 Nexus Repository Manager3 分析&amp;以及三个类的回显构造](https://hu3sky.github.io/2020/04/08/CVE-2020-10204_CVE-2020-10199:%20Nexus%20Repository%20Manager3%20%E5%88%86%E6%9E%90&amp;%E4%BB%A5%E5%8F%8A%E4%B8%89%E4%B8%AA%E7%B1%BB%E7%9A%84%E5%9B%9E%E6%98%BE%E6%9E%84%E9%80%A0/#%E5%9B%9E%E6%98%BE)
- [Nexus Repository Manager(CVE-2020-10199/10204)漏洞分析及回显利用方法的简单讨论](https://www.cnblogs.com/magic-zero/p/12641068.html)
- [CVE-2020-10199](https://github.com/threedr3am/learnjavabug/tree/master/nexus/CVE-2020-10199)
- [CVE-2020-10204](https://github.com/threedr3am/learnjavabug/tree/master/nexus/CVE-2020-10204)