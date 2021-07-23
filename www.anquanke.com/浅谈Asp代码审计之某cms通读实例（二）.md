> 原文链接: https://www.anquanke.com//post/id/183506 


# 浅谈Asp代码审计之某cms通读实例（二）


                                阅读量   
                                **200079**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0123791f51d2d952d1.png)](https://p5.ssl.qhimg.com/t0123791f51d2d952d1.png)



## 0x1 前言(Preface)

阅读此文之前，如果不会搭建相关审计环境，建议从我第一篇文章开始看起[浅谈Mac上手 Asp and Asp.net 代码审计（一）](https://www.anquanke.com/post/id/180040),关于asp的审计应该是很久以前的东西，但是经常在内网渗透或者红队中遇到asp的老系统，同时也为了扩展自己的知识面，在web方向打下基础。此篇文章可能比较小众，欢迎各位师傅拍砖指点。(Ps.此教程还是从小白的角度出发,因为作者本身就是小白)



## 0x2 审计对象(Audit Object)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b52318d4628fd14f.png)

这个系统是不是感觉有点怀旧的感觉,这就是新云网站管理系统V3.0.0,源码可以在网上搜索下载到,



## 0x3 asp代码审计一些特点(Feature)

asp程序写的真的很原始,读起来逻辑很连贯,而且基本都是单入口的,包含文件内容一般是一些全局配置的内容,所以通读asp程序,就是逐个文件去读,当然有些小技巧,提高阅读速度，快速定位有弱点的位置，下面就是分享下自己的学习过程啦。

小白是不是感觉自己不懂vbscript就不能上手asp代码审计了呢? 那么可以先补充下基础知识再继续学习,如下是vbscript的基础语法

asp程序一般支持VBSCRIPT 和 jscript ,但是常见的都是vbscript语法,所以我们只说下vbscript的基础语法。

asp关键词基本都是大驼峰命名,即首字母大写,但是vbscript语法是不区分大小写

asp文件VBscript标识开头:

```
&lt;%@ LANGUAGE = VBScript CodePage = 936%&gt;
```

变量声明:

```
Dim html
```

数组:

Dim array(2) ‘跟我们平时学的大小不太一样

Dim array(2,3) ‘3行4列多维数组

单行注释:

```
'
```

字符串链接符:

```
&amp;
```

字符串:

必须用双引号括起来

常用输出:

```
Response.Write("Hello World!")
```

for循环语句:

```
for i=0 to 3:
    ......
next

Do
....
Loop

For Each .... Next ...
```

流程控制语句:

```
If ... Then ... '只执行一条语句
If... Then ... End If '可以执行多条语句
If ... Then ... Else ...
If ... Then ... ElseIf ...
Select ... Case
```

过程:

```
' --  Sub过程
Sub Name(str1, str2)
    ........
End Sub
' -- 调用
1.Call Name(str1, str2)
2. Name ' --无参调用
' --  Function
Function Name(number)
.........
End Function

' -- Function 过程
Function GetName()
Response.Write "test"
End Function
GetName
' --- 区别
' -- Sub没有返回值，而Fubnction有返回值。
' -- Sub不能放在表达式中，而Function可以。
```

类的使用:

```
Class ClassName
Type  VariableName
Private Sub Class_Initialize() '构造过程
Reponse.Write("class initialize starting")
End Sub
Private Sub Class_Terminate() '析构过程
Response.Write("class end")
End Class
```

下面是我在熟悉这些语法的时候本地练习的代码:

```
&lt;%@ Language = vbscript CodePage = 936 %&gt;
&lt;%
Dim html 'declaration,i
Dim array(2)
array(0) = "array[0]"
array(1) = "array[1]"
array(2) = "array[2]"
html="123" 'value  variable
Response.Write("123" &amp; html &amp; "&lt;/br&gt;") 'output result
for i=0 to 2
    Response.Write(i)
    Response.Write(array(i) &amp; "&lt;/br&gt;")
next
Dim Num1,Num2
Num1 = 10 
Num2 = 20
If Num1 &lt; Num2 Then Response.Write("Num1 &lt; Num2 ! Right!")

Response.Write("&lt;/br&gt;")

If Num1 &lt; Num2 Then
    Response.Write("Num1 &lt; Num2 ! Right! 1")
    Response.Write("Num1 &lt; Num2 ! Right! 2")
End If

Response.Write("&lt;/br&gt;")

If Num2 &lt; Num1 Then
    Response.Write("Num1 &gt; Num2 ! Right!")
Else
    Response.Write("Num1 &lt; Num2 ! Right!")
End If

Response.Write("&lt;/br&gt;")

Response.Write("Select Case Example")
Response.Write("&lt;/br&gt;")
Dim Week
Week = WeekDay(date)
Select Case Week
Case 1
    Response.Write("1")
Case 2
    Response.Write("2")
Case 3
    Response.Write("3")
Case 4
    Response.Write("4")
Case 5
    Response.Write("5")
Case 6
    Response.Write("6")
Case 7
    Response.Write("7")  
End Select
Response.Write("&lt;/br&gt;")
Response.Write("For Each  Example")
Dim Num(10)
For i = 0 To 5
    Num(i) = i
Next
Dim j
For Each j In Num
    Response.Write(j &amp; "&lt;/br&gt;")
Next

Response.Write(" proccess and function Example" &amp; "&lt;/br&gt;")
Sub Res(content)
    Response.Write("Sub test " &amp; content &amp; "&lt;/br&gt;")
End Sub
Sub test() ' no parameter function
    Response.Write("&lt;/br&gt; i am test &lt;/br&gt;")
End Sub
Call Res("i am content")
Res "123"
test ' --no parameter call
Function GetName()
Response.Write "I am GetName Function"
End Function
GetName
Class MyClass 
    Private TestProperty
    Private Sub Class_Initialize()
       Response.Write("&lt;/br&gt;Initialize starting!")
       TestProperty = "test"
    End Sub
    Private Sub Class_Terminate()
       Response.Write("Terminate End!")
    End Sub
    Public Property Let SetProperty(ByVal str)
       TestProperty = "&lt;/br&gt;" &amp; "change:" &amp; str
    End Property
    Public Property Get GetProperty()
       GetProperty = TestProperty &amp;  "&lt;/br&gt;" '返回值
    End Property
End Class
Dim obj
Set obj = New MyClass
obj.SetProperty="123"
Response.Write(obj.GetProperty)
Set obj = nothing '释放对象
%&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a3165cba1e3caa61.png)



## 0x4 开始代码审计之旅(Main)

### <a name="header-n43"></a>0x4.1 cms程序结构

command:tree -L 2 -c

├── Announce.Asp<br>
├── cclist.asp<br>
├── conn.asp<br>
├── const.asp<br>
├── count.asp<br>
├── database  // 数据库文件 Access<br>
│   ├── #collection.asa<br>
│   ├── #newasp.asa<br>
│   ├── IPAddress.dat<br>
│   └── maillist.mdb<br>
├── index.asp<br>
├── login.asp<br>
├── runads.asp<br>
├── search.asp<br>
├── showerr.asp<br>
├── skin //仰视文件 忽略<br>
├── vote //投票模块<br>
│   ├── join.asp<br>
│   ├── newaspvote.fla<br>
│   ├── showvote.js<br>
│   ├── vote.asp<br>
│   ├── vote.htm<br>
│   └── vote.swf<br>
├── images //静态文件 忽略<br>
├── inc  //配置文件<br>
│   ├── FlashChannel.asp<br>
│   ├── GetCode.asp<br>
│   ├── NewsChannel.asp<br>
│   ├── NoCheckCode.asp<br>
│   ├── SoftChannel.asp<br>
│   ├── Std_StranJF.Js<br>
│   ├── UploadCls.Asp<br>
│   ├── base64.asp<br>
│   ├── chkinput.asp<br>
│   ├── classmenu.asp<br>
│   ├── cls_custom.asp<br>
│   ├── cls_down.asp<br>
│   ├── cls_editor.asp<br>
│   ├── cls_main.asp<br>
│   ├── cls_md5.asp<br>
│   ├── cls_payment.asp<br>
│   ├── cls_public.asp<br>
│   ├── const.asp<br>
│   ├── email.asp<br>
│   ├── function.asp<br>
│   ├── main.js<br>
│   ├── md5.asp<br>
│   ├── online.asp<br>
│   ├── ubbcode.asp<br>
│   ├── upload.inc<br>
│   └── xslt<br>
├── admin //后台文件<br>
│   ├── Admin_CreateFlash.Asp<br>
│   ├── Admin_UploadFile.Asp<br>
│   ├── admin_admanage.asp<br>
│   ├── admin_article.asp<br>
│   ├── admin_book.asp<br>
│   ├── admin_card.asp<br>
│   ├── admin_channel.asp<br>
│   ├── admin_classad.asp<br>
│   ├── admin_comment.asp<br>
│   ├── admin_confirm.asp<br>
│   ├── admin_helpview.asp<br>
│   ├── admin_link.asp<br>
│   ├── admin_mailist.asp<br>
│   ├── admin_mailout.asp<br>
│   ├── admin_main.asp<br>
│   ├── admin_makenews.asp<br>
│   ├── admin_message.asp<br>
│   ├── admin_online.asp<br>
│   ├── admin_other.asp<br>
│   ├── admin_password.asp<br>
│   ├── admin_paymode.asp<br>
│   ├── admin_probe.asp<br>
│   ├── admin_replace.asp<br>
│   ├── admin_setting.asp<br>
│   ├── admin_special.asp<br>
│   ├── admin_template.asp<br>
│   ├── admin_user.asp<br>
│   ├── admin_vote.asp<br>
│   ├── check.asp<br>
│   ├── Admin_ArticleGather.asp<br>
│   ├── Admin_CreateArticle.Asp<br>
│   ├── Admin_CreateSoft.Asp<br>
│   ├── Admin_SoftGather.asp<br>
│   ├── CleanCache.asp<br>
│   ├── Logdata.asa<br>
│   ├── about.asp<br>
│   ├── admin_account.asp<br>
│   ├── admin_announce.asp<br>
│   ├── admin_articleset.asp<br>
│   ├── admin_bottom.asp<br>
│   ├── admin_classify.asp<br>
│   ├── admin_config.asp<br>
│   ├── admin_conform.asp<br>
│   ├── admin_cookies.asp<br>
│   ├── admin_createindex.asp<br>
│   ├── admin_custom.asp<br>
│   ├── admin_database.asp<br>
│   ├── admin_downfile.asp<br>
│   ├── admin_downlog.asp<br>
│   ├── admin_flash.asp<br>
│   ├── admin_group.asp<br>
│   ├── admin_index.asp<br>
│   ├── admin_jsfile.asp<br>
│   ├── admin_label.asp<br>
│   ├── admin_left.asp<br>
│   ├── admin_loadskin.asp<br>
│   ├── admin_log.asp<br>
│   ├── admin_login.asp<br>
│   ├── admin_logout.asp<br>
│   ├── admin_makeflash.asp<br>
│   ├── admin_makesoft.asp<br>
│   ├── admin_master.asp<br>
│   ├── admin_selfile.asp<br>
│   ├── admin_server.asp<br>
│   ├── admin_soft.asp<br>
│   ├── admin_softerr.asp<br>
│   ├── admin_softset.asp<br>
│   ├── admin_top.asp<br>
│   ├── admin_userorder.asp<br>
│   ├── images<br>
│   ├── remoteupload.asp<br>
│   ├── setup.asp<br>
│   ├── showerr.asp<br>
│   ├── upload.asp<br>
│   └── include<br>
├── js //js文件忽略<br>
├── user //用户模块<br>
│   ├── Upfile.asp<br>
│   ├── Upload.asp<br>
│   ├── activepass.asp<br>
│   ├── addmoney.asp<br>
│   ├── articlelist.asp<br>
│   ├── articlepost.asp<br>
│   ├── changeinfo.asp<br>
│   ├── changepsw.asp<br>
│   ├── check.asp<br>
│   ├── checkreg.asp<br>
│   ├── config.asp<br>
│   ├── confirm.asp<br>
│   ├── downlog.asp<br>
│   ├── favorite.asp<br>
│   ├── flash.asp<br>
│   ├── flashlist.asp<br>
│   ├── flashpost.asp<br>
│   ├── foot.inc<br>
│   ├── friend.asp<br>
│   ├── head.inc<br>
│   ├── help.asp<br>
│   ├── images<br>
│   ├── index.asp<br>
│   ├── login.asp<br>
│   ├── logout.asp<br>
│   ├── main.asp<br>
│   ├── message.asp<br>
│   ├── payment.asp<br>
│   ├── receive.asp<br>
│   ├── reg.asp<br>
│   ├── return.asp<br>
│   ├── sendpass.asp<br>
│   ├── softlist.asp<br>
│   ├── softpost.asp<br>
│   ├── style.css<br>
│   ├── user_style.css<br>
│   ├── usercard.asp<br>
│   ├── userlist.asp<br>
│   └── usersms.asp<br>
├── GuestBook //访客模块<br>
│   ├── check.js<br>
│   ├── config.asp<br>
│   ├── del.asp<br>
│   ├── edit.asp<br>
│   ├── editreply.asp<br>
│   ├── images<br>
│   ├── index.asp<br>
│   ├── post.asp<br>
│   ├── search.js<br>
│   ├── showreply.asp<br>
│   ├── write.asp<br>
│   └── emot<br>
├── Link //链接模块<br>
│   ├── UploadPic<br>
│   ├── addlink.asp<br>
│   ├── delink.asp<br>
│   ├── editlink.asp<br>
│   ├── index.asp<br>
│   ├── link.asp<br>
│   └── link.gif<br>
├── adfile //忽略<br>
├── flash //音频模块<br>
│   ├── GetCode.asp<br>
│   ├── RemoveCache.Asp<br>
│   ├── UploadFile<br>
│   ├── UploadPic<br>
│   ├── comment.asp<br>
│   ├── config.asp<br>
│   ├── down.asp<br>
│   ├── downfile.asp<br>
│   ├── download.asp<br>
│   ├── hits.asp<br>
│   ├── index.asp<br>
│   ├── list.asp<br>
│   ├── play.html<br>
│   ├── rssfeed.asp<br>
│   ├── search.asp<br>
│   ├── show.asp<br>
│   ├── showbest.asp<br>
│   ├── showhot.asp<br>
│   ├── shownew.asp<br>
│   └── special.asp<br>
├── soft //软件模块<br>
│   ├── GetCode.asp<br>
│   ├── RemoveCache.Asp<br>
│   ├── UploadFile<br>
│   ├── UploadPic<br>
│   ├── comment.asp<br>
│   ├── config.asp<br>
│   ├── download.asp<br>
│   ├── error.asp<br>
│   ├── hits.asp<br>
│   ├── index.asp<br>
│   ├── list.asp<br>
│   ├── previewimg.asp<br>
│   ├── rssfeed.asp<br>
│   ├── search.asp<br>
│   ├── show.asp<br>
│   ├── showbest.asp<br>
│   ├── showhot.asp<br>
│   ├── shownew.asp<br>
│   ├── showtype.asp<br>
│   ├── softdown.asp<br>
│   └── special.asp<br>
├── support //介绍模块<br>
│   ├── about.asp<br>
│   ├── about.ini<br>
│   ├── advertise.asp<br>
│   ├── advertise.ini<br>
│   ├── declare.asp<br>
│   ├── declare.ini<br>
│   ├── help.asp<br>
│   ├── help.ini<br>
│   ├── sitemap.asp<br>
│   └── 2.asp<br>
├── api //api模块<br>
│   ├── api.config<br>
│   ├── api_reponse.asp<br>
│   ├── api_user.xml<br>
│   ├── cls_api.asp<br>
│   └── web.config<br>
├── article //文章模块<br>
│   ├── GetCode.asp<br>
│   ├── RemoveCache.Asp<br>
│   ├── UploadFile<br>
│   ├── UploadPic<br>
│   ├── comment.asp<br>
│   ├── config.asp<br>
│   ├── content.asp<br>
│   ├── hits.asp<br>
│   ├── index.asp<br>
│   ├── list.asp<br>
│   ├── rssfeed.asp<br>
│   ├── search.asp<br>
│   ├── sendmail.asp<br>
│   ├── show.asp<br>
│   ├── showbest.asp<br>
│   ├── showhot.asp<br>
│   ├── shownew.asp<br>
│   └── special.asp<br>
├── editor //编辑器模块<br>
│   ├── FCKeditor<br>
│   └── UBBeditor<br>
├── UploadFile //空文件夹<br>
├── web.config // 配置iis的

可以看出来这个经典的asp程序,就是模块化开发的即视感,比如

http://10.211.55.20:8084/soft/就对应着 soft目录下的文件,然后都是单入口模式。

用的最多就是包含数据库链接、用户验证等文件的手段,用来联系整个程序。

### <a name="header-n49"></a>0x4.2 审计思路

我个人感觉像asp的cms其实代码量不大,而且结构相当简单,所以我比较喜欢一个一个文件的去读。但是为了提高效率我们可以选择结合功能点去阅读。

先从index.asp文件为开端,code as:

```
&lt;!--#include file="conn.asp"--&gt;
&lt;!--#include file="const.asp"--&gt;
&lt;!--#include file="inc/cls_public.asp"--&gt;
&lt;%
Dim HtmlFileName, HtmlTemplate 
HTML.ShowIndex(0)
Set HTML = Nothing
CloseConn
%&gt;
```

文件最开始加载了conn.asp,我们选择跟进看看

```
&lt;%@ LANGUAGE = VBScript CodePage = 936%&gt; '@指令用来进行一些配置  VBSCRIPT 语法 936代表是gb2312编码
&lt;%
Option Explicit
Dim startime,Conn,db,Connstr
Response.Buffer = True
startime = Timer()
'--定义数据库类别，1为SQL数据库，0为Access数据库
Const isSqlDataBase = 0

Dim NowString, NewAsp, MyAppPath
MyAppPath = ""
'-- 是否开启伪静态功能(False=否，True=是)
Const IsURLRewrite = False
'--系统XML版本设置，最低版本 Const MsxmlVersion=""
Const MsxmlVersion = ".3.0"

If IsSqlDataBase = 1 Then
    '-----------------------SQL数据库连接参数---------------------------------------
    NowString = "GetDate()"
    '--SQL数据库连接参数：数据库名(SqlDatabaseName)、用户名(SqlUsername)、用户密码(SqlPassword)
    '--连接名(SqlLocalName)（本地用(local)，外地用IP）
    Const SqlDatabaseName = "newasp"
    Const SqlUsername = "sa"          
    Const SqlPassword = "newasp" 
    Const SqlLocalName = "(local)"
    '-------------------------------------------------------------------------------
Else
    '-----------------------ACCESS数据库连接----------------------------------------
    NowString = "Now()"
    '--ACCESS数据库连接路径；数据库默认在database目录，第一次使用请修改默认数据库名或路径
    '--数据库路径可以使用绝对路径
    db = "database/#newasp.asa"
    '-------------------------------------------------------------------------------
End If

Dim DBPath
'-- 采集数据库连接路径
DBPath = "database/#Collection.asa"

Sub ConnectionDatabase()
    On Error Resume Next
    If IsSqlDataBase = 1 Then
       Connstr = "Provider = Sqloledb; User ID = " &amp; SqlUsername &amp; "; Password = " &amp; SqlPassword &amp; "; Initial Catalog = " &amp; SqlDatabaseName &amp; "; Data Source = " &amp; SqlLocalName &amp; ";"
    Else
       Connstr = "Provider=Microsoft.Jet.OLEDB.4.0;Data Source=" &amp; ChkMapPath(MyAppPath &amp; db)
    End If
    Set Conn = Server.CreateObject("ADODB.Connection")
    Conn.Open Connstr
    If Err Then
       Err.Clear
       Set Conn = Nothing
        Response.Write "数据库连接出错，请打开conn.asp文件检查连接字串。"
       Response.End
    End If
End Sub

Sub CloseConn()
    Set Newasp = Nothing
End Sub
'================================================
' 函数名：ChkMapPath
' 作  用：相对路径转换为绝对路径
' 参  数：strPath ----原路径
' 返回值：绝对路径
'================================================
Function ChkMapPath(ByVal strPath)
    Dim fullPath
    strPath = Replace(Replace(Trim(strPath), "/", "\"), "\\", "\")

    If strPath = "" Then strPath = "."
    If InStr(strPath,":\") = 0 Then
       fullPath = Server.MapPath(strPath)
    Else
       strPath = Replace(strPath,"..\","")
       fullPath = Trim(strPath)
       If Right(fullPath, 1) = "\" Then
           fullPath = Left(fullPath, Len(fullPath) - 1)
       End If
    End If
    ChkMapPath = fullPath
End Function
%&gt;
```

感觉asp的程序注释写的真的是特别直观,conn.asp主要是数据库链接文件,然后返回一个句柄，我使用的是access数据库,所以我们可以记录下获得的信息:

db = “database/#newasp.asa” //数据库路径 asa 我们可以查看下有没有默认的账户和口令和了解下结构

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010495e556431d173a.png)

这些数据库结构对于Access数据库类型的注入来说是绝对必要的,因为access没有元数据表,只能爆破表名。

我们跟进下一个包含的文件const.asp

```
&lt;!--#include file="inc/cls_main.asp"--&gt;  'Class NewaspMain_Cls 类文件 还有其他类的实现
&lt;!--#include file="inc/function.asp"--&gt; ' 一些方法,感觉是一大堆堆起来的,没必要细读,还是根据功能点去找代码实现效率高点。
&lt;%
Set NewAsp = New NewaspMain_Cls '实例化了对象
NewAsp.ReadConfig '调用了ReadConfig方法
ImagePath = Newasp.InstallDir &amp; "images/" 
%&gt;
```

然后我们继续跟进下一个包含文件inc/cls_public.asp (代码写的相当长)



```
&lt;!--#include file="classmenu.asp"--&gt;
&lt;%
Dim HTML
Set HTML = New NewaspPublic_Cls
Class NewaspPublic_Cls
    Public CurrentClass,ThisHtmlPath,FirstCalss,ParentClass
    Private Cmd
    
    Private Sub Class_Initialize()
       On Error Resume Next
       Newasp.LoadTemplates 0, 0, 0
    End Sub
'............................. 省略
Public Function ShowIndex(ByVal isHtml)
       Dim HtmlContent
       Newasp.m_intChannelID = 0
       Newasp.LoadTemplates 0, 1, 0
    HtmlContent = Newasp.HtmlContent '载入模版
    HtmlContent = Replace(HtmlContent, "`{`$ChannelRootDir`}`", Newasp.InstallDir) '替换标签
       HtmlContent = Replace(HtmlContent, "`{`$InstallDir`}`", Newasp.InstallDir)
       If Len(Newasp.HtmlSetting(1)) &lt; 2 Then
           HtmlContent = Replace(HtmlContent, "`{`$PageTitle`}`", "首页")
       Else
           HtmlContent = Replace(HtmlContent, "`{`$PageTitle`}`", Newasp.HtmlSetting(1))
       End If
       HtmlContent = Replace(HtmlContent, "`{`$IndexTitle`}`", "首页")
       HtmlContent = Replace(HtmlContent, "`{`$ChannelID`}`", 0)
       HtmlContent = ReadAnnounceContent(HtmlContent, 0)
       HtmlContent = ReadClassMenu(HtmlContent)
       HtmlContent = ReadClassMenubar(HtmlContent)
       HtmlContent = ReadArticlePic(HtmlContent)
       HtmlContent = ReadSoftPic(HtmlContent)
       HtmlContent = ReadArticleList(HtmlContent)
       HtmlContent = ReadSoftList(HtmlContent)
       HtmlContent = ReadFlashList(HtmlContent)
       HtmlContent = ReadFlashPic(HtmlContent)
       HtmlContent = ReadFriendLink(HtmlContent)
       HtmlContent = ReadNewsPicAndText(HtmlContent)
       HtmlContent = ReadSoftPicAndText(HtmlContent)
       HtmlContent = ReadGuestList(HtmlContent)
       HtmlContent = ReadAnnounceList(HtmlContent)
       HtmlContent = ReadPopularArticle(HtmlContent)
       HtmlContent = ReadPopularSoft(HtmlContent)
       HtmlContent = ReadPopularFlash(HtmlContent)
       HtmlContent = ReadStatistic(HtmlContent)
       HtmlContent = ReadUserRank(HtmlContent)
       HtmlContent = Replace(HtmlContent, "`{`$SkinPath`}`", Newasp.SkinPath)
       HtmlContent = Replace(HtmlContent, "`{`$InstallDir`}`", Newasp.InstallDir)
       If isHtml Then
           ShowIndex = HtmlContent
       Else
           Response.Write HtmlContent
       End If
    End Function

这就是上面最开始 index.asp

&lt;!--#include file="conn.asp"--&gt;
&lt;!--#include file="const.asp"--&gt;
&lt;!--#include file="inc/cls_public.asp"--&gt;
&lt;%
Dim HtmlFileName, HtmlTemplate  
HTML.ShowIndex(0) '这里调用的是 inc/cls_public.asp 类下NewaspPublic_Cls的ShowIndex方法用来渲染首页
Set HTML = Nothing
CloseConn '关闭数据库链接
%&gt;
```

在这个cms我还想提个关键点:

有个很关键的类(Class NewaspMain_Cls),该类的Newasp实例是这个cms的全局核心对象:

我们需要查看它的构造方法,可以看到通过Cookie设置了很多用户属性,(这些先记下来)

```
GetUserip = CheckStr(getIP)
       membername = CheckStr(Request.Cookies(Cookies_Name)("username"))
       memberpass = CheckStr(Request.Cookies(Cookies_Name)("password"))
       menbernickname = CheckStr(Request.Cookies(Cookies_Name)("nickname"))
       membergrade = ChkNumeric(Request.Cookies(Cookies_Name)("UserGrade"))
       membergroup = CheckStr(Request.Cookies(Cookies_Name)("UserGroup"))
       memberclass = ChkNumeric(Request.Cookies(Cookies_Name)("UserClass"))
       memberid = ChkNumeric(Request.Cookies(Cookies_Name)("userid"))
       CheckPassword = CheckStr(Request.Cookies(Cookies_Name)("CheckPassword"))
```

上面演示了如何对单文件不断回溯从而找到相应的处理类和方法,下面我就是通过这种方法,来通读整个cms,鉴于文章篇幅，下面我会从简表述一些挖掘过程。

### <a name="header-n72"></a>0x4.3 SQL注入

关于挖掘asp程序的SQL注入,我们首先通过上文的通读方法，找到关键的过滤函数,如果没有过滤函数，那么就是任意注入啦，如果有过滤函数，我们就有两条路子

1.过滤函数不严谨导致绕过

2.寻找程序猿粗心忘记过滤的可控点

代码有几个过滤函数,分别如下:

C:\Users\xq17\Desktop\wwwroot\inc\cls_main.asp

```
Public Function CheckBadstr(str) ' 246 line
       If IsNull(str) Then
    CheckBadstr = vbNullString 'str为空则转换为vb的空类型
           Exit Function
       End If
  str = Replace(str, Chr(0), vbNullString) '替换截断字符 
  str = Replace(str, Chr(34), vbNullString) '双引号
       str = Replace(str, "%", vbNullString)
       str = Replace(str, "@", vbNullString)
       str = Replace(str, "!", vbNullString)
       str = Replace(str, "^", vbNullString)
       str = Replace(str, "=", vbNullString)
       str = Replace(str, "--", vbNullString)
       str = Replace(str, "$", vbNullString)
  str = Replace(str, "'", vbNullString) '去掉单引号
       str = Replace(str, ";", vbNullString)
       str = Replace(str, "&lt;", vbNullString)
       str = Replace(str, "&gt;", vbNullString)
  CheckBadstr = Trim(str) '删除字符串两侧的空格,然后返回函数值
    End Function
```

access数据库没有反斜杠,其他系统可以考虑下,用了这个函数基本大概率没办法注入了。



```
Public Function ChkNumeric(ByVal CHECK_ID)
  If CHECK_ID &lt;&gt; "" And IsNumeric(CHECK_ID) Then 'IsNumeric 是vbscript的判断,没漏洞
           If CHECK_ID &lt; 0 Then CHECK_ID = 0
      If CHECK_ID &gt; 2147483647 Then CHECK_ID = 0 '防溢出
           CHECK_ID = CLng(CHECK_ID)
       Else
           CHECK_ID = 0
       End If
       ChkNumeric = CHECK_ID
    End Function

Public Function CheckStr(ByVal str)
       If IsNull(str) Then
           CheckStr = ""
           Exit Function
       End If
  str = Replace(str, Chr(0), "")'这个特性能用来绕过关键词
  CheckStr = Replace(str, "'", "''")'这个直接替换单引号为双引号
    End Function

'=============================================================
    '函数名：ChkFormStr
    '作  用：过滤表单字符
    '参  数：str   ----原字符串
    '返回值：过滤后的字符串
    '=============================================================
Public Function ChkFormStr(ByVal str) '这个函数主要防止xss
       Dim fString
       fString = str
       If IsNull(fString) Then
           ChkFormStr = ""
           Exit Function
       End If
       fString = Replace(fString, "'", "&amp;#39;")
       fString = Replace(fString, Chr(34), "&amp;quot;")
       fString = Replace(fString, Chr(13), "")
       fString = Replace(fString, Chr(10), "")
       fString = Replace(fString, Chr(9), "")
       fString = Replace(fString, "&gt;", "&amp;gt;")
       fString = Replace(fString, "&lt;", "&amp;lt;")
       fString = Replace(fString, "&amp;nbsp;", " ")
       ChkFormStr = Trim(JAPEncode(fString))
    End Function
    '=============================================================
    '函数作用：过滤SQL非法字符
    '=============================================================
    Public Function CheckRequest(ByVal str,ByVal strLen)
       On Error Resume Next
       str = Trim(str)
       str = Replace(str, Chr(0), "")
       str = Replace(str, "'", "")
       str = Replace(str, "%", "")
       str = Replace(str, "^", "")
       str = Replace(str, ";", "")
       str = Replace(str, "*", "")
       str = Replace(str, "&lt;", "")
       str = Replace(str, "&gt;", "")
       str = Replace(str, "|", "")
       str = Replace(str, "and", "")
       str = Replace(str, "chr", "")
       str = Replace(str, "@", "")
       str = Replace(str, "$", "")
       
       If Len(str) &gt; 0 And strLen &gt; 0 Then
           str = Left(str, strLen)
       End If
       CheckRequest = str
    End Function
```

总结下: ChkNumeric CheckStr ChkFormStr(xss) CheckRequest CheckBadstr(xsss) 还有很多其他的方,asp程序比较杂,遇到再细跟就行了,都没办法闭合单引号。

所以我们找注入点也是两个思路:

1.找没有单引号包括的可控语句,且没做类型判断

2.没有进行函数消毒的可控参数进入SQL查询

读完了全部文件，发现了作者对这个程序修修补补的痕迹，对一些历史漏洞点进行重复多次过滤，或者补充过滤(asp程序维护成本高)，但是作者一开始的出发习惯还是挺好的,基本都是

SQL = “SELECT TOP 1 * FROM NC_Ca 这样的格式去进行SQL查询,所以作者估计是认真匹配正则然后修补了,所以很遗憾,这个系统我读了2次,还是没找到前台的注入(函数逻辑缝缝补补),又因为是Access数据库,拿到后台注入基本没啥用，除非是那种update的点可能结合getshell来玩下,所以我当时就放弃，欢迎各位师傅继续跟进下这个系统研究一波。

### <a name="header-n91"></a>0x4.2 逻辑漏洞

一个纯粹出于学习而发现的无限刷票漏洞(鸡肋且垃圾的洞)

wwwroot\vote\vote.asp

```
&lt;!--#include file="../conn.asp"--&gt;
&lt;!--#include file="../inc/const.asp"--&gt;
&lt;%
Dim voteid, MyChoose, i, Rs, SQL
If Not IsObject(Conn) Then ConnectionDatabase
voteid = CLng(Request("voteid"))
If Request.Cookies("vote_"&amp;voteid) = "newaspvote_" &amp;voteid Then
    Response.Write("&amp;back=已经参与过投票，谢谢")
    Response.End
Else
    Response.Cookies("vote_"&amp;voteid) = "newaspvote_" &amp;voteid
    Response.Cookies("vote_"&amp;voteid).expires = Date + 3650
    Response.Cookies("vote_"&amp;voteid).domain = Request.ServerVariables("SERVER_NAME")
    MyChoose = Split(Request("myChoose"), ",", -1, 1)
    Set Rs = server.CreateObject("adodb.recordset")
    SQL = "SELECT * FROM NC_Vote WHERE id = " &amp;voteid
    Rs.Open SQL, Conn, 1, 3
    If Not (Rs.BOF And Rs.EOF) Then
       For i = 1 To 5
           If MyChoose(i -1) = "true" Then
              Rs("ChooseNum_"&amp;i&amp;"") = Rs("ChooseNum_"&amp;i&amp;"") + 1
           End If
       Next
       Rs.update
       For i = 1 To 5
           If MyChoose(i -1) = "true" Then
              Conn.Execute ("UPDATE NC_Vote SET VoteNum=VoteNum+1 WHERE id=" &amp;Rs("id"))
           End If
       Next
    End If
    Rs.Close
    Set Rs = Nothing
    Response.Write("&amp;back=投票已经送达，谢谢参与")
End If
CloseConn
%&gt;

Response.Cookies("vote_"&amp;voteid) = "newaspvote_" &amp;voteid 
Response.Cookies("vote_"&amp;voteid).expires = Date + 3650
Response.Cookies("vote_"&amp;voteid).domain = Request.ServerVariables("SERVER_NAME")
'首先投票的成功的话,会设置Cookie的"newaspvote_" &amp;voteid  来代表已经投过票了
If Request.Cookies("vote_"&amp;voteid) = "newaspvote_" &amp;voteid Then
    Response.Write("&amp;back=已经参与过投票，谢谢")
    Response.End
' -- 这个代码是通过cookie匹配来判断的相等则说明已经投过了,但是因为Cookie可控，我们直接burp，去掉这个字段就可以无限刷票了,一般安全的投票是绑定session来限制的。
```



### <a name="header-n97"></a>0x4.3 XSS漏洞

这个系统过滤的挺严格的,但是细心找还是能找到几处有意思的xss。

首先是注册的地方:

user/reg.asp code as

```
ElseIf Newasp.CheckStr(Request("action")) = "reg" Then '34 lines
Call RegNewMember '跟进这个函数
'----------------------------------------
'--- 下面我会一行一行去读然后删掉那些跟可控无关的语句
Sub RegNewMember()
    Dim Rs,SQL
    Dim UserPassWord,strUserName,strGroupName,Password
    Dim rndnum,num1
    Dim Question,Answer,usersex,sex
    On Error Resume Next
  '---------- 这里过滤了input框的所以value,省略
   Set Rs = Newasp.Execute("SELECT username FROM NC_User WHERE username='" &amp; strUserName &amp; "'")
  ' --------- 这里是用户名邮箱唯一性验证，省略
    '-----------------------------------------------------------------
    '系统整合
    '-----------------------------------------------------------------
    Dim API_Newasp,API_SaveCookie,SysKey
    If API_Enable Then
    '---------------------无关代码省略
    '---------------这里是重点---------
    Rs.Close:Set Rs = Nothing
    Set Rs = Server.CreateObject("ADODB.Recordset")
  SQL = "select * from NC_User where (userid is null)'这里打开了NC_User表
    Rs.Open SQL,Conn,1,3
    '------- 下面进行了修改表的操作
    Rs.Addnew
    Rs("username") = strUserName '过滤了
       Rs("password") = Password
    Rs("nickname") = Newasp.CheckBadstr(Request.Form("nickname")) '过滤了
       Rs("UserGrade") = 1
    Rs("UserGroup") = strGroupName '不可控
       Rs("UserClass") = 0
       If CInt(Newasp.AdminCheckReg) = 1 Then
           Rs("UserLock") = 1
       Else
           Rs("UserLock") = 0
       End If
       Rs("UserFace") = "face/1.gif"
       Rs("userpoint") = CLng(Newasp.AddUserPoint)
       Rs("usermoney") = 0
       Rs("savemoney") = 0
       Rs("prepaid") = 0
       Rs("experience") = 10
       Rs("charm") = 10
    Rs("TrueName") = Newasp.CheckBadstr(Request.Form("username")) '过滤了
    Rs("usersex") = usersex '不可控
    Rs("usermail") = Newasp.CheckStr(Request.Form("usermail"))'过滤了
       Rs("oicq") = ""
    Rs("question") = Question '过滤了
       Rs("answer") = md5(Answer)
       Rs("JoinTime") = Now()
       Rs("ExpireTime") = Now()
       Rs("LastTime") = Now()
       Rs("Protect") = 0
       Rs("usermsg") = 0
    Rs("userlastip") = Newasp.GetUserIP ' 这是漏洞点跟进这里
       If CInt(Newasp.AdminCheckReg) = 0 And CInt(Newasp.MailInformPass) = 0 Then
           Rs("userlogin") = 1
       Else
           Rs("userlogin") = 0
       End If
       Rs("UserToday") = "0,0,0,0,0,0,0,0,0,0,0"
       Rs("usersetting") = ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
       Rs("ip") = Newasp.GetUserIP
       Rs("Badness") = 0
       Rs("isask") = 0
       Rs.update
       Rs.Close
    '--------------------下面代码省略--------------------
```

里面有个关键代码:



```
Rs("userlastip") = Newasp.GetUserIP选择跟进这个属性

Path:C:\Users\xq17\Desktop\wwwroot\inc\cls_main.asp

GetUserip = CheckStr(getIP) '跟进CheckStr函数
    Private Function getIP() 
       Dim strIPAddr 
       If Request.ServerVariables("HTTP_X_FORWARDED_FOR") = "" Or InStr(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), "unknown") &gt; 0 Then 
           strIPAddr = Request.ServerVariables("REMOTE_ADDR") 
       ElseIf InStr(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), ",") &gt; 0 Then 
           strIPAddr = Mid(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), 1, InStr(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), ",")-1)
           Actforip = Request.ServerVariables("REMOTE_ADDR")
       ElseIf InStr(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), ";") &gt; 0 Then 
           strIPAddr = Mid(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), 1, InStr(Request.ServerVariables("HTTP_X_FORWARDED_FOR"), ";")-1)
           Actforip = Request.ServerVariables("REMOTE_ADDR")
       Else 
        strIPAddr = Request.ServerVariables("HTTP_X_FORWARDED_FOR")'这里可以控制
           Actforip = Request.ServerVariables("REMOTE_ADDR")
       End If 
    getIP = Replace(Trim(Mid(strIPAddr, 1, 30)), "'", "") '这里没有过滤双引号
    End Function

