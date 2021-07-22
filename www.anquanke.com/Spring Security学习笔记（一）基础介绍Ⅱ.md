> 原文链接: https://www.anquanke.com//post/id/173029 


# Spring Security学习笔记（一）基础介绍Ⅱ


                                阅读量   
                                **221350**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01260b0ad92efef646.png)](https://p5.ssl.qhimg.com/t01260b0ad92efef646.png)

[Spring Security学习笔记（一）基础介绍I](https://www.anquanke.com/post/id/172803)

作者：Dayeh@小米安全中心 首席音乐家

## Spring Security 5.1.4 RELEASE

书接上文，在上一篇中介绍了Spring Security的基本组件以及基本的认证流程，此篇介绍一下Spring Security的一些核心服务。



## 2 核心服务

Spring Security中还有许多十分重要的接口，特别是AuthenticationManager, UserDetailsService 和AccessDecisionManager，Spring Security提供了一些实现，用户亦可自己实现定制的认证授权机制。下面我们来具体看一下几个接口及Spring Security提供的实现，从而有助于了解在认证授权环节中它们的具体作用，以及如何使用。

### 2.1 AuthenticationManager, ProviderManager and AuthenticationProvider

AuthenticationManger是一个接口，用来完成认证的逻辑，开发者可按照自己的项目设计需求进行实现。如果，我们希望能够组合使用多种认证服务，比如基于数据库和LDAP服务器的认证服务，Spring Security也是支持的。

ProviderManager是Spring Security提供的一个实现，但是它本身不处理认证请求，而是将任务委托给一个配置好的AuthenticationProvider的列表，其中每一个AuthenticationProvider按序确认能否完成认证，每个provider如果认证失败，会抛出一个异常，如果认证通过，则会返回一个Authentication对象。

**AuthenticationManager**

AuthenticationManger是一个接口，其中只有一个方法authenticate，用来尝试对传入的Authentication对象进行认证。

这里保留了源码中的一大段注释，其中包括了该接口的作用，以及在实现时应当注意的一些问题，这里不多做叙述，我们目前只需要了解这个接口的作用即可，感兴趣的同学可以自行阅读源码中的注释。

```
/**
 * Processes an `{`@link Authentication`}` request.
 *
 * @author Ben Alex
 */
public interface AuthenticationManager `{`
    // ~ Methods
    // ========================================================================================================

    /**
     * Attempts to authenticate the passed `{`@link Authentication`}` object, returning a
     * fully populated &lt;code&gt;Authentication&lt;/code&gt; object (including granted authorities)
     * if successful.
     * &lt;p&gt;
     * An &lt;code&gt;AuthenticationManager&lt;/code&gt; must honour the following contract concerning
     * exceptions:
     * &lt;ul&gt;
     * &lt;li&gt;A `{`@link DisabledException`}` must be thrown if an account is disabled and the
     * &lt;code&gt;AuthenticationManager&lt;/code&gt; can test for this state.&lt;/li&gt;
     * &lt;li&gt;A `{`@link LockedException`}` must be thrown if an account is locked and the
     * &lt;code&gt;AuthenticationManager&lt;/code&gt; can test for account locking.&lt;/li&gt;
     * &lt;li&gt;A `{`@link BadCredentialsException`}` must be thrown if incorrect credentials are
     * presented. Whilst the above exceptions are optional, an
     * &lt;code&gt;AuthenticationManager&lt;/code&gt; must &lt;B&gt;always&lt;/B&gt; test credentials.&lt;/li&gt;
     * &lt;/ul&gt;
     * Exceptions should be tested for and if applicable thrown in the order expressed
     * above (i.e. if an account is disabled or locked, the authentication request is
     * immediately rejected and the credentials testing process is not performed). This
     * prevents credentials being tested against disabled or locked accounts.
     *
     * @param authentication the authentication request object
     *
     * @return a fully authenticated object including credentials
     *
     * @throws AuthenticationException if authentication fails
     */
    Authentication authenticate(Authentication authentication)
            throws AuthenticationException;
`}`
```

**ProviderManager**

ProviderManager是Authentication的一个实现，并将具体的认证操作委托给一系列的AuthenticationProvider来完成，从而可以实现支持多种认证方式。为了帮助阅读和理解源码具体做了什么，这里删除了原来的一部分注释，并对重要的部分进行了注释说明。

```
public class ProviderManager implements AuthenticationManager, MessageSourceAware,
        InitializingBean `{`

    private static final Log logger = LogFactory.getLog(ProviderManager.class);

    private AuthenticationEventPublisher eventPublisher = new NullEventPublisher();
    private List&lt;AuthenticationProvider&gt; providers = Collections.emptyList();
    protected MessageSourceAccessor messages = SpringSecurityMessageSource.getAccessor();
    private AuthenticationManager parent;
    private boolean eraseCredentialsAfterAuthentication = true;

    /**
     * 用List&lt;AuthenticationProvider&gt;初始化一个ProviderManager
     * 也就是上文提到的，ProviderManager将具体的认证委托给不同的provider，从而支持不同的认证方式
     */      
    public ProviderManager(List&lt;AuthenticationProvider&gt; providers) `{`
        this(providers, null);
    `}`

    /**
     * 也可以为其设置一个父类
     */
    public ProviderManager(List&lt;AuthenticationProvider&gt; providers,
            AuthenticationManager parent) `{`
        Assert.notNull(providers, "providers list cannot be null");
        this.providers = providers;
        this.parent = parent;
        checkState();
    `}`

    public void afterPropertiesSet() throws Exception `{`
        checkState();
    `}`

    private void checkState() `{`
        if (parent == null &amp;&amp; providers.isEmpty()) `{`
            throw new IllegalArgumentException(
                    "A parent AuthenticationManager or a list "
                            + "of AuthenticationProviders is required");
        `}`
    `}`

    /**
     * ProviderManager的核心方法，authentication方法尝试对传入的Authentication对象进行认证，传入的Authentication是
     * 以用户的提交的认证信息，比如用户名和密码，创建的一个Authentication对象。
     * 
     * 会依次询问各个AuthenticationProvider，当provider支持对传入的Authentication认证，
     * 便会尝试使用该provider进行认证。如果有多个provider都支持认证传入的Authentication对象，
     * 则只会使用第一个支持的provider进行认证。
     *
     * 一旦有一个provider认证成功了，便会忽略之前任何provider抛出的异常，之后的provider也不会再
     * 继续认证的尝试。
     *
     * 如果所有provider都认证失败，方法则会抛出最后一个provider抛出的异常。
     */
    public Authentication authenticate(Authentication authentication)
            throws AuthenticationException `{`
        Class&lt;? extends Authentication&gt; toTest = authentication.getClass();
        AuthenticationException lastException = null;
        AuthenticationException parentException = null;
        Authentication result = null;
        Authentication parentResult = null;
        boolean debug = logger.isDebugEnabled();

        // 依次使用各个provider尝试进行认证
        for (AuthenticationProvider provider : getProviders()) `{`
            // 如果provider不支持对传入的Authentication进行认证，则跳过。
            if (!provider.supports(toTest)) `{`
                continue;
            `}`

            if (debug) `{`
                logger.debug("Authentication attempt using "
                        + provider.getClass().getName());
            `}`

            try `{`
                // 调用provider的authenticate方法进行认证
                result = provider.authenticate(authentication);

                // 如果认证成功，则将authentication中用户的细节信息复制到result中
                // 然后跳出循环，不再尝试后面其他的provider
                if (result != null) `{`
                    copyDetails(authentication, result);
                    break;
                `}`
            `}`
            catch (AccountStatusException e) `{`
                prepareException(e, authentication);
                // 如果待认证的账号信息无误，但是账号本身异常，比如账号停用了，则抛出AccountStatusException异常，
                // 并通过prepareException方法，发布一个AbstractAuthenticationFailureEvent，避免继续尝试其他provider进行认证
                throw e;
            `}`
            catch (InternalAuthenticationServiceException e) `{`
                prepareException(e, authentication);
                throw e;
            `}`
            catch (AuthenticationException e) `{`
                // 如果该provider认证失败，捕获异常AuthenticationException后不抛出，继续尝试下一个provider
                // lastException会记录下最后一个认证失败的provider抛出的AuthenticationException异常。
                lastException = e;
            `}`
        `}`

        if (result == null &amp;&amp; parent != null) `{`
            // 如果所有provider都没能认证成功，则交给父类尝试认证
            try `{`
                result = parentResult = parent.authenticate(authentication);
            `}`
            catch (ProviderNotFoundException e) `{`
                // 父类如果抛出该异常不做处理，因为后面有对子类抛出该异常的处理
            `}`
            catch (AuthenticationException e) `{`
                // 父类也没能认证成功，则最后一个异常为来自父类认证失败的异常
                lastException = parentException = e;
            `}`
        `}`

        if (result != null) `{`
            if (eraseCredentialsAfterAuthentication
                    &amp;&amp; (result instanceof CredentialsContainer)) `{`
                // 认证成功，从Authentication中删除密码秘钥等敏感信息
                ((CredentialsContainer) result).eraseCredentials();
            `}`

            // 如果父类认证成功，则会发布一个AuthenticationSuccessEvent，
            // 这一步检查，防止子类重复发布
            if (parentResult == null) `{`
                eventPublisher.publishAuthenticationSuccess(result);
            `}`

            //返回的result为一个Authentication，其中包含了已认证用户的信息
            return result;

        `}`

        if (lastException == null) `{`
            lastException = new ProviderNotFoundException(messages.getMessage(
                    "ProviderManager.providerNotFound",
                    new Object[] `{` toTest.getName() `}`,
                    "No AuthenticationProvider found for `{`0`}`"));
        `}`

        // 如果父类认证失败，会发布一个AbstractAuthenticationFailureEvent
        // 这一步检查，防止子类重复发布
        if (parentException == null) `{`
            prepareException(lastException, authentication);
        `}`

        throw lastException;
    `}`

    @SuppressWarnings("deprecation")
    private void prepareException(AuthenticationException ex, Authentication auth) `{`
        eventPublisher.publishAuthenticationFailure(ex, auth);
    `}`

    /**
     * 从source中复制用户的信息到dest
     *
     * Copies the authentication details from a source Authentication object to a
     * destination one, provided the latter does not already have one set.
     *
     * @param source source authentication
     * @param dest the destination authentication object
     */
    private void copyDetails(Authentication source, Authentication dest) `{`
        if ((dest instanceof AbstractAuthenticationToken) &amp;&amp; (dest.getDetails() == null)) `{`
            AbstractAuthenticationToken token = (AbstractAuthenticationToken) dest;

            token.setDetails(source.getDetails());
        `}`
    `}`

    public List&lt;AuthenticationProvider&gt; getProviders() `{`
        return providers;
    `}`

    public void setMessageSource(MessageSource messageSource) `{`
        this.messages = new MessageSourceAccessor(messageSource);
    `}`

    public void setAuthenticationEventPublisher(
            AuthenticationEventPublisher eventPublisher) `{`
        Assert.notNull(eventPublisher, "AuthenticationEventPublisher cannot be null");
        this.eventPublisher = eventPublisher;
    `}`

    /**
     * 设置是否要在认证完成后，让Authentication调用自己的eraseCredentials方法来清除密码信息。
     *
     * If set to, a resulting `{`@code Authentication`}` which implements the
     * `{`@code CredentialsContainer`}` interface will have its
     * `{`@link CredentialsContainer#eraseCredentials() eraseCredentials`}` method called
     * before it is returned from the `{`@code authenticate()`}` method.
     *
     * @param eraseSecretData set to `{`@literal false`}` to retain the credentials data in
     * memory. Defaults to `{`@literal true`}`.
     */
    public void setEraseCredentialsAfterAuthentication(boolean eraseSecretData) `{`
        this.eraseCredentialsAfterAuthentication = eraseSecretData;
    `}`

    public boolean isEraseCredentialsAfterAuthentication() `{`
        return eraseCredentialsAfterAuthentication;
    `}`

    private static final class NullEventPublisher implements AuthenticationEventPublisher `{`
        public void publishAuthenticationFailure(AuthenticationException exception,
                Authentication authentication) `{`
        `}`

        public void publishAuthenticationSuccess(Authentication authentication) `{`
        `}`
    `}`
`}`
```

至此可以看到，ProviderManager的认证逻辑还是很简单清晰的，我们也可以比较清楚理解AuthenticationManager，ProviderManager和AuthenticationProvider的关系了。

**AuthenticationProvider**

AuthenticationProvider也是一个接口，用来完成具体的认证逻辑。不同的认证方式有不同的实现，Spring Security中提供了多种实现，包括DaoAuthenticationProvider,AnonymousAuthenticationProvider和LdapAuthenticationProvider等。其中最简单的DaoAuthenticationProvider会在后面介绍，首先来看一下AuthenticationProvider的源码。同样的，保留了源码中的注释，感兴趣的同学可以细读，这里只做简单的介绍。

可以看到，AuthenticationProvider中只有2个方法：
- authenticate完成具体的认证逻辑，如果认证失败，抛出AuthenticationException异常
- supports判断是否支持传入的Authentication认证信息
```
/**
 * Indicates a class can process a specific
 * `{`@link org.springframework.security.core.Authentication`}` implementation.
 *
 * @author Ben Alex
 */
public interface AuthenticationProvider `{`
    // ~ Methods
    // ========================================================================================================
​
    /**
     * Performs authentication with the same contract as
     * `{`@link org.springframework.security.authentication.AuthenticationManager#authenticate(Authentication)`}`
     * .
     *
     * @param authentication the authentication request object.
     *
     * @return a fully authenticated object including credentials. May return
     * &lt;code&gt;null&lt;/code&gt; if the &lt;code&gt;AuthenticationProvider&lt;/code&gt; is unable to support
     * authentication of the passed &lt;code&gt;Authentication&lt;/code&gt; object. In such a case,
     * the next &lt;code&gt;AuthenticationProvider&lt;/code&gt; that supports the presented
     * &lt;code&gt;Authentication&lt;/code&gt; class will be tried.
     *
     * @throws AuthenticationException if authentication fails.
     */
    Authentication authenticate(Authentication authentication)
            throws AuthenticationException;
​
    /**
     * Returns &lt;code&gt;true&lt;/code&gt; if this &lt;Code&gt;AuthenticationProvider&lt;/code&gt; supports the
     * indicated &lt;Code&gt;Authentication&lt;/code&gt; object.
     * &lt;p&gt;
     * Returning &lt;code&gt;true&lt;/code&gt; does not guarantee an
     * &lt;code&gt;AuthenticationProvider&lt;/code&gt; will be able to authenticate the presented
     * instance of the &lt;code&gt;Authentication&lt;/code&gt; class. It simply indicates it can
     * support closer evaluation of it. An &lt;code&gt;AuthenticationProvider&lt;/code&gt; can still
     * return &lt;code&gt;null&lt;/code&gt; from the `{`@link #authenticate(Authentication)`}` method to
     * indicate another &lt;code&gt;AuthenticationProvider&lt;/code&gt; should be tried.
     * &lt;/p&gt;
     * &lt;p&gt;
     * Selection of an &lt;code&gt;AuthenticationProvider&lt;/code&gt; capable of performing
     * authentication is conducted at runtime the &lt;code&gt;ProviderManager&lt;/code&gt;.
     * &lt;/p&gt;
     *
     * @param authentication
     *
     * @return &lt;code&gt;true&lt;/code&gt; if the implementation can more closely evaluate the
     * &lt;code&gt;Authentication&lt;/code&gt; class presented
     */
    boolean supports(Class&lt;?&gt; authentication);
`}`
```

**DaoAuthenticationProvider**

DaoAuthenticationProvider是Spring Security提供的最简单的一个AuthenticationProvider的实现，也是框架中最早支持的。它使用UserDetailsService作为一个DAO来查询用户名、密码以及用户的权限GrantedAuthority。它认证用户的方式就是简单的比较UsernamePasswordAuthenticationToken中由用户提交的密码和通过UserDetailsService查询获得的密码是否一致。

下面我们来看一下DaoAuthenticationProvider的源码，对于源码的说明也写在了注释中。

DaoAuthenticationProvider继承了AbstractUserDetailsAuthenticationProvider，而后者实现了AuthenticationProvider接口。

```
public class DaoAuthenticationProvider extends AbstractUserDetailsAuthenticationProvider `{`

    /**
     * The plaintext password used to perform
     * PasswordEncoder#matches(CharSequence, String)`}`  on when the user is
     * not found to avoid SEC-2056.
     */
    private static final String USER_NOT_FOUND_PASSWORD = "userNotFoundPassword";

    private PasswordEncoder passwordEncoder;

    /**
     * The password used to perform
     * `{`@link PasswordEncoder#matches(CharSequence, String)`}` on when the user is
     * not found to avoid SEC-2056. This is necessary, because some
     * `{`@link PasswordEncoder`}` implementations will short circuit if the password is not
     * in a valid format.
     */
    private volatile String userNotFoundEncodedPassword;

    private UserDetailsService userDetailsService;

    private UserDetailsPasswordService userDetailsPasswordService;

    public DaoAuthenticationProvider() `{`
        setPasswordEncoder(PasswordEncoderFactories.createDelegatingPasswordEncoder());
    `}`

    @SuppressWarnings("deprecation")
    protected void additionalAuthenticationChecks(UserDetails userDetails,
            UsernamePasswordAuthenticationToken authentication)
            throws AuthenticationException `{`

        // 用户未提交密码，抛出异常BadCredentialsException
        if (authentication.getCredentials() == null) `{`
            logger.debug("Authentication failed: no credentials provided");

            throw new BadCredentialsException(messages.getMessage(
                    "AbstractUserDetailsAuthenticationProvider.badCredentials",
                    "Bad credentials"));
        `}`

        // 从传入了Authentication对象中获取用户提交的密码
        String presentedPassword = authentication.getCredentials().toString();

        // 用passwordEncoder的matches方法，比较用户提交的密码和userDetails中查询到的正确密码。
        // 由于用户密码的存放一般都是hash后保密的，因此userDetails获取到的密码一般是一个hash值，而用户提交
        // 的是一个明文密码，因此需要对用户提交的密码进行同样的hash计算后再进行比较。
        if (!passwordEncoder.matches(presentedPassword, userDetails.getPassword())) `{`
            logger.debug("Authentication failed: password does not match stored value");

            throw new BadCredentialsException(messages.getMessage(
                    "AbstractUserDetailsAuthenticationProvider.badCredentials",
                    "Bad credentials"));
        `}`
    `}`

    protected void doAfterPropertiesSet() throws Exception `{`
        Assert.notNull(this.userDetailsService, "A UserDetailsService must be set");
    `}`

    protected final UserDetails retrieveUser(String username,
            UsernamePasswordAuthenticationToken authentication)
            throws AuthenticationException `{`
        prepareTimingAttackProtection();
        try `{`
            UserDetails loadedUser = this.getUserDetailsService().loadUserByUsername(username);
            if (loadedUser == null) `{`
                throw new InternalAuthenticationServiceException(
                        "UserDetailsService returned null, which is an interface contract violation");
            `}`
            return loadedUser;
        `}`
        catch (UsernameNotFoundException ex) `{`
            mitigateAgainstTimingAttack(authentication);
            throw ex;
        `}`
        catch (InternalAuthenticationServiceException ex) `{`
            throw ex;
        `}`
        catch (Exception ex) `{`
            throw new InternalAuthenticationServiceException(ex.getMessage(), ex);
        `}`
    `}`

    @Override
    protected Authentication createSuccessAuthentication(Object principal,
            Authentication authentication, UserDetails user) `{`
        boolean upgradeEncoding = this.userDetailsPasswordService != null
                &amp;&amp; this.passwordEncoder.upgradeEncoding(user.getPassword());
        if (upgradeEncoding) `{`
            String presentedPassword = authentication.getCredentials().toString();
            String newPassword = this.passwordEncoder.encode(presentedPassword);
            user = this.userDetailsPasswordService.updatePassword(user, newPassword);
        `}`
        return super.createSuccessAuthentication(principal, authentication, user);
    `}`

    private void prepareTimingAttackProtection() `{`
        if (this.userNotFoundEncodedPassword == null) `{`
            this.userNotFoundEncodedPassword = this.passwordEncoder.encode(USER_NOT_FOUND_PASSWORD);
        `}`
    `}`

    private void mitigateAgainstTimingAttack(UsernamePasswordAuthenticationToken authentication) `{`
        if (authentication.getCredentials() != null) `{`
            String presentedPassword = authentication.getCredentials().toString();
            this.passwordEncoder.matches(presentedPassword, this.userNotFoundEncodedPassword);
        `}`
    `}`

    /**
     * Sets the PasswordEncoder instance to be used to encode and validate passwords. If
     * not set, the password will be compared using `{`@link PasswordEncoderFactories#createDelegatingPasswordEncoder()`}`
     *
     * @param passwordEncoder must be an instance of one of the `{`@code PasswordEncoder`}`
     * types.
     */
    public void setPasswordEncoder(PasswordEncoder passwordEncoder) `{`
        Assert.notNull(passwordEncoder, "passwordEncoder cannot be null");
        this.passwordEncoder = passwordEncoder;
        this.userNotFoundEncodedPassword = null;
    `}`

    protected PasswordEncoder getPasswordEncoder() `{`
        return passwordEncoder;
    `}`

    public void setUserDetailsService(UserDetailsService userDetailsService) `{`
        this.userDetailsService = userDetailsService;
    `}`

    protected UserDetailsService getUserDetailsService() `{`
        return userDetailsService;
    `}`

    public void setUserDetailsPasswordService(
            UserDetailsPasswordService userDetailsPasswordService) `{`
        this.userDetailsPasswordService = userDetailsPasswordService;
    `}`
`}`
```

**AbstractUserDetailsAuthenticationProvider**

可以看到DaoAuthenticationProvider继承自AbstractUserDetailsAuthenticationProvider, 而一个provider最核心的authenticate方法，便写在了AbstractUserDetailsAuthenticationProvider中，下面我们只关注一下authenticate这个方法的源码。

```
public Authentication authenticate(Authentication authentication)
            throws AuthenticationException `{`
        Assert.isInstanceOf(UsernamePasswordAuthenticationToken.class, authentication,
                () -&gt; messages.getMessage(
                        "AbstractUserDetailsAuthenticationProvider.onlySupports",
                        "Only UsernamePasswordAuthenticationToken is supported"));

        // 从传入的Authentication对象中获取用户名
        String username = (authentication.getPrincipal() == null) ? "NONE_PROVIDED"
                : authentication.getName();

        // 根据用户名，从缓存中获取用户的UserDetails
        boolean cacheWasUsed = true;
        UserDetails user = this.userCache.getUserFromCache(username);

        if (user == null) `{`
            cacheWasUsed = false;
            // 如果从缓存中没有获取到用户，则通过方法retrieveUser来获取用户信息
            // retrieve方法为一个抽象方法，不同的子类中有不同的实现，而在子类中，一般又会通过UserDetailService来获取用户信息，返回UserDetails
            try `{`
                user = retrieveUser(username,
                        (UsernamePasswordAuthenticationToken) authentication);
            `}`
            catch (UsernameNotFoundException notFound) `{`
                logger.debug("User '" + username + "' not found");

                if (hideUserNotFoundExceptions) `{`
                    throw new BadCredentialsException(messages.getMessage(
                            "AbstractUserDetailsAuthenticationProvider.badCredentials",
                            "Bad credentials"));
                `}`
                else `{`
                    throw notFound;
                `}`
            `}`

            Assert.notNull(user,
                    "retrieveUser returned null - a violation of the interface contract");
        `}`

        try `{`
            preAuthenticationChecks.check(user);
            // additionalAuthenticationChecks为具体的认证逻辑，是一个抽象方法，在子类中实现。
            // 比如前文中DaoAuthenticationProvider中，便是比较用户提交的密码和UserDetails中的密码
            additionalAuthenticationChecks(user,
                    (UsernamePasswordAuthenticationToken) authentication);
        `}`
        catch (AuthenticationException exception) `{`
            if (cacheWasUsed) `{`
                // There was a problem, so try again after checking
                // we're using latest data (i.e. not from the cache)
                cacheWasUsed = false;
                user = retrieveUser(username,
                        (UsernamePasswordAuthenticationToken) authentication);
                preAuthenticationChecks.check(user);
                additionalAuthenticationChecks(user,
                        (UsernamePasswordAuthenticationToken) authentication);
            `}`
            else `{`
                throw exception;
            `}`
        `}`

        postAuthenticationChecks.check(user);

        if (!cacheWasUsed) `{`
            this.userCache.putUserInCache(user);
        `}`

        Object principalToReturn = user;

        if (forcePrincipalAsString) `{`
            principalToReturn = user.getUsername();
        `}`

        return createSuccessAuthentication(principalToReturn, authentication, user);
    `}`
```

可以看到在DaoAuthenticationProvider中还用到UserDetailsService来查询用户的密码权限信息，并包装为UserDetails返回，然后与用户提交的用户名密码信息进行比较来完成认证。UserDetailsService和UserDetails在不同的provider中都会被用到，关于这两个接口的说明，在下一篇文章中介绍。



## 总结

最后我们总结一下这几个接口和类

[![](https://p3.ssl.qhimg.com/t01bab1641205acb087.png)](https://p3.ssl.qhimg.com/t01bab1641205acb087.png)

这些类和接口之间的关系，大致可以用下图进行表示

[![](https://p4.ssl.qhimg.com/t011366421e39280ef2.png)](https://p4.ssl.qhimg.com/t011366421e39280ef2.png)
