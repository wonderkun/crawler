> 原文链接: https://www.anquanke.com//post/id/190170 


# MyBatis 和 SQL 注入的恩恩怨怨


                                阅读量   
                                **1187128**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t019817257e653fdf5e.jpg)](https://p4.ssl.qhimg.com/t019817257e653fdf5e.jpg)



作者：madneal@平安银行应用安全团队

MyBatis 是一种持久层框架，介于 JDBC 和 Hibernate 之间。通过 MyBatis 减少了手写 SQL 语句的痛苦，使用者可以灵活使用 SQL 语句，支持高级映射。但是 MyBatis 的推出不是只是为了安全问题，有很多开发认为使用了 MyBatis 就不会存在 SQL 注入了，真的是这样吗？使用了 MyBatis 就不会有 SQL 注入了吗？答案很明显是 NO。 MyBatis 它只是一种持久层框架，它并不会为你解决安全问题。当然，如果你能够遵循规范，按照框架推荐的方法开发，自然也就避免 SQL 注入问题了。本文就将 MyBatis 和 SQL 注入这些恩恩怨怨掰扯掰扯。（注本文所说的 MyBatis 默认指的是 Mybatis3）

## 起源

写本文的起源主要是来源于内网发现的一次 SQL 注入。我们发现内网的一个请求的 keyword 参数存在 SQL 注入，简单地介绍一下需求背景。基本上这个接口就是实现多个字段可以实现 keyword 的模糊查询，这应该是一个比较常见的需求。只不过这里存在多个查询条件。经过一番搜索，我们发现问题的核心处于以下代码：

```
public Criteria addKeywordTo(String keyword) `{`
  StringBuilder sb = new StringBuilder();
  sb.append("(display_name like '%" + keyword + "%' or ");
  sb.append("org like '" + keyword + "%' or ");
  sb.append("status like '%" + keyword + "%' or ");
  sb.append("id like '" + keyword + "%') ");
  addCriterion(sb.toString());
  return (Criteria) this;
`}`
```

很明显，需求是希望实现 `diaplay_name`, `org`, `status` 以及 `id` 的模糊查询，但开发在这里自己创建了一个 `addKeywordTo` 方法，通过这个方法创建了一个涉及多个字段的模糊查询条件。有一个有趣的现象，在内网发现的绝大多数 SQL 注入的注入点基本都是模糊查询的地方。可能很多开发往往觉得模糊查询是不是就不会存在 SQL 注入的问题。分析一下这个开发为什么会这么写，在他没有意识到这样的写法存在 SQL 注入问题的时候，这样的写法他可能认为是最省事的，到时直接把查询条件拼进去就可以了。以上代码是问题的核心，我们再看一下对应的 xml 文件：

```
&lt;sql id="Example_Where_Clause" &gt;
    &lt;where &gt;
      &lt;foreach collection="oredCriteria" item="criteria" separator="or" &gt;
        &lt;if test="criteria.valid" &gt;
          &lt;trim prefix="(" suffix=")" prefixOverrides="and" &gt;
            &lt;foreach collection="criteria.criteria" item="criterion" &gt;
              &lt;choose &gt;
                &lt;when test="criterion.noValue" &gt;
                  and $`{`criterion.condition`}`
                &lt;/when&gt;
                &lt;when test="criterion.singleValue" &gt;
                  and $`{`criterion.condition`}` #`{`criterion.value`}`
                &lt;/when&gt;
                &lt;when test="criterion.betweenValue" &gt;
                  and $`{`criterion.condition`}` #`{`criterion.value`}` and #`{`criterion.secondValue`}`
                &lt;/when&gt;
                &lt;when test="criterion.listValue" &gt;
                  and $`{`criterion.condition`}`
                  &lt;foreach collection="criterion.value" item="listItem" open="(" close=")" separator="," &gt;
                    #`{`listItem`}`
                  &lt;/foreach&gt;
                &lt;/when&gt;
              &lt;/choose&gt;
            &lt;/foreach&gt;
          &lt;/trim&gt;
        &lt;/if&gt;
      &lt;/foreach&gt;
    &lt;/where&gt;
  &lt;/sql&gt;

    &lt;select id="selectByExample" resultMap="BaseResultMap" parameterType="com.doctor.mybatisdemo.domain.userExample" &gt;
    select
    &lt;if test="distinct" &gt;
      distinct
    &lt;/if&gt;
    &lt;include refid="Base_Column_List" /&gt;
    from user
    &lt;if test="_parameter != null" &gt;
      &lt;include refid="Example_Where_Clause" /&gt;
    &lt;/if&gt;
    &lt;if test="orderByClause != null" &gt;
      order by $`{`orderByClause`}`
    &lt;/if&gt;
  &lt;/select&gt;
```

我们再回过头看一下上面 JAVA 代码中的 `addCriterion` 方法，这个方法是通过 MyBatis generator 生成的。

```
protected void addCriterion(String condition) `{`
    if (condition == null) `{`
        throw new RuntimeException("Value for condition cannot be null");
    `}`
    criteria.add(new Criterion(condition));
`}`
```

这里的 `addCriterion` 方法只传入了一个字符串参数，这里其实使用了重载，还有其它的 `addCriterion` 方法传入的参数个数不同。这里使用的方法只传入了一个参数，被理解为 `condition`，因此只是添加了一个只有 `condition` 的 Criterion。现在再来看 xml 中的 `Example_Where_Clause`，在遍历 criteria 时，由于 criterion 只有 condition 没有 value,那么只会进去条件 `criterion.noValue`，这样整个 SQL 注入的形成就很清晰了。

```
&lt;when test="criterion.noValue" &gt;
    and $`{`criterion.condition`}`
&lt;/when&gt;
```

### <a class="reference-link" name="%E6%AD%A3%E7%A1%AE%E5%86%99%E6%B3%95"></a>正确写法

既然上面的写法不正确，那正确的写法应该是什么呢？第一种，我们可以用一种非常简单直接的方法，在 `addKeywordTo` 方法里面 对 keword 进行过滤，这样其实也可以避免 SQL 注入。通过正则匹配将 keyword 里面所有非字母或者数字的字符都替换成空字符串，这样自然也就不可能存在 SQL 注入了。

```
keyword = keyword.replaceAll("[^a-zA-Z0-9\s+]", "");
```

但是这种写法并不是一种科学的写法，这样的写法存在一种弊端，就是如果你的 keyword 需要包含符号该怎么办，那么你是不是就要考虑更多的情况，是不是就需要添加更多的逻辑判断，是不是就存在被绕过的可能了？那么正确的写法应该是什么呢？其实 [mybatis 官网](http://mybatis.org/generator/generatedobjects/exampleClassUsage.html) 已经给出了 Comple Queries 的范例：

```
TestTableExample example = new TestTableExample();

  example.or()
    .andField1EqualTo(5)
    .andField2IsNull();

  example.or()
    .andField3NotEqualTo(9)
    .andField4IsNotNull();

  List&lt;Integer&gt; field5Values = new ArrayList&lt;Integer&gt;();
  field5Values.add(8);
  field5Values.add(11);
  field5Values.add(14);
  field5Values.add(22);

  example.or()
    .andField5In(field5Values);

  example.or()
    .andField6Between(3, 7);
```

上面等同的 SQL 语句是：

```
where (field1 = 5 and field2 is null)
     or (field3 &lt;&gt; 9 and field4 is not null)
     or (field5 in (8, 11, 14, 22))
     or (field6 between 3 and 7)

```

现在让我们将一开始的 `addKeywordTo` 方法进行改造：

```
public void addKeywordTo(String keyword, UserExample userExample) `{`
  userExample.or().andDisplayNameLike("%" + keyword + "%");
  userExample.or().andOrgLike(keyword + "%");
  userExample.or().andStatusLike("%" + keyword + "%");
  userExample.or().andIdLike(keyword + "%");
`}`
```

这样的写法才是一种比较标准的写法了。`or()` 方法会产生一个新的 Criteria 对象，添加到 oredCriteria 中，并返回这个 Criteria 对象，从而可以链式表达，为其添加 Criterion。这样添加的的 Criteria 就是包含 condition 以及 value 的，在做条件查询的时候，就会进入到 `criterion.singleValue` 中，那么 keyword 参数只会传入到 value 中，而 value 是通过 `#`{``}`` 传入的。

```
&lt;when test="criterion.singleValue" &gt;
  and $`{`criterion.condition`}` #`{`criterion.value`}`
&lt;/when&gt;
```

总结以下，导致这个 SQL 注入的原因还是开发没有按照规范来写，自己造轮子写了一个方法来进行模糊查询，殊不知带来了 SQL 注入漏洞。其实，Mybatis generator 已经为每个字段生成了丰富的方法，只要合理使用，就一定可以避免 SQL 注入问题。

[![](https://p2.ssl.qhimg.com/dm/609_1024_/t01dd1ab1980a2ff9c4.png)](https://p2.ssl.qhimg.com/dm/609_1024_/t01dd1ab1980a2ff9c4.png)



## 使用 #`{``}` 可以避免 SQL 注入吗

如果你猛地一看到这个问题，你可能会觉得迟疑？使用 `#`{``}`` 就可以彻底杜绝 SQL 注入么，不一定吧。但如果你仔细分析一下，你就会发现答案是肯定的。具体的原因让我和你娓娓道来。

首先我们需要先搞清楚 MyBatis 中 `#`{``}`` 是如何声明的。当参数通过 `#`{``}`` 声明的，参数就会通过 PreparedStatement 来执行，即预编译的方式来执行。预编译你应该不陌生，因为在 JDBC 中就已经有了预编译的接口。这也对应了开头文中我们提到的一点，Mybatis 并不是能解决 SQL 注入的核心，预编译才是。预编译不仅可以对 SQL 语句进行转义，避免 SQL 注入，还可以增加执行效率。Mybatis 底层其实也是通过 JDBC 来实现的。以 MyBatis 3.3.1 为例，jdbc 中的 SqlRunner 就设计到具体 SQL 语句的实现。

[![](https://p1.ssl.qhimg.com/dm/1024_668_/t017e1ee9b2d905ad05.png)](https://p1.ssl.qhimg.com/dm/1024_668_/t017e1ee9b2d905ad05.png)

以 update 方法为例,可以看到就是通过 JAVA 中 PreparedStatement 来实现 sql 语句的预编译。

```
public int update(String sql, Object... args) throws SQLException `{`
    PreparedStatement ps = this.connection.prepareStatement(sql);

    int var4;
    try `{`
        this.setParameters(ps, args);
        var4 = ps.executeUpdate();
    `}` finally `{`
        try `{`
            ps.close();
        `}` catch (SQLException var11) `{`
            ;
        `}`

    `}`

    return var4;
`}`
```

值得注意的一点是，这里的 PreparedStatement 严格意义上来说并不是完全等同于预编译。其实预编译分为客户端的预编译以及服务端的预编译，4.1 之后的 MySql 服务器端已经支持了预编译功能。很多主流持久层框架(MyBatis，Hibernate)其实都没有真正的用上预编译，预编译是要我们自己在参数列表上面配置的，如果我们不手动开启，JDBC 驱动程序 5.0.5 以后版本 默认预编译都是关闭的。需要通过配置参数来进行开启：

```
jdbc:mysql://localhost:3306/mybatis?&amp;useServerPrepStmts=true&amp;cachePrepStmts=true
```

数据库 SQL 执行包含多个阶段如下图所示，但我们这里针对于 SQL 语句客户端的预编译在发送到服务端之前就已经完成了。在服务器端主要考虑的就是性能问题，这不是本文的重点。当然，每一个数据库实现的预编译方式可能都有一些差别。但是对于防止 SQL 注入，在 MyBatis 中只要使用 `#`{``}`` 就可以了，因为这样就会实现 SQL 语句的参数化，避免直接引入恶意的 SQL 语句并执行。

[![](https://p0.ssl.qhimg.com/t013b55c42309644d99.png)](https://p0.ssl.qhimg.com/t013b55c42309644d99.png)



## MyBatis generator 的使用

对于使用 MyBatis，MyBatis generator 肯定是必不可少的使用工具。MyBatis 是针对 MyBatis 以及 iBATIS 的代码生成工具，支持 MyBatis 的所有版本以及 iBATIS 2.2.0 版本以上。因为在现实的业务开发中，肯定会涉及到很多表，开发不可能自己一个去手写相应的文件。通过 MyBatis generator 就可以生成相应的 POJO 文件、 SQL Map XML 文件以及可选的 JAVA 客户端代码。常用的使用 MyBatis generator 的方式是直接通过使用 Maven 的 mybatis-generator-maven-plugin 插件，只要准备好配置文件以及数据库相关信息，就可以通过这个插件生成相应代码了。

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
 &lt;!DOCTYPE generatorConfiguration PUBLIC "-//mybatis.org//DTD MyBatis Generator Configuration 1.0//EN" "http://mybatis.org/dtd/mybatis-generator-config_1_0.dtd"&gt;
&lt;generatorConfiguration&gt;
    &lt;context id="MysqlTables" targetRuntime="MyBatis3"&gt;
        &lt;commentGenerator&gt;
            &lt;property name="suppressAllComments" value="false" /&gt;
            &lt;property name="suppressDate" value="false" /&gt;
        &lt;/commentGenerator&gt;

        &lt;!-- 数据库链接URL、用户名、密码 --&gt;
        &lt;jdbcConnection driverClass="com.mysql.cj.jdbc.Driver"
                        connectionURL="jdbc:mysql://localhost:3306/mybaits_test"
                        userId="xxx"
                        password="xxx"&gt;
        &lt;/jdbcConnection&gt;

        &lt;javaTypeResolver&gt;
            &lt;property name="forceBigDecimals" value="true" /&gt;
        &lt;/javaTypeResolver&gt;

        &lt;javaModelGenerator targetPackage="com.doctor.mybatisdemo.domain" targetProject="src/main/java/"&gt;
            &lt;property name="constructorBased" value="false" /&gt;
            &lt;property name="enableSubPackages" value="false" /&gt;
            &lt;property name="trimStrings" value="true" /&gt;
        &lt;/javaModelGenerator&gt;

        &lt;sqlMapGenerator targetPackage="myBatisGeneratorDemoConfig" targetProject="src/main/resources"&gt;
            &lt;property name="enableSubPackages" value="false" /&gt;
        &lt;/sqlMapGenerator&gt;

        &lt;javaClientGenerator type="XMLMAPPER" targetPackage="com.doctor.mybatisdemo.dao" targetProject="src/main/java/"&gt;
            &lt;property name="enableSubPackages" value="false" /&gt;
        &lt;/javaClientGenerator&gt;

&lt;!--         要生成那些表(更改tableName和domainObjectName就可以) --&gt;
        &lt;table tableName="user" domainObjectName="user"/&gt;
    &lt;/context&gt;
&lt;/generatorConfiguration&gt;
```

[![](https://p4.ssl.qhimg.com/dm/1024_891_/t01bcc5f5cd9e3e08b1.png)](https://p4.ssl.qhimg.com/dm/1024_891_/t01bcc5f5cd9e3e08b1.png)

在这里我想强调的是一个关键参数的配置，即 `targetRuntime` 参数。这个参数有2种配置项，即 `MyBatis3` 和 `MyBatis3Simple`，`MyBatis3` 为默认配置项。MyBatis3Simple 只会生成基本的增删改查，而 MyBatis3 会生成带条件的增删改查，所有的条件都在 XXXexample 中封装。使用 MyBatis3 时，enableSelectByExample，enableDeleteByExample，enableCountByExample 以及 enableUpdateByExample 这些属性为 true，就会生成相应的动态语句。这也就是我们上述 `Example_Where_Clause` 生成的原因。

如果使用配置项 `MyBatis3Simple`，那么生成的 SQL Map XML 文件将非常简单，只包含一些基本的方法，也不会产生上面的动态方法。可以这么说，如果你使用 `MyBatis3Simple` 话，并且不额外改造，因为里面所有的变量都是通过 `#`{``}`` 引入，就不可能会有 SQL 注入的问题。但是现实业务中往往涉及到复杂的查询条件，而且一般开发使用的都是祖传配置文件，所以到底是使用 `MyBatis3` 还是 `MyBatis3Simple`，还是需要具体问题，具体看待。不过如果你是使用默认配置，你就需要当心了，谨记一点，外部传入的参数是极有可能是不安全的，是不可以直接引入处理的。意思到这一点，就基本可以很好地避免 SQL 注入问题了。

我创建了一个 Github 仓库 [mb-generator](https://github.com/neal1991/mb-generator)，这个仓库里面的 mybatis3 分支以及 mybatis3simple 分支分别是使用不同的配置项生成的代码，你可以去看一看生成的代码具体差别有哪一些，可以看一看使用不同配置项的具体差别。



## 总结

这篇文章从内网的一个 SQL 注入漏洞引发的对 MyBatis 的使用问题思考，对 MyBatis 中 `#`{``}`` 工作的原理以及 Mybatis generator 的使用多个方面做了进一步的思考。可以总结以下几点：
- 能不使用拼接就不要使用拼接，这应该也是避免 SQL 注入最基本的原则
- 在使用 `$`{``}`` 传入变量的时候，一定要注意变量的引入和过滤，避免直接通过 `$`{``}`` 传入外部变量
- 不要自己造轮子，尤其是在安全方面，其实在这个问题上，框架已经提供了标准的方法。如果按照规范开发的话，也不会导致 SQL 注入问题
- 可以注意 MyBatis 中 `targetRuntime` 的配置，如果不需要复杂的条件查询的话，建议直接使用 `MyBatis3Simple`。这样可以更好地直接杜绝风险，因为一旦有风险点，就有发生问题的可能。


## Reference
- [https://blog.csdn.net/Marvel__Dead/article/details/69486947](https://blog.csdn.net/Marvel__Dead/article/details/69486947)
- [https://www.jianshu.com/p/7ef5499d5f60](https://www.jianshu.com/p/7ef5499d5f60)