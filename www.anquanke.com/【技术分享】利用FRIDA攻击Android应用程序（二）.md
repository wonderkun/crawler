
# 【技术分享】利用FRIDA攻击Android应用程序（二）


                                阅读量   
                                **183261**
                            
                        |
                        
                                                                                                                                    ![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85759/t012f09d5120e5ceaf8.jpg)](./img/85759/t012f09d5120e5ceaf8.jpg)



翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

稿费：190RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**传送门**

[**【技术分享】利用FRIDA攻击Android应用程序（一）******](http://bobao.360.cn/learning/detail/3641.html)

<br>

在[本系列文章的第一篇](http://bobao.360.cn/learning/detail/3641.html)中，我们已经对Frida的原理进行了详细的介绍，现在，我们将演示如何通过Frida搞定crackme问题。有了第一篇的内容作为基础，理论上讲这应该不是什么难事。如果你想亲自动手完成本文介绍的实验的话，请下载 

[OWASP Uncrackable Crackme Level 1](https://github.com/OWASP/owasp-mstg/blob/master/OMTG-Files/02_Crackmes/List_of_Crackmes.md) ([APK](https://github.com/OWASP/owasp-mstg/blob/master/OMTG-Files/02_Crackmes/01_Android/Level_01/UnCrackable-Level1.apk))

[BytecodeViewer](http://bytecodeviewer.com/)

[dex2jar](https://github.com/pxb1988/dex2jar)

当然，这里假定您已在计算机上成功地安装了Frida（版本9.1.16或更高版本），并在（已经获得root权限的）设备上启动了相应服务器的二进制代码。我们这里将在模拟器中使用Android 7.1.1 ARM映像。

然后，请在您的设备上安装Uncrackable Crackme Level 1应用程序： 

```
adb install sg.vantagepoint.uncrackable1.apk
```

安装完成后，从模拟器的菜单（右下角的橙色图标）启动它： 

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f02c75b8490888ec.png)

一旦启动应用程序，您就会注意到它不太乐意在已经获取root权限的设备上运行： 

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dcd24e7bd758f5c0.png)

如果单击“OK”，应用程序会立即退出。嗯，不太友好啊。看起来我们无法通过这种方法来搞定crackme。真是这样吗？让我们看看到底怎么回事，同时考察一下这个应用程序的内部运行机制。

现在，使用dex2jar将apk转换为jar文件： 



```
michael@sixtyseven:/opt/dex2jar/dex2jar-2.0$ ./d2j-dex2jar.sh -o /home/michael/UnCrackable-Level1.jar /home/michael/UnCrackable-Level1.apk 
dex2jar /home/michael/UnCrackable-Level1.apk -&gt; /home/michael/UnCrackable-Level1.jar
```

然后，将其加载到BytecodeViewer（或其他支持Java的反汇编器）中。你也可以尝试直接加载到BytecodeViewer中，或直接提取classes.dex，但是试了一下好像此路不通，所以我才提前使用dex2jar完成相应的转换。

为了使用CFR解码器，需要在BytecodeViewer中依次选择View-&gt; Pane1-&gt; CFR-&gt; Java。如果你想将反编译器的结果与Smali反汇编（通常比反编译稍微准确一些）进行比较的话，可以将Pane2设置为Smali代码。

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0176182b07864c9919.png)

下面是CFR解码器针对应用程序的MainActivity的输出结果： 



```
package sg.vantagepoint.uncrackable1;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.text.Editable;
import android.view.View;
import android.widget.EditText;
import sg.vantagepoint.uncrackable1.a;
import sg.vantagepoint.uncrackable1.b;
import sg.vantagepoint.uncrackable1.c;
public class MainActivity
extends Activity {
    private void a(String string) {
        AlertDialog alertDialog = new AlertDialog.Builder((Context)this).create();
        alertDialog.setTitle((CharSequence)string);
        alertDialog.setMessage((CharSequence)"This in unacceptable. The app is now going to exit.");
        alertDialog.setButton(-3, (CharSequence)"OK", (DialogInterface.OnClickListener)new b(this));
        alertDialog.show();
    }
    protected void onCreate(Bundle bundle) {
        if (sg.vantagepoint.a.c.a() || sg.vantagepoint.a.c.b() || sg.vantagepoint.a.c.c()) {
            this.a("Root detected!"); //This is the message we are looking for
        }
        if (sg.vantagepoint.a.b.a((Context)this.getApplicationContext())) {
            this.a("App is debuggable!");
        }
        super.onCreate(bundle);
        this.setContentView(2130903040);
    }
    public void verify(View object) {
        object = ((EditText)this.findViewById(2131230720)).getText().toString();
        AlertDialog alertDialog = new AlertDialog.Builder((Context)this).create();
        if (a.a((String)object)) {
            alertDialog.setTitle((CharSequence)"Success!");
            alertDialog.setMessage((CharSequence)"This is the correct secret.");
        } else {
            alertDialog.setTitle((CharSequence)"Nope...");
            alertDialog.setMessage((CharSequence)"That's not it. Try again.");
        }
        alertDialog.setButton(-3, (CharSequence)"OK", (DialogInterface.OnClickListener)new c(this));
        alertDialog.show();
    }
}
```

通过查看其他反编译的类文件，我们发现它是一个小应用程序，并且貌似可以通过逆向解密例程和字符串修改例程来解决这个crackme问题。然而，既然有神器Frida在手，自然会有更方便的手段可供我们选择。首先，让我们看看这个应用程序是在哪里检查设备是否已获取root权限的。在“Root detected”消息上面，我们可以看到： 

```
if (sg.vantagepoint.a.c.a() || sg.vantagepoint.a.c.b() || sg.vantagepoint.a.c.c())
```

如果你查看sg.vantagepoint.a.c类的话，你就会发现与root权限有关的各种检查： 



```
public static boolean a()
    {
        String[] a = System.getenv("PATH").split(":");
        int i = a.length;
        int i0 = 0;
        while(true)
        {
            boolean b = false;
            if (i0 &gt;= i)
            {
                b = false;
            }
            else
            {
                if (!new java.io.File(a[i0], "su").exists())
                {
                    i0 = i0 + 1;
                    continue;
                }
                b = true;
            }
            return b;
        }
    }
    public static boolean b()
    {
        String s = android.os.Build.TAGS;
        if (s != null &amp;&amp; s.contains((CharSequence)(Object)"test-keys"))
        {
            return true;
        }
        return false;
    }
    public static boolean c()
    {
        String[] a = new String[7];
        a[0] = "/system/app/Superuser.apk";
        a[1] = "/system/xbin/daemonsu";
        a[2] = "/system/etc/init.d/99SuperSUDaemon";
        a[3] = "/system/bin/.ext/.su";
        a[4] = "/system/etc/.has_su_daemon";
        a[5] = "/system/etc/.installed_su_daemon";
        a[6] = "/dev/com.koushikdutta.superuser.daemon/";
        int i = a.length;
        int i0 = 0;
        while(i0 &lt; i)
        {
            if (new java.io.File(a[i0]).exists())
            {
                return true;
            }
            i0 = i0 + 1;
        }
        return false;
    }
```

在Frida的帮助下，我们可以通过覆盖它们使所有这些方法全部返回false，这一点我们已经在第一篇中介绍过了。但是，当一个函数由于检测到设备已经取得了root权限而返回true时，结果会怎样呢？ 正如我们在MainActivity函数中看到的那样，它会打开一个对话框。此外，它还会设置一个onClickListener，当我们按下OK按钮时就会触发它： 

```
alertDialog.setButton(-3, (CharSequence)"OK", (DialogInterface.OnClickListener)new b(this));
```

这个onClickListener的实现代码如下所示： 



```
package sg.vantagepoint.uncrackable1;
class b implements android.content.DialogInterface$OnClickListener {
    final sg.vantagepoint.uncrackable1.MainActivity a;
    b(sg.vantagepoint.uncrackable1.MainActivity a0)
    {
        this.a = a0;
        super();
    }
    public void onClick(android.content.DialogInterface a0, int i)
    {
        System.exit(0);
    }
}
```

它的功能并不复杂，实际上只是通过System.exit（0）退出应用程序而已。所以我们要做的事情就是防止应用程序退出。为此，我们可以用Frida覆盖onClick方法。下面，让我们创建一个文件uncrackable1.js，并把我们的代码放入其中： 



```
setImmediate(function() { //prevent timeout
    console.log("[*] Starting script");
    Java.perform(function() {
      bClass = Java.use("sg.vantagepoint.uncrackable1.b");
      bClass.onClick.implementation = function(v) {
         console.log("[*] onClick called");
      }
      console.log("[*] onClick handler modified")
    })
})
```

如果你已经阅读了本系列文章的第一篇的话，这个脚本应该不难理解：将我们的代码封装到setImmediate函数中，以防止超时，然后通过Java.perform来使用Frida用于处理Java的方法。接下来，我们将得到一个类的包装器，可用于实现OnClickListener接口并覆盖其onClick方法。在我们的版本中，这个函数只是向控制台写一些输出。与之前不同的是，它不会退出应用程序。由于原来的onClickHandler被替换为Frida注入的函数，因此它绝对不会被调用了，所以当我们点击对话框的OK按钮时，应用程序就不退出了。好了，让我们实验一下：打开应用程序（使其显示“Root detected”对话框） 

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0176182b07864c9919.png)

并注入脚本： 

```
frida -U -l uncrackable1.js sg.vantagepoint.uncrackable1
```

Frida注入代码需要几秒钟的时间，当你看到“onClick handler modified”消息时说明注入完成了（当然，注入完成时你也可以得到一个shell之前，因为可以把我们的代码放入一个setImmediate包装器中，从而让Frida在后台执行它）。

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010e4948f23a392a13.png)

