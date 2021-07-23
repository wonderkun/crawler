> 原文链接: https://www.anquanke.com//post/id/86999 


# 【技术分享】如何在Rubygems.org上实现远程代码执行


                                阅读量   
                                **79874**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：justi.cz
                                <br>原文地址：[https://justi.cz/security/2017/10/07/rubygems-org-rce.html](https://justi.cz/security/2017/10/07/rubygems-org-rce.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t018e96349497781378.png)](https://p5.ssl.qhimg.com/t018e96349497781378.png)

译者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**概述**

[**rubygems.org**](https://rubygems.org/)是目前一个非常流行的ruby依赖库托管服务，而本文所介绍的技术将通过rubygems.org上的一个反序列化漏洞来实现远程代码执行。不过在本文发稿之前，该漏洞([**CVE-2017-090**](https://www.cve.mitre.org/cgi-bin/cvename.cgi?name=2017-0903)**3**)已经被成功修复，具体信息请参考官方发表的声明文件【[传送门](http://blog.rubygems.org/2017/10/09/unsafe-object-deserialization-vulnerability.html)】。

如果你之前曾经开发过ruby应用程序的话，你很可能已经使用过rubygems.org的服务了。当然了，作为社区中的一个热门ruby依赖托管服务，你肯定会信任该网站在你计算机中所运行的任何程序，不然你也不会选择rubygems.org啦！但是，比如说当你运行命令gem install rails时，gem工具会从rubygems.org获取rails工具源码及其相应的依赖组件，然后自动将所有组件全部安装部署好。但需要注意的是，任何人在注册了一个rubygems.org账号之后，都可以发布gems程序。

**<br>**

**漏洞分析**

Ruby gems实际上就是**tar压缩文件**，所以运行完tar -xvf foo.gem命令之后，你将会得到下面这三种文件：



```
metadata.gz
data.tar.gz
checksums.yaml.gz
```

这些文件都是gzip压缩文件。metadata.gz中包含一个YAML文件，其中存储了跟gem相关的信息，例如工具名称、开发者信息以及版本号等等。data.tar.gz中包含的是另一个存储了工具完整源代码的tar压缩文档。checksums.yaml.gz中同样包含了一个YAML文件，而这个YAML文件中存储的是gem内容的加密哈希。

在此之前，我一直都不知道“解析不受信任的YAML文件”这种行为是[非常危险](https://www.sitepoint.com/anatomy-of-an-exploit-an-in-depth-look-at-the-rails-yaml-vulnerability/)的，因为我一直认为它跟JSON一样是一种良性的数据交换格式。实际上，YAML允许我们对任意对象进行编码，它跟Python的[pickle](https://docs.python.org/2/library/pickle.html)非常相似。

当你向rubygems.org上传一个gem之后，应用程序会调用Gem::Package.new(body).spec，而rubygems gem（拥有上述方法）会使用一种不安全的方法来调用YAML.load，并在gem中加载YAML文件。

但是，rubygems.org的开发人员是知道这一点的（很可能是因为这一次【[事件](https://docs.google.com/document/d/10tuM51VKRcSHJtUZotraMlrMHWK1uXs8qQ6Hmguyf1g/edit#heading=h.vklh7bga5mlq)】才知道的）。在2013年，开发人员曾尝试修复过这个问题([monkey-patching](https://github.com/rubygems/rubygems.org/commit/334bff6beb072f17c252dee97a03b5c7b81aef02#diff-61d2ac84a9d683aaee31dfc7bec7e8c0))，并让YAML以及gem解析库只允许接受白名单列表中规定的数据类型，而且在2015年rubygems.org甚至开始使用[Psych.safe_load](https://github.com/rubygems/rubygems.org/commit/63bb533ffc3543f4aab049d3af4f83b606442044#diff-61d2ac84a9d683aaee31dfc7bec7e8c0)了。

不幸的是，monkey-patching根本就没有效果，因为它之修复了Gem::Specification#from_yaml方法。如果我们真的弄清楚了#spec方法在调用过程中所发生的事情，我们就会发现它还会调用#verify方法，其中最重要的部分如下列代码所示：



```
# ...
  @gem.with_read_io do |io|
    Gem::Package::TarReader.new io do |reader|
    read_checksums reader
 
    verify_files reader
    end
  end
 
  verify_checksums @digests, @checksums
# ...
#read_checksums方法的相关代码如下所示：
# ...
  Gem.load_yaml
 
  @checksums = gem.seek 'checksums.yaml.gz' do |entry|
    Zlib::GzipReader.wrap entry do |gz_io|
      YAML.load gz_io.read # oops
    end
  end
# ...
```

非常好，接下来我们就可以用我们所能控制的输入数据来调用YAML.load了。但是，我们如何利用这个漏洞呢？一开始，我曾尝试在YAML.load调用其自己的时候来运行我自己的漏洞利用代码，但是实现这个的难度远远比我想象的要困难得多，虽然我可以对任意对象进行反序列化操作，但我真正能够对这些对象所做的操作以及我所能调用的方法实际上是极其有限的。rubygems.org所使用的YAML解析库Psych只允许我调用例如#[]=，#init_with以及#marshal_load之类的方法。这里的#marshal_load并不是Marshal.load，如果是Marshal.load的话那可就简单多了。但是对于绝大多数对象来说，这些方法并不能给攻击者提供多大的灵活性，因为这些对象的常见方法一般都是初始化一些变量然后返回一些值。也有人说某些标准rails库中的对象拥有危险的#[]=方法，但是我并没有找到。

于是接下来，我又回头开始分析rubygems.org应用程序，我想要确定它会将@checksums变量用在哪里，我们可以在任何类中设置一个相关实例吗?#verify_checksums的相关代码如下所示：



```
# ...
  checksums.sort.each do |algorithm, gem_digests|
    gem_digests.sort.each do |file_name, gem_hexdigest|
      computed_digest = digests[algorithm][file_name]
# ...
```

所以，如果我们能够构建一个恶意对象并尝试调用#sort方法的话，我们就可以利用该漏洞来做一些危险的事情了。最终，我设计了如下所示的PoC。其中，有效的攻击Payload包含在base-64编码的代码之中，但我的PoC代码只会在命令行界面中输出字符串“opps”：



```
SHA1: !ruby/object:Gem::Package::TarReader
  io: !ruby/object:Gem::Package::TarReader::Entry
    closed: false
    header: 'foo'
    read: 0
    io: !ruby/object:ActiveSupport::Cache::MemoryStore
      options: `{``}`
      monitor: !ruby/object:ActiveSupport::Cache::Strategy::LocalCache::LocalStore
        registry: `{``}`
      key_access: `{``}`
      data:
        '3': !ruby/object:ActiveSupport::Cache::Entry
          compressed: true
          value: !binary '
          eJx1jrsKAjEQRbeQNT4QwQ9Q8hlTRXGL7UTFemMysIGYCZNZ0b/XYsHK8nIO
          nDtRBGbvJDzxMuRMLABHzIzOSqD0G+jbVMQmhzfLwd4jnphebwUrE0ZAoJrz
          YQpLE0PCRKGCmSnsWr3p0PW000S56G5eQ91cv9oDpScPC8YyRIG18WOMmGD7
          /1X1AV+XPlQ='
```

完成最后一步操作之后，我们还要回头调用#sort方法。在最后一步操作中，我们可以得到一个ActiveSupport::Cache::Entry对象。这个对象扮演着一个非常重要的角色，因为当#value方法被调用时，@compressed的值为true，而它将会调用Marshal.load方法，[并对攻击者所提供的数据进行解析处理](https://github.com/rails/rails/blob/5-1-stable/activesupport/lib/active_support/cache.rb#L618)。这也就意味着，它将负责执行攻击者所提供的代码。这里所使用的数据提取方法在之前已经介绍过了，感兴趣的同学可以参考【[这篇文章](https://github.com/charliesome/charlie.bz/blob/master/posts/rails-3.2.10-remote-code-execution.md)】。不幸的是，我们无法使用YAML来对这个对象进行反序列化处理并实现代码执行，因为它几乎没有提供任何可以直接调用的方法，包括设置实例变量的方法在内。在这种情况下，我们必须要使用Marshal.load来完成对象的加载。

接下来，ActiveSupport::Cache::MemoryStore对象会在一个名叫@data的哈希变量中存放我们的恶意对象。在其父类ActiveSupport::Cache::Store中，定义了一个名叫#read的方法，这个方法可以在MemoryStore中调用#read_entry方法。简单说来，#read_entry方法的作用就是从@data存放的数据中提取出entry并将其返回给调用者。

针对MemoryStore#read方法的调用来自于针对Gem::Package::TarReader::Entry#read的调用，而它本身又会被Gem::Package::TarReader#each方法带哦用。当读取的结果返回给调用者之后，#size方法将会在返回值中被调用，并最终执行我们的恶意Payload（恶意对象）。

最后，由于Gem::Package::TarReader定义了“include Enumerable”，调用其#sort方法的对象还会调用其#each方法，并开启上述的整个攻击链。

**<br>**

**总结**

对我来说，这一次的研究让我深刻地意识到了YAML其功能强大之处。在将来，YAML.load方法很可能会被修改成只允许接收白名单中定义的类来当作可选参数了，而这也会让对复杂对象的反序列化操作变成了一种可选行为。

就目前的情况来看，YAML.load方法确实应该改名为YAML.unsafe_load之类的，这样一来广大用户在使用这个方法的时候就会知道它其实是一种非常不安全的方法，而用户应该使用的是YAML.safe_load…:D

最后，感谢rubygems.org的团队能够对我提交的安全报告予以快速响应，如果他们没有设立这样一个高效的[](https://hackerone.com/rubygems)[漏洞奖励计划](https://hackerone.com/rubygems)的话，这是不可能办到的，这一点值得其他社区项目团队以及大型企业学习。