getIP = Replace(Trim(Mid(strIPAddr, 1, 30)), "'", "")
```

可以看到这里只是限制了长度为30(完全可以写xss啦),但是没有过滤双引号,这样子就很容易出事情啦,在后台目录下搜索

userlastip这个key寻找输出点。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010e9d4404715c6359.png)

果断跟进去看看有没有啥过滤的。

```
Sub EditUser()
    Call PageTop
    Dim userid,username
    userid = Newasp.ChkNumeric(Request("userid"))
    username = Replace(Request("username"), "'", "")
    If userid = 0 Then
       SQL = "SELECT * FROM NC_user WHERE username='" &amp; username &amp; "'"
    Else
       SQL = "SELECT * FROM NC_user WHERE userid=" &amp; userid
    End If
  Set Rs = Newasp.Execute(SQL) '这里直接获取到了sql查询后的对象
    If Rs.BOF And Rs.EOF Then
       FoundErr = True
       ErrMsg = ErrMsg + "&lt;li&gt;Sorry！没有找到任何会员。或者您选择了错误的系统参数!&lt;/li&gt;"
       Exit Sub
    End If
  '然后后面直接就是插入了HTMl的input的value,可以看到是双引号的,至此完成xss
  &lt;td class="tablerow1"&gt;&lt;input size="30" name="userlastip" value="     &lt;%=Rs("userlastip")%&gt;" type="text" /&gt;&lt;/td&gt;
