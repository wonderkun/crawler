> 原文链接: https://www.anquanke.com//post/id/83658 


# Locky勒索软件潮来袭，请躲避


                                阅读量   
                                **190602**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01aef5e26d3bb7711a.jpg)](https://p4.ssl.qhimg.com/t01aef5e26d3bb7711a.jpg)

**        概述**

        **自2月以来，360威胁情报中心监测到一大波勒索软件潮，国内单位组织陆续开始受到的冲击，公司对外的邮箱收到大量如下携带恶意附件的邮件。**

[![](https://p0.ssl.qhimg.com/t01415a74f16cb77f39.png)](https://p0.ssl.qhimg.com/t01415a74f16cb77f39.png)

        邮件内容大致如下：

[![](https://p2.ssl.qhimg.com/t0164ba354ba0e2a4ad.png)](https://p2.ssl.qhimg.com/t0164ba354ba0e2a4ad.png)

        员工如不小心打开恶意附件，恶意软件会对外连接服务器下载组件，加密系统上的重要文件，要求用户付费解密。

**<br>**

**        样本行为分析**

        邮件附件为只有两个JS脚本的压缩包：

[![](https://p0.ssl.qhimg.com/t01a460521e837bc9c2.png)](https://p0.ssl.qhimg.com/t01a460521e837bc9c2.png)

[![](https://p5.ssl.qhimg.com/t014927050395c2b8a6.png)](https://p5.ssl.qhimg.com/t014927050395c2b8a6.png)

        JS经过混淆，通过分析得知，受害者双击执行JS后创建MSXML2.XMLHTTP对象下载http://vaseline-amar-ujala.in/euwiyr4hdc可执行文件，并通过WScript.Shell对象的run方法启动Locky主进程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014eb1a25aa075dea5.png)

        下载的exe经过大量的混淆处理：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012dd98aa0b9be4ef9.png)

        进程启动后将机器ID写入HKEY_CURRENT_USERSoftwareLockyid，并将用到的加密公钥写入HKEY_CURRENT_USERSoftwareLockypubkey：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019e07395d14104016.png)

[![](https://p4.ssl.qhimg.com/t012233913e4e3c388b.png)](https://p4.ssl.qhimg.com/t012233913e4e3c388b.png)

        随后木马开始遍历目录寻找.xls、.ppt、.doc、.wb2、.jpg、.wav等文件格式，使用RSA加密为Id+哈希.locky文件，并在存在文档得目录下写入恢复指导文档：

[![](https://p0.ssl.qhimg.com/t01dc00b77912e648ca.png)](https://p0.ssl.qhimg.com/t01dc00b77912e648ca.png)

[![](https://p3.ssl.qhimg.com/t01ff1084b7dc37394d.png)](https://p3.ssl.qhimg.com/t01ff1084b7dc37394d.png)

        完成加密后将HKEY_CURRENT_USERSoftwareLockycompleted设置为1，并通过加密的数据告知服务器：

[![](https://p1.ssl.qhimg.com/t01a34d210ae8da7bc0.png)](https://p1.ssl.qhimg.com/t01a34d210ae8da7bc0.png)

 

        如下是部分通信地址列表：

[http://78.40.108.39/main.php](http://78.40.108.39/main.php)

[http://51.255.107.8/main.php](http://51.255.107.8/main.php)

[http://51.255.107.10/main.php](http://51.255.107.10/main.php)

[http://51.254.181.122/main.php](http://51.254.181.122/main.php)

[http://195.64.154.114/main.php](http://195.64.154.114/main.php)

[http://188.127.231.116/main.php](http://188.127.231.116/main.php)

[http://149.202.109.205/main.php](http://149.202.109.205/main.php)

 

        最后将桌面设置为恢复指导图，并弹出恢复指导文档，等待受害者交付赎金：

[![](https://p5.ssl.qhimg.com/t011a97696ee33baf5e.png)](https://p5.ssl.qhimg.com/t011a97696ee33baf5e.png)

**<br>**

**        感染情况与建议**

        根据360威胁情报中心的数据，自3月以来确认中招的用户超过万人，淘宝上甚至已经出现协助代付款解密的服务。在此建议用户不要随意点击来源不明的邮件，目前360安全卫士已对此勒索软件做持续的查杀。

 

**        IOC**

        攻击者用于存放恶意代码的Downloader服务器大都是被攻陷的合法站点，以下是部分列表，请在边界设备上予以阻断。



hxxp://1.casino-engine.ru/engine/core/76tr5rguinml.exe

hxxp://1.casino-engine.ru/modules/images/87yhb54cdfy.exe

hxxp://111.208.4.230:82/1Q2W3E4R5T6Y7U8I9O0P1Z2X3C4V5B/saigonnew.com.vn/system/logs/76tr5rguinml.exe

hxxp://120.52.72.52/biosoftbelgium.com/c3pr90ntcsf0/system/logs/76tr5rguinml.exe

hxxp://120.52.72.57/thuanhshop.com/c3pr90ntcsf0/system/logs/4trf3g45.exe

hxxp://178.33.176.229/ber.exe

hxxp://2.casino-engine.ru/img/multigaminator/4trf3g45.exe

hxxp://50.28.211.199/hdd0/89o8i76u5y4

hxxp://51457642.de.strato-hosting.eu/980k7j6h5

hxxp://academiasuperior.net/wp-includes/rest-api/5h45hg4b

hxxp://accessinvestment.net/4/0vexw3s5

hxxp://aexpress.co/system/logs/086tg7

hxxp://aimsande.com/87yg756f5.exe

hxxp://aksci.net/system/logs/98yhb764d.exe

hxxp://alexkote.ru/wp-content/plugins/87tg7v645c.exe

hxxp://alumaxgroup.in/87yg756f5.exe

hxxp://anro.kiev.ua/vqmod/vqcache/4trf3g45.exe

hxxp://aqarhits.com/system/logs/87tg7v645c.exe

hxxp://ari-ev.com/system/logs/765uy453gt5

hxxp://aroham.com/87yg756f5.exe

hxxp://art-studia-sharm.com.ua/libraries/simplepie/765g473bf34

hxxp://art-wiz.ru/wp-includes/SimplePie/7ygvtyvb7niim.exe

hxxp://astralia.ro/08o76g445g

hxxp://azshop24.com.vn/system/logs/87tg7v645c.exe

hxxp://baiya.org/image/templates/7ygvtyvb7niim.exe

hxxp://behrozan.ir/system/logs/7t6f65g.exe

hxxp://beltshoesnmore.com/system/logs/87yhb54cdfy.exe

hxxp://besttec-cg.com/89ok8jhg

hxxp://bindulin.by/system/logs/7ygvtyvb7niim.exe

hxxp://biomir.ajanslive.com/system/logs/78tgh76.exe

hxxp://biosoftbelgium.com/system/logs/76tr5rguinml.exe

hxxp://browardcountystore.com/system/cache/223

hxxp://buyfuntees.com/system/logs/7t6f65g.exe

hxxp://c001456.aaa.ididp.com/system/logs/87yg756f5.exe

hxxp://casewerkz.demowebsite.net/system/logs/87yhb54cdfy.exe

hxxp://cazasports.com/system/logs/uy78hn654e.exe

hxxp://ccac3323.com.sapo.pt/0y7bf3r

hxxp://cherryuk.co.uk/system/logs/uy78hn654e.exe

hxxp://chinhuanoithat.com/system/logs/uy78hn654e.exe

hxxp://clubxtoys.com/system/logs/lkj87h.exe

hxxp://cocowashi.com/system/logs/76tr5rguinml.exe

hxxp://creditwallet.net/87yg756f5.exe

hxxp://croqqer.org/wp-content/uploads/5h45hg4b

hxxp://cuagonhaviet.com.vn/system/logs/lkj87h.exe

hxxp://cyberbuh.pp.ua/97kh65gh5

hxxp://demo.essarinfotech.net/87yg756f5.exe

hxxp://demo.rublemag.ru/system/logs/87yhb54cdfy.exe

hxxp://demo2.master-pro.biz/modules/payments/76tr5rguinml.exe

hxxp://demo2.master-pro.biz/plugins/markitup/4trf3g45.exe

hxxp://dgcustomgraphics.com/system/logs/98yhb764d.exe

hxxp://dolcevita-ykt.ru/system/logs/uy78hn654e.exe

hxxp://dommediciny.ru/system/logs/76h5gf43wg54

hxxp://donutes.33499.info/system/logs/87yhb54cdfy.exe

hxxp://dropshipaanbod.nl/system/logs/uy78hn654e.exe

hxxp://dsignshop.com.au/system/logs/87tg7v645c.exe

hxxp://effone.com/js/playstation4.exe

hxxp://eiadmeodeda.securalive.ca/8fjvimkel1/c987ah8j9ei1.php

hxxp://e-journal.respati.ac.id/8y74hfb

hxxp://electime.com/wp-content/themes/765g473bf34

hxxp://elogistic.ir/wp-admin/network/87hg8n54

hxxp://emotos.ru/admin/model/87yhb54cdfy.exe

hxxp://escortbayan.xelionphonesystem.com/wp-content/plugins/hello123/89h8btyfde445.exe

hxxp://estudiomatera.com.ar/763fdvf

hxxp://fashion-girl.od.ua/catalog/controller/87hg8n54

hxxp://fb7707vd.bget.ru/admin/language/4trf3g45.exe

hxxp://fibrefamily.ru/system/logs/87tg7v645c.exe

hxxp://fkaouane.free.fr/67uh54gb4

hxxp://flaxxup.com/87yg756f5.exe

hxxp://for-sale.pk/system/logs/87yhb54cdfy.exe

hxxp://fortyseven.com.ar/system/logs/7t6f65g.exe

hxxp://g200.qdesign.vn/system/logs/87yhb54cdfy.exe

hxxp://galit-law.co.il/32tguynjk

hxxp://gargsons.com/87yg756f5.exe

hxxp://giveitallhereqq.com/69.exe

hxxp://giveitallhereqq.com/80.exe

hxxp://giveitalltheresqq.com/69.exe

hxxp://giveitalltheresqq.com/80.exe

hxxp://gladilki.bohush.ru/system/library/a.exe

hxxp://glslindia.com/87yg756f5.exe

hxxp://gwentpressurewashers.com/system/logs/7ygvtyvb7niim.exe

hxxp://heenaz.in/system/logs/98yhb764d.exe

hxxp://hellomississmithqq.com/69.exe

hxxp://hellomississmithqq.com/80.exe

hxxp://het-havenhuis.nl/099oj6hg

hxxp://hipnotixx.com/27h8n

hxxp://hitronic.org/system/logs/76tr5rguinml.exe

hxxp://hkhc-shop.lms.hk/system/logs/87yg7g

hxxp://howisittomorrowff.com/69.exe

hxxp://hppl.net/87yg756f5.exe

hxxp://ihsanind.com/system/logs/87jhg44g5

hxxp://imgointoeatnowcc.com/69.exe

hxxp://imgointoeatnowcc.com/80.exe

hxxp://imgointoeatnowcc.com/80.exe

hxxp://imperiovintage.com.br/system/logs/76tr5rguinml.exe

hxxp://indianexporthouse.eu/system/logs/uy78hn654e.exe

hxxp://iperfume.co.il/system/logs/4trf3g45.exe

hxxp://ipovareshka.ru/system/logs/76tr5rguinml.exe

hxxp://italco.com.ua/system/logs/98yhb764d.exe

hxxp://iwear.md/system/logs/7t6f65g.exe

hxxp://izzy-cars.nl/9uj8n76b5.exe

hxp://jewellery.jagodesh.com/system/logs/iu8y7g6b

hxxp://jldoptics.com/system/logs/87tg7v645c.exe

hxxp://joecockerhereqq.com/69.exe

hxxp://joecockerhereqq.com/80.exe

hxxp://jorgecodas.com/76t2gr345

hxxp://kiddyshop.kiev.ua/image/data/87tg7v645c.exe

hxxp://kidtuning.ro/7r5fyf6

hxxp://kievelectric.kiev.ua/art/media/87tg7v645c.exe

hxxp://klariss.cz/87yg756f5.exe

hxxp://kokoko.himegimi.jp/54g4

hxxp://komplektik.com/system/logs/76tr5rguinml.exe

hxxp://lahmar.choukri.perso.neuf.fr/78hg4wg

hxxp://lampusorotmurah.com/system/logs/78tgh76.exe

hxxp://lapdatcamerachatluongcao.com/system/logs/uy78hn654e.exe

hxxp://leaderjewelleryco.com/admin/controller/87yhb54cdfy.exe

hxxp://lhs-mhs.org/9uj8n76b5.exe

hxxp://lightsroom.ru/system/logs/87tg7v645c.exe

hxxp://liquor1.slvtechnologies.com/system/logs/7ygvtyvb7niim.exe

hxxp://livewireradio.net/wp-admin/js/765g473bf34

hxxp://magic-beauty.com.ua/system/logs/98yhb764d.exe

hxxp://mail-dedmoroz.com.ua/adminka/templ/7ygvtyvb7niim.exe

hxxp://mansolution.in.th/system/logs/7ygvtyvb7niim.exe

hxxp://massage-himmel.de/978yhen2

hxxp://maxbeauty.dp.ua/administrator/manifests/765g473bf34

hxxp://maybridalsash.com/system/cache/111

hxxp://mercadohiper.com.br/system/logs/uy78hn654e.exe

hxxp://ministerepuissancejesus.com/o097jhg4g5

hxxp://mobile-house.be/system/logs/98yhb764d.exe

hxxp://myonlinedeals.pk/system/logs/43d5f67n8

hxxp://myphampro.com/system/logs/87yhb54cdfy.exe

hxxp://nagrobkipelplin.conceptreklamy.pl/modules/mod_wrapper/4trf3g45.exe

hxxp://ncrweb.in/system/logs/7t6f65g.exe

hxxp://newleaf.org.in/87yg756f5.exe

hxxp://nguoitieudungthongthai.com/system/logs/987i6u5y4t

hxxp://nhinh.com/system/logs/uy78hn654e.exe

hxxp://nobilitas.cz/0954t4h45

hxxp://nro.gov.sd/23r35y44y5

hxxp://nypizza.ru/system/logs/7ygvtyvb7niim.exe

hxxp://ohammam.fr/system/logs/23f3rf33.exe

hxxp://ohbelleza.linkium.mx/system/logs/87yhb54cdfy.exe

hxxp://ohellograndpaqq.com/69.exe

hxxp://ohellograndpaqq.com/80.exe

hxxp://ohelloguyff.com/70.exe

hxxp://ohelloguyqq.com/70.exe

hxxp://ohelloguyzzqq.com/85.exe

hxxp://onsancompany.com/system/logs/uy78hn654e.exe

hxxp://ozono.org.es/k7j6h5gf

hxxp://pacificgiftcards.com/3/67t54cetvy

hxxp://parturiencies3f9.besaba.com/76t2gr345

hxxp://perfumy_alice.republika.pl/08h867g5

hxxp://peterdickem.com/87745g

hxxp://phatfx.net/98h8n23r23

hxxp://phongsachviettech.com/system/logs/98yg7b

hxxp://planetarchery.com.au/system/logs/q32r45g54

hxxp://printisimo.ru/image/cache/7ygvtyvb7niim.exe

hxxp://ptunited.net/system/logs/87tg7v645c.exe

hxxp://pugmahons.com/~pugmahons/56er5f6g7b

hxxp://realvacantcolony.tradersnetwork.co/97adguwod/08h13rfi982y.php

hxxp://regentsanctionbisexual.isupplementscanada.com/97adguwod/08h13rfi982y.php

hxxp://rem.az/system/logs/lkj87h.exe

hxxp://risetravel.net/wp-includes/theme-compat/765g473bf34

hxxp://rmdszms.ro/2/87yv5cds

hxxp://saabvolvo.com.ua/system/logs/7ygvtyvb7niim.exe

hxxp://saachi.co/system/logs/43ghy8n

hxxp://sabriduman.com/wp-content/plugins/hello123/89h8btyfde445.exe

hxxp://saigonnew.com.vn/system/logs/76tr5rguinml.exe

hxxp://sales-teleselling.eu.org/wp-includes/fonts/5h45hg4b

hxxp://scorpyofilms.com/67j5h5h4

hxxp://scs-smesi.ru/published/PD/87tg7v645c.exe

hxxp://shapes.com.pk/system/logs/87tg7v645c.exe

hxxp://shoescorner.gr/system/logs/76tr5rguinml.exe

hxxp://shofukai.web.fc2.com/23rt54y56

hxxp://shop.celiodent.com/system/cache/111

hxxp://shopphpmvc.e-groups.vn/system/logs/lkj87h.exe

hxxp://shopthoitrangphukien.com/system/logs/7ygvtyvb7niim.exe

hxxp://sigmahardware.com.my/system/logs/7ygvtyvb7niim.exe

hxxp://silvermarket.gr/system/logs/78tgh76.exe

hxxp://sitemar.ro/5/92buyv5

hxxp://sm1.by/vqmod/xml/76tr5rguinml.exe

hxxp://smeja.de/i876jh556h

hxxp://smokediscount.de/786u5h

hxxp://snosto.com/wp-admin/includes/i75rg456

hxxp://softcrk.com/system/logs/4trf3g45.exe

hxxp://softworksbd.com/73tgbf334

hxxp://solucionesdubai.com.ve/system/logs/uy78hn654e.exe

hxxp://sribinayakelectricals.com/system/logs/78tgh76.exe

hxxp://srv35613.ht-test.ru/storage/plugins/76tr5rguinml.exe

hxxp://stalu.sk/43dfg7hy

hxxp://stepsaweb.com/system/logs/uy78hn654e.exe

hxxp://stopmeagency.free.fr/9uj8n76b5.exe

hxxp://storageinbath.co.uk/78jh5h

hxxp://store.suhaskhamkar.in/system/logs/78tgh76.exe

hxxp://sub4.gustoitalia.ru/system/logs/87tg7v645c.exe

hxxp://superiorelectricmotors.com/wp-content/plugins/hello123/89h8btyfde445.exe

hxxp://supply-division.dk/system/logs/76tr5rguinml.exe

hxxp://surfcash.7u.cz/0o9k7jh55

hxxp://surgitek.co.uk/system/logs/98yt

hxxp://surprise.co.in/system/logs/87tg7v645c.exe

hxxp://svetluchok.com.ua/admin/images/7ygvtyvb7niim.exe

hxxp://szkoleniasluzb.pl/67j5hg

hxxp://tcpos.com.vn/system/logs/56y4g45gh45h

hxxp://tekstil-world.ru/vqmod/install/7ygvtyvb7niim.exe

hxxp://test.sharmx.com.ua/sdideep/87hg8n54

hxxp://texfibre.eu/system/logs/87tg7v645c.exe

hxxp://thaihost.biz/bestylethai.com/43t3gh4

hxxp://theskcreativearts.com/45tg

hxxp://thewhitemug.co.uk/system/logs/4trf3g45.exe

hxxp://thietbianninhngocphuoc.com/system/logs/98yhb764d.exe

hxxp://thietbicokhi.com.vn/system/logs/7ygvtyvb7niim.exe

hxxp://thisisitsqq.com/69.exe

hxxp://thisisitsqq.com/80.exe

hxxp://thuanhshop.com/system/logs/4trf3g45.exe

hxxp://tianshilive.ru/vqmod/xml/87yhb54cdfy.exe

hxxp://tomkinshop.net/system/logs/87yhb54cdfy.exe

hxxp://torgtehnik.ru/system/cache/…/1.exe

hxxp://tracks4africa.li/43f

hxxp://tradesolutions.me.uk/8i76

hxxp://tramps-ike.gr/8i67uy4g

hxxp://tratancuongthainguyen.com/v4v5g45hg.exe

hxxp://trieugiatrang.net/image/cache/87yhb54cdfy.exe

hxxp://trimchic.co.uk/system/logs/lkj87h.exe

hxxp://tuning.com.mx/v4v5g45hg.exe

hxxp://u1847.netangels.ru/system/smsgate/7ygvtyvb7niim.exe

hxxp://ubermensch.altervista.org/system/logs/87yhb54cdfy.exe

hxxp://vaanifashion.com/system/logs/uy78hn654e.exe

hxxp://vacationinbath.co.uk/v4v5g45hg.exe

hxxp://vacationinbath.com/v4v5g45hg.exe

hxxp://valerieannefashions.co.uk/v4v5g45hg.exe

hxxp://vartashakti.com/v4v5g45hg.exe

hxxp://vfwuc.eu.org/wp-content/uploads/5h45hg4b

hxxp://vgp3.vitebsk.by/6/98yh8bb

hxxp://vikasartsjodhpur.com/v4v5g45hg.exe

hxxp://vip-creme.de/v4v5g45hg.exe

hxxp://vip-shape.de/v4v5g45hg.exe

hxxp://vital4age.de/v4v5g45hg.exe

hxxp://vital4age.eu/v4v5g45hg.exe

hxxp://washitallawayff.com/69.exe

hxxp://washitallawayff.com/80.exe

hxxp://webmail.p55.be/v4v5g45hg.exe

hxxp://wechselkur.de/v4v5g45hg.exe

hxxp://whatskv.com/v4v5g45hg.exe

hxxp://winjoytechnologies.com/v4v5g45hg.exe

hxxp://wireless-sync.com/system/cache/111

hxxp://workplace-communication.eu.org/wp-includes/pomo/5h45hg4b

hxxp://www.aebnworld.com/98o7kj56h

hxxp://www.aggiesaquariums.com.au/wp-includes/y78hiuok

hxxp://www.almraah.com/wp-content/uploads/y78hiuok

hxxp://www.avdanrenault.com/system/logs/4trf3g45.exe

hxxp://www.dentiera-rotta.it/files/Fedex/fedex.exe

hxxp://www.ekowen.sk/09y8j

hxxp://www.findtube.gr/templates/atomic/js/111.exe

hxxp://www.fotoleonia.it/files/sample.exe

hxxp://www.freeadultcontent.us/98o7kj56h

hxxp://www.freepussyshow.com/9oi654gh3

hxxp://www.gruposdemediosrrr.com/9oi654gh3

hxxp://www.gw-fs.co.uk/873y4g7bf3

hxxp://www.houseman.cz/files/10003c.exe

hxxp://www.istruiscus.it/7643grb

hxxp://www.kidshealingcrohnsandcolitis.com/8y7hybigv

hxxp://www.kidshealingcrohnsandcolitis.org/8y7hybigv

hxxp://www.koinerestaurant.com/parallax/piatti/promt.exe

hxxp://www.livegirlshow.com/8i5ju4g34

hxxp://www.liveshowgirl.com/8i5ju4g34

hxxp://www.momstav.com/087hg67

hxxp://www.myxxxlinks.com/4ggh45yh45

hxxp://www.myxxxlinks.com:20480/4ggh45yh45

hxxp://www.nenitasthumbs.com/4ggh45yh45

hxxp://www.nevjegydesign.hu/0k6j6n4h4

hxxp://www.nevjegyportal.hu/0k6j6n4h4

hxxp://www.notebooktable.ru/system/logs/7ygvtyvb7niim.exe

hxxp://www.promumedical.com/system/logs/87tg7v645c.exe

hxxp://www.silko.ir/k8j5h

hxxp://www.souqaqonline.com/system/logs/87tg7v645c.exe

hxxp://www.tech-filter.ru/system/logs/78tgh76.exe

hxxp://www.toolsavenue.com/system/cache/87yhb54cdfy.exe

hxxp://www.trasachthainguyen.com/0l9k7j6

hxxp://www.tuttiesauriti.org/wp-content/plugins/hello123/89h8btyfde445.exe

hxxp://www.vtipnetriko.cz/9oi86j5hg4

hxxp://xn--80ahetikodul.xn--p1ai/system/logs/4trf3g45.exe

hxxp://xn--b1afonddk2l.xn--p1ai/system/logs/7t6f65g.exe

hxxp://yander.by/system/logs/uy78hn654e.exe

hxxp://zarabotoknasayte.zz.mu/7/sh87hg5v4
