> 原文链接: https://www.anquanke.com//post/id/93023 


# 看我如何逆向iPhoneX的Home Indicator


                                阅读量   
                                **139028**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Sash Zats，文章来源：zats.io
                                <br>原文地址：[http://blog.zats.io/2017/12/27/iPhone-X-home-button/](http://blog.zats.io/2017/12/27/iPhone-X-home-button/)

译文仅供参考，具体内容表达以及含义原文为准

## 一、前言

Apple在iPhone X上取消了之前一直存在的物理Home键，取而代之的是位于屏幕底部的一个横线，官方称之为Home Indicator。当我第一次见到Home Indicator时，我比较感兴趣的是该横线的行为模式：不管是以任意壁纸作为背景的锁屏界面上，还是在显示任意内容的第三方app上（如视频应用或者游戏应用，此时背景内容变化会比较快），它都必须处于可见状态。

[![](https://p3.ssl.qhimg.com/t01460d64ea6d7f1ed0.png)](https://p3.ssl.qhimg.com/t01460d64ea6d7f1ed0.png)

很显然UIKit并不会向我们透露这方面的相关信息，因此我们需要自己动手，弄清楚Home Indicator的构建原理。

## 二、找出Home Indicator类

为了弄清楚应该在哪里寻找相关代码，我试着去寻找类似的UI元素。最开始我认为系统状态栏是最为接近的一种元素。与Home Indicator一样，系统状态栏也会出现在锁屏界面上，也会被添加到每一个app窗口中。因此我最开始尝试在UIKit中寻找包含与状态栏有关的一些代码。搜索GitHub上已有的UIKit头文件代码后，我并没有找到与新的Home Indicator有关的任何代码。接下来，我想探索的是SpringBoard，这是一个“app”，位于CoreServices目录中，包含与锁屏及主屏幕有关的各种系统功能。使用`class-dump`（安装命令为`$ brew install class-dump`）导出SpringBoard中包含的类后，我们可以找到一个比较有趣的东西：`SBHomeGrabberView`。这对我们而言是个不错的开始：

```
$ class-dump /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/Library/CoreSimulator/Profiles/Runtimes/iOS.simruntime/Contents/Resources/RuntimeRoot/System/Library/CoreServices/SpringBoard.app/SpringBoard

...

@interface SBHomeGrabberView : UIView &lt;_UISettingsKeyPathObserver, SBAttentionAwarenessClientDelegate, MTLumaDodgePillBackgroundLuminanceObserver&gt;
`{`
    SBHomeGrabberSettings *_settings;
    MTLumaDodgePillView *_pillView;
    SBAttentionAwarenessClient *_idleTouchAwarenessClient;
    _Bool _touchesAreIdle;
    _Bool _autoHides;
    long long _luma;
    unsigned long long _suppressLumaUpdates;
`}`

@property(nonatomic) _Bool autoHides; // @synthesize autoHides=_autoHides;
- (void).cxx_destruct;
- (void)lumaDodgePillDidDetectBackgroundLuminanceChange:(id)arg1;
```

接下来，让我们将整段代码从SpringBoard中加载到我们自己的虚拟应用中，以便将该视图添加到窗口中，检查该视图是否就是我们苦苦寻找的目标。这段代码并不复杂，基本思想如下：

```
#import &lt;dlfcn.h&gt;

// somewhere in viewDidLoad
dlopen([binaryPath cStringUsingEncoding:NSUTF8StringEncoding], RTLD_NOW);
UIView *const view = [[NSClassFromString(@"SBHomeGrabberView") alloc] init];
[view sizeToFit];
[self.view addSubview:view];
```

以上代码不需要经过太多改动，我们就可以得到如下效果：

[![](https://p0.ssl.qhimg.com/t012175471c8c668d65.png)](https://p0.ssl.qhimg.com/t012175471c8c668d65.png)

这的确就是我们所寻找的目标，现在我们可以来分析一下这个视图的构建过程。为了了解实现细节，我选择使用Hopper Disassembler，免费版的已经足以满足我们的使用需求。在这个应用的帮助下，我们可以更好理解汇编代码（虽然我自己对汇编代码本身也不是特别了解）。我们所需要做的就是打开一个二进制文件，查找其中比较感兴趣的那些方法。跳转到该方法后，在顶部区域切换为伪代码视图。这样该应用就会生成Objective-C、C++以及汇编语言混合而成的代码，可读性大大提高。

[![](https://p0.ssl.qhimg.com/t0118dda0a3d64b2709.png)](https://p0.ssl.qhimg.com/t0118dda0a3d64b2709.png)

具体步骤如下：

1、输入类名，查看所有已实现的方法。

2、随着时间的推移，你会逐渐掌握技巧，知道如何挖掘“有趣”的那些方法。选择以公开的UIKit方法开始总归是不错的选择，因为Apple的工程师也会使用这些方法。这也是我选择从`-[SBHomeGrabberView initWithFrame:]`开始的原因所在。

3、除非你很习惯于阅读汇编代码，否则还是选择伪代码模式比较好。

4、尽量理解其中代码。有时候代码本身看起来就比较好理解，有时候你会陷入代码的迷宫中无法自拔。

就我自己而言，我发现阅读实现细节本身就是一件非常有趣的事情。有时候我单纯只是因为觉得“有趣”才这么做，有时候则是想更好地理解某些行为背后的原因。

回到我们的`SBHomeGrabberView`上来，我们可以看到它只是一个比较简单的封装器（某些地方除外，比如`AWAttentionAwarenessConfiguration`，回头我们再来处理它），其中添加了一个`MTLumaDodgePillView`子视图。最开始我认为它的定义应该位于Metal框架中（因为使用了`MTL`前缀），但看起来它又有点过于具体，不应该在Metal这类“底层”框架中定义。此外，Matthias也在Twitter上指出，这个类的前缀实际上是`MT`，并不是`MTL`。幸运的是，如果我们将某个二进制文件（如SpringBoard）载入这个app中，我们同时也可以访问该文件后续加载的所有库。想要知道哪个库定义某个类并不困难，只需要使用`dladdr`即可：

```
const Class MTLumaDodgePillViewClass = NSClassFromString(@"MTLumaDodgePillView");
Dl_info dlInfo;
dladdr((__bridge void *)MTLumaDodgePillViewClass, &amp;dlInfo);
dlInfo.dli_fname; // path to the binary defining the symbol (class in this case)
```

以上代码可以添加到我们设计的那个应用中，稍加运行即可。此外，我们也可以选择使用`lldb`。很少人知道lldb支持变量设置功能。使用`lldb`的优点在于我们并不需要重新编译目标应用，缺点在于`lldb`需要知道代码中的具体类型，因为它并不能访问头文件，因此我们需要额外花些精力，处理变量及函数返回结果的类型：

```
(lldb) e Dl_info $dlInfo
(lldb) e (void)dladdr((__bridge void *)NSClassFromString(@"MTLumaDodgePillView"), &amp; $dlInfo);
(lldb) p $dlInfo.dli_fname
(const char *) $1 = 0x00006000001fd900 "/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/Library/CoreSimulator/Profiles/Runtimes/iOS.simruntime/Contents/Resources/RuntimeRoot/System/Library/PrivateFrameworks/MaterialKit.framework/MaterialKit"
```

如上所述，`MTLumaDodgePillView`的定义位于`/System/Library/PrivateFrameworks/MaterialKit.framework/MaterialKit`中。

```
@class MTLumaDodgePillView;

@protocol MTLumaDodgePillBackgroundLuminanceObserver &lt;NSObject&gt;
- (void)lumaDodgePillDidDetectBackgroundLuminanceChange:(MTLumaDodgePillView *)arg1;
@end

@interface MTLumaDodgePillView : UIView
@property(nonatomic, weak) id &lt;MTLumaDodgePillBackgroundLuminanceObserver&gt; backgroundLumninanceObserver;
@property(nonatomic) MTLumaDodgePillViewStyle style;
@property(nonatomic, readonly) MTLumaDodgePillViewBackgroundLuminance backgroundLuminance;
@end
```

信息量并不大。为了找到`MTLumaDodgePillViewStyle`以及`MTLumaDodgePillViewBackgroundLuminance`的具体值，我们只要查看相关的方法描述即可。根据描述，它会将整数值转换为常量形式的字符串，如下所示：

```
typedef NS_ENUM(NSInteger, MTLumaDodgePillViewStyle) `{`
 MTLumaDodgePillViewStyleNone = 0,
 MTLumaDodgePillViewStyleThin = 1,
 MTLumaDodgePillViewStyleGray = 2,
 MTLumaDodgePillViewStyleBlack = 3,
 MTLumaDodgePillViewStyleWhite = 4,
`}`;

typedef NS_ENUM(NSInteger, MTLumaDodgePillViewBackgroundLuminance) `{`
 MTLumaDodgePillViewBackgroundLuminanceUnknown = 0,
 MTLumaDodgePillViewBackgroundLuminanceDark = 1,
 MTLumaDodgePillViewBackgroundLuminanceLight = 2,
`}`;
```

最后我们还要注意`backgroundLumninanceObserver`这个API，每当目标视图改变外观时，这个函数都会调用回调函数。

## 三、构建我们自己的MTLumaDodgePillView

我们离目标已经越来越近，`MTLumaDodgePillViewStyle`本身只是有序数字的一个封装器。在内部中，它还包含许多私有类：它可以作为调用`CABackdropLayer`（私有类，自iOS 7以上系统引入）的代理，使用了一整套`CAFilter`（私有类，自iOS 2以上系统引入），其中包括名为`kCAFilterHomeAffordanceBase`的一个滤镜类。iOS从7开始引入了毛玻璃特效，而`CABackdropLayer`正是该特性背后的推动者。简而言之，它负责克隆图层后的视图层次结构，收集相关内容的统计信息。此外，任何CALayer都支持将QuartzCore过滤器应用于任何图层上。只要克隆视图的层次结构以及应用在试图上的过滤器，我们就可以产生`UIVisualEffectView`提供的所有变化效果。我们来看一下最基本的一种毛玻璃效果：

```
UIBlurEffect *blur = [UIBlurEffect effectWithStyle:UIBlurEffectStyleLight];
UIVisualEffectView *blurView = [[UIVisualEffectView alloc] initWithEffect:blur];
```

为了生成这种效果，我们只需要：高斯（Gaussian）模糊、饱和度滤镜（saturation filter）以及使用source over混合模式的纯白色图层即可。过滤器部分的大致代码如下所示：

```
CAFilter *const blur = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterGaussianBlur];
[blur setValue:@30 forKey:@"inputRadius"];
CAFilter *const saturate = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterColorSaturate];
[saturate setValue:@1.8 forKey:@"inputAmount"];
CABackdropLayer *backdrop = [NSClassFromString(@"CABackdropLayer") new];
backdrop.filters = @[ blur, saturate ];

CALayer *overlay = [CALayer new];
overlay.backgroundColor = [UIColor colorWithWhite:1 alpha:0.3].CGColor;
overlay.compositeFilter = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterSourceOver];

[layer addSublayer:backdrop];
[layer addSublayer:overlay];
```

## 四、综合应用

最后一步就是打开`-[MTLumaDodgePillView initWithFrame:]`，它会显示复制该特效时MaterialKit需要创建的那些过滤器：

```
CAFilter *const blur = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterGaussianBlur];
CAFilter *const colorBrightness = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterColorBrightness];
CAFilter *const colorSaturate = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterColorSaturate];
```

为了得到每个过滤器的真实值，我们需要使用view debugger暂停执行过程，选择我们添加的某个视图，从右侧的视图或图层区复制具体地址。

[![](https://p2.ssl.qhimg.com/t0105801d5fcf7508dd.png)](https://p2.ssl.qhimg.com/t0105801d5fcf7508dd.png)

现在，我们可以在控制台（console）中使用我们选择的那些地址，将这些地址作为视图以及图层的索引加以使用。

```
(lldb) po 0x7fc81331a8a0
&lt;MTLumaDodgePillView:0x7fc81331a8a0 frame=`{``{`120.5, 107.5`}`, `{`134, 5`}``}` style=white backgroundLuminance=unknown&gt;

(lldb) po ((CALayer *)0x600000226d60).filters
&lt;__NSArrayI 0x60000005e450&gt;(
homeAffordanceBase,
gaussianBlur,
colorBrightness,
colorSaturate
)

(lldb) po [((CALayer *)0x600000226d60).filters[0] valueForKey:@"inputAmount"]
1

(lldb) po [((CALayer *)0x600000226d60).filters[0] valueForKey:@"inputAddWhite"]
0.71
```

你可能会注意到，我们在上面使用了显示类型转换，以调用那些整数的属性，之所以这么做是为了帮助lldb适配这些指针背后对象的具体类型。

找到`-[MTLumaDodgePillView initWithFrame:]`中的所有属性后，我们需要在每个属性上应用`valueForKey:`操作。这个过程有点枯燥，但我实在不想去查找原始的style定义文件（假设具体定义位于某个plist中）。一旦操作完成，只需要使用QuartzCore我们可以重构视图：

```
CAFilter *const homeAffordanceBase = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterHomeAffordanceBase];
UIImage *const lumaDodgeMap = [UIImage imageNamed:@"lumaDodgePillMap" inBundle:[NSBundle bundleForClass:viewClass] compatibleWithTraitCollection:nil];
[homeAffordanceBase setValue:(__bridge id)lumaDodgeMap.CGImage forKey:@"inputColorMap"];
CAFilter *const blurFilter = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterGaussianBlur];
CAFilter *const colorBrightness = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterColorBrightness];
CAFilter *const colorSaturate = [(id)NSClassFromString(@"CAFilter") filterWithType:kCAFilterColorSaturate];

// MTLumaDodgePillViewStyleThin values
[homeAffordanceBase setValue:@0.31 forKey:@"inputAmount"];
[homeAffordanceBase setValue:@0.37275 forKey:@"inputAddWhite"];
[homeAffordanceBase setValue:@0.4 forKey:@"inputOverlayOpacity"];
[blurFilter setValue:@10 forKey:@"inputRadius"];
[blurFilter setValue:@YES forKey:@"inputHardEdges"];
[colorBrightness setValue:@0.06 forKey:@"inputAmount"];
[colorSaturate setValue:@1.15 forKey:@"inputAmount"];

CALayer *layer = [NSClassFromString(@"CABackdropLayer") new];
layer.frame = CGRectInset(self.view.bounds, 100, 100);
layer.filters = @[ homeAffordanceBase, blurFilter, colorSaturate, colorSaturate ];
layer.cornerRadius = 10;
[self.view.layer addSublayer:layer];
```

新的滤镜貌似使用的是`lumaDodgePullMap`图像来映射输入图像，其他方面则直接使用了我们在`UIVisualEffectView`实现代码中看到的那些过滤器。最终结果如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d7b3dcb84f8b8abf.gif)

## 五、总结

希望这篇文章能在逆向工程方面给大家带来更多体验，在Objective-C语言的二进制程序中保留着许多有用的信息，能给逆向工程带来更有趣的体验。如果有什么问题或想法，欢迎通过Twitter随时向<a>@zats</a>反馈。

感谢<a>@warpling</a>、<a>@myell0w</a>以及<a>@shaps</a>在本文成稿过程中给予的帮助。

## 六、拓展阅读
- [Markov Chains with GameplayKit](http://blog.zats.io/2015/08/29/markov-chains-with-gameplaykit/)
- [copy vs strong (retain)](http://blog.zats.io/2015/08/27/copy-vs-retain/)
- [GKRandomDistribution, GKShuffledDistribution and the GKGaussianDistribution](http://blog.zats.io/2015/08/15/randoms/)