```

过程演示下:

[![](https://p0.ssl.qhimg.com/t018488dbeb9c668974.png)](https://p0.ssl.qhimg.com/t018488dbeb9c668974.png)

[![](https://p1.ssl.qhimg.com/t011f3b566ba5d0aa0f.png)](https://p1.ssl.qhimg.com/t011f3b566ba5d0aa0f.png)

这里可以利用组合拳结合社工来getshell,还有这个系统的cookie里面包含了md5的密码和用户名,代码很简单,自己去读下就知道了。

### <a name="header-n116"></a>0x4.4 上传点分析

首先程序的上传点也是分为前台用户和后台用户处的,这里可以进行分析下是否可以进行绕过上传

user 目录下存在
1. C:\Users\xq17\Desktop\wwwroot\user\Upfile.asp
1. C:\Users\xq17\Desktop\wwwroot\user\Upload.asp
这两个上传点,下面分析下程序是如何限制和过滤后缀的，然后探讨下绕过的可能性

Upload.asp code as

```
&lt;!--#include file="setup.asp"--&gt; '不存在
&lt;!--#include file="check.asp"--&gt; ' 跟进这个可以发现,没办法绕过权限判断
&lt;!--#include file="../inc/UploadCls.Asp"--&gt;
&lt;%
'=====================================================================
' 软件名称：新云网站管理系统
' 当前版本：Newasp Site Management System Version 3.0
' 文件名称：upload.asp
' 更新日期：2007-4-2
' 官方网站：新云网络(www.newasp.net www.newasp.cn) QQ：94022511
'=====================================================================
' Copyright 2004-2007 newasp.net - All Rights Reserved.
' newasp is a trademark of newasp.net
'=====================================================================
Server.ScriptTimeOut = 18000
Dim UploadObject,AllowFileSize,AllowFileExt
Dim sUploadDir,SaveFileName,PathFileName,url
Dim sAction,sType,SaveFilePath,UploadPath,m_strInstance,m_intMaxsize
Dim m_strFiletype,m_strType,m_strFileExt,m_strRootPath,m_intshow,m_intRename
Dim ChannelSetting,m_intThumbnail,m_intAutoRename,m_strUploadFileDir,m_strUploadPicDir
'Dim m_intBindDomain,m_strNamedPath
'm_intBindDomain = CInt(Newasp.BindDomain)
'm_strNamedPath = Newasp.NamedPath
'-----   ..............................  减少篇幅，省略了大部分代码
%&gt;
```

跟进这个check.asp

```
&lt;%
Dim GroupSetting,Cookies_Name,UserLastIP
Dim rsmember,sqlmember,MemberName,MemberEmail,memberid
MemberName = Newasp.CheckBadstr(Newasp.memberName) '可控
memberid = Newasp.ChkNumeric(Newasp.memberid) '可控
UserLastIP = Newasp.CheckStr(Request.Cookies(Newasp.Cookies_Name)("userlastip")) '可控

