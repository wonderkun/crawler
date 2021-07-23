> 原文链接: https://www.anquanke.com//post/id/172803 


# Spring Security学习笔记（一）基础介绍I


                                阅读量   
                                **198310**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01cac4202fffde6585.png)](https://p4.ssl.qhimg.com/t01cac4202fffde6585.png)



作者：Dayeh@小米安全中心 首席音乐家

## Spring Security 5.1.4 RELEASE

对于使用Java进行开发的同学来说，Spring算是一个比较热门的选择，包括现在流行的Spring Boot更是能快速上手，并让开发者更好的关注业务核心的开发，而免去了原来冗杂的配置过程。从Spring 4开始推荐使用代码进行配置，更是降低了配置的难度，远离了让人看得头大的xml配置文件。

这篇文章主要想系统的介绍一下Spring Security这个框架。当需要进行一些认证授权的开发时，常用的Java安全框架主要有Apache Shiro和Spring Security。两者相比，Shiro更为轻量化，简单易用，而Spring Security作为Spring的亲儿子，功能更强大，和Spring项目的结合度更好，而使用的学习成本相较于Shiro会略高一些。

在讲代码之前，想先介绍一下Spring Security中的一些基本组件及服务，以便于更好理解后文的代码。基本架构的介绍，主要来自于官方文档，进行了选择性的翻译，参考的版本是Spring Security 5.1.4 RELEASE，感兴趣的同学也可以直接前往阅读英文原文。



## 1 基本架构

### 1.1 核心组件

从Spring Security 3.0开始，组件spring-security-corejar包中的内容进行了精简，不再包含任何web应用安全，LDAP或命名空间配置的代码。

**SecurityContextHolder**

最基本的对象，用来存储当前的安全上下文（security context），包含了当前登录的用户信息。默认使用ThreadLocal保存细节信息，因此这些信息对于同一个线程内容调用的方法都是可用的。当用户的请求处理完成后，框架会自动清理线程而不必用户关心。但是由于某些应用由于其对线程的使用方式，并不适合使用ThreadLocal，则需要根据情况，在启动前设置SecurityContextHolder的策略。

在SecurityContextHolder中保存了当前活跃用户的信息。Spring Security使用一个Authentication对象来表示这些信息。在程序的任何地方，都可以用以下代码来获取当前认证用户的信息。

```
Object principal = SecurityContextHolder.getContext().getAuthentication().getPrincipal();

if (principal instanceof UserDetails) `{`
    String username = ((UserDetails)principal).getUsername();
`}` else `{`
    String username = principal.toString();
`}`
```

**UserDetailsService**

在接口UserDetailService中只有一个方法，接收一个字符串返回一个UserDetails对象，当认证成功后，UserDetails会被用来构造一个Authentication对象保存在SecurityContextHolder中。

```
UserDetails loadUserByUsername(String username) throws UsernameNotFoundException;
```

UserDetailsService的实现，主要是用来加载用户信息，并向其他组件提供这些信息，并不能进行认证用户的操作，认证的操作由AuthenticationManager完成。

如果用户想自定义一个认证流程，则需要实现AuthenticationProvider接口。

**GrantedAuthority**

Authentication的getAuthorities( )方法返回GrantedAuthority的对象数组。GrantAuthority对象一般由UserDetailsService加载。

**总结**

ScurityContextHolder获取SecurityContext

SecurityContext保存了Authentication以及其他一些请求相关的安全信息

Authentication表示一个认证用户信息

GrantedAuthority表示授予用户的权限信息

UserDetails包含了构建Authentication对象需要的必要信息，这些信息来自于应用的DAO或其他数据源

UserDetailsService根据传入用户名字符串构建一个UserDetails对象

### 1.2 认证环节

一个基本的认证环节包括：
1. 用户输入用户名和密码
1. 系统验证用户名密码正确
1. 系统获取该用户的角色、权限等信息。
以上三个步骤完成了一个认证过程，在Spring Security中，相应地完成了以下动作：
1. 后端获取到用户名和密码并用之生成一个UsernamePasswordAuthenticationToken对象，UsernamePasswordAuthenticationToken是Authentication的一个实现类。
1. token被传入AuthenticationManager的实例中进行校验
1. 认证成功后，AuthenticationManager会返回一个Authentication实例，其中包括了用户所有细节信息，包括角色、权限等
1. 通过调用SecurityContextHolder.getContext().setAuthentication(…)建立安全上下文，传入Authentication对象
完成以上过程后，当前用户认证完成。以下代码示范了一个认证环节最基本的流程（并非SpringSecurity框架源码）

```
import org.springframework.security.authentication.*;
import org.springframework.security.core.*;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;

public class AuthenticationExample `{`

// 0. 创建一个AuthenticationManager实例，之后用于用户校验 (具体实现在下方)  
private static AuthenticationManager am = new SampleAuthenticationManager();

public static void main(String[] args) throws Exception `{`
    BufferedReader in = new BufferedReader(new InputStreamReader(System.in));

    // 1. 用户在界面输入用户名密码
    while(true) `{`
    System.out.println("Please enter your username:");
    String name = in.readLine();
    System.out.println("Please enter your password:");
    String password = in.readLine();

    try `{`
        // 2. 用户名和密码生成一个UsernamePasswordAuthenticationToken对象
        Authentication request = new UsernamePasswordAuthenticationToken(name, password);

        // 3. 使用AuthenticationManager实例校验token
        Authentication result = am.authenticate(request);

        // 4. 校验成功，将包含用户信息的Authentication实例加入security context
        SecurityContextHolder.getContext().setAuthentication(result);
        break;
    `}` catch(AuthenticationException e) `{`
        // 认证失败，捕获异常
        System.out.println("Authentication failed: " + e.getMessage());
    `}`
    `}`
    System.out.println("Successfully authenticated. Security context contains: " +
            SecurityContextHolder.getContext().getAuthentication());
`}`
`}`


// AuthenticationManager的实现
class SampleAuthenticationManager implements AuthenticationManager `{`
static final List&lt;GrantedAuthority&gt; AUTHORITIES = new ArrayList&lt;GrantedAuthority&gt;();

static `{`
    AUTHORITIES.add(new SimpleGrantedAuthority("ROLE_USER"));
`}`

public Authentication authenticate(Authentication auth) throws AuthenticationException `{`

    //该方法内写认证通过的条件，此处demo判断条件是，用户名等于密码即认证通过
    if (auth.getName().equals(auth.getCredentials())) `{`
    return new UsernamePasswordAuthenticationToken(auth.getName(),
        auth.getCredentials(), AUTHORITIES);
    `}`
    throw new BadCredentialsException("Bad Credentials");
`}`
`}`
```

**直接设置SecurityContextHolder**

Spring Security并不关心一个Authentication实例是如何放进SecurityContextHolder的，只要保证在SecurityContextHolder中有一个有效的Authentication表示一个认证的用户即可，然后AbstractSecurityInterceptor便可用来授权用户的操作了。因此，开发者亦可选择使用其他认证框架提供的认证信息。开发者只需要写使用一个过滤器获取来自第三方的用户信息，然后构造一个Authentication对象放入到SecurityContextHolder即可。但是如果不使用内置的认证，有些原本自动完成的事情就需要由开发者来处理了，比如需要在一开始创建HTTP session来缓存上下文。

### 1.3 Web应用中的认证

在处理Web应用中的认证，Spring Security中主要参与的有ExceptionTranslationFilter和AuthenticationEntryPoint，以及一个认证机制，用来调用AuthenticationManager完成核心的认证部分。

**ExceptionTranslationFilter**

是一个Spring Security的过滤器，用来检测所有抛出的Spring Security的异常，通常这些异常都由AbstractSecurityInterceptor抛出。AbstractSecurityInterceptor只负责抛出异常，而ExceptionTranslationFilter则负责确定如何处理异常，比如当前用户认证了但权限不够，则返回403错误码，或者当前用户还未认证，则发起一个AuthenticationPoint。

**Authentication Mechanism**

当浏览器提交用户的认证信息后，服务器需要收集这些信息，而在Spring Security中，从客户端获取认证信息的功能称为“认证机制” (authentication mechanism)。比如Basic authentication，当收集到客户端提交的认证信息后，后端就会创建一个Authentication对象，然后交给AuthenticationManager校验。

随后authentication mechanism会收到一个包含完整信息的Authentication对象，并认为请求合法，然后把Authentication放入SecurityContextHolder，随后原请求便会发起重试。如果AuthenticationManager拒绝了请求，那么认证机制便会要求客户端重试。

**保存用户认证信息**

一般在一个Web应用中，用户登录后，服务器会缓存用户的认证信息，用户后续的操作通过其session id进行身份认证。Spring Security框架中，保存SecurityContext的任务交给SecurityContextPersistenceFilter，其默认将安全上下文信息保存为HttpSessio属性。每当请求来，它都会通过SecurityContextHolder来获取认证信息，并在请求结束后，清除SecurityContextHolder。出于安全考虑，不要直接从HttpSession中去获取安全上下文，而应该通过SecurityContextHolder获取。

### 1.4 权限控制（授权）

Spring Security的权限控制，依赖于AOP。权限控制可以应用在方法调用上，也可用在web请求上。Spring Security中主要负责进行权限控制决定的是AccessDecisionManager。

**Secure Objects**

安全对象指一切可以加上安全配置的对象，最常见的例子是方法的调用和web请求。

每个支持的安全对象都有一个自己的拦截器，这个拦截器是AbstractSecurityInterceptor子类，当AbstractSecurityInterceptor被调用的时候，SecurityContextHolder中会包含一个有效的Authentication对象，如果当前用户主体已经被认证。AbstractSecurityInterceptor在处理安全对象的请求时候，流程如下：
1. 查看和当前请求关联的配置属性(configuration attributes)
1. 将当前的安全对象、Authentication对象以及配置属性提交给AccessDecisionManager，由其做一个授权的决定。
1. 在调用发生的位置可选的更换Authentication对象
1. 完成授权后，允许安全对象的调用进行。
1. 当调用返回后，即刻调用AfterInvocationManager（如果配置了）
**Configuration Attributes**

配置属性用接口ConfigAttribute表示，可以理解为被AbstractSecurityInterceptor使用的具有特殊意义的字符串。AbsractSecurityInterceptor中配置了SecurityMetadataSource用来查看安全对象的配置属性。配置属性可以用来简单表示一个角色名，或者更复杂的意义，它的用处取决于AccessDecisionManager实现的复杂性。或者简单来说，配置属性只是表示特殊含义的，比如角色名的字符串，但是其具体如何解读，取决于AccessDedcisionManager的实现。举个简单得例子，当我们使用默认的AccessDedcisionManager的实现时，可以在一个方法或者一个url请求的注释里加入配置属性ROLE_A，这表示，只有当用户的GrantedAuthority匹配ROLE_A的时候，才被允许使用这个方法或调用这个请求。这里只做简单得说明，具体使用在后文中展开。

**Security interceptors and the “secure object” model**

下图是安全拦截器和安全对象的模型，给出了各个组件之间的关系，有个别组件在简介中没有提到，将在后文的使用说明中展开。

[![](https://p0.ssl.qhimg.com/t0190d85a50ba27b6cd.png)](https://p0.ssl.qhimg.com/t0190d85a50ba27b6cd.png)
