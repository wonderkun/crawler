> 原文链接: https://www.anquanke.com//post/id/233661 


# Internet Explorer漏洞分析（三）——VBScript Scripting Engine初探


                                阅读量   
                                **228667**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0164c8628e29316500.jpg)](https://p2.ssl.qhimg.com/t0164c8628e29316500.jpg)

```
1.本文一共1514个字 28张图 预计阅读时间10分钟
2.本文作者erfze 属于Gcow安全团队复眼小组 未经过许可禁止转载
3.本篇文章是文章Internet Explorer漏洞分析(三)[下]——CVE-2014-6332的前置知识,对vbscrip.dll组件进行逆向分析，以及VBScript数据类型，数组，VarType函数，LenB函数详细分析，并介绍VBS脚本调试技巧
4.本篇文章十分适合漏洞安全研究人员进行交流学习
5.若文章中存在说得不清楚或者错误的地方 欢迎师傅到公众号后台留言中指出 感激不尽
```

近来分析Internet Explorer历史漏洞，遂对VBScript脚本解析引擎进行研究，具体环境如下：
- OS版本：Windows 7 Service Pack 1
- Internet Explorer版本：8.0.7601.17514
- vbscript.dll版本：5.8.7601.17514


## 0x01 变量

VBScript中仅有一种数据类型——Variant。其结构定义如下：

```
typedef struct tagVARIANT `{`
  union `{`
    struct `{`
      VARTYPE vt;
      WORD    wReserved1;
      WORD    wReserved2;
      WORD    wReserved3;
      union `{`
        LONGLONG     llVal;
        LONG         lVal;
        BYTE         bVal;
        SHORT        iVal;
        FLOAT        fltVal;
        DOUBLE       dblVal;
        VARIANT_BOOL boolVal;
        VARIANT_BOOL __OBSOLETE__VARIANT_BOOL;
        SCODE        scode;
        CY           cyVal;
        DATE         date;
        BSTR         bstrVal;
        IUnknown     *punkVal;
        IDispatch    *pdispVal;
        SAFEARRAY    *parray;
        BYTE         *pbVal;
        SHORT        *piVal;
        LONG         *plVal;
        LONGLONG     *pllVal;
        FLOAT        *pfltVal;
        DOUBLE       *pdblVal;
        VARIANT_BOOL *pboolVal;
        VARIANT_BOOL *__OBSOLETE__VARIANT_PBOOL;
        SCODE        *pscode;
        CY           *pcyVal;
        DATE         *pdate;
        BSTR         *pbstrVal;
        IUnknown     **ppunkVal;
        IDispatch    **ppdispVal;
        SAFEARRAY    **pparray;
        VARIANT      *pvarVal;
        PVOID        byref;
        CHAR         cVal;
        USHORT       uiVal;
        ULONG        ulVal;
        ULONGLONG    ullVal;
        INT          intVal;
        UINT         uintVal;
        DECIMAL      *pdecVal;
        CHAR         *pcVal;
        USHORT       *puiVal;
        ULONG        *pulVal;
        ULONGLONG    *pullVal;
        INT          *pintVal;
        UINT         *puintVal;
        struct `{`
          PVOID       pvRecord;
          IRecordInfo *pRecInfo;
        `}` __VARIANT_NAME_4;
      `}` __VARIANT_NAME_3;
    `}` __VARIANT_NAME_2;
    DECIMAL decVal;
  `}` __VARIANT_NAME_1;
`}` VARIANT;
```

其中`VARTYPE`可参阅[Microsoft Docs——VARIANT Type Constants][https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oaut/3fe7db9f-5803-4dc4-9d14-5425d3f5461f。例：](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oaut/3fe7db9f-5803-4dc4-9d14-5425d3f5461f%E3%80%82%E4%BE%8B%EF%BC%9A)

```
'显式声明
Dim Name,Age,Hex,Pi
Name="Ethon"
Age=27
Hex=&amp;h80000000
Pi=3.1415926

'隐式声明
Hello="ABC123"
```

赋值对应函数为`vbscript!AssignVar`，于该函数处设断，查看其参数：

[![](https://p5.ssl.qhimg.com/t017b74b7698cc5bd2e.png)](https://p5.ssl.qhimg.com/t017b74b7698cc5bd2e.png)

`0x400C`表示`VT_VARIANT`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01659309f2c3f99361.png)

判断`pvargSrc—&gt;vt`值(具体数值可自行分析，不赘述)，若均不满足，执行如下语句：

[![](https://p5.ssl.qhimg.com/t0142cbd646611694bf.png)](https://p5.ssl.qhimg.com/t0142cbd646611694bf.png)

简单来说，即`VariantCopyInd(&amp;pvarDest, pvargSrc)`——&gt;copy `pvarDest` to `pvarg`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012964400445b27cd4.png)

隐式声明变量其`pvarg`全为零：

[![](https://p1.ssl.qhimg.com/t0100f909427ac45b70.png)](https://p1.ssl.qhimg.com/t0100f909427ac45b70.png)



## 0x02 数组

数组存储结构由`SAFEARRAY`定义：

```
typedef struct tagSAFEARRAY `{`
  USHORT         cDims;
  USHORT         fFeatures;
  ULONG          cbElements;
  ULONG          cLocks;
  PVOID          pvData;
  SAFEARRAYBOUND rgsabound[1];
`}` SAFEARRAY;
```

其中各字段含义可参阅[Microsoft Docs——SAFEARRAY][https://docs.microsoft.com/en-us/windows/win32/api/oaidl/ns-oaidl-safearray](https://docs.microsoft.com/en-us/windows/win32/api/oaidl/ns-oaidl-safearray) ，`SAFEARRAYBOUND`结构定义如下：

```
typedef struct tagSAFEARRAYBOUND `{`
  ULONG cElements;
  LONG  lLbound;
`}` SAFEARRAYBOUND, *LPSAFEARRAYBOUND;
```

数组定义及赋值操作：

```
Dim stu_name(3)

stu_name(0)="Alan"
stu_name(1)="Susan"
stu_name(2)="Lisa"
stu_name(3)="Mary"
```

VBS中数组下标由0开始，数组元素个数为n+1(`Dim array_name(n)`)。另一种定义数组方法：

```
Dim stu_name

stu_name=Array("Alan","Susan","Lisa","Mary")
```

对应函数为`vbscript!MakeArray`：

[![](https://p0.ssl.qhimg.com/t01c52381e5744fbdf6.png)](https://p0.ssl.qhimg.com/t01c52381e5744fbdf6.png)

传递给函数的参数有二——`cDims`对应维数，`VAR`对应n。`cDims`应介于1-64：

[![](https://p4.ssl.qhimg.com/t0113393a0754f9840a.png)](https://p4.ssl.qhimg.com/t0113393a0754f9840a.png)

先来看一维数组的创建：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018a6ef270dce15360.png)

为`rgsabound`结构各字段赋值：

[![](https://p1.ssl.qhimg.com/t01f421deb4ad1bdbd8.png)](https://p1.ssl.qhimg.com/t01f421deb4ad1bdbd8.png)

之后则直接调用`SafeArrayCreate`函数进行创建，各参数含义可参阅[Microsoft Docs——SafeArrayCreate][https://docs.microsoft.com/en-us/windows/win32/api/oleauto/nf-oleauto-safearraycreate](https://docs.microsoft.com/en-us/windows/win32/api/oleauto/nf-oleauto-safearraycreate) 。创建完成：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a68eee92e4d3575b.png)

为数组元素赋值则直接将该元素所在内存偏移传递给`vbscript!AssignVar`：

[![](https://p5.ssl.qhimg.com/t015381608400c87688.png)](https://p5.ssl.qhimg.com/t015381608400c87688.png)

下面来看看二维数组(`Dim stu_name(2,3)`)创建过程：

[![](https://p1.ssl.qhimg.com/t019a3ffe5c812fcee9.png)](https://p1.ssl.qhimg.com/t019a3ffe5c812fcee9.png)

可以看到数组各维大小于内存中并列存储，之后调用`VAR::PvarGetTypeVal`逐一读取为`rgsabound`中`cElements`字段赋值：

[![](https://p1.ssl.qhimg.com/t0111a306b351807eea.png)](https://p1.ssl.qhimg.com/t0111a306b351807eea.png)

各维大小于内存中由最高维——&gt;最低维存储，故读取时首先计算出`v3`变量指向最低维大小所在内存偏移，之后递减。创建完成：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014da06d038911bc22.png)

`Redim`语句用于重新定义数组大小：

```
'定义一维动态数组
Dim MyArray()
'重新定义该数组大小
ReDim MyArray(3) 
MyArray(0) = "A" 
MyArray(1) = "B"
MyArray(2) = "C"
MyArray(3) = "C"
```

再次调用`vbscript!MakeArray`过程如下：

[![](https://p2.ssl.qhimg.com/t018f123f22a3426e22.png)](https://p2.ssl.qhimg.com/t018f123f22a3426e22.png)

而在重新定义时加上`Preserve`关键字用于保留之前元素：

```
Dim MyArray()
ReDim MyArray(3)
MyArray(0) = "A"
MyArray(1) = "B"
MyArray(2) = "C"
MyArray(3) = "D"
ReDim Preserve MyArray(5)
MyArray(4) = "E"
MyArray(5) = "F"
```

其对应`vbscript!RedimPreserveArray`函数：

[![](https://p2.ssl.qhimg.com/t0146ed3a78ae6b1acc.png)](https://p2.ssl.qhimg.com/t0146ed3a78ae6b1acc.png)

为`psaboundNew`各字段赋值完成后传递给`SafeArrayRedim`函数：

[![](https://p3.ssl.qhimg.com/t01afe8566c41a6a8a0.png)](https://p3.ssl.qhimg.com/t01afe8566c41a6a8a0.png)



## 0x03 可用于调试时函数

`IsEmpty(var)`对应`vbscript!VbsIsEmpty`，其第三个参数对应`var`。一例：

```
&lt;!doctype html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
&lt;/head&gt;

&lt;body&gt;
&lt;script LANGUAGE="VBScript"&gt;
    dim a
    a = &amp;h1234
    IsEmpty(a)
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

[![](https://p0.ssl.qhimg.com/t011e9230b7753fa6e7.png)](https://p0.ssl.qhimg.com/t011e9230b7753fa6e7.png)

`IsObject(var)`对应`vbscript!VbsIsObject`，同样，其第三个参数对应`var`。一例：

```
&lt;!doctype html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
&lt;/head&gt;

&lt;body&gt;
&lt;script LANGUAGE="VBScript"&gt;
    dim a
    a = &amp;h1234
    IsObject(a)
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

[![](https://p1.ssl.qhimg.com/t0145570f1a78b7ae75.png)](https://p1.ssl.qhimg.com/t0145570f1a78b7ae75.png)

在调试时可借助这两个函数以确定变量值或内存位置。



## 0x04 VarType函数

```
&lt;!doctype html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
&lt;/head&gt;

&lt;body&gt;
&lt;script LANGUAGE="VBScript"&gt;
    dim a
    a = &amp;h1234
    VarType(a)
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

`VarType`对应`vbscript!VbsVarType`，其调用`GetVarType`函数获取类型值并完成赋值操作：

[![](https://p2.ssl.qhimg.com/t016d30ec93e057edd6.png)](https://p2.ssl.qhimg.com/t016d30ec93e057edd6.png)

参数1用于存储类型值，参数2为`VarType`参数：

[![](https://p2.ssl.qhimg.com/t013a1902905df7199d.png)](https://p2.ssl.qhimg.com/t013a1902905df7199d.png)

`GetVarType`函数调用`PvarGetVarVal`——判断类型值是否为`0x4A`或`0x0C`：

[![](https://p5.ssl.qhimg.com/t0167a8e920dbbe00a0.png)](https://p5.ssl.qhimg.com/t0167a8e920dbbe00a0.png)

之后与`0x09`进行比较，若不是则直接返回对象进而获取`vt`值：

[![](https://p5.ssl.qhimg.com/t01195cf7345201c9a5.png)](https://p5.ssl.qhimg.com/t01195cf7345201c9a5.png)

由`VbsVarType`函数完成最终赋值给参数1操作：

[![](https://p4.ssl.qhimg.com/t016ea15e858f529ab2.png)](https://p4.ssl.qhimg.com/t016ea15e858f529ab2.png)



## 0x05 LenB函数

```
&lt;!doctype html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
&lt;/head&gt;

&lt;body&gt;
&lt;script LANGUAGE="VBScript"&gt;
On Error Resume Next
Dim length,a
a=1.12345678901235
length=LenB("Hello")
length=LenB(a)
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

该函数用于返回存储字符串字节大小，其对应`vbscript!VbsLenB`。参数为字符串时，该函数先是`call VAR::BstrGetVal`，返回`pbstrVal`：

[![](https://p5.ssl.qhimg.com/t0119efb61aae8c7bfd.png)](https://p5.ssl.qhimg.com/t0119efb61aae8c7bfd.png)

之后`call cbLengthBstr`返回长度：

[![](https://p5.ssl.qhimg.com/t01c77e2dd6c4783227.png)](https://p5.ssl.qhimg.com/t01c77e2dd6c4783227.png)

参数为变量时， `VAR::BstrGetVal`函数调用`VAR::PvarConvert`，将其内容转换为字符串：

[![](https://p4.ssl.qhimg.com/t01c250a757f3b4756f.png)](https://p4.ssl.qhimg.com/t01c250a757f3b4756f.png)

之后再进行计算：

[![](https://p1.ssl.qhimg.com/t01bf50fac5120cb2fe.png)](https://p1.ssl.qhimg.com/t01bf50fac5120cb2fe.png)

`cbLengthBstr`函数功能仅是读取字符串存储位置之前4字节内容，该内容为字符串长度：

[![](https://p4.ssl.qhimg.com/t018d696ca9f7754eef.png)](https://p4.ssl.qhimg.com/t018d696ca9f7754eef.png)



## 0x06 参阅链接
- [Microsoft Docs——SAFEARRAY structure](https://docs.microsoft.com/en-us/windows/win32/api/oaidl/ns-oaidl-safearray)
- [Microsoft Docs——VARIANT structure](https://docs.microsoft.com/en-us/windows/win32/api/oaidl/ns-oaidl-variant)
- [Microsoft Docs——VARIANT Type Constants](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-oaut/3fe7db9f-5803-4dc4-9d14-5425d3f5461f)
- [Microsoft Docs——SafeArrayCreate](https://docs.microsoft.com/en-us/windows/win32/api/oleauto/nf-oleauto-safearraycreate)
- [Microsoft Docs——DECIMAL structure](https://docs.microsoft.com/en-us/windows/win32/api/wtypes/ns-wtypes-decimal-r1)