If Trim(MemberName) = "" Or memberid = 0 Then
    Response.Redirect ("./login.asp")
End If
MemberName = Left(MemberName,45) '限制名字长度
If Trim(Request.Cookies(Newasp.Cookies_Name)) = "" Then
    Response.Redirect ("./login.asp")
End If
GroupSetting = Split(Newasp.UserGroupSetting(CInt(Newasp.membergrade)), "|||")'可控
Call GetUserTodayInfo
Cookies_Name = "usercookies_" &amp; Newasp.memberid '可控

If Trim(Request.Cookies(Cookies_Name)) = "" Then '跳过
    Response.Cookies(Cookies_Name)("userip") = Newasp.GetUserIP
    Response.Cookies(Cookies_Name)("dayarticlenum") = 0
    Response.Cookies(Cookies_Name)("daysoftnum") = 0
    Response.Cookies(Cookies_Name).Expires = Date + 1
End If

sqlmember = "SELECT userid,UserLock,usermail,userlastip FROM NC_User WHERE username='" &amp; MemberName &amp; "' And UserGrade="&amp; CInt(Newasp.membergrade) &amp;" And userid=" &amp; CLng(memberid)
Set rsmember = Newasp.Execute(sqlmember)
If rsmember.BOF And rsmember.EOF Then '代表是空数据集
    Response.Cookies(Newasp.Cookies_Name) = ""
    Set rsmember = Nothing
  Response.Redirect "login.asp" '跳过这里
    Response.End