然后，点击应用程序中的OK按钮。如果一切顺利的话，应用程序就不会退出了。

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012a52a96cc337c315.png)

我们看到对话框消失了，这样我们就可以输入密码了。下面让我们输入一些内容，点击Verify，看看会发生什么情况： 

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e4da3184ffa81fdb.png)

不出所料，这是一个错误的密码。但是这并不要紧，因为我们真正要找的是：加密/解密例程以及结果和输入的比对。

再次检查MainActivity时，我们注意到了下面的函数 

```
public void verify(View object) {
```

它调用了类sg.vantagepoint.uncrackable1.a的方法： 

```
if (a.a((String)object)) {
```

下面是sg.vantagepoint.uncrackable1.a类的反编译结果： 



```
package sg.vantagepoint.uncrackable1;
import android.util.Base64;
import android.util.Log;
/*
 * Exception performing whole class analysis ignored.
 */
public class a {
    public static boolean a(String string) {
        byte[] arrby = Base64.decode((String)"5UJiFctbmgbDoLXmpL12mkno8HT4Lv8dlat8FxR2GOc=", (int)0);
        byte[] arrby2 = new byte[]{};
        try {
            arrby2 = arrby = sg.vantagepoint.a.a.a((byte[])a.b((String)"8d127684cbc37c17616d806cf50473cc"), (byte[])arrby);
        }
        catch (Exception var2_2) {
            Log.d((String)"CodeCheck", (String)("AES error:" + var2_2.getMessage()));
        }
        if (!string.equals(new String(arrby2))) return false;
        return true;
    }
    public static byte[] b(String string) {
        int n = string.length();
        byte[] arrby = new byte[n / 2];
        int n2 = 0;
        while (n2 &lt; n) {
            arrby[n2 / 2] = (byte)((Character.digit(string.charAt(n2), 16) &lt;&lt; 4) + Character.digit(string.charAt(n2 + 1), 16));
            n2 += 2;
        }
        return arrby;
    }
}
```

