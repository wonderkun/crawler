> 原文链接: https://www.anquanke.com//post/id/188575 


# NSO间谍软件：你们要人权，我们要人命


                                阅读量   
                                **585320**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t0125c0bd289e8be791.jpg)](https://p2.ssl.qhimg.com/t0125c0bd289e8be791.jpg)



天下人权斗士苦NSO久矣，今天我们来说一说杀人不见血的国际监控组织NSO。

来自以色列的NSO集团，是世界上最秘密的监视技术制造商，也是令人闻风丧胆的“网络军火商”。它最得意的网络武器Pegasus，就是一款可以监控目标人物的手机间谍软件。

攻击者首先会构造一个包含漏洞利用的特制链接发送到目标人物手机中，一旦目标人物点击该链接，就会实现一系列的0-day攻击，在隐蔽和无权限需要的情况下安装恶意软件，最终攻击者就能控制该手机。

据统计，Pegasus被用在全球至少45个国家，至少10个攻击组织在进行着活跃的跨境入侵监控行为。

更瘆人的是，别人家的软件要钱，NSO家的软件要命。

在2016年，阿联酋著名人权捍卫者艾哈迈德·曼索尔（Ahmed Mansoor）联系到Citizen Lab组织，分享了自己手机中包含Pegasus的消息，而经Lookout公司研究发现，最终以报告的形式，向世人揭露了Pegasus手机监测软件的丑陋面容。

这款软件主要进行监测与攻击，而在针对阿联酋人权维护者Ahmed Mansoor进行针对性攻击。

不止阿联酋，远在墨西哥的人权斗士同样如此。

2017年，墨西哥调查记者Javier Valdez被人从车内拖出，连射12枪，倒在了自己一手创办的《Riodoc》周刊编辑部附近。

枪击案前，Javier Valdez 和同事们收到了精心设计的短信，手机在无感知的情况下被安装了Pegasus软件。从此，手机像打开了大闸，各种私人邮件、敏感信息、图片视频源源不断被送到犯罪分子手中，一场惨剧由此酿成。

在 Javier被谋杀一周之后，他那同为记者的妻子也成为 Pegasus 恶意软件的攻击目标，以及二十多个记者同事。

[![](https://p4.ssl.qhimg.com/t016fc7f6d0bfc9edb7.jpg)](https://p4.ssl.qhimg.com/t016fc7f6d0bfc9edb7.jpg)

Pegasus杀红了眼，沙特政府表示这很NSO，反手就从他们那儿购买了服务。

到了2018年，沙特的异见人士卡舒吉惨遭肢解，血腥程度让全球震惊了。这位记者之所以能在短短十几分钟时间，以极其残忍暴力的方式，撒手人寰，同样与Pegasus恶意软件密切相关。

原来，手机中暗藏的毒瘤Pegasus ，暴露了这位记者的全部行踪，也让15人的暗杀小组有可乘之机，活活将卡舒吉割头、断指……完全肢解，上演人间惨剧。

[![](https://p2.ssl.qhimg.com/t01ecc440e52974af26.jpg)](https://p2.ssl.qhimg.com/t01ecc440e52974af26.jpg)

从阿联酋、墨西哥到沙特，Pegasus带来的屠杀远没有结束。2019，“杀人软件”Pegasus再次在摩洛哥露头，有机构曝光摩洛哥知名人权捍卫者（HRD）马蒂·蒙吉布和Abdessadak El Bouchattaoui遭到NSO集团间谍软件的定向攻击，且极可能是此前一次次上演屠杀风波的Pegasus软件。

曝光内容中指出，此次攻击，最早可追述到2017年10月，由于目标更侧重于缩小两位人权捍卫者开展工作的空间，让他们“免于一死”，不过后续是否会受到生命威胁，没有人敢断言。



## 短信钓鱼攻击细节

我们发现，马蒂二人遭受的是恶意短信攻击。

这些短信包含着指向NSO Group的Pegasus间谍软件网站的恶意链接，如果点击了短信中的链接，那么他们手机就会被强行安装Pegasus。

像“澳门博彩”一样烦人的垃圾短信，源源不断地发到马蒂二人手机，而且还都是一模一样的文本内容，是不是感觉像吞了苍蝇一样恶心？

那就对了，攻击者“贴心”地附上停止接收的办法：点击（恶意）链接。

二人表示压力山大，换作是我也得慌得一批。

## 网络劫持攻击细节

因为Safari的浏览历史记录都存储在本地的SQLite数据库中，这些数据不仅保留了特定链接的单独访问记录，还记录了其初始访问和最终访问的记录。

所以我们能够重现攻击过程中的网页重定向和按时间排序的网页请求。

7月22日，马蒂打开Safari浏览器，并在地址栏中手动输入“yahoo.fr”访问雅虎，然后Safari首先与http：// yahoo.fr 进行未加密的连接。

通常情况，雅虎会立即将浏览器重定向到其默认的TLS安全站点https://fr.yahoo.com/。但是，马蒂的浏览器历史记录显示，该页面显示不到3毫秒，就重定向到非常可疑的网站：

hxxps：//bun54l2b67.get1tn0w.free247downloads.com：30495/szev4hz

在这次访问之后，又重定向到了当前域名另外一个不同参数的地址：

hxxps：//bun54l2b67.get1tn0w.free247downloads.com：30495 / szev4hz＃048634787343287485982474853012724998054718494423286

注意，仅当访问未加密传输的http连接时，才可以进行这种重定向，例如http：//yahoo.fr。

大约30秒后，马蒂再次访问Yahoo，不过这一次是在Google上搜索“yahoo.fr mail ”，他被定向到了正确地址，然后他在该页面阅读电子邮件。

我们认为，这是典型的网络被劫持的表现，通常这类攻击被称为“中间人”攻击。

攻击者已经控制了目标的网络连接，可以监视和劫持目标的网络请求及流量，从而任意更改目标设备的网络访问行为，例如可以将设备重定位到恶意网站，并且整个过程无需受害者进行任何交互操作。

这样的攻击可能发生在和目标设备相连的任何网络节点。在这种情况下，由于目标设备是iPhone，仅通过移动网络连接，因此最有可能的攻击节点可能是放置在目标附近的恶意移动基站，或者可能移动运营商的核心网络基础设施被控制后启用这种类型的攻击。

除此以外，由于此攻击是通过网络“无感知”执行的，而不是通过恶意短信和社会工程学执行的，因此它避免任何用户交互，对受害者几乎不可见踪迹、极难发现。

换言之，当马蒂访问雅虎时，他的电话可能受到了中间人攻击，Safari的网络访问被自动重定向到恶意软件的服务器，继而试图静默安装间谍软件。

对设备的进一步分析，发现了在2019年3月至2019年7月之间，间谍软件Pegasus至少对马蒂进行了四次类似的中间人攻击尝试。（注意：每次尝试后，重定向的URL随不同的子域，端口号和URI都会略有变化。）并且很显然，至少成功进行了一次中间人攻击。

还有更鸡贼的，大家都知道，每当应用程序崩溃时，iPhone都会存储一个日志文件，跟踪崩溃的确切原因，这些崩溃日志可以无限期地存储在手机上。

而对马蒂的手机分析发现：有一次，在Safari重定向发生后的几秒钟，所有这些崩溃文件咔咔咔全都被清除。这很可能是间谍软件故意执行的清除操作，目的是清除漏洞利用的痕迹，然后执行攻击并强制重启手机。

[![](https://p4.ssl.qhimg.com/t017d0c205c7c80901c.jpg)](https://p4.ssl.qhimg.com/t017d0c205c7c80901c.jpg)

分析发现，马蒂收到的恶意短信中主要包含以下3个域名:
<td valign="top" width="217">Stopsms.biz</td><td valign="top" width="314"></td>
<td valign="top" width="268">infospress .com</td><td valign="top" width="314"></td>
<td valign="top" width="268">Hmizat.co</td><td valign="top" width="314">该域名似乎假冒了摩洛哥的电子商务公司Hmizate</td>

如果以为域名就这几个，抱歉了，NSO集团发布的恶意域名六百个起步，并且与一些国家/地区强相关。国际黑客组织不都这样吗？一般不出手，出手不一般。

例如，使用国家代码（例如“zm”）的域名很可能是与赞比亚相关，并以“zm”作为后缀或前缀来突出显示。
<td valign="top" width="624">Onlineshopzm.com</td>
<td valign="top" width="624">Zednewszm.com</td>
<td valign="top" width="624">zm-banks.com</td>
<td valign="top" width="624">zm-weather.com</td>

例如刚果：
<td valign="top" width="220">Nothernkivu.com</td><td valign="top" width="343">刚果民主共和国的地区北基伍</td>

或与非洲地区相关：
<td valign="top" width="616">Afriquenouvelle.com</td>
<td valign="top" width="616">Allafricaninfo.com</td>

我们还发现了许多域名，这些域可能是与俄语国家相关，例如：
<td valign="top" width="218">centrasia-news.com</td><td valign="top" width="449">假冒新闻网站（http://ca-news.org/），在反对派激进分子中很受欢迎</td>
<td valign="top" width="218">Mystulchik.com</td><td valign="top" width="449"></td>
<td valign="top" width="218">odnoklass-profile.com</td><td valign="top" width="449">“Odnoklassniki”是在俄语国家中流行的社交媒体网络</td>
<td valign="top" width="218">sputnik-news.info</td><td valign="top" width="449">人造卫星新闻（https://sputniknews.com）</td>

许多域名则很可能与哈萨克斯坦相关
<td valign="top" width="262">Tengrinews.co</td><td valign="top" width="320"></td>
<td valign="top" width="262">Sergek.info</td><td valign="top" width="320">sergek.kz是哈萨克斯坦的视频监控系统</td>
<td valign="top" width="211">egov-sergek.info</td><td valign="top" width="320">Egov.kz是哈萨克斯坦的电子政府网站</td>
<td valign="top" width="262">egov-segek.info</td><td valign="top" width="320"></td>
<td valign="top" width="262">Mykaspi.com</td><td valign="top" width="320">来自哈萨克斯坦的银行机构</td>
<td valign="top" width="262">kaspi-payment.com</td><td valign="top" width="320">来自哈萨克斯坦的银行机构</td>

而这些域名使用了拉脱维亚语，很可能针对的拉脱维亚的目标：
<td valign="top" width="221">e-sveiciens.com</td><td valign="top" width="310">拉脱维亚语的“电子问候”</td>
<td valign="top" width="272">Klientuserviss.com</td><td valign="top" width="310">拉脱维亚的“客户服务”</td>
<td valign="top" width="272">Kurjerserviss.com</td><td valign="top" width="310">拉脱维亚的“客户服务”</td>
<td valign="top" width="272">Reklamas.info</td><td valign="top" width="310">拉脱维亚语中的“广告”</td>

以下域名可能在匈牙利使用：
<td valign="top" width="314">Legyelvodas.com</td><td valign="top" width="310">该匈牙利语链接可能与沃达丰（Vodafone）相关</td>

还更多以假乱真的新闻网站域名，我都有点相信是真的：
<td valign="top" width="218">Theastafrican.com</td><td valign="top" width="449">假冒肯尼亚报纸媒体（http://www.theeastafrican.co.ke/）</td>
<td valign="top" width="218">Ajelnews.net</td><td valign="top" width="449">假冒沙特阿拉伯新闻网站Ajel News（http://ajel.sa）</td>
<td valign="top" width="218">akhbara-aalawsat.com</td><td valign="top" width="449">假冒阿拉伯新闻网站Asharq Al-Awsat（https://aawsat.com）</td>
<td valign="top" width="218">centrasia-news.com</td><td valign="top" width="449">假冒中亚新闻（http://ca-news.org/），在反对派激进分子中很受欢迎</td>
<td valign="top" width="218">Tengrinews.co</td><td valign="top" width="449">假冒哈萨克斯坦新闻网站Tengri News（http://tengrinews.kz）</td>
<td valign="top" width="218">akhbar-arabia.com</td><td valign="top" width="449">可能假冒阿拉伯新闻网站Akhbar Arabia（https://akhbararabia.net/）</td>
<td valign="top" width="218">gulfnews.info</td><td valign="top" width="449">可能假冒海湾新闻（https://gulfnews.com）</td>
<td valign="top" width="218">eltiempo-news.com</td><td valign="top" width="449">假冒哥伦比亚报纸El Tiempo（https://eltiempo.com）</td>
<td valign="top" width="218">sputnik-news.info</td><td valign="top" width="449">人造卫星新闻（https://sputniknews.com）</td>



## 零日反思

不只屠杀，更是网络安全“核威胁”

去年同期，CitizenLab（公民实验室）指出，在全球范围内共有174人被公开报道受到了NSO间谍软件的侵害，而这只是已知的人数，当前被攻击而不自知的受害者也大有人在。

尼莫拉说：

他们追杀犹太人，我没有说话——因为我不是犹太人；

最后他们奔我而来，却再也没有人站起来为我说话了。

最终，NSO集团制造的“网络炸弹”，会不会威胁到每一个人。

零日情报局编辑

微信公众号：lingriqingbaoju

参考资料：

AMNESTY《摩洛哥：以NSO Group的间谍软件为目标的人权维护者》《国际特赦组织在NSO推动的运动目标中》