Else
    If rsmember("UserLock") &gt; 0 Then
       Response.Cookies(Newasp.Cookies_Name) = ""
       Set rsmember = Nothing
       ErrMsg = "&lt;li&gt;你的用户名已被锁定,你不能登陆！如要开通此帐号，请联系管理员。&lt;/li&gt;"
       Call Returnerr(ErrMsg)
       Response.End
    End If
    If Newasp.ChkNumeric(GroupSetting(41)) = 2 Then
       If rsmember("userlastip") &lt;&gt; UserLastIP Or UserLastIP &lt;&gt; Newasp.GetUserIP Then
           Response.Cookies(Newasp.Cookies_Name) = ""
           Set rsmember = Nothing
           ErrMsg = "&lt;li&gt;你已经在其他地方登录，本系统不允许两个人使用同一个帐号登录。&lt;/li&gt;"
           Call Returnerr(ErrMsg)
           Response.End
       End If
    End If
    MemberEmail = Trim(rsmember("usermail"))
End If
Set rsmember = Nothing

If CInt(Newasp.memberclass) &gt; 0 Then '可控
    Dim rsUserClass,SQLUserClass
    Set rsUserClass = Server.CreateObject("ADODB.Recordset")
    SQLUserClass = "SELECT userid,UserClass,UserLock,ExpireTime FROM NC_User WHERE username='" &amp; MemberName &amp; "' And userid=" &amp; CLng(Newasp.memberid)
    rsUserClass.Open SQLUserClass,Conn,1,3
    If rsUserClass.BOF And rsUserClass.EOF Then
       Response.Cookies(Newasp.Cookies_Name) = ""
       rsUserClass.Close:Set rsUserClass = Nothing
       Response.Redirect "login.asp"
    Else
       If rsUserClass("UserLock") &gt; 0 Then
           Response.Cookies(Newasp.Cookies_Name) = ""
           rsUserClass.Close:Set rsUserClass = Nothing
           Response.Redirect "login.asp"
       End If
       If DateDiff("D", CDate(rsUserClass("ExpireTime")), Now()) &gt; 0 And rsUserClass("UserClass") &lt;&gt; 999 Then
           rsUserClass("UserClass") = 999
           rsUserClass.Update
       End If
    End If
    rsUserClass.Close:Set rsUserClass = Nothing
