> 原文链接: https://www.anquanke.com//post/id/247598 


# yapi 远程命令执行漏洞分析


                                阅读量   
                                **66192**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t013c22bfb27e978605.jpg)](https://p3.ssl.qhimg.com/t013c22bfb27e978605.jpg)



作者：0x4qE@知道创宇404实验室

## 0x01 简述

[Yapi](https://github.com/YMFE/yapi) 是高效、易用、功能强大的 api 管理平台，旨在为开发、产品、测试人员提供更优雅的接口管理服务。可以帮助开发者轻松创建、发布、维护 API，YApi 还为用户提供了优秀的交互体验，开发人员只需利用平台提供的接口数据写入工具以及简单的点击操作就可以实现接口的管理。

2021年7月8日，有用户在 GitHub 上发布了遭受攻击的相关信息。攻击者通过注册用户，并使用 Mock 功能实现远程命令执行。命令执行的原理是 Node.js 通过 `require('vm')` 来构建沙箱环境，而攻击者可以通过原型链改变沙箱环境运行的上下文，从而达到沙箱逃逸的效果。通过 `vm.runInNewContext("this.constructor.constructor('return process')()")` 即可获得一个 process 对象。

### <a class="reference-link" name="%E5%BD%B1%E5%93%8D%E7%89%88%E6%9C%AC"></a>影响版本

Yapi &lt;= 1.9.2



## 0x02 复现

复现环境为 Yapi 1.9.2，[Docker 环境](https://hub.docker.com/r/0x4qe/yapi_1.9.2_rce)已上传到 Dokcer Hub。

攻击者通过注册功能注册一个新用户，在新建项目页面创建一个新项目。

[![](https://p2.ssl.qhimg.com/t01547b4d3e398c7ccc.png)](https://p2.ssl.qhimg.com/t01547b4d3e398c7ccc.png)

在设置 -&gt; 全局 mock 脚本中添加恶意代码。设置命令为反弹 shell 到远程服务器。

[![](https://p0.ssl.qhimg.com/t01e7d11c57c2194e33.png)](https://p0.ssl.qhimg.com/t01e7d11c57c2194e33.png)

POC如下：

[![](https://p3.ssl.qhimg.com/t012f60ba32dffd44d8.png)](https://p3.ssl.qhimg.com/t012f60ba32dffd44d8.png)

随后添加接口，访问提供的 mock 地址。

[![](https://p5.ssl.qhimg.com/t01db32e65ac83eb381.png)](https://p5.ssl.qhimg.com/t01db32e65ac83eb381.png)

随后即可在远程服务器上收到来自命令执行反弹的 shell。

[![](https://p1.ssl.qhimg.com/t015a2def4b799614d6.png)](https://p1.ssl.qhimg.com/t015a2def4b799614d6.png)



## 0x03 漏洞分析

在 Github 上发布的新版本 1.9.3 已经修复了这个漏洞。[https://github.com/YMFE/yapi/commit/37f7e55a07ca1c236cff6b0f0b00e6ec5063c58e](https://github.com/YMFE/yapi/commit/37f7e55a07ca1c236cff6b0f0b00e6ec5063c58e)[/https://github.com/YMFE/yapi/commit/37f7e55a07ca1c236cff6b0f0b00e6ec5063c58e](//github.com/YMFE/yapi/commit/37f7e55a07ca1c236cff6b0f0b00e6ec5063c58e)

核心问题在`server/utils/commons.js line 635`

[![](https://p3.ssl.qhimg.com/t0163cfdc65473eda0b.png)](https://p3.ssl.qhimg.com/t0163cfdc65473eda0b.png)

修复后的代码引入了新的动态脚本执行模块 [safeify](https://github.com/Houfeng/safeify)，替换了原有的 [vm](https://nodejs.org/api/vm.html) 模块。根据 Node.js 官方的描述

> The vm module is not a security mechanism. Do not use it to run untrusted code.

`vm` 模块并不是一个完全安全的动态脚本执行模块。先来看看 vm 有哪些执行命令的函数。

[![](https://p4.ssl.qhimg.com/t01d59cdde03fd8e23f.png)](https://p4.ssl.qhimg.com/t01d59cdde03fd8e23f.png)

根据[官方文档](https://nodejs.org/api/vm.html#vm_vm_runincontext_code_contextifiedobject_options)，这三个函数都有一个参数 `contextObject` 用来表示上下文。但是这个上下文并不是完全隔离地运行的，可以通过原型链的形式实现沙箱逃逸。

```
&gt; vm.runInNewContext("this")
`{``}` // this 是一个空对象

&gt; vm.runInNewContext("this.constructor")
[Function: Object] // 通过 this.constructor 可以获得一个对象的构造方法

&gt; vm.runInNewContext("this.constructor('a')")
[String: 'a'] // 获得了一个字符串对象

&gt; vm.runInNewContext("this.constructor.constructor('return process')")
[Function: anonymous] // 获得了一个匿名函数 function() `{` return process; `}`

&gt; vm.runInNewContext("this.constructor.constructor('return process')()")
process `{`
  title: 'node',
  version: 'v10.19.0',
  ...
`}` // 获得了一个 process() 函数的执行结果
  // 接下来就可以通过 process.mainModule.require('chile_process').execSync('command') 来执行任意代码
```

有一种防护方案是将上下文对象的原型链赋值成 null，就可以防止利用 this.constructor 进行沙盒逃逸。`const contextObject = Object.create(null)`，但是这种方法有个缺点，这样禁用了内置的函数，业务需求完全得不到实现。有文章[Node.js沙盒逃逸分析](https://jelly.jd.com/article/5f7296d0c526ae0148c2a2bb)提到可以用 `vm.runInNewContext('"a".constructor.constructor("return process")().exit()', ctx);`绕过原型链为 null 的限制。测试后发现无效，如果不考虑业务需求的话，`Object.create(null)`应该是一种终极的解决方案了。

接下来我们可以下断点跟进看看漏洞是如何被利用的。在`server/utils/commons.js line 635`处下断点，构造 mock 脚本，然后访问 mock 接口，程序运行停止在断点处。使用 F11 `Step into` 进入`server/utils/conmmons.js`处，单步调试至`line 289`，再用 F11 进入沙盒环境。

```
const sandbox = this // 将沙盒赋给了变量 sandbox
const process = this.constructor.constructor('return process')() // 利用原型链进行沙盒逃逸获得 process 对象
mockJson = process.mainModule.require('child_process').execSync('whoami &amp;&amp; ps -ef').toString() // 给 sandbox.mockJson 赋值了命令执行的结果
```

函数执行结束后会调用 `context.mockJson = sandbox.mockJson` 并将 mockJson 作为 req.body 返回用户，于是就可以在页面中看到命令执行的反馈。



## 0x04 防护方案

1、更新 Yapi 至官方发布的 1.9.3，新版本用了更为安全的 safeify 模块，可以有效地防止这个漏洞。

2、如果没有使用注册的需求，建议关闭 Yapi 的注册功能。通过修改 Yapi 项目目录下的 config.json 文件，将 closeRegister 字段修改为 true 并重启服务即可。

3、如果没有 Mock 功能的需求，建议关闭 Yapi 的 Mock 功能。



## 0x05 相关链接

1、[高级Mock可以获取到系统操作权限](https://github.com/YMFE/yapi/issues/2099)<br>
2、[Node.js命令执行和沙箱安全](https://mp.weixin.qq.com/s/obDPE6ZWauDG7PeIES6sHA)<br>
3、[Node.js沙盒逃逸分析](https://jelly.jd.com/article/5f7296d0c526ae0148c2a2bb)
