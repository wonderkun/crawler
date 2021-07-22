> 原文链接: https://www.anquanke.com//post/id/209772 


# 减轻对旧版Web应用程序的SQL注入攻击


                                阅读量   
                                **138705**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Rasoul Jahanshahi,Adam Doupé,Manuel Egele，文章来源：adamdoupe.com
                                <br>原文地址：[https://adamdoupe.com/publications/asiaccs20-sqlblock.pdf](https://adamdoupe.com/publications/asiaccs20-sqlblock.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01a3d822e9051579aa.png)](https://p3.ssl.qhimg.com/t01a3d822e9051579aa.png)



SQL注入（SQLi）攻击对Web应用程序的安全性构成了重大威胁。现有方法不支持面向对象的编程，这使这些方法无法保护诸如Wordpress，Joomla或Drupal之类的Web应用程序免受SQLi攻击。

为PHP Web应用程序提出了一种新颖的混合静态-动态分析，该分析限制了每个PHP函数用于访问数据库的能力。工具SQLBlock将Web应用程序中易受攻击的PHP函数的攻击面减少为一组查询描述符，这些描述符说明了PHP函数的良性功能。SQLBlock实现是开源的，可从[https://www.github.com/BUseclab/SQLBlock](https://www.github.com/BUseclab/SQLBlock) 获得。此外，提供了五个Docker容器，其中包括在评估中使用的总共11个易受攻击的PHP Web应用程序和插件。

将SQLBlock实现为MySQL和PHP的插件，本文方法不需要对Web应用程序进行任何修改。对Wordpress、Joomla、Drupal、Magento及其插件中的11个SQLi漏洞评估了SQLBlock，证明了SQLBlock可以以可忽略的性能开销成功地阻止了所有11种SQLi漏洞（即在负载很重的Web服务器上最多3％）



## 0x01 Introduction

诸如社交网络，新闻，在线商店和金融服务之类的服务的用户数量不断增长，使得这些服务成为攻击者诱人的敏感信息来源。赛门铁克最近的报告显示，从2017年到2018年，Web攻击增加了56％。 SQLi是一种代码注入攻击，攻击者旨在在数据库上执行任意SQL查询。 2018年，在前四大最受欢迎的Web应用程序（即Wordpress，Joomla，Drupal和Magento）中发现的SQLi漏洞数量比上一年增加了267％。

在确定SQLi漏洞和防御Web应用程序上的SQLi攻击方面进行了大量研究。建议的方法使用了各种技术，例如静态分析，动态分析或静态-动态分析的混合。尽管静态分析方法很有希望，但静态分析无法确定输入清理是否正确执行。如果清理功能未正确清理用户输入，则仍可能发生SQLi攻击。

此外，用于在PHP Web应用程序中查找SQLi漏洞的现有静态分析方法不支持面向对象编程（OOP）代码。静态分析中的此类缺陷使诸如Wordpress，Joomla和Drupal之类的Web应用程序中未检测到SQLi漏洞，超过40％的活动网站正在使用它们。

先前的动态分析使用污点分析和查询分析树的比较来检测Web应用程序上的SQLi攻击。这种动态分析遵循对SQLi攻击的不完整定义，其中SQLi攻击总是会更改SQL查询的语法结构。概要文件（Profile）是良性发出的SQL查询的分析树与发出查询的PHP函数之间的映射。用这种方法创建的概要文件太粗糙了，特别是现代和复杂的Web应用程序（例如Drupal和Joomla）定义了执行所有数据库操作的数据库API。

数据库API使用封装原理创建SQL查询，该封装原理允许本地函数在不将SQL查询作为参数传递的情况下向数据库发出SQL查询。在这种情况下，现有方法会将SQL查询映射到数据库API中的功能，而不是映射到使用数据库API与数据库进行通信的功能。因此，现有方法创建了一个粗粒度的映射，可以使攻击者执行模仿SQLi攻击。

SEPTIC是一种阻止数据库内部SQLi攻击的工具。在训练模式下，SEPTIC记录一个概要文件，该概要文件将良性发出的SQL查询的解析树映射到标识符。 SEPTIC在mysql和mysqli中生成标识符； PHP中的两个数据库扩展，用于与MySQL数据库通信。该标识符是从PHP调用堆栈推断出来的，该调用堆栈发出了对mysql或mysqli API中的一种方法的调用，该方法用于对数据库执行SQL查询（例如mysql_query）。标识符是PHP调用栈中将SQL查询作为参数传递的一系列函数。在强制模式下，SEPTIC根据在训练模式下获得的概要文件检查SQL查询的解析树。 SEPTIC的设计有两个未解决的挑战：

（i）SQL查询的分析树与概要文件的严格比较导致SEPTIC拒绝了一系列动态但良性的SQL查询，从而导致误报。

（ii）SEPTIC概要文件的粗粒度映射使攻击者能够成功执行模仿SQLi攻击。在SEPTIC中创建标识符的方法没有考虑到Web应用程序不一定将SQL查询作为参数的事实。结果，SEPTIC将SQL查询分配给数据库API中的一小部分函数作为标识符。

评估了SEPTIC针对Drupal中的Drupalgeddon漏洞的保护模型，Drupal中的数据库API使用封装概念，这意味着Drupal的函数不会将SQL查询作为参数传递给数据库API。因此，SEPTIC将所有发出的SQL查询映射到数据库API中相同的功能序列，而不是通过数据库API与数据库交互的功能。在训练模式下，SEPTIC通过将所有接收到的SQL查询映射到单个标识符来创建其概要文件。概要文件中的这种映射意味着与Drupal中的数据库通信的任何功能都可以在SEPTIC的概要文件中发出所有SQL查询。例如，攻击者可以在SEPTIC存在的情况下利用Drupalgeddon漏洞，并使用登录功能发出SQL查询以创建管理员用户。

考虑到现有防御PHP Web应用程序的SQLi攻击的挑战和开放性问题，提出了一种新颖的混合静态-动态分析及其实现SQLBlock，以防御OOP Web应用程序免受SQLi攻击。 SQLBlock包含四个步骤，以保护Web应用程序免受SQLi攻击。第一步，SQLBlock通过单元测试或Web应用程序的良性浏览收集良性输入，并在发出的SQL查询与发出查询的函数之间创建映射。静态分析对于准确确定数据库API并随后确定使用该API与数据库正确通信的PHP函数是必需的。在下一步中，SQLBlock在训练模式下基于Web应用程序中每个功能发出的查询来创建概要文件。

SQLBlock中的概要文件是发出SQL查询的功能与描述SQL查询的良性功能的查询描述符之间的映射。在最后一步中，SQLBlock在数据库内部强制执行概要文件，以防止在运行时执行任何与概要文件不匹配的SQL查询。根据最流行的四个真实世界Web应用程序Wordpress，Drupal，Joomla，Magento及其插件中的11个已知SQLi漏洞对系统进行评估。 SQLBlock可以抵御所有SQLi攻击，而SEPTIC只能抵御数据集中的四种SQLi攻击。



## 0x02 Background

在本节中概述了PHP中的面向对象程序命名以及用于与MySQL数据库通信的PHP扩展，之后讨论MySQL及其插件架构。对于静态分析，必须了解PHP中的OOP模型。除此之外，PHP中用于与MySQL进行通信的数据库扩展的知识以及MySQL插件的功能还影响了SQLBlock的实现。然后讨论影响SQLBlock步骤3中创建的概要文件的不同类型的SQLi攻击。

### <a class="reference-link" name="%EF%BC%881%EF%BC%89PHP"></a>（1）PHP

PHP是一种开放源代码服务器端脚本语言。根据W3Techs ，所有网站中有79.1％使用PHP作为服务器端语言。 PHP支持称为插件的二进制扩展，这些扩展为PHP提供了其他功能，例如密码算法，邮件传输或数据库通信。

PHP中的数据库API提供了用于与数据库进行通信的接口。数据库API可以是特定于数据库的，例如MySQL和SQLite，也可以是通用接口，例如用于访问各种数据库的PHP数据对象（PDO）。mysqli扩展提供了使用PHP脚本访问MySQL数据库的功能。与mysql（用于访问MySQL的另一个PHP扩展）相比，mysqli提供了三个附加功能：对准备好的语句，多条语句查询和事务的支持。由于上述其他功能，PHP Web应用程序倾向于使用mysqli。

PDO是一个抽象层，无论数据库类型如何，它都提供用于访问数据库的一致API。此功能允许PHP脚本使用同一段PHP代码连接到不同类型的数据库并发出查询。尽管PDO提供了用于访问数据库的简洁的API，但它仅提供了通用的查询构建功能。例如，PDO既不支持一个字符串中的多个SQL查询，异步查询，也不支持具有持久连接的自动清除。

PHP支持面向对象的编程模型，该模型引入了三个用于开发PHP Web应用程序的新概念：继承，多态和封装。继承和多态性使开发人员可以通过多种方式扩展类的功能或实现接口。封装将数据和方法捆绑到一个单元中。因此，OOP允许开发人员创建模块化程序并扩展PHP数据库扩展的功能。另外，PHP提供了动态功能，例如从动态字符串创建对象。 new是用于从PHP中的类创建对象的关键字。 new关键字的参数可以是类名或表示类名的字符串。

除了数据库API的面向对象设计之外，PHP Web应用程序还实现数据库过程。数据库过程处理从数据库API实例化的对象，并从数据库API或数据库API的子类型返回对象。在本文中，将数据库API和过程称为数据库访问层。网络应用程序中的数据库访问层处理网络应用程序模块与数据库之间的通信。 SQLBlock通过相对于Web应用程序的OOP实现静态地推理PHP Web应用程序的源代码来确定PHP Web应用程序中的数据库访问层。

### <a class="reference-link" name="%EF%BC%882%EF%BC%89MySQL"></a>（2）MySQL

MySQL是一个开源数据库管理系统。根据Datanyze的数据，截至2019年8月，Internet上已部署网站的46.03％使用了MySQL。 MySQL支持插件API，使开发人员可以扩展MySQL的功能。 MySQL插件可以实现用户身份验证，查询重写组件或新的解析器，以获取其他关键字和功能。 MySQL插件可以访问不同的数据结构，具体取决于它们的角色。本文特别感兴趣的是查询重写插件，它可以在MySQL执行之前收到查询时检查和修改查询。

查询重写插件可以访问MySQL收到的SQL查询的分析树。解析树中基于其类型的每个节点都包含有关它代表的来自SQL查询的元素的信息。例如，函数节点（例如IN，&lt;）包含有关传递给SQL函数的参数数量的信息。 SQLBlock使用每个节点在其训练和执行期间包含的信息。 Postparse插件还可以访问有关SQL查询类型（例如SELECT，INSERT）和SQL查询需要访问的表名称的信息。 SQLBlock使用以上信息为每个接收到的SQL查询创建和实施查询描述符。

### <a class="reference-link" name="%EF%BC%883%EF%BC%89SQL%E6%B3%A8%E5%85%A5%E6%94%BB%E5%87%BB"></a>（3）SQL注入攻击

SQL注入（SQLi）是一种代码注入攻击，攻击者能够控制SQL查询以执行恶意SQL语句来操纵数据库。 SQLi攻击分为八类：

（1）重言式：攻击者向SQL查询的条件子句（即where子句）中注入了一段代码，使得SQL查询始终求值为true [16]。攻击的目的从绕过身份验证到提取数据不等，具体取决于在应用程序中如何使用返回的数据。

（2）非法/逻辑错误的查询：利用此漏洞，攻击者可以修改SQL查询以引起语法，类型转换或逻辑错误。如果网络应用程序的错误页面显示数据库错误，则攻击者可以了解有关后端数据库的信息。此漏洞可能成为进一步攻击的垫脚石，进一步向攻击者揭示了可注入的参数。

（3）联合查询：在联合查询攻击中，攻击者诱使应用程序为给定查询添加数据库表中的数据。攻击者添加了一个或多个附加的SELECT子句（以关键字UNION开头），该子句导致数据库中其他表的结果合并到原始SQL查询的结果。这种攻击的目的是从数据库中的其他表中提取数据。

（4）附带查询：附带查询使攻击者可以将至少一个其他查询附加到原始查询中。因此，数据库在一个字符串中接收多个查询以执行。攻击者无意修改原始查询，而是要添加其他查询。使用the带的查询，攻击者可以插入，提取或修改数据以及执行远程命令以及从数据库提取数据。攻击是否成功取决于数据库是否允许从单个字符串执行多个查询。

（5）存储过程：存储过程是封装重复性任务的一组SQL查询。存储过程还允许与操作系统[16]交互，该交互可以由另一个应用程序，命令行或另一个存储过程调用。虽然数据库具有一组默认存储过程，但是存储过程中的SQL查询可能像存储过程外部的SQL查询一样容易受到攻击。

（6）推理：在这种类型的攻击中，阻止了应用程序和数据库返回反馈和错误消息；因此，攻击者无法验证注入是否成功。在推理攻击中，攻击者尝试根据对已经存储在数据库中的数据的正确/错误问题的答案来提取数据。

（7）替代编码：为了逃避检测，攻击者使用不同的编码方法将其有效载荷发送到数据库。应用程序的每一层都部署了各种方法来处理编码。处理转义字符之间的区别可以帮助攻击者逃避应用程序层并在数据库层上执行替代的编码字符串。

（8）二阶注入：一种常见的误解是已经存储在数据库中的数据可以安全提取。在二阶攻击中，攻击者将其精心制作的SQL查询发送到数据库，以将其攻击有效负载存储在数据库中。恶意有效负载将保持休眠状态，直到数据库由于另一个查询将其返回为止，并且恶意有效负载被不安全地用于创建另一个SQL查询。



## 0x03 System Overview

[![](https://p2.ssl.qhimg.com/t0198ff559a2ac95b60.png)](https://p2.ssl.qhimg.com/t0198ff559a2ac95b60.png)

在本节中将说明SQLBlock如何记录良性SQL查询并限制Web应用程序中的函数对数据库的访问。上图概述了SQLBlock如何保护Web应用程序免受SQLi攻击。具体来说，SQLBlock通过观察Web应用程序发出的良性查询来记录概要文件。然后，SQLBlock从数据库内部针对Web应用程序发送到数据库的每个查询强制执行概要文件。

在步骤1中，SQLBlock对Web应用程序执行静态分析，以识别在Web应用程序的脚本中使用的数据库过程。每个Web应用程序都会进行一次此分析，并且SQLBlock在训练和执行概要文件期间会使用此信息。

在步骤2中，SQLBlock处于训练模式，并记录Web应用程序发出的良性SQL查询。 SQLBlock可以在训练中使用良性浏览跟踪或Web应用程序的单元测试。 SQLBlock在MySQL接收到的良性SQL查询与使用数据库访问层向数据库发出查询的Web应用程序中的函数之间创建映射。

在步骤3中，SQLBlock利用前两个步骤中的信息来组装受信任的数据库访问概要文件。该概要文件是一组允许的表，SQL函数以及Web应用程序中每个函数可以发出的SQL查询的类型。第三步结束时，SQLBlock获取必要的信息，以保护Web应用程序免受SQLi攻击。

在步骤4中，SQLBlock通过根据步骤3中生成的受信任的概要文件过滤对数据库的访问，来保护正在运行的Web应用程序免受未经授权的数据库访问。修改后的数据库扩展名（例如PHP中的PDO）会在每个SQL查询的末尾附加执行信息（即调用堆栈）作为注释，然后再将其发送到MySQL。

在执行每个SQL查询之前，SQLBlock将从SQL查询中提取附加的执行信息，并标识使用数据库访问层与数据库进行通信的功能。 SQLBlock对照与该查询使用的功能相对应的概要文件检查查询。最后，如果SQL查询与概要文件匹配，则MySQL执行查询并返回结果。

### <a class="reference-link" name="%EF%BC%881%EF%BC%89Web%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E7%9A%84%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>（1）Web应用程序的静态分析

Web应用程序数据库访问层提供了一个统一的界面来与不同的数据库进行交互。在步骤1中，SQLBlock通过静态分析Web应用程序来识别数据库访问层。为此，SQLBlock创建了一个类依赖图（CDG）。 CDG是有向图CDG =（V，E），其中顶点（V）是Web应用程序中的类和接口。如果v1扩展类v2并实现接口v2，则在v1∈V和v2∈V之间绘制边e1,2∈E。

创建CDG之后，SQLBlock会提取Web应用程序中扩展数据库API（例如PHP中的PDO）的类和接口的列表。为此，手动识别数据库扩展类（例如，PHP中的mysqli）。然后，SQLBlock遍历CDG的顶点，并检查顶点是否已连接到数据库API。如果将顶点连接到数据库API，则SQLBlock会将其添加到数据库访问层。如果SQLBlock的类的方法初始化PHP中的数据库API实例（例如mysqli_init），则还将类添加到数据库访问层。在此迭代的最后，SQLBlock拥有扩展数据库API的Web应用程序中所有类和接口的列表。

除了Web应用程序中数据库API的面向对象设计之外，对数据库的操作（例如SELECT操作）也具有过程。数据库过程处理从数据库API创建对象的过程，并为Web应用程序中的模块设置正确的参数。数据库过程从数据库API的子类型返回对象。

SQLBlock分析Web应用程序中返回的对象的功能和过程的主体。如果返回的对象来自Web应用程序中数据库API的子类型，则SQLBlock会将其视为数据库过程。在此步骤的最后，SQLBlock提取有关数据库API以及数据库过程的信息。这是SQLBlock查找在训练和执行概要文件期间使用数据库访问层与数据库进行通信的功能所必需的。

[![](https://p5.ssl.qhimg.com/t01482216431d368d93.png)](https://p5.ssl.qhimg.com/t01482216431d368d93.png)

上图b显示了扩展数据库API mysqli的类的PHP代码片段。b中还有一个名为executeQuery的数据库过程，该过程从DatabaseConnectionmysqli返回一个对象，该对象是mysqli的子类。上图a显示了另一个代码片段，实现了名为get_public_info的函数，该函数使用executeQuery从数据库中检索数据。 SQLBlock将DatabaseConnectionmysqli标识为mysqli的子类，并将executeQuery标识为数据库过程。

### <a class="reference-link" name="%EF%BC%882%EF%BC%89%E5%9C%A8Web%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E4%B8%AD%E6%94%B6%E9%9B%86%E6%9C%89%E5%85%B3%E6%95%B0%E6%8D%AE%E5%BA%93%E8%AE%BF%E9%97%AE%E7%9A%84%E4%BF%A1%E6%81%AF"></a>（2）在Web应用程序中收集有关数据库访问的信息

在第2步中，使用良性跟踪或单元测试来训练SQLBlock以学习良性SQL查询。第2步包含两个组件，这些组件一起工作以在MySQL中接收到的SQL查询与组成SQL查询的函数之间创建映射。第一个组件将执行信息附加到每个SQL查询的末尾，然后再将其发送到数据库。执行信息包括Web应用程序中的调用堆栈，该调用堆栈导致使用数据库扩展名（例如PHP中的PDO或mysqli）将SQL查询发送到数据库。

第二部分，一个MySQL插件，拦截对MySQL的传入SQL查询的执行。当MySQL通过良性跟踪或单元测试接收到SQL查询时，SQLBlock会记录MySQL接收到的SQL查询，包括附加到SQL查询中的执行信息。由于SQLBlock可以访问SQL查询的语法分析树，因此SQLBlock遍历语法分析树，并在SQL查询的语法分析树中记录有关节点类型的信息。 SQLBlock还会记录SQL查询访问的表的列表以及SQL查询中的操作类型（例如SELECT操作）。

### <a class="reference-link" name="%EF%BC%883%EF%BC%89%E5%88%9B%E5%BB%BA%E6%A6%82%E8%A6%81%E6%96%87%E4%BB%B6"></a>（3）创建概要文件

步骤3中的SQLBlock利用步骤2中从良性SQL查询收集的访问日志，并生成一个概要文件，该概要文件定义了与数据库交互的Web应用程序中每个功能对数据库的访问。特别是，概要文件包含Web应用程序中每个功能的一组查询描述符。查询描述符包括四个组成部分。每个组件都指定了数据库访问的不同方面，将在下面进行解释。<br>
•操作：表示SQL查询中的操作类型。该操作可以是SELECT，INSERT，UPDATE，DELETE等。该概要文件记录每个SQL查询中的操作类型。强制执行操作类型消除了SQLi攻击执行其他操作的可能性。例如，当概要文件仅指定SELECT操作时，SQL查询无法执行INSERT SQL查询。

•表：确定SQL查询可以对其进行操作的表。限制SQL查询中使用的表可防止攻击者在其他表上执行SQL查询。

•逻辑运算符：指示SQL查询中使用的逻辑运算。逻辑运算符限制了攻击者在SQL查询中使用重言式攻击从表中提取数据的能力。

•SQL函数：确定查询使用的函数列表。该组件还记录传递给每个函数的参数的类型。功能列表限制攻击者仅使用在训练期间记录的功能。这限制了攻击者对数据库使用备用编码和存储过程攻击的能力。

在步骤3的结尾，SQLBlock为Web应用程序中的每个功能获取了一组查询描述符，这些功能基于在步骤2中获得的训练数据发布了SQL查询。

### <a class="reference-link" name="%EF%BC%884%EF%BC%89%E4%BF%9D%E6%8A%A4Web%E5%BA%94%E7%94%A8"></a>（4）保护Web应用

在最后一步中，SQLBlock处于强制模式，并使用在步骤3中创建的概要文件来限制Web应用程序中每个功能对数据库的访问。当数据库接收到SQL查询时，SQLBlock提取有关所接收的SQL查询的操作类型，表访问和解析树的信息。随后，SQLBlock从附加到传入SQL查询的执行信息中提取发出SQL查询的函数。

之后，SQLBlock在概要文件中查找并检索与构成和发出SQL查询的函数相关的查询描述符。对于与函数关联的每个查询描述符，SQLBlock会将查询描述符的每个组件与从接收到的SQL查询中获得的信息进行比较。首先，SQLBlock检查接收到的SQL查询和查询描述符中的操作类型是否相同。

其次，SQLBlock检查收到的SQL查询中的表列表。接收到的SQL查询中的表列表必须是查询描述符中的表列表的子集。对于逻辑运算符，SQLBlock检查MySQL接收到的SQL查询中的逻辑运算符是否是查询描述符中逻辑运算符的子集。最后，SQLBlock检查接收到的SQL查询中使用的函数以及参数的类型。函数和参数的类型必须在记录的查询描述符中。 SQLBlock采用保守的方法，仅当与该函数关联的查询描述符的所有四个组件都授权SQL查询时，才允许数据库执行SQL查询。



## 0x04 Implementation

在本节中详细介绍了构建SQLBlock需要解决的实现挑战。首先说明SQLBlock如何静态分析PHP Web应用程序以识别数据库访问层；然后描述SQLBlock如何使用MySQL插件API记录数据库接收的SQL查询，将说明SQLBlock如何基于发布到数据库的SQL查询为每个PHP函数创建一个精确的概要文件；最后描述了SQLBlock使用MySQL插件API限制数据库访问的方法。

### <a class="reference-link" name="%EF%BC%881%EF%BC%89Web%E5%BA%94%E7%94%A8%E7%A8%8B%E5%BA%8F%E7%9A%84%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>（1）Web应用程序的静态分析

在步骤1中，SQLBlock分析Web应用程序以确定Web应用程序中PHP脚本之间的数据库API和数据库接口。SQLBlock执行对流量不敏感的分析，该分析着重于查找数据库API，接口和过程。

SQLBlock使用libmagic识别Web应用程序中的所有PHP文件。使用php-parser将每个PHP脚本解析成一个抽象的syn tax tree（AST）。 SQLBlock通过扫描表示相应定义的AST节点来标识类，接口和抽象定义。SQLBlock检查整个PHP Web应用程序中的接口和类定义，以推断出类和接口之间的依赖关系。在分析过程中，SQLBlock在以下情况下创建类依赖关系图（CDG）并在接口和类之间绘制边：1）接口扩展了另一个接口。 2）一个类实现一个接口。 3）一个类扩展了另一个类。

创建CDG之后，静态分析器（SA）遍历CDG的节点，以识别有助于PHP Web应用程序与数据库之间进行通信的类和接口。为了达到这个目的，SQLBlock从PDO和mysqli类开始。 PHP中两个最受欢迎的数据库扩展。 SQLBlock创建与CDG中的PDO或mysqli类共享一条边的类和接口的列表。例如，在前图b中的代码创建CDG之后，SA将DatabaseConnectionmysqli标识为mysqli的子类。

SA还必须标识数据库过程。 SA通过分析过程返回的对象类型来确定过程是否为数据库过程。如果过程从数据库API的子类返回对象，则SA会将其标记为数据库过程。为了确定函数返回的对象类型，SA分析了返回语句的AST节点。 SA有两种情况值得关注：

•使用new关键字实例化对象：如果函数正在return语句中使用new关键字实例化对象，则SA将分析传递给new关键字的参数。如果参数是数据库API的子类的名称，则SA将该功能标记为数据库过程。如果参数是变量，则SA会执行轻量级的静态分析，作为对构成值的字符串进行常量折叠的有限形式。如果解析的值是数据库API的子类，则SA将该功能标记为数据库过程。

•变量：如果函数返回变量，则SA在AST上向后迭代到变量的最后一个赋值，并检查该赋值是否是类实例化。如果是类实例化，则SA尝试如上所述解析实例化对象的类型。

如前所述，PHP Web应用程序经常使用变量作为自变量，使用new关键字从类创建对象。在分析过程中，SA会使用字符串表示形式跟踪在PHP脚本中传递给new的参数。

#### <a class="reference-link" name="a%EF%BC%89%E5%AD%97%E7%AC%A6%E4%B8%B2%E8%A1%A8%E7%A4%BA%E5%BD%A2%E5%BC%8F"></a>a）字符串表示形式

SA在处理变量分配和常量定义时遇到字符串，字符串可以是文字成分，函数返回值和变量的混合。

SA在AST中的分配节点上进行迭代时，会将来自分配节点的一组信息记录在哈希表中。 SA跟踪变量名称和赋值右侧的组件。 SA还记录了赋值语句所在的函数的名称或类和方法的名称。例如，在图2b的第21行中，函数executeQuery具有赋值语句。赋值的右侧连接一个常量字符串和一个函数的返回值。 SA在分配的左侧记录变量的名称，以及常量字符串的值和该函数的返回值。 SA还在右侧记录操作的类型（如下所述，这是一个串联操作）。 SA实现常见的字符串操作来解析分配的值。

#### <a class="reference-link" name="b%EF%BC%89%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%93%8D%E4%BD%9C"></a>b）字符串操作

SQLBlock管理与字符串有关的频繁操作：

变量：传递给new的参数可以包含脚本中定义的变量。 SA在脚本，类或函数的范围内跟踪变量定义。进行变量分配时，SA为变量及其值创建一个对象。

串联：在PHP中，可以通过将多个组件与连接在一起来构造字符串。和。=运算符。 SA通过创建串联对象来处理字符串串联，并添加串联语句中存在的组件。

#### <a class="reference-link" name="c%EF%BC%89%E8%AF%86%E5%88%AB%E6%95%B0%E6%8D%AE%E5%BA%93%E8%BF%87%E7%A8%8B%E3%80%82"></a>c）识别数据库过程。

为了识别数据库过程，SA遍历分配并通过查找相同类和函数中的变量来解析字符串中变量的值。如果存在一个没有值的变量，则SA将该值作为正则表达式.*通配符重发。 SA在生成的正则表达式和数据库API子类列表之间寻找匹配项。例如，在前图b中的第21行，SA无法确定$ this-&gt; getDriver的返回值。而是，SA将值表示为.*通配符。 SA在数据库API子类列表中搜索与正则表达式DatabaseConnection *相匹配的类，并找到一个名为DatabaseConnectionmysqli的类。 SA将executeQuery标记为数据库过程。在此步骤的最后，SA具有数据库访问层类，接口和过程的列表。

### <a class="reference-link" name="%EF%BC%882%EF%BC%89%E6%A6%82%E8%A6%81%E6%96%87%E4%BB%B6%E6%95%B0%E6%8D%AE%E6%94%B6%E9%9B%86"></a>（2）概要文件数据收集

此步骤训练SQLBlock在发出的SQL查询和依赖于数据库访问层发出SQL查询的Web应用程序功能之间创建映射。在此步骤中收集的信息对于在步骤3中生成查询描述符是必需的。为每个SQL查询收集的信息包含操作，访问表，逻辑运算符，查询使用的SQL函数以及每个SQL函数中的参数类型。

#### <a class="reference-link" name="a%EF%BC%89%E9%99%84%E5%8A%A0PHP%E8%B0%83%E7%94%A8%E5%A0%86%E6%A0%88"></a>a）附加PHP调用堆栈

当MySQL收到SQL查询时，SQLBlock必须推断哪个PHP函数实际发出了SQL查询，为此修改了PDO和mysqli扩展的MySQL驱动程序的源代码。此修改将PHP调用堆栈作为注释添加到查询的末尾，然后再将其发送到数据库。

要访问PHP调用栈，使用Zend框架的内置函数zend_fetch_debug_backtrace。 Zend保留有关正在执行的PHP脚本的调用堆栈的信息。此信息包括函数，类，它们各自的参数，文件和发出调用的行号。修改后的数据库扩展（DE）提取PHP调用堆栈，并将其作为注释附加到SQL查询的末尾。

#### <a class="reference-link" name="b%EF%BC%89%E4%BB%8E%E8%A7%A3%E6%9E%90%E6%A0%91%E4%B8%AD%E6%8F%90%E5%8F%96%E4%BF%A1%E6%81%AF"></a>b）从解析树中提取信息

记录器插件（PR）充当解析后的MySQL插件。 PR可以访问有关MySQL中解析的SQL查询的各种信息：操作类型（例如SELECT操作等），表的名称以及SQL查询的解析树。 MySQL提供了一个解析树访问器功能，PR用来访问SQL查询的解析树。

但是，MySQL仅允许插件访问查询的文字值，例如解析树中的用户输入。因为SQLBlock需要有关已解析的SQL查询的更多信息，所以修改了MySQL服务器的源代码，以便该插件也可以访问非文字值。当MySQL调用PR时，PR记录MySQL接收到的SQL查询。之后，PR遍历SQL查询的解析树并记录每个节点的类型。如果该节点表示SQL查询中的SQL函数，则PR还将记录该SQL函数中使用的参数数量。

在SQL查询中代表SQL函数的节点还保存SQL函数中使用的参数数量。之后，PR记录传递给SQL函数的参数的类型，因为它们出现在SQL查询的解析树中。最后，PR记录该表以及MySQL接收到的SQL查询的操作类型。在MySQL中，有关SQL查询的操作类型的信息显示为数字。因此，PR将SQL查询的操作类型记录为概要文件中的编码数字。下图显示了函数get_public_info执行时在概要文件中记录的信息。

[![](https://p2.ssl.qhimg.com/t01dfbed3ae99d2c5a8.png)](https://p2.ssl.qhimg.com/t01dfbed3ae99d2c5a8.png)

在步骤2的结尾，SQLBlock具有有关所接收的SQL查询的详细信息，以进行训练。

### <a class="reference-link" name="%EF%BC%883%EF%BC%89%E5%88%9B%E5%BB%BA%E6%A6%82%E8%A6%81%E6%96%87%E4%BB%B6"></a>（3）创建概要文件

在步骤3中，概要文件生成器（PG）为访问数据库的Web应用程序中的每个PHP函数创建一个概要文件。 PG将步骤2中的训练数据作为输入。

PG从步骤2中读取记录的信息。如上图所示，第一行是包含PHP调用堆栈的SQL查询。使用在步骤1中创建的列表，PG必须推断哪个PHP使用数据库访问层将SQL查询发送到数据库。这是一个棘手的问题，因为调用堆栈上的最后一个函数可能是一个辅助函数，该辅助函数对应用程序发出所有查询（实际上，这就是编写诸如Wordpress和Joomla之类的现代PHP应用程序的方式）。

PG遍历PHP调用堆栈中的函数堆栈，并在步骤1中检查该函数或方法是否被识别为数据库过程或数据库API方法。PG从PHP调用堆栈中的最后一个调用开始，在堆栈上进行迭代，直到某个函数不是数据库过程或数据库API方法为止。 PG将此功能标识为创建数据库查询的功能。

例如，上图中的第1行显示了MySQL收到的SQL查询，包括PHP调用栈。 PG将mysqli检测为PHP中的数据库扩展，并将DatabaseConnectionmysqli检测为扩展mysqli的类。然后，PG访问下一个函数executeQuery，该函数在步骤1中被标识为数据库过程。 PHP调用堆栈中的下一个函数是get_public_info。 get_public_info不在步骤1的数据库过程列表中，因此PG将其标识为使用数据库访问层将SQL查询发送到数据库的PHP函数。 PG然后将更新get_public_info的查询描述符。

然后，PG遍历SQL查询的分析树的节点，并提取所有逻辑运算符。如果所有逻辑运算符都相同，则PG用相应的值更新cond。如果两个逻辑运算符（即OR和AND）都在SQL查询的分析树的节点中，则PG会将cond设置为“ Both”。如果SQL查询中没有逻辑运算符，则PG将cond设置为“无”。PG指定get_public_info在其SQL查询中不使用任何逻辑运算符。

PG从SQL查询的解析树中遍历节点列表，并提取SQL查询中使用的函数的名称以及它们各自的参数。由于传递给SQL函数的参数数量可以是可变的，因此PG不会记录每个参数的类型。相反，PG总结了SQL函数所依赖的参数类型。 MySQL中有多种类型的函数，例如数字，字符串，比较和日期函数。除比较类型外，所有上述SQL函数类型都接收少于或等于两个参数，或修改传递给该函数的第一个参数的内容。 MySQL中的比较函数（例如&lt;，IN等）将单个参数与可变大小的参数数组进行比较。

此外，单个参数作为SQL比较函数中的第一个参数出现。因此，PG会分别记录传递给SQL函数的第一个参数的类型。如果参数是表列，则PG将其记录为FIELD参数，否则PG将其记录为LITERAL参数。之后，PG遍历传递给SQL函数的其余参数。如果所有其他自变量的类型都是相同的类型（即FIELD或LITERAL），则PG在概要文件中记录相应类型的值。否则，PG将类型设置为var。例如，基于前图，PG指定函数get_public_info使用函数“&gt;”，第一个参数是表列，第二个参数是LITERAL。

最后，PG读取有关表名称和SQL查询类型的信息。例如，基于前图中的第3行，PG推断出函数get_public_info使用0类型的SQL查询（即SELECT SQL查询）访问表public_info。

在第3步结束时，PG为Web应用程序中的每个PHP函数提供了一组查询描述符，这些描述符在第2步的训练过程中发出了SQL查询。

### <a class="reference-link" name="%EF%BC%884%EF%BC%89%E4%BF%9D%E6%8A%A4Web%E5%BA%94%E7%94%A8"></a>（4）保护Web应用

在步骤4中，强制实施程序插件（PE）处于强制执行模式。 PE使用在步骤3中生成的概要文件，并保护数据库免受偏离该概要文件的查询的影响。与PG相似，PE被实现为后插件，从而使它可以访问接收到的SQL查询的解析树。 PE还使用与之前所述相同的PHP数据库扩展。 PE读取每个PHP函数的概要文件，并使用它来分析接收到的查询。

收到查询后，MySQL解析SQL查询并调用PE。 PE使用第相同方法找到调用堆栈并提取发出查询的PHP函数。然后，PE在与PHP函数关联的概要文件中找到查询描述符。 PE根据为PHP函数找到的每个查询描述符的所有四个组件检查查询。对于操作类型，PE检查收到的SQL查询是否具有与概要文件中记录的操作类型相同的操作类型。 PE还检查为接收到的SQL查询访问的表的列表是查询描述符中列出的表访问的子集。接收到的SQL查询中使用的逻辑运算符必须是查询描述符中逻辑运算符的子集。

最后，收到的SQL查询只能使用查询描述符中列出的函数的子集。 PE还检查传递给每个函数的参数是否与查询描述符中记录的参数具有相同的类型。仅当SQL查询与概要文件中至少一个查询描述符的所有四个组成部分匹配时，PE才允许MySQL执行SQL查询并返回结果。否则，PE将False返回给MySQL服务器，从而中止查询的执行并将错误返回给Web应用程序，从而阻止执行潜在的恶意攻击者控制的SQL查询。



## 0x05 Evalution

评估了SQLBlock防止对一组流行的PHP Web应用程序进行SQLi攻击的能力，还检查了网络应用的良性浏览过程中SQLBlock的误报率。此外，评估了良性浏览的第3步的性能开销。为了进行评估回答了以下研究问题：

RQ1 SQLBlock的静态分析有多精确？

RQ2 SQLBlock对流行的Web应用程序中的现实世界SQLi漏洞有效吗？

RQ3 SQLBlock关于性能开销和误报的实用性如何？

### <a class="reference-link" name="%EF%BC%881%EF%BC%89%E8%AF%84%E4%BC%B0%E7%AD%96%E7%95%A5"></a>（1）评估策略

在评估中对每个Web应用程序执行了一次静态分析，评估了通过RQ1中的静态分析解决的数据库访问层。然后，利用数据库访问层来回答RQ2和RQ3。使用每个Web应用程序的官方单元测试训练并构建了SQLBlock的概要文件，并将生成的概要文件用于实验以回答RQ2和RQ3。官方单元测试通过执行测试输入并验证其结果来检查Web应用程序中功能的正确性。

与Web爬虫相比，单元测试的优势在于，无需管理员的手动干预，特别是无需为Web应用程序中的每种表单提供语义正确的输入。网络应用的单元测试是专门针对其实施量身定制的，因此有可能实现更高的代码覆盖率。下图显示与Burp套件相比，Drupal的单元测试实现了更高的线路覆盖率，并且几乎涵盖了Burp Suite涵盖的所有线路。但是，也可以使用其他方法（例如Web爬虫）来训练SQLBlock。

[![](https://p4.ssl.qhimg.com/t013e383d0393c087f4.png)](https://p4.ssl.qhimg.com/t013e383d0393c087f4.png)

### <a class="reference-link" name="%EF%BC%882%EF%BC%89%E8%AF%84%E4%BC%B0%E6%95%B0%E6%8D%AE%E9%9B%86"></a>（2）评估数据集

在四个最受欢迎的PHP Web应用程序Wordpress，Joomla，Drupal和Magento上评估了SQLBlock。据W3Techs称，这些Web应用程序在所有现有内容管理系统（CMS）中占据70.5％的市场份额，并在互联网上的所有实时网站中合计占38.4％。管理员安装插件和其他组件以自定义Web应用程序并扩展其功能。为了在评估中反映此行为，还评估了插件上的SQLBlock。

安装了四个易受攻击的Wordpress插件，分别称为Easy-Modal，Polls，Form-maker和Autosuggest。还在Joomla中安装了三个易受攻击的插件，分别为jsJobs，JE图片库和QuickContact。为了评估SQLBlock的防御能力，选择了包含已知SQLi漏洞的Web应用程序和插件的最新版本。还考虑了数据集中SQLi漏洞的类型，以包括所有类型的SQLi漏洞以进行全面评估，在不同的Web应用程序和插件中总共收集了11个SQLi漏洞。

### <a class="reference-link" name="%EF%BC%883%EF%BC%89%E8%A7%A3%E5%86%B3%E6%95%B0%E6%8D%AE%E5%BA%93%E8%AE%BF%E9%97%AE%E5%B1%82%EF%BC%88RQ1%EF%BC%89"></a>（3）解决数据库访问层（RQ1）

在步骤1中，SQLBlock扫描PHP Web应用程序以标识用于与数据库进行通信的数据库访问层。步骤1是在PHP调用栈中标识正确函数的关键步骤，该函数依赖于数据库访问层与数据库进行交互。

[![](https://p1.ssl.qhimg.com/t018588aa36dc1ad0ab.png)](https://p1.ssl.qhimg.com/t018588aa36dc1ad0ab.png)

上表列出了已解析的数据库访问层统计信息。已解析的子类列指定了扩展PHP中的数据库API的类数。已解析的数据库过程列显示了从数据库API的子类返回对象的函数数量。由于Web应用程序中的数据库访问层没有基础知识，因此手动分析SA的输出是否为真。 PHP Web应用程序中数据库API的子类还实现了接口，以简化操作，例如遍历对象中的元素和计数元素。例如，Drupal实现了Iterator和Countable，以便PHP脚本可以遍历或计算数据库返回给PHP脚本的记录数。

由于Drupal在数据库API的子类中实现Countable和Iterator，因此SA将这两个接口添加到数据库访问层。如上表所示，在评估过程中观察到的唯一误报是由Iterator和Countable接口引起的。数据集中除Wordpress之外的所有Web应用程序都在其数据库API子类和数据库过程中使用了封装，这表明必须识别用于创建概要文件的数据库访问层。在不标识数据库访问层的情况下，SQLBlock的操作类似于SEPTIC，并将接收到的查询映射到单个标识符。

### <a class="reference-link" name="%EF%BC%884%EF%BC%89%E9%98%B2%E5%BE%A1%E8%83%BD%E5%8A%9B%EF%BC%88RQ2%EF%BC%89"></a>（4）防御能力（RQ2）

[![](https://p2.ssl.qhimg.com/t0191c8ae5c930cc1b9.png)](https://p2.ssl.qhimg.com/t0191c8ae5c930cc1b9.png)

针对上表中列出的11个SQLi漏洞评估了SQLBlock的防御功能。构建并部署了五个Docker容器，这些容器运行Web应用程序的脆弱版本和插件。使用Metasploit Framework ，exploit-db和sqlmap的漏洞利用这些漏洞。如果攻击者可以将恶意SQL代码注入Web应用程序中生成的查询中，并且数据库执行恶意SQL查询，则认为攻击成功。

对于此评估，使用了RQ1中的静态分析结果。使用了各自存储库中Web应用程序的官方单元测试对SQLBlock进行了训练。创建概要文件后，将SQLBlock配置为强制模式，并评估exploit-db和Metasploit Framework中的利用是否成功。攻击者不仅限于在评估中使用漏洞利用，还可以制作其SQL查询来规避SQLBlock。为了评估这种攻击的可能性，还使用了sqlmap来为上表中列出的漏洞生成各种攻击。

在上表，列出了SQL Block防御Web应用程序攻击的SQLi漏洞列表。表中的第二列代表分配给每个漏洞的ID。用C标记了驻留在Web应用程序核心中的SQLi漏洞。第三列显示了为利用相应漏洞而执行的攻击类型。 SQLBlock保护Web应用程序免受数据集中所有11个SQLi漏洞的侵害，而SEPTIC仅能防御仅驻留在Wordpress插件中的四个SQLi漏洞。

为了评估绕开SQLBlock的可能性，还列出了每个Web应用程序或插件中易受攻击的PHP函数可以发出的SQL查询的可用查询描述符。例如，针对表中第一个漏洞的任何潜在利用都仅限于对表wp_em_modals的UPDATE查询，而无需其他逻辑运算符。此外，该漏洞利用程序只能使用SQL函数 “ = ” and “ IN ”。

### <a class="reference-link" name="%EF%BC%885%EF%BC%89%E6%80%A7%E8%83%BD%EF%BC%88RQ3%EF%BC%89"></a>（5）性能（RQ3）

性能/响应能力是Web应用程序的关键因素，因此评估了SQLBlock的性能开销。在SQLBlock中，前三个步骤可以脱机执行。步骤1和3是自动的，不依赖管理员的帮助。在步骤2中，管理员必须在Web应用程序中执行单元测试或创建良性流量以训练SQLBlock。步骤4被部署为MySQL插件和一组针对恶意SQL查询的修改后的PHP数据库扩展到沙箱数据库。 MySQL服务器在启动时会加载SQLBlock的保护插件。 SQLBlock加载概要文件，并等待传入的SQL查询。在具有4Gb内存2133Mhz DDR4，运行Linux 4.9.0，Nginx 1.13.0，PHP 7.1.20和MySQL 5.7的4核Intel Core i7-6700上执行实验。

为了进行性能评估，创建了一个Docker 容器，该容器使用包含Drupal 7.0 Web应用程序的PHP，Nginx和MySQL的默认配置运行。使用ApacheBench（一种用于对HTTP Web服务器进行基准测试的工具）来衡量SQLBlock的性能开销，通过增加ApacheBench中的并发级别来模拟现实情况。并发级别显示一次打开的请求数，在Drupal 7.0中测量了index.html的网络响应时间，该响应向MySQL发出了26条查询。为了获得更精确的结果，在多个并发级别上测量了10,000个请求的响应时间。

下表列出了上述情况的结果，表中的第一列显示了每个测试的并发级别。表中的接下来的两列介绍了具有/不具有SQLBlock的Drupal的网络响应时间。如下表所示，SQLBlock产生的服务器网络响应时间的开销少于（2.5％）。基于SQLBlock提供的强大保护，认为这种开销是可以接受的。此外，SQLBlock是不注重性能优化的原型。这样的优化可能会进一步减少开销。

[![](https://p1.ssl.qhimg.com/t01bad63291de5b4389.png)](https://p1.ssl.qhimg.com/t01bad63291de5b4389.png)

还测量了MySQL中查询的执行时间。修改了MySQL的源代码，以计算MySQL执行SQL查询所需的时间。在本实验中，使用ApacheBench向Drupal 7.0中的index.html发送10,000个请求，该请求向MySQL发出了总共260,000个查询。测量了两种不同情况下发出查询的平均执行时间。第一种情况是没有SQLBlock插件的MySQL，第二种情况是在MySQL中启用了SQLBlock的插件。上表的最后两列显示了所有收到的MySQL查询的平均执行时间。每个查询的MySQL SQLBlock性能开销小于0.31毫秒。

### <a class="reference-link" name="%EF%BC%886%EF%BC%89%E8%AF%AF%E6%8A%A5%E8%AF%84%E4%BC%B0"></a>（6）误报评估

如果SQLBlock阻止对数据库的良性查询，则将操作视为误报。对于误报评估，使用Wordpress 4.7和Drupal 7.0评估了SQLBlock。对于每个Web应用程序，都使用了RQ2中内置的概要文件。然后将SQLBlock配置为强制模式，并重放了Selenium收集的浏览跟踪。浏览记录以用户和管理员的身份浏览了该Web应用程序，目的是尽可能覆盖该Web应用程序。

[![](https://p0.ssl.qhimg.com/t01ce0a55e6456a180c.png)](https://p0.ssl.qhimg.com/t01ce0a55e6456a180c.png)

根据上表，在良性浏览和单元测试期间，只有10.11％发出的查询具有相同的查询结构。发出的查询的查询结构上的这种合法差异使以前基于查询结构建立其概要文件的方法无法区分良性SQL查询和恶意SQL查询。例如，对于Drupal 7.0，SEPTIC在同一测试中的假阳性率超过89％。只要查询与概要文件中与PHP函数关联的查询描述符中的至少一个匹配，SQLBlock允许查询在MySQL中执行。在对Drupal的误报测试中，SQLBlock没有阻止来自良性Selenium浏览的任何查询。这表明尽管训练和测试期间的PHP函数使用了不同的查询，但查询描述符是相同的。

上表显示在的良性浏览中，有82.57％的查询与为SQLBlock的个人资料记录的查询相似。尽管在Wordpress的训练和测试过程中类似的已发布查询的比率高于Drupal，但SQLBlock在良性浏览期间阻止了7个唯一查询，相当于所有已发布查询的5％。 WordPress中误报的主要原因有两个。第一个原因是MySQL根据传递给查询中SQL函数的参数修改查询。例如，如果传递给查询中IN语句的数组的长度为1，则MySQL会将IN语句修改为等号（=）语句。

在查询中以及随后在查询的分析树中进行的此修改会导致SQLBlock出现误报，因为SQLBlock在执行方面遇到的功能与概要文件中的功能不同。第二个原因是概要文件中缺少PHP函数。在实施期间，如果SQLBlock找不到发布SQL查询的PHP函数的任何查询描述符，则SQLBlock会阻止SQL查询。在Wordpress中，七分之六的误报是由于在良性浏览期间缺少PHP函数的查询描述符而引起的，这意味着覆盖训练过程中可以发出查询的所有函数是SQLBlock的重要因素 。



## 0x06 Discussion and Limitations

**eval函数：**PHP Web应用程序广泛使用在PHP中实现的动态功能，例如eval函数，该函数将字符串参数评估为PHP代码。当前，SQLBlock不在eval内部处理函数和类定义。 Web应用程序可以使用eval动态定义数据库API或过程，并在整个Web应用程序中使用它。这导致在步骤1中生成PHP数据库API和PHP Web应用程序接口的不完整列表。在这种情况下，SQLBlock会将查询描述符映射到一小组PHP函数，这些函数可以使攻击者执行恶意查询。在以后的工作中，可以改进SQLBlock中的静态分析器，以处理传递给eval的静态PHP代码，以确定更精确的数据库访问层。

**训练期间的覆盖范围不完整：**PHP Web应用程序会根据用户输入生成动态查询。这种方法使得不可能在训练阶段向数据库发出所有可能的查询。动态分析的训练阶段不完整，SQLBlock也不例外。的Wordpress误报测试表明，所发出查询的不完全覆盖会导致SQLBlock阻止良性查询。



## 0x07 Conclusion

提出了SQLBlock（一种动态静态混合技术）来限制PHP Web应用程序对数据库的访问。在训练步骤中，SQLBlock会推断发出的SQL查询及其各自的PHP调用堆栈。使用轻量级的静态分析，SQLBlock提取了PHP Web应用程序中的数据库API和过程列表。在第三步中，SQLBlock为在向数据库发出SQL查询的PHP Web应用程序中的每个PHP函数创建一组查询描述符。

在最后一步中，SQLBlock充当MySQL插件，基于生成的查询描述符来限制PHP Web应用程序和MySQL的交互。 SQLBlock可以防止SQLi攻击最流行的四个PHP Web应用程序和七个插件中的11个漏洞，而对于Drupal 7.0则没有任何误报，而对于Wordpress良性浏览的误报率却很少（七个）。