End If
%&gt;
```

这些基本都可以控制,也就是说我们可以绕过验证模块进行上传,我们继续跟进看下上传的流程

这里我整理下对应文件的逻辑:

入口: Upload.asp 一层包含:inc/UploadCls.Asp 二层包含:Upload.inc

Upload.inc :

class: UpFileClass FileInfoClass

UploadCls.Asp:

class: UpFileCls FileInfoCls

强烈推荐看UploadCls.Asp文件内的注释,能帮助我们快速理解变量含义

然后我们重新去读 Upload.asp

```
Server.ScriptTimeOut = 18000
Dim UploadObject,AllowFileSize,AllowFileExt
Dim sUploadDir,SaveFileName,PathFileName,url
Dim sAction,sType,SaveFilePath,UploadPath
Dim m_strFileExt,m_strRootPath,m_strInstance
UploadObject = CInt(Newasp.UploadClass)   '上传文件对象 --- 0=无组件上传,1=Aspupload3.0组件,2=SA-FileUp 4.0组件 默认是0无组件上传

AllowFileSize = CLng(Newasp.UploadFileSize * 1024 )
AllowFileExt = Newasp.UploadFileType '后台可以修改，存储在数据库的类型
'---- exe|rar|zip|gif|jpg|png|bmp|swf|mid|rm| 默认
AllowFileExt = Replace(Replace(Replace(UCase(AllowFileExt), "ASP", ""), "ASPX", ""), "|", ",") '这里可以进行绕过 AASPSP 这样就可以绕过
url = Split(Request.ServerVariables("SERVER_PROTOCOL"), "/")(0) &amp; "://" &amp; Request.ServerVariables("HTTP_HOST")
'--- url = HTTP://10.211.55.20:8084
sType = UCase(Request.QueryString("sType")) '可控
If Newasp.CheckPost=False Then '限制为post方法
    Call Returnerr(Postmsg)
    Response.End
End If

Dim ChannelSetting,m_strUploadPicDir