注意在a方法末尾的string.equals比较，以及在上面的try代码块中字符串arrby2的创建。arrby2是函数sg.vantagepoint.a.a.a的返回值。string.equals会将我们的输入与arrby2进行比较。所以，我们要追踪sg.vantagepoint.a.a的返回值。

现在，我们可以着手对这些字符串操作函数和解密函数进行逆向工程，并处理原始加密字符串了，实际上它们也包含在上面的代码中。或者，我们还可以让应用程序替我们完成字符串的处理和加密工作，而我们只要钩住sg.vantagepoint.a.a.a函数来捕获其返回值就可以坐享其成了。返回值是我们的输入将要与之比较的解密字符串（它以字节数组的形式返回）。具体可以参考下面的脚本： 



```
aaClass = Java.use("sg.vantagepoint.a.a");
        aaClass.a.implementation = function(arg1, arg2) {
            retval = this.a(arg1, arg2);
            password = ''
            for(i = 0; i &lt; retval.length; i++) {
               password += String.fromCharCode(retval[i]);
            }
            console.log("[*] Decrypted: " + password);
            return retval;
        }
        console.log("[*] sg.vantagepoint.a.a.a modified");
```

其中，我们覆盖了sg.vantagepoint.a.a.a函数，截获其返回值并将其转换为可读字符串。这正是我们要找的解密字符串，所以我们将其打印到控制台。

