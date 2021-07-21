> 原文链接: https://www.anquanke.com//post/id/235460 


# 技术分享：看我如何窃取任意GitHub Actions敏感信息


                                阅读量   
                                **258850**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者teddykatz，文章来源：blog.teddykatz.com
                                <br>原文地址：[https://blog.teddykatz.com/2021/03/17/github-actions-write-access.html﻿](https://blog.teddykatz.com/2021/03/17/github-actions-write-access.html%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0134094b0519e3062c.jpg)](https://p3.ssl.qhimg.com/t0134094b0519e3062c.jpg)



## 写在前面的话

我个人的安全研究方法，就是去尝试奇怪的东西，然后看看会发生什么。现代软件中通常会存在大量的漏洞，工程团队通常必须根据每个漏洞影响的用户数量来确定漏洞的修复优先级。结果就显而易见了，像容易导致服务器死机的漏洞就会很快被修复。但是，如果特殊情况下才会出现的问题，并且没有明显的影响，那么这个漏洞可能会存在很长一段时间。与此同时，项目中还会不断增加新的代码，这也就意味着，每当我们发现其中一个漏洞时，我们还可以尝试用其他不同的方法来触发漏洞代码并查看是否还存在其他的漏洞。

在这篇文章中，我将跟大家分享如何窃取任意GitHub Actions敏感信息的相关方法。



## 关于GitHub Actions

大家知道，持续集成由很多操作组成，比如抓取代码、运行测试、登录远程服务器，发布到第三方服务等等。GitHub 把这些操作就称为Actions。

很多操作在不同项目里面是类似的，完全可以共享。GitHub 注意到了这一点，想出了一个很妙的点子，允许开发者把每个操作写成独立的脚本文件，存放到代码仓库，使得其他开发者可以引用。如果你需要某个Action，不必自己写复杂的脚本，直接引用他人写好的Action即可，整个持续集成过程，就变成了一个Actions的组合。这就是GitHub Actions最特别的地方。

在 GitHub Actions 的仓库中自动化、自定义和执行软件开发工作流程。 您可以发现、创建和共享操作以执行您喜欢的任何作业（包括 CI/CD），并将操作合并到完全自定义的工作流程中。



## 对pull请求输入下手

近期，我在GitHub的pull请求中发现了一个漏洞。

每个pull请求都应该有一个“基分支”（也称为“基引用”），该分支用于指定一组提议的更改要与之进行比较的分支。一般来说，这个基本分支就是存储库的主分支。

作为pull请求的创建者，我们可以决定它应该拥有哪个基分支。例如，我们可以将基分支设置为另一个仍在进行中的分支，或者更新频率较低的发布分支，而不是将其设置为主分支。

但这是一个作为字符串提供的用户输入，因此我们不需要提供分支名称。如果我们使用GitHub的API创建了一个pull请求，并将“基分支”名称设置为其他名称（如commit哈希），会发生什么情况？

```
mutation `{`
    createPullRequest(input: `{`
        repositoryId: “…”title: “Update README.md”headRefName: “not - an - aardvark: patch - 1”

        # ? ??this is a commit hash,
        not a ref baseRefName: "fd9cfdc590e789ae559b5a7878e7e6b929a249d9"
    `}`) `{`
        __typename
    `}`
`}`
```

当我在测试存储库上尝试此操作时，GitHub返回了一个错误：

```
`{`“errors”: [`{`“message”: “Base ref must be a branch”
    `}`]
`}`
```

很好，这很合理！

但是，我我刚刚发现了另一个问题，GitHub在创建pull请求时比在编辑请求时应用了更严格的验证。接下来，我便打算尝试使用有效的基分支创建pull请求，然后将基分支名称编辑为commit哈希。令人惊讶的是，我竟然成功了！我最终拿到了一个pull请求，其基分支是一个commit。



## 如此“荒谬”的pull请求

值得注意的是，“基分支是commit的pull请求”其实并没有什么意义。在Git术语中，分支和commit是不同类型的东西，它们不能互换。通常，我们可以通过更新基分支来“合并”pull请求，以指向包含pull请求中更改的新commit。但是，我们还不清楚如果基分支本身就是commit的情况下，“合并”pull请求意味着什么。因为由特定哈希标识的commit是不可变的，我们也无法将其合并到其他commit中。

不过，软件有时所作的事情并不一定要有意义，所以我们才能拿到一个基分支为commit的pull请求：

[![](https://p5.ssl.qhimg.com/t0167b5f8e570fb3726.png)](https://p5.ssl.qhimg.com/t0167b5f8e570fb3726.png)

GitHub的UI会尝试显示这个pull请求，但UI会显示称有合并冲突。但是，这个pull请求中实际上没有任何合并冲突。因此我怀疑后端的某些代码会尝试模拟合并，然后UI便会认为错误是由合并冲突造成的。

另外，我还尝试将基引用设置为commit短哈希（而不是完整的40个字符的哈希）。然后，当我用相同的短哈希推送另一个commit时，UI中指向基分支的链接开始返回404（因为它链接到一个不明确的短哈希），但其他的一切似乎都在继续正常工作。



## GitHub Actions崩溃的原因

先稍等一下，我们先来讨论一下GitHub Actions这个内置于GitHub中的自动化平台。GitHub Actions实际上是一个托管bot服务，它允许项目在沙盒中运行任意代码，以响应GitHub上发生的事件。例如，GitHub操作的一些常见用法包括每次有人推送commit时运行项目的测试、将最近的更改部署到外部服务器以及为新创建的GitHub问题添加标签等等。（我曾经维护过大型开源项目，我可以证明这样的自动化非常有用。）

**<a class="reference-link" name="GitHub%20Actions%E6%9C%89%E4%B8%80%E4%B8%AA%E6%9C%89%E8%B6%A3%E7%9A%84%E6%9D%83%E9%99%90%E6%A8%A1%E5%9E%8B%EF%BC%9A%E6%80%BB%E7%BB%93%E5%A6%82%E4%B8%8B%EF%BC%9A"></a>GitHub Actions有一个有趣的权限模型：总结如下：**

1、GitHub Actions的配置项由一系列工作流组成，存储在项目代码库的.github/workflows/文件夹中。每一个工作流都能够监听代码库的指定事件，并执行对应事件的代码。

2、对于需要敏感信息的工作流，维护人员还可以通过GitHub库设置添加自定义密码来实现。然后，工作流的配置可以指定将敏感数据注入到环境变量中。只有对存储库具有写权限的人才能访问敏感数据，并且在存储库被fork时不会泄露敏感数据。

3、默认情况下，每一个库都会有一个名为GITHUB_TOKEN的敏感数据，它是一个GitHub API令牌，可以给用户提供写入权限。



## GitHub Actions如何处理pull请求？GitHub Actions如何处理pull请求？

触发自动化以响应pull请求通常很有用。例如，维护人员可能希望自动运行项目的测试，以便参与者可以看到他们的更改是否破坏了任何东西。除此之外，维护人员可能还希望自动向新的pull请求添加注释和标签。但是重要的是，pull请求的发起者并不能访问存储库的敏感数据。为了解决这个问题，GitHub提供了两种不同的方法来通过pull请求触发操作工作流：

1、pull_request事件可以模拟pull请求的合并，并根据合并提交时的配置和代码触发操作工作流。这个功能用于运行测试，并验证在合并pull请求时代码是否仍能工作。但是，由于pull请求中的代码可能是恶意的，因此运行由pull_request事件触发的工作流时不会访问存储库的敏感数据。

2、pull_request_target事件将根据配置项和pull请求基分支的代码来触发Actions工作流。由于基分支是基础代码库本身的一部分，而不是fork的一部分，因此由pull_request_target触发的工作流是受信任的，并且可以在访问敏感数据的情况下运行，这是为了给新的pull请求添加注释和标签。



## pull请求和GitHub Actions

实际上，我们之前创建的那些貌似毫无意义的pull请求其实也并不是完全没用的，因为它会产生破坏GitHub操作权限模型的副作用。

综上所述，攻击者将能够做到下列事情：

1、fork任意一个使用GitHub Actions的公开代码库；

2、创建一个该库的pull请求；

3、使用pull_request_target事件创建一个恶意Actions工作流，然后单独向该fork库commit；

4、将第二步基分支的pull请求更新为第三步的commit哈希；

然后恶意Actions工作流将立即运行，并从目标存储库中获取敏感数据。此时，攻击者将拥有对目标存储库的写访问权限，除此之外他们还可以通过GitHub访问存储库与之集成的任何服务。

许多开源项目会直接使用保存为GitHub Actions敏感数据的凭据，而且还会直接从GitHub发布到包管理器。因此，攻击者有可能通过在一堆开源项目上同时利用此问题，窃取其所有包管理器凭据，并发布一堆包含恶意软件的包更新，从而发动更大规模的供应链攻击。



## 参考资料

1、[https://danluu.com/everything-is-broken/](https://danluu.com/everything-is-broken/)<br>
2、[https://www.reddit.com/r/WhereDidTheSiloGo/search?q=subreddit%3AWhereDidTheSiloGo&amp;restrict_sr=on&amp;sort=top&amp;t=all](https://www.reddit.com/r/WhereDidTheSiloGo/search?q=subreddit%3AWhereDidTheSiloGo&amp;restrict_sr=on&amp;sort=top&amp;t=all)<br>
3、[https://docs.github.com/en/graphql/reference/mutations#createpullrequest](https://docs.github.com/en/graphql/reference/mutations#createpullrequest)<br>
4、[https://blog.teddykatz.com/2021/03/10/fork-collab-abuse.html](https://blog.teddykatz.com/2021/03/10/fork-collab-abuse.html)<br>
5、[https://blog.teddykatz.com/2019/11/12/github-actions-dos.html](https://blog.teddykatz.com/2019/11/12/github-actions-dos.html)<br>
6、[https://www.goodreads.com/quotes/7570350-the-patient-says-doctor-it-hurts-when-i-do-this](https://www.goodreads.com/quotes/7570350-the-patient-says-doctor-it-hurts-when-i-do-this)<br>
7、[https://github.com/features/actions](https://github.com/features/actions)<br>
8、[https://docs.github.com/en/actions/reference/encrypted-secrets](https://docs.github.com/en/actions/reference/encrypted-secrets)<br>
9、[https://docs.github.com/en/actions/reference/authentication-in-a-workflow#about-the-github_token-secret](https://docs.github.com/en/actions/reference/authentication-in-a-workflow#about-the-github_token-secret)<br>
10、[https://gist.github.com/not-an-aardvark/357547edf338f8fa9920bbcd286e3a7b](https://gist.github.com/not-an-aardvark/357547edf338f8fa9920bbcd286e3a7b)<br>
11、[https://docs.github.com/en/actions/guides/publishing-nodejs-packages#publishing-packages-to-the-npm-registry](https://docs.github.com/en/actions/guides/publishing-nodejs-packages#publishing-packages-to-the-npm-registry)<br>
12、[https://eslint.org/blog/2018/07/postmortem-for-malicious-package-publishes](https://eslint.org/blog/2018/07/postmortem-for-malicious-package-publishes)