If Len(Newasp.Channel_Setting &amp;"") &lt; 30 Then Newasp.Channel_Setting = "0|||1|||2|||3|||4|||0|||1|||UploadPic/|||UploadFile/|||"
ChannelSetting = Split(Newasp.Channel_Setting &amp; "|||||||||||||||", "|||")
m_strUploadPicDir = Replace(Trim(ChannelSetting(7)), "\", "/") ' :UploadPic
If Len(m_strUploadPicDir) &lt; 2 Then m_strUploadPicDir = "UploadPic/"
If Right(m_strUploadPicDir,1) &lt;&gt; "/" Then m_strUploadPicDir = m_strUploadPicDir &amp; "/"

m_strInstance = "content"
  m_strRootPath = Newasp.InstallDir ' /

  Select Case ChannelID ' 可控，这里为1
    Case 0
       If stype = "AD" Then
           UploadPath = "adfile/UploadPic/"
           sUploadDir = Newasp.InstallDir &amp; UploadPath
       ElseIf stype = "LINK" Then
           UploadPath = "link/UploadPic/"
           sUploadDir = Newasp.InstallDir &amp; UploadPath
       Else
           UploadPath = "UploadFile/"
           sUploadDir = Newasp.InstallDir &amp; UploadPath
       End If
    Case Else
       UploadPath = m_strUploadPicDir
       sUploadDir = Newasp.InstallDir &amp; Newasp.ChannelDir &amp; UploadPath
       m_strRootPath = Newasp.InstallDir &amp; Newasp.ChannelDir
End Select

  sAction = UCase(Trim(Request.QueryString("action"))) 'sava
If sAction = "SAVE" Then
    If CInt(Newasp.StopUpload) = 1 Then
       Response.Write ("&lt;script&gt;alert('对不起!本频道未开放上传功能!');history.go(-1)&lt;/script&gt;")
       Response.End
    End If
    If CInt(GroupSetting(20)) &lt;&gt; 1 Then
       Response.Write ("&lt;script&gt;alert('对不起!您没有上传文件的权限');history.go(-1)&lt;/script&gt;")
       Response.End
    End If
    If CLng(UserToday(1)) =&gt; CLng(GroupSetting(21)) Then
       Response.Write ("&lt;script&gt;alert('对不起!您每天只能上传" &amp; GroupSetting(21) &amp; "个文件。');history.go(-1)&lt;/script&gt;")
       Response.End
    End If
    Select Case UploadObject
       Case 0,1,2,3
       Call UploadFile  '跟进这个函数 在下面就可以看到了
       Case 999
           Response.Write ("&lt;script&gt;alert('本系统未开放上传功能!');history.go(-1)&lt;/script&gt;")
           Response.End
       Case Else
           Response.Write ("&lt;script&gt;alert('本系统未开放上传功能!');history.go(-1)&lt;/script&gt;")
           Response.End
    End Select
    Dim strUserToday
    strUserToday = UserToday(0) &amp;","&amp; UserToday(1)+1 &amp;","&amp; UserToday(2) &amp;","&amp; UserToday(3) &amp;","&amp; UserToday(4) &amp;","&amp; UserToday(5)
    UpdateUserToday(strUserToday)
    SaveFilePath = UploadPath &amp; SaveFilePath
    Call OutScript(SaveFilePath)
Else
    Call UploadMain
End If
Sub UploadFile()
    Dim Upload,FilePath,sFilePath,FormName,File,F_FileName
    Dim PreviewSetting,DrawInfo,Previewpath,strPreviewPath
    Dim PreviewName,F_Viewname,MakePreview
    '-- 是否生成缩略图片
    MakePreview = False
    Previewpath = Newasp.InstallDir &amp; Newasp.ChannelDir
    strPreviewPath = m_strUploadPicDir &amp; CreatePath(Previewpath &amp; m_strUploadPicDir)
    PreviewPath = Previewpath &amp; strPreviewpath
    PreviewSetting = Split(Newasp.PreviewSetting, ",")
    If CInt(PreviewSetting(2)) = 1 Then
       DrawInfo = PreviewSetting(5)
    ElseIf CInt(PreviewSetting(2)) = 2 Then
       DrawInfo = Newasp.InstallDir &amp; PreviewSetting(10)
    Else
       DrawInfo = ""
    End If
    If DrawInfo = "0" Then
       DrawInfo = ""
       PreviewSetting(2) = 0
    End If
    sFilePath = CreatePath(sUploadDir) '按日期生成目录
    FilePath = sUploadDir &amp; sFilePath
'-------- FilePath =  /article/UploadPic/2019-8/
'下面开始调用UploadCls.Asp的类了,简单读一下
    Set Upload = New UpFile_Cls
Upload.UploadType = UploadObject              '设置上传组件类型 0
    Upload.UploadPath = FilePath              '设置上传路径
    Upload.MaxSize    = AllowFileSize                 '单位 KB
    Upload.InceptMaxFile = 10                 '每次上传文件个数上限
    Upload.InceptFileType    = AllowFileExt              '设置上传文件限制
    Upload.ChkSessionName    = "uploadPic"
    '预览图片设置
    Upload.MakePreview       = MakePreview
    Upload.PreviewType       = CInt(PreviewSetting(0))       '设置预览图片组件类型
    Upload.PreviewImageWidth = CInt(PreviewSetting(3))       '设置预览图片宽度
    Upload.PreviewImageHeight   = CInt(PreviewSetting(4))       '设置预览图片高度
    Upload.DrawImageWidth       = CInt(PreviewSetting(13))      '设置水印图片或文字区域宽度
    Upload.DrawImageHeight      = CInt(PreviewSetting(14))      '设置水印图片或文字区域高度
    Upload.DrawGraph     = CCur(PreviewSetting(11))      '设置水印透明度
    Upload.DrawFontColor     = PreviewSetting(7)         '设置水印文字颜色
    Upload.DrawFontFamily       = PreviewSetting(8)         '设置水印文字字体格式
    Upload.DrawFontSize      = CInt(PreviewSetting(6))       '设置水印文字字体大小
    Upload.DrawFontBold      = CInt(PreviewSetting(9))       '设置水印文字是否粗体
    Upload.DrawInfo          = DrawInfo           '设置水印文字信息或图片信息
    Upload.DrawType          = CInt(PreviewSetting(2))       '0=不加载水印 ，1=加载水印文字，2=加载水印图片
    Upload.DrawXYType    = CInt(PreviewSetting(15))     '"0" =左上，"1"=左下,"2"=居中,"3"=右上,"4"=右下
    Upload.DrawSizeType      = CInt(PreviewSetting(1))       '"0"=固定缩小，"1"=等比例缩小
    If PreviewSetting(12)&lt;&gt;"" Or PreviewSetting(12)&lt;&gt;"0" Then
       Upload.TransitionColor   = PreviewSetting(12)        '透明度颜色设置
    End If
    '执行上传
'--------- 调用了SaveUpFile方法 我们跟进看看
    Upload.SaveUpFile
    If Upload.ErrCodes&lt;&gt;0 Then
'----------这个点就是报错什么类型不对啥的点 --------
       Response.write ("&lt;script&gt;alert('错误："&amp; Upload.Description &amp; "');history.go(-1)&lt;/script&gt;")
       Exit Sub
    End If
'至少一个
    If Upload.Count &gt; 0 Then
       For Each FormName In Upload.UploadFiles
           Set File          = Upload.UploadFiles(FormName)
           SaveFilePath      = sFilePath &amp; File.FileName
           F_FileName        = FilePath &amp; File.FileName
           m_strFileExt      = File.FileExt
           '创建预览及水印图片
           If Upload.PreviewType&lt;&gt;999 and File.FileType=1 then
              PreviewName = "p" &amp; Replace(File.FileName,File.FileExt,"") &amp; "jpg"
              F_Viewname = Previewpath &amp; PreviewName
              '创建预览图片:Call CreateView(原始文件的路径,预览文件名及路径,原文件后缀)
              Upload.CreateView F_FileName,F_Viewname,File.FileExt
              If CBool(MakePreview) Then
                  Call OutPreview(strPreviewPath &amp; PreviewName)
              End If
           End If
           Set File = Nothing
       Next
    Else
       Call OutAlertScript("请选择一个有效的上传文件。")
       Exit Sub
    End If
    Set Upload = Nothing
End Sub

Sub UploadMain()
    Dim PostRanNum
    Randomize
    PostRanNum = Int(900*rnd)+1000
    Session("uploadPic") = Cstr(PostRanNum)
%&gt;
```

读完可以确定Upload.SaveUpFile这个是重点方法,我们选择跟进看看



```
Public Sub SaveUpFile()
       On Error Resume Next
       Select Case (Upload_Type) 
           Case 0
              ObjName = "无组件"
              Set UploadObj = New UpFile_Class
              If Err.Number&lt;&gt;0 Then
                  ErrCodes = 1
              Else
           SaveFile_0 '跟进这个
              End If
           Case 1
    '..................................省略无关代码
       
    End Sub

Private Sub SaveFile_0()
       Dim FormName,Item,File
       Dim FileExt,FileName,FileType,FileToBinary
       UploadObj.InceptFileType = InceptFile
       UploadObj.MaxSize = FileMaxSize
       UploadObj.GetDate () '取得上传数据
       FileToBinary = Null
  '-------- 这里是设置ErrCodes的关键代码,后面会进行判断必须要为0，初始值为0
  ' 在这里是对应的ErrorCodes对应的错误信息
  'Public Property Get Description
    '   Select Case ErrCodes
    '      Case 1 : Description = "不支持 " &amp; ObjName &amp; " 上传，服务器可能未安装该组件。"
    '      Case 2 : Description = "暂未选择上传组件！"
    '      Case 3 : Description = "请先选择你要上传的文件!"
    '      Case 4 : Description = "文件大小超过了限制 " &amp; (FileMaxSize\1024) &amp; "KB!"
    '   Case 5 : Description = "文件类型不正确!"
    '      Case 6 : Description = "已达到上传数的上限！"
    '      Case 7 : Description = "请不要重复提交！"
    '      Case Else
    End Property
       If Not IsEmpty(SessionName) Then ' SessionName = uploadPic
           If Session(SessionName) &lt;&gt; UploadObj.Form(SessionName) or Session(SessionName) = Empty Then
              ErrCodes = 7
              Exit Sub
           End If
       End If
       
       IsRename = ChkBoolean(UploadObj.Form("Rename"))
       If IsMakePreview Then
           m_blnNoThumbnail = ChkBoolean(UploadObj.Form("NoThumbnail"))
           If m_blnNoThumbnail Then
              IsMakePreview = False
           Else
              IsMakePreview = True
           End If
       End If
       
       If UploadObj.Err &gt; 0 then
           Select Case UploadObj.Err
              Case 1 : ErrCodes = 3
              Case 2 : ErrCodes = 4
              Case 3 : ErrCodes = 5
           End Select
           Exit Sub
       Else
           For Each FormName In UploadObj.File    ''列出所有上传了的文件
              If Count&gt;MaxFile Then
                  ErrCodes = 6
                  Exit Sub
              End If
              
              Set File = UploadObj.File(FormName)
              FileExt = FixName(File.FileExt) '后缀replace
              If CheckFileExt(FileExt) = False then '后缀判断
                  ErrCodes = 5
                  EXIT SUB
              End If
              If Not IsRename Then
                  FileName = FormatName(FileExt)
              Else
                  FileName = File.FileName
              End If
              FileType = CheckFiletype(FileExt) '0
              If IsBinary Then
                  FileToBinary = File.FileData
              End If
              If File.FileSize&gt;0 Then
                  File.SaveToFile Server.Mappath(FilePath &amp; FileName) '然后这里进行了保存，跟进这个
                  AddData FormName , _ 
                         FileName , _
                         FilePath , _
                         File.FileSize , _
                         File.FileType , _
                         FileType , _
                         FileToBinary , _
                         FileExt , _
                         File.FileWidth , _
                         File.FileHeight
                  Count = Count + 1
                  CountSize = CountSize + File.FileSize
                  FileMaxSize = CCur(CountSize)
              End If
              Set File=Nothing
           Next
           For Each Item in UploadObj.Form
              If UploadForms.Exists (Item) Then _
                  UploadForms(Item) = UploadForms(Item) &amp; ", " &amp; UploadObj.Form(Item) _
              Else _
              UploadForms.Add Item , UploadObj.Form(Item)
           Next
           If Not IsEmpty(SessionName) Then Session(SessionName) = Empty
       End If
    End Sub
```

这里有三个关键的check方法(都是根据ext来搞的)



```
Private Function FixName(Byval UpFileExt)
       If IsEmpty(UpFileExt) Then Exit Function
       FixName = Lcase(UpFileExt)
       FixName = Replace(FixName,Chr(0),"") '这里干掉了字符
       FixName = Replace(FixName,".","")
       FixName = Replace(FixName,"'","")
       FixName = Replace(FixName,"asp","")
       FixName = Replace(FixName,"asa","")
       FixName = Replace(FixName,"aspx","")
       FixName = Replace(FixName,"cer","") '这里可以进行一下绕过ccerer
       FixName = Replace(FixName,"cdx","")
       FixName = Replace(FixName,"htr","")
    End Function

Private Function CheckFileExt(FileExt)
       Dim Forumupload,i
       CheckFileExt=False
       If FileExt="" or IsEmpty(FileExt) Then
           CheckFileExt = False
           Exit Function
       End If
       If FileExt="asp" or FileExt="asa" or FileExt="aspx" Then '这里直接白名写死了
           CheckFileExt = False
           Exit Function
       End If
       Forumupload = Split(InceptFile,",")
       For i = 0 To ubound(Forumupload)
           If FileExt = Trim(Forumupload(i)) Then
              CheckFileExt = True
              Exit Function
           Else
              CheckFileExt = False
           End If
       Next
    End Function
    Private Function CheckFiletype(Byval FileExt) '返回类型
       FileExt = Lcase(Replace(FileExt,".",""))
       Select Case FileExt
              Case "gif", "jpg", "jpeg","png","bmp","tif","iff"
                  CheckFiletype=1
              Case "swf", "swi"
                  CheckFiletype=2
              Case "mid", "wav", "mp3","rmi","cda"
                  CheckFiletype=3
              Case "avi", "mpg", "mpeg","ra","ram","wov","asf"
                  CheckFiletype=4
              Case Else
                  CheckFiletype=0
       End Select
    End Function

              FileExt = FixName(File.FileExt) '后缀replace
              If CheckFileExt(FileExt) = False then '后缀判断
                  ErrCodes = 5
                  EXIT SUB
              End If
' -------------- FixName(替换为空) +  CheckFileExt(后台可设置任意类型) =&gt; 导致绕过限制cer

File.SaveAs Server.Mappath(FilePath &amp; FileName)
AddData File.Name , _  ' 换行符 类似python的 \
              FileName , _
              FilePath , _
              File.Size , _
              File.ContentType , _
              FileType , _
              FileToBinary , _
              FileExt , _
              File.ImageWidth , _
              File.ImageHeight

    Private Sub AddData( Form_Name,File_Name,File_Path,File_Size,File_ContentType,File_Type,File_Data,File_Ext,File_Width,File_Height )
       Set FileInfo = New FileInfo_Cls
           FileInfo.FormName = Form_Name
           FileInfo.FileName = File_Name
           FileInfo.FilePath = File_Path
           FileInfo.FileSize = File_Size
           FileInfo.FileType = File_Type
           FileInfo.FileContentType = File_ContentType
           FileInfo.FileExt = File_Ext
           FileInfo.FileData = File_Data
           FileInfo.FileHeight = File_Height
           FileInfo.FileWidth = File_Width
           UploadFiles.Add Form_Name , FileInfo
       Set FileInfo = Nothing
    End Sub
```

AddData这个方法是设置那个对象的一些属性。

我们跟进这个最后保存的方法看看:

```
Set UploadObj = New UpFile_Class
Set File = UploadObj.File(FormName) '生成File对象的过程
Server.CreateObject ("Scripting.Dictionary") 'ActiveX对象实例
```

所以最后调用的就是:

```
Public Sub SaveToFile (Byval Path)
       Dim Ext,oFileStream
       Ext = LCase(Mid(Path, InStrRev(Path, ".") + 1)) '取后缀
       If Ext &lt;&gt; FileExt Then Exit Sub '这里的话进行了二次验证
       If Trim(Path)="" or FileStart=0 or FileName="" or Right(Path,1)="/" Then Exit Sub
       ' 上面就是一些常规判断
       If InStr(1, Path, ".asp", 1) &gt; 0 Then Exit Sub
       '从第一个字符开始搜索 采取文本比较.asp在path的位置 vbscript都是从1开始的要区别开来
       'On Error Resume Next
       Set oFileStream = CreateObject ("Adodb.Stream")'刘属性
       oFileStream.Type = 1
       oFileStream.Mode = 3
       oFileStream.Open
       oUpFileStream.Position = FileStart
       oUpFileStream.CopyTo oFileStream,FileSize
       oFileStream.SaveToFile Path,2 '读取流开始(长度)存到指定路径
       oFileStream.Close
       Set oFileStream = Nothing 
    End Sub
```

上面就是上传文件的步骤,下面看看怎么返回上传的路径:

```
Call OutScript(SaveFilePath)
```

同样是这个文件的后面一些输出方法和一些没啥关系的输出(这个大概看看就可以知道路径是怎么返回的):

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0148584d28ce204a88.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0185303dce2dc01296.png)

可以发现和上面是对应的。

### <a name="header-n159"></a>0x4.5 后台getshell

#### <a name="header-n160"></a>0x 4.5.1 备份数据库getshell

这个应该可以说是很经典的漏洞了,操作相当简单,但是我们可以从代码层面进行解读一下。
1. 上传图片马，获取到路径
1. 把图片马通过备份功能修改为asp后缀
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ddd5dd2677c956cd.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01591963ea0faa1994.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0124d39f8b6969f2cb.png)

根据抓包得到url /admin/admin_database.asp?action=BackupData&amp;act=Backup,单入口我们直接跟进这个文件就行了。



```
Dim bkfolder, bkdbname, fso, fso1
Dim Action
Action = LCase(Request("action"))

Select Case Action
    Case "renamedata" '数据库更名
       If Not ChkAdmin("RenameData") Then
           Server.Transfer("showerr.asp")
           Request.End
       End If
       Call RenameData()
Case "backupdata" '备份数据 进入这里
If Not ChkAdmin("BackupData") Then '验证权限
           Server.Transfer("showerr.asp")
           Request.End
       End If
       If request("act") = "Backup" Then
       If IsSqlDataBase = 1 Then
              Call BackupSqlDatabase()
       Else
       Call BackupDatabase()'调用过程
       End If
' -------- 过程代码如下

Sub BackupDatabase()
  Dbpath = request.Form("Dbpath") '获取可控的数据文件路径
    If InStr(Dbpath, ":") = 0 Then
       Dbpath = Server.MapPath(Dbpath)
    Else
    Dbpath = Dbpath 
    End If
    bkfolder = request.Form("bkfolder")
    bkdbname = request.Form("bkdbname")
  Set Fso = server.CreateObject("scripting.filesystemobject") '创建Fso对象
  If fso.FileExists(dbpath) Then '判断dbpath路径是否存在
    If CheckDir(bkfolder) = True Then 'CheckDir是判断是否存在目录
      fso.CopyFile dbpath, bkfolder&amp; "\"&amp; bkdbname '这里直接把dbpath文件copy到了控制的bkdbname
       Else
           MakeNewsDir bkfolder
           fso.CopyFile dbpath, bkfolder&amp; "\"&amp; bkdbname
       End If
       Succeed("备份数据库成功，您备份的数据库路径为" &amp;bkfolder&amp; "\"&amp; bkdbname)
    Else
       FoundErr = True
       ErrMsg = "找不到您所需要备份的文件。"
       Exit Sub
    End If
End Sub
```

所以成因非常简单,一般防御这种，可以直接把数据库路径写死，但是也不安全，特别是asa这种后缀数据库，所以最好用白名单去限制备份的后缀。

#### <a name="header-n174"></a>0x4.5.2 上传getshell的突破

经过上面分析，核心上传代码还是那两个包含文件，所以前台和后台上传文件虽然不一样，但是过滤是一样的，那么能不能突破这个上传呢，我这里简单说下,代码非常暴力的多次遇到asp就exit了,所以说没有办法,但是有时候可以利用解析漏洞等做点事情。

#### <a name="header-n176"></a>0x4.5.3 插入配置文件shell

上面其实我都是列举了经典的asp程序getshell思路,这个系统把配置文件都是存入了数据库,所以没有办法进行getshell,一般只要不过滤单引号，然后把网站设置这些写入了类似config.asp等文件的就可以getshell,下次可以分析一波这种系统的漏洞,如何闭合写asp一句话也是一种技巧。



## 0x5 关于这个系统的碎碎念

很遗憾没有挖掘到比较好的漏洞,但是我觉得有时候展示自己失败的和第一次尝试的过程，对新手会更有启发，代码审计其实更多是体力活，需要耐心和重复审计，后面如果有机会等进一步提高了asp代码审计的能力，我会再回溯这个系统。



## 0x6 感想(Thought)

第一次接触新语言的的代码审计，我个人还是推崇自己先静态读一次，这样能快速增加自己对新语言的熟悉感，所以这个cms我基本是逐行地去读，虽然说速度挺慢的，但是能让我更好地去理解开发者的心思，也更容易发现脆弱点。因为已经熟悉了asp程序的结构，后面挖掘其他cms的话，为了提高效率，会进行动态审计。由于最近在进修一些关于红队的知识，也没有HW等一些实战机会了，估计比较难遇到一些有趣的asp程序了，不过我接下来这几天可以记录下自己第一次做红队时从信息收集-&gt;撕开小口子-&gt;自闭-&gt;钓鱼攻击-&gt;免杀及其邮件伪造的文章跟各位师傅探讨下。



## 0x6 参考链接(Refer Link)

[Web.config设置system.webServer](https://www.cnblogs.com/xcsn/p/6939628.html)

[ASP入门（十六）-ASP开发的规范](https://www.cnblogs.com/pchmonster/p/4739147.html)