将上述代码放到一起，就组成了一个完整的脚本： 



```
setImmediate(function() {
    console.log("[*] Starting script");
    Java.perform(function() {
        bClass = Java.use("sg.vantagepoint.uncrackable1.b");
        bClass.onClick.implementation = function(v) {
         console.log("[*] onClick called.");
        }
        console.log("[*] onClick handler modified")
        aaClass = Java.use("sg.vantagepoint.a.a");
        aaClass.a.implementation = function(arg1, arg2) {
            retval = this.a(arg1, arg2);
            password = ''
            for(i = 0; i &lt; retval.length; i++) {
               password += String.fromCharCode(retval[i]);
            }
            console.log("[*] Decrypted: " + password);
            return retval;
        }
        console.log("[*] sg.vantagepoint.a.a.a modified");
    });
});
```

现在，我们来运行这个脚本。然后，将其保存为uncrackable1.js，并执行下列命令（如果Frida没有自动重新运行的话） 

```
frida -U -l uncrackable1.js sg.vantagepoint.uncrackable1
```

耐心等待，直到您看到消息sg.vantagepoint.a.a发生变化，然后在Root detected对话框中单击OK，在secret code中输入一些字符，然后按Verify按钮。哎，运气好像不太好啊。

但是，请注意Frida的输出： 



```
michael@sixtyseven:~/Development/frida$ frida -U -l uncrackable1.js sg.vantagepoint.uncrackable1
     ____
    / _  |   Frida 9.1.16 - A world-class dynamic instrumentation framework
   | (_| |
    &gt; _  |   Commands:
   /_/ |_|       help      -&gt; Displays the help system
   . . . .       object?   -&gt; Display information about 'object'
   . . . .       exit/quit -&gt; Exit
   . . . .
   . . . .   More info at http://www.frida.re/docs/home/
[*] Starting script
[USB::Android Emulator 5554::sg.vantagepoint.uncrackable1]-&gt; [*] onClick handler modified
[*] sg.vantagepoint.a.a.a modified
[*] onClick called.
[*] Decrypted: I want to believe
```

太好了。我们实际上已经得到了解密的字符串：I want to believe。那么，我们赶紧输入这个字符串，看看是否正确： 

[![](./img/85759/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011531b94f54e9279b.png)

本文到此结束，但愿读者阅读本文后，能够对学习Frida的动态二进制插桩功能有所帮助。

<br>



**传送门**

[**【技术分享】利用FRIDA攻击Android应用程序（一）******](http://bobao.360.cn/learning/detail/3641.html)

<br>
