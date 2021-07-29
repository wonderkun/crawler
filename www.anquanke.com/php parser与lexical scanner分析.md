> 原文链接: https://www.anquanke.com//post/id/247356 


# php parser与lexical scanner分析


                                阅读量   
                                **15047**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01c1da609a111c054a.jpg)](https://p4.ssl.qhimg.com/t01c1da609a111c054a.jpg)



## 前言

目的：学习语义分析工具的编写原理从而实现自己编写语义分析工具。

读完本文只需要记得phpparser基于zend’s lexical scanner，zend’s lexical scanner基于re2c。下一次我们会分析一下re2c看看究竟抽象化是怎么通过代码实现的。



## 简单的例子入手

从readme中的例子入手

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E6%8A%BD%E8%B1%A1%E5%8C%96"></a>抽象化

```
&lt;?php
use PhpParser\Error;
use PhpParser\NodeDumper;
use PhpParser\ParserFactory;

$code = &lt;&lt;&lt;'CODE'
&lt;?php

function test($foo)
`{`
    var_dump($foo);
`}`
CODE;

$parser = (new ParserFactory)-&gt;create(ParserFactory::PREFER_PHP7);
try `{`
    $ast = $parser-&gt;parse($code);
`}` catch (Error $error) `{`
    echo "Parse error: `{`$error-&gt;getMessage()`}`\n";
    return;
`}`

$dumper = new NodeDumper;
echo $dumper-&gt;dump($ast) . "\n";

?&gt;
```

首先引用了Error NodeDumper ParserFactory

code是\&lt;? php function test($foo)`{` var_dump($foo);`}`?&gt;

new一个parserfactory执行create

那么我们打开parserfactory文件查看create函数

函数原型是public function create(int $kind, Lexer $lexer = null, array $parserOptions = []) : Parser `{`

同时文件开头定义PHP7为1

也就是kind=1

进入函数内部，lexer=null所以new一个emulative

switch return new multiple参数是new php7和 php5

php7参数是lexer 和parseroptions

lexer=new emulative parseroptions=null

所以parser的值是multiple

然后下一句 ast = parser-&gt;parse(code)

转到parser，函数原型public function parse(string $code, ErrorHandler $errorHandler = null)：

```
public function parse(string $code, ErrorHandler $errorHandler = null) `{`
        if (null === $errorHandler) `{`
            $errorHandler = new ErrorHandler\Throwing;
        `}`

        list($firstStmts, $firstError) = $this-&gt;tryParse($this-&gt;parsers[0], $errorHandler, $code);
        if ($firstError === null) `{`
            return $firstStmts;
        `}`

        for ($i = 1, $c = count($this-&gt;parsers); $i &lt; $c; ++$i) `{`
            list($stmts, $error) = $this-&gt;tryParse($this-&gt;parsers[$i], $errorHandler, $code);
            if ($error === null) `{`
                return $stmts;
            `}`
        `}`

        throw $firstError;
    `}`
```

调用tryparse函数，调用parserabstract的parse函数。

```
public function parse(string $code, ErrorHandler $errorHandler = null) `{`
        $this-&gt;errorHandler = $errorHandler ?: new ErrorHandler\Throwing;

​    $this-&gt;lexer-&gt;startLexing($code, $this-&gt;errorHandler);
​    $result = $this-&gt;doParse();

​    // Clear out some of the interior state, so we don't hold onto unnecessary
​    // memory between uses of the parser
​    $this-&gt;startAttributeStack = [];
​    $this-&gt;endAttributeStack = [];
​    $this-&gt;semStack = [];
​    $this-&gt;semValue = null;

​    return $result;
`}`
```

调用lexer的startlexing

```
public function startLexing(string $code, ErrorHandler $errorHandler = null) `{`
        if (null === $errorHandler) `{`
            $errorHandler = new ErrorHandler\Throwing();
        `}`

​    $this-&gt;code = $code; // keep the code around for __halt_compiler() handling
​    $this-&gt;pos  = -1;
​    $this-&gt;line =  1;
​    $this-&gt;filePos = 0;

​    // If inline HTML occurs without preceding code, treat it as if it had a leading newline.
​    // This ensures proper composability, because having a newline is the "safe" assumption.
​    $this-&gt;prevCloseTagHasNewline = true;

​    $scream = ini_set('xdebug.scream', '0');

​    $this-&gt;tokens = @token_get_all($code);
​    $this-&gt;postprocessTokens($errorHandler);

​    if (false !== $scream) `{`
​        ini_set('xdebug.scream', $scream);
​    `}`
`}`
```

执行token_get_all

使用 Zend 引擎的词汇扫描仪将给定字符串解析为 PHP 语言令牌

实现了将不同格式的代码转换成通用语言令牌。

随后执行postprocesstokens对token进行处理，记录每一部分的位置，并进行划分。

再执行doparse

对每个token都只记录开始和结束。

随后记录状态，和数据流分析一样，要记录每一句代码执行之前的状态和执行之后的状态，而这些状态存储在statestack中，也就是抽象堆中。

随后执行getnexttoken函数，记录代码所在起始和结束行，token起始和结束位置，所在文件起始和结束位置。

随后判断这个token在不在我们当前分析的代码块中，并将token插入到AST中的执行位置

返回结果

最后dump输出结果

```
array(
    0: Stmt_Function(
        byRef: false
        name: Identifier(
            name: test
        )
        params: array(
            0: Param(
                type: null
                byRef: false
                variadic: false
                var: Expr_Variable(
                    name: foo
                )
                default: null
            )
        )
        returnType: null
        stmts: array(
            0: Stmt_Expression(
                expr: Expr_FuncCall(
                    name: Name(
                        parts: array(
                            0: var_dump
                        )
                    )
                    args: array(
                        0: Arg(
                            value: Expr_Variable(
                                name: foo
                            )
                            byRef: false
                            unpack: false
                        )
                    )
                )
            )
        )
    )
)
```

stmt__function记录函数定义，identifier标记name是test，params记录函数参数。Expr_variable表示变量，name记录变量名，stmts是函数内部代码。stmt_expression记录表达式，expr_Funccall表示调用函数，name记录函数名，args记录参数

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%AE%9E%E7%8E%B0"></a>实现

```
use PhpParser\Node;
use PhpParser\Node\Stmt\Function_;
use PhpParser\NodeTraverser;
use PhpParser\NodeVisitorAbstract;

$traverser = new NodeTraverser();
$traverser-&gt;addVisitor(new class extends NodeVisitorAbstract `{`
    public function enterNode(Node $node) `{`
        if ($node instanceof Function_) `{`
            // Clean out the function body
            $node-&gt;stmts = [];
        `}`
    `}`
`}`);

$ast = $traverser-&gt;traverse($ast);
echo $dumper-&gt;dump($ast) . "\n";
```

将抽象函数enternode定义，执行traverse函数

```
public function traverse(array $nodes) : array `{`
        $this-&gt;stopTraversal = false;

​    foreach ($this-&gt;visitors as $visitor) `{`
​        if (null !== $return = $visitor-&gt;beforeTraverse($nodes)) `{`
​            $nodes = $return;
​        `}`
​    `}`

​    $nodes = $this-&gt;traverseArray($nodes);

​    foreach ($this-&gt;visitors as $visitor) `{`
​        if (null !== $return = $visitor-&gt;afterTraverse($nodes)) `{`
​            $nodes = $return;
​        `}`
​    `}`

​    return $nodes;
`}`
```

执行$nodes = $this-&gt;traverseArray($nodes);

```
protected function traverseArray(array $nodes) : array `{`
        $doNodes = [];

​    foreach ($nodes as $i =&gt; &amp;$node) `{`
​        if ($node instanceof Node) `{`
​            $traverseChildren = true;
​            $breakVisitorIndex = null;

​            foreach ($this-&gt;visitors as $visitorIndex =&gt; $visitor) `{`
​                $return = $visitor-&gt;enterNode($node);
​                if (null !== $return) `{`
​                    if ($return instanceof Node) `{`
​                        $this-&gt;ensureReplacementReasonable($node, $return);
​                        $node = $return;
​                    `}` elseif (self::DONT_TRAVERSE_CHILDREN === $return) `{`
​                        $traverseChildren = false;
​                    `}` elseif (self::DONT_TRAVERSE_CURRENT_AND_CHILDREN === $return) `{`
​                        $traverseChildren = false;
​                        $breakVisitorIndex = $visitorIndex;
​                        break;
​                    `}` elseif (self::STOP_TRAVERSAL === $return) `{`
​                        $this-&gt;stopTraversal = true;
​                        break 2;
​                    `}` else `{`
​                        throw new \LogicException(
​                            'enterNode() returned invalid value of type ' . gettype($return)
​                        );
​                    `}`
​                `}`
​            `}`

​            if ($traverseChildren) `{`
​                $node = $this-&gt;traverseNode($node);
​                if ($this-&gt;stopTraversal) `{`
​                    break;
​                `}`
​            `}`

​            foreach ($this-&gt;visitors as $visitorIndex =&gt; $visitor) `{`
​                $return = $visitor-&gt;leaveNode($node);

​                if (null !== $return) `{`
​                    if ($return instanceof Node) `{`
​                        $this-&gt;ensureReplacementReasonable($node, $return);
​                        $node = $return;
​                    `}` elseif (\is_array($return)) `{`
​                        $doNodes[] = [$i, $return];
​                        break;
​                    `}` elseif (self::REMOVE_NODE === $return) `{`
​                        $doNodes[] = [$i, []];
​                        break;
​                    `}` elseif (self::STOP_TRAVERSAL === $return) `{`
​                        $this-&gt;stopTraversal = true;
​                        break 2;
​                    `}` elseif (false === $return) `{`
​                        throw new \LogicException(
​                            'bool(false) return from leaveNode() no longer supported. ' .
​                            'Return NodeTraverser::REMOVE_NODE instead'
​                        );
​                    `}` else `{`
​                        throw new \LogicException(
​                            'leaveNode() returned invalid value of type ' . gettype($return)
​                        );
​                    `}`
​                `}`

​                if ($breakVisitorIndex === $visitorIndex) `{`
​                    break;
​                `}`
​            `}`
​        `}` elseif (\is_array($node)) `{`
​            throw new \LogicException('Invalid node structure: Contains nested arrays');
​        `}`
​    `}`

​    if (!empty($doNodes)) `{`
​        while (list($i, $replace) = array_pop($doNodes)) `{`
​            array_splice($nodes, $i, 1, $replace);
​        `}`
​    `}`

​    return $nodes;
`}`
```

实现进入子节点并记录

其中因为我们补充的enternode是$node-&gt;stmts = [];

所以最终结果是

```
array(
    0: Stmt_Function(
        byRef: false
        name: Identifier(
            name: test
        )
        params: array(
            0: Param(
                type: null
                byRef: false
                variadic: false
                var: Expr_Variable(
                    name: foo
                )
                default: null
            )
        )
        returnType: null
        stmts: array(
        )
    )
)
```

也就是仅仅记录函数本身不包括其中内容和操作。

所以结论就是phpparser的抽象化是由token_get_all实现的，生成AST是其主要部分，代码分析操作由接口实现。

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="Zend%20engine%E2%80%99s%20lexical%20scanner"></a>Zend engine’s lexical scanner

我们看看Zend engine’s lexical scanner的源码，来学习一下词汇扫描仪是怎么抽象化代码的。

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E5%88%9D%E5%A7%8B%E5%8C%96"></a>初始化

```
ZEND_API zend_result open_file_for_scanning(zend_file_handle *file_handle)
`{`
    char *buf;
    size_t size;
    zend_string *compiled_filename;

if (zend_stream_fixup(file_handle, &amp;buf, &amp;size) == FAILURE) `{`
    /* Still add it to open_files to make destroy_file_handle work */
    zend_llist_add_element(&amp;CG(open_files), file_handle);
    file_handle-&gt;in_list = 1;
    return FAILURE;
`}`

ZEND_ASSERT(!EG(exception) &amp;&amp; "stream_fixup() should have failed");
zend_llist_add_element(&amp;CG(open_files), file_handle);
file_handle-&gt;in_list = 1;

/* Reset the scanner for scanning the new file */
SCNG(yy_in) = file_handle;
SCNG(yy_start) = NULL;

if (size != (size_t)-1) `{`
    if (CG(multibyte)) `{`
        SCNG(script_org) = (unsigned char*)buf;
        SCNG(script_org_size) = size;
        SCNG(script_filtered) = NULL;

​        zend_multibyte_set_filter(NULL);

​        if (SCNG(input_filter)) `{`
​            if ((size_t)-1 == SCNG(input_filter)(&amp;SCNG(script_filtered), &amp;SCNG(script_filtered_size), SCNG(script_org), SCNG(script_org_size))) `{`
​                zend_error_noreturn(E_COMPILE_ERROR, "Could not convert the script from the detected "
​                        "encoding \"%s\" to a compatible encoding", zend_multibyte_get_encoding_name(LANG_SCNG(script_encoding)));
​            `}`
​            buf = (char*)SCNG(script_filtered);
​            size = SCNG(script_filtered_size);
​        `}`
​    `}`
​    SCNG(yy_start) = (unsigned char *)buf;
​    yy_scan_buffer(buf, size);
`}` else `{`
​    zend_error_noreturn(E_COMPILE_ERROR, "zend_stream_mmap() failed");
`}`

if (CG(skip_shebang)) `{`
    BEGIN(SHEBANG);
`}` else `{`
    BEGIN(INITIAL);
`}`

if (file_handle-&gt;opened_path) `{`
    compiled_filename = zend_string_copy(file_handle-&gt;opened_path);
`}` else `{`
    compiled_filename = zend_string_copy(file_handle-&gt;filename);
`}`

zend_set_compiled_filename(compiled_filename);
zend_string_release_ex(compiled_filename, 0);

RESET_DOC_COMMENT();
CG(zend_lineno) = 1;
CG(increment_lineno) = 0;
return SUCCESS;

`}`
```

首先初始化SCNG的内容然后调用BEGIN，BEGIN在最开始定义为#define BEGIN(state) YYSETCONDITION(STATE(state))

YYSETCONDITION的定义是#define YYSETCONDITION(s) SCNG(yy_state) = s

也就是设置state = s

随后执行

zend_set_compiled_filename(compiled_filename);

zend_set_compiled_filename的定义是

```
ZEND_API zend_string *zend_set_compiled_filename(zend_string *new_compiled_filename)
`{`
    CG(compiled_filename) = zend_string_copy(new_compiled_filename);
    return new_compiled_filename;
`}`
```

调用zend_string_copy最终返回文件名

再执行RESET_DOC_COMMENT();

```
#define RESET_DOC_COMMENT() do `{` \
    if (CG(doc_comment)) `{` \
        zend_string_release_ex(CG(doc_comment), 0); \
        CG(doc_comment) = NULL; \
    `}` \
`}` while (0)
```

zend_string_release_ex

```
static zend_always_inline void zend_string_release_ex(zend_string *s, bool persistent)
`{`
    if (!ZSTR_IS_INTERNED(s)) `{`
        if (GC_DELREF(s) == 0) `{`
            if (persistent) `{`
                ZEND_ASSERT(GC_FLAGS(s) &amp; IS_STR_PERSISTENT);
                free(s);
            `}` else `{`
                ZEND_ASSERT(!(GC_FLAGS(s) &amp; IS_STR_PERSISTENT));
                efree(s);
            `}`
        `}`
    `}`
`}`
```

persistent是0 所以执行efree

```
ZEND_API void ZEND_FASTCALL _efree(void *ptr ZEND_FILE_LINE_DC ZEND_FILE_LINE_ORIG_DC)
`{`
#if ZEND_MM_CUSTOM
    if (UNEXPECTED(AG(mm_heap)-&gt;use_custom_heap)) `{`
        _efree_custom(ptr ZEND_FILE_LINE_RELAY_CC ZEND_FILE_LINE_ORIG_RELAY_CC);
        return;
    `}`
#endif
    zend_mm_free_heap(AG(mm_heap), ptr ZEND_FILE_LINE_RELAY_CC ZEND_FILE_LINE_ORIG_RELAY_CC);
`}`
```

```
static zend_always_inline void zend_mm_free_heap(zend_mm_heap *heap, void *ptr ZEND_FILE_LINE_DC ZEND_FILE_LINE_ORIG_DC)
`{`
    size_t page_offset = ZEND_MM_ALIGNED_OFFSET(ptr, ZEND_MM_CHUNK_SIZE);

if (UNEXPECTED(page_offset == 0)) `{`
    if (ptr != NULL) `{`
        zend_mm_free_huge(heap, ptr ZEND_FILE_LINE_RELAY_CC ZEND_FILE_LINE_ORIG_RELAY_CC);
    `}`
`}` else `{`
    zend_mm_chunk *chunk = (zend_mm_chunk*)ZEND_MM_ALIGNED_BASE(ptr, ZEND_MM_CHUNK_SIZE);
    int page_num = (int)(page_offset / ZEND_MM_PAGE_SIZE);
    zend_mm_page_info info = chunk-&gt;map[page_num];

​    ZEND_MM_CHECK(chunk-&gt;heap == heap, "zend_mm_heap corrupted");
​    if (EXPECTED(info &amp; ZEND_MM_IS_SRUN)) `{`
​        zend_mm_free_small(heap, ptr, ZEND_MM_SRUN_BIN_NUM(info));
​    `}` else /* if (info &amp; ZEND_MM_IS_LRUN) */ `{`
​        int pages_count = ZEND_MM_LRUN_PAGES(info);

​        ZEND_MM_CHECK(ZEND_MM_ALIGNED_OFFSET(page_offset, ZEND_MM_PAGE_SIZE) == 0, "zend_mm_heap corrupted");
​        zend_mm_free_large(heap, chunk, page_num, pages_count);
​    `}`
`}`

`}`
```

处理堆栈中的数据，清空上一次分析的内存

```
ZEND_API zend_op_array *compile_file(zend_file_handle *file_handle, int type)
`{`
    zend_lex_state original_lex_state;
    zend_op_array *op_array = NULL;
    zend_save_lexical_state(&amp;original_lex_state);

if (open_file_for_scanning(file_handle)==FAILURE) `{`
    if (!EG(exception)) `{`
        if (type==ZEND_REQUIRE) `{`
            zend_message_dispatcher(ZMSG_FAILED_REQUIRE_FOPEN, ZSTR_VAL(file_handle-&gt;filename));
        `}` else `{`
            zend_message_dispatcher(ZMSG_FAILED_INCLUDE_FOPEN, ZSTR_VAL(file_handle-&gt;filename));
        `}`
    `}`
`}` else `{`
    op_array = zend_compile(ZEND_USER_FUNCTION);
`}`

zend_restore_lexical_state(&amp;original_lex_state);
return op_array;

`}`
```

主要执行语句是zend_compile(ZEND_USER_FUNCTION);

```
static zend_op_array *zend_compile(int type)
`{`
    zend_op_array *op_array = NULL;
    bool original_in_compilation = CG(in_compilation);

CG(in_compilation) = 1;
CG(ast) = NULL;
CG(ast_arena) = zend_arena_create(1024 * 32);

if (!zendparse()) `{`
    int last_lineno = CG(zend_lineno);
    zend_file_context original_file_context;
    zend_oparray_context original_oparray_context;
    zend_op_array *original_active_op_array = CG(active_op_array);

​    op_array = emalloc(sizeof(zend_op_array));
​    init_op_array(op_array, type, INITIAL_OP_ARRAY_SIZE);
​    CG(active_op_array) = op_array;

​    /* Use heap to not waste arena memory */
​    op_array-&gt;fn_flags |= ZEND_ACC_HEAP_RT_CACHE;

​    if (zend_ast_process) `{`
​        zend_ast_process(CG(ast));
​    `}`

​    zend_file_context_begin(&amp;original_file_context);
​    zend_oparray_context_begin(&amp;original_oparray_context);
​    zend_compile_top_stmt(CG(ast));
​    CG(zend_lineno) = last_lineno;
​    zend_emit_final_return(type == ZEND_USER_FUNCTION);
​    op_array-&gt;line_start = 1;
​    op_array-&gt;line_end = last_lineno;
​    zend_init_static_variables_map_ptr(op_array);
​    pass_two(op_array);
​    zend_oparray_context_end(&amp;original_oparray_context);
​    zend_file_context_end(&amp;original_file_context);

​    CG(active_op_array) = original_active_op_array;
`}`

zend_ast_destroy(CG(ast));
zend_arena_destroy(CG(ast_arena));

CG(in_compilation) = original_in_compilation;

return op_array;

`}`
```

其中init_op_array(op_array, type, INITIAL_OP_ARRAY_SIZE);原型是

```
void init_op_array(zend_op_array *op_array, zend_uchar type, int initial_ops_size)
`{`
    op_array-&gt;type = type;
    op_array-&gt;arg_flags[0] = 0;
    op_array-&gt;arg_flags[1] = 0;
    op_array-&gt;arg_flags[2] = 0;

op_array-&gt;refcount = (uint32_t *) emalloc(sizeof(uint32_t));
*op_array-&gt;refcount = 1;
op_array-&gt;last = 0;
op_array-&gt;opcodes = emalloc(initial_ops_size * sizeof(zend_op));

op_array-&gt;last_var = 0;
op_array-&gt;vars = NULL;

op_array-&gt;T = 0;

op_array-&gt;function_name = NULL;
op_array-&gt;filename = zend_string_copy(zend_get_compiled_filename());
op_array-&gt;doc_comment = NULL;
op_array-&gt;attributes = NULL;

op_array-&gt;arg_info = NULL;
op_array-&gt;num_args = 0;
op_array-&gt;required_num_args = 0;

op_array-&gt;scope = NULL;
op_array-&gt;prototype = NULL;

op_array-&gt;live_range = NULL;
op_array-&gt;try_catch_array = NULL;
op_array-&gt;last_live_range = 0;

op_array-&gt;static_variables = NULL;
ZEND_MAP_PTR_INIT(op_array-&gt;static_variables_ptr, NULL);
op_array-&gt;last_try_catch = 0;

op_array-&gt;fn_flags = 0;

op_array-&gt;last_literal = 0;
op_array-&gt;literals = NULL;

op_array-&gt;num_dynamic_func_defs = 0;
op_array-&gt;dynamic_func_defs = NULL;

ZEND_MAP_PTR_INIT(op_array-&gt;run_time_cache, NULL);
op_array-&gt;cache_size = zend_op_array_extension_handles * sizeof(void*);

memset(op_array-&gt;reserved, 0, ZEND_MAX_RESERVED_RESOURCES * sizeof(void*));

if (zend_extension_flags &amp; ZEND_EXTENSIONS_HAVE_OP_ARRAY_CTOR) `{`
    zend_llist_apply_with_argument(&amp;zend_extensions, (llist_apply_with_arg_func_t) zend_extension_op_array_ctor_handler, op_array);
`}`

`}`
```

也就是初始化所有的标签，然后执行memset

zend_file_context_begin

```
void zend_file_context_begin(zend_file_context *prev_context) /* `{``{``{` */
`{`
    *prev_context = CG(file_context);
    FC(imports) = NULL;
    FC(imports_function) = NULL;
    FC(imports_const) = NULL;
    FC(current_namespace) = NULL;
    FC(in_namespace) = 0;
    FC(has_bracketed_namespaces) = 0;
    FC(declarables).ticks = 0;
    zend_hash_init(&amp;FC(seen_symbols), 8, NULL, NULL, 0);
`}`
```

zend_oparray_context_begin

```
void zend_oparray_context_begin(zend_oparray_context *prev_context) /* `{``{``{` */
`{`
    *prev_context = CG(context);
    CG(context).opcodes_size = INITIAL_OP_ARRAY_SIZE;
    CG(context).vars_size = 0;
    CG(context).literals_size = 0;
    CG(context).fast_call_var = -1;
    CG(context).try_catch_offset = -1;
    CG(context).current_brk_cont = -1;
    CG(context).last_brk_cont = 0;
    CG(context).brk_cont_array = NULL;
    CG(context).labels = NULL;
`}`
/* `}``}``}` */
```

#### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="%E6%8A%BD%E8%B1%A1%E5%8C%96"></a>抽象化

抽象化部分在zend_ini_scanner，zned_language_scanner，zend_operators等文件中

如zend_operators的_is_numeric_string_ex对数字类型进行分析

```
ZEND_API zend_uchar ZEND_FASTCALL _is_numeric_string_ex(const char *str, size_t length, zend_long *lval,
    double *dval, bool allow_errors, int *oflow_info, bool *trailing_data) /* `{``{``{` */
`{`
    const char *ptr;
    int digits = 0, dp_or_e = 0;
    double local_dval = 0.0;
    zend_uchar type;
    zend_ulong tmp_lval = 0;
    int neg = 0;

if (!length) `{`
    return 0;
`}`

if (oflow_info != NULL) `{`
    *oflow_info = 0;
`}`
if (trailing_data != NULL) `{`
    *trailing_data = false;
`}`

/* Skip any whitespace

 * This is much faster than the isspace() function */
   while (*str == ' ' || *str == '\t' || *str == '\n' || *str == '\r' || *str == '\v' || *str == '\f') `{`
   str++;
   length--;
   `}`
   ptr = str;

if (*ptr == '-') `{`
    neg = 1;
    ptr++;
`}` else if (*ptr == '+') `{`
    ptr++;
`}`

if (ZEND_IS_DIGIT(*ptr)) `{`
    /* Skip any leading 0s */
    while (*ptr == '0') `{`
        ptr++;
    `}`

​    /* Count the number of digits. If a decimal point/exponent is found,

  * it's a double. Otherwise, if there's a dval or no need to check for
    * a full match, stop when there are too many digits for a long */
      for (type = IS_LONG; !(digits &gt;= MAX_LENGTH_OF_LONG &amp;&amp; (dval || allow_errors)); digits++, ptr++) `{`

check_digits:
            if (ZEND_IS_DIGIT(*ptr)) `{`
                tmp_lval = tmp_lval * 10 + (*ptr) - '0';
                continue;
            `}` else if (*ptr == '.' &amp;&amp; dp_or_e &lt; 1) `{`
                goto process_double;
            `}` else if ((*ptr == 'e' || *ptr == 'E') &amp;&amp; dp_or_e &lt; 2) `{`
                const char *e = ptr + 1;

​            if (*e == '-' || *e == '+') `{`
​                ptr = e++;
​            `}`
​            if (ZEND_IS_DIGIT(*e)) `{`
​                goto process_double;
​            `}`
​        `}`

​        break;
​    `}`

​    if (digits &gt;= MAX_LENGTH_OF_LONG) `{`
​        if (oflow_info != NULL) `{`
​            *oflow_info = *str == '-' ? -1 : 1;
​        `}`
​        dp_or_e = -1;
​        goto process_double;
​    `}`
`}` else if (*ptr == '.' &amp;&amp; ZEND_IS_DIGIT(ptr[1])) `{`

process_double:
        type = IS_DOUBLE;

​    /* If there's a dval, do the conversion; else continue checking

  * the digits if we need to check for a full match */
    if (dval) `{`
        local_dval = zend_strtod(str, &amp;ptr);
    `}` else if (!allow_errors &amp;&amp; dp_or_e != -1) `{`
        dp_or_e = (*ptr++ == '.') ? 1 : 2;
        goto check_digits;
    `}`
    `}` else `{`
    return 0;
    `}`

if (ptr != str + length) `{`
    const char *endptr = ptr;
    while (*endptr == ' ' || *endptr == '\t' || *endptr == '\n' || *endptr == '\r' || *endptr == '\v' || *endptr == '\f') `{`
        endptr++;
        length--;
    `}`
    if (ptr != str + length) `{`
        if (!allow_errors) `{`
            return 0;
        `}`
        if (trailing_data != NULL) `{`
            *trailing_data = true;
        `}`
    `}`
`}`

if (type == IS_LONG) `{`
    if (digits == MAX_LENGTH_OF_LONG - 1) `{`
        int cmp = strcmp(&amp;ptr[-digits], long_min_digits);

​        if (!(cmp &lt; 0 || (cmp == 0 &amp;&amp; *str == '-'))) `{`
​            if (dval) `{`
​                *dval = zend_strtod(str, NULL);
​            `}`
​            if (oflow_info != NULL) `{`
​                *oflow_info = *str == '-' ? -1 : 1;
​            `}`

​            return IS_DOUBLE;
​        `}`
​    `}`

​    if (lval) `{`
​        if (neg) `{`
​            tmp_lval = -tmp_lval;
​        `}`
​        *lval = (zend_long) tmp_lval;
​    `}`

​    return IS_LONG;
`}` else `{`
​    if (dval) `{`
​        *dval = local_dval;
​    `}`

​    return IS_DOUBLE;
`}`

`}`
```

首先对空格之类跳过，（原文件行数，下同）3177-3182是对+-运算符的提取和标记。3184-3212是获取数字，while跳过开头的0，对于数字使用long的范围去匹配避免麻烦。出现.则跳转到double处理。

zend_compile中的reserved_class_name是对类名进行分析，选取特定长度进行比对获取相对应的类名

```
static const struct reserved_class_name reserved_class_names[] = `{`
    `{`ZEND_STRL("bool")`}`,
    `{`ZEND_STRL("false")`}`,
    `{`ZEND_STRL("float")`}`,
    `{`ZEND_STRL("int")`}`,
    `{`ZEND_STRL("null")`}`,
    `{`ZEND_STRL("parent")`}`,
    `{`ZEND_STRL("self")`}`,
    `{`ZEND_STRL("static")`}`,
    `{`ZEND_STRL("string")`}`,
    `{`ZEND_STRL("true")`}`,
    `{`ZEND_STRL("void")`}`,
    `{`ZEND_STRL("never")`}`,
    `{`ZEND_STRL("iterable")`}`,
    `{`ZEND_STRL("object")`}`,
    `{`ZEND_STRL("mixed")`}`,
    `{`NULL, 0`}`
`}`;

static bool zend_is_reserved_class_name(const zend_string *name) /* `{``{``{` */
`{`
    const struct reserved_class_name *reserved = reserved_class_names;

const char *uqname = ZSTR_VAL(name);
size_t uqname_len = ZSTR_LEN(name);
zend_get_unqualified_name(name, &amp;uqname, &amp;uqname_len);

for (; reserved-&gt;name; ++reserved) `{`
    if (uqname_len == reserved-&gt;len
        &amp;&amp; zend_binary_strcasecmp(uqname, uqname_len, reserved-&gt;name, reserved-&gt;len) == 0
    ) `{`
        return 1;
    `}`
`}`

return 0;

`}`
```

zend_scan_escape_string首先判断这一行代码长度，如果当前行是空行则zend_lineno加一。一直到这一行的末尾，执行skip_escape_conversion。过程中如果遇到特殊字符$则退出，如果是标志x，u等数据类型的符号，则改变堆栈存储方式，如果是空格之类的符号就跳过。

分析完当前行后，需要分析下一有意义的行。这就是next_newline的作用。检测到回车如果存在下一行且下一行为换行，那么跳过两行，否则跳过一行。

```
static zend_result zend_scan_escape_string(zval *zendlval, char *str, int len, char quote_type)
`{`
    char *s, *t;
    char *end;

if (len &lt;= 1) `{`
    if (len &lt; 1) `{`
        ZVAL_EMPTY_STRING(zendlval);
    `}` else `{`
        zend_uchar c = (zend_uchar)*str;
        if (c == '\n' || c == '\r') `{`
            CG(zend_lineno)++;
        `}`
        ZVAL_INTERNED_STR(zendlval, ZSTR_CHAR(c));
    `}`
    goto skip_escape_conversion;
`}`

ZVAL_STRINGL(zendlval, str, len);

/* convert escape sequences */
s = Z_STRVAL_P(zendlval);
end = s+Z_STRLEN_P(zendlval);
while (1) `{`
    if (UNEXPECTED(*s=='\\')) `{`
        break;
    `}`
    if (*s == '\n' || (*s == '\r' &amp;&amp; (*(s+1) != '\n'))) `{`
        CG(zend_lineno)++;
    `}`
    s++;
    if (s == end) `{`
        goto skip_escape_conversion;
    `}`
`}`

t = s;
while (s&lt;end) `{`
    if (*s=='\\') `{`
        s++;
        if (s &gt;= end) `{`
            *t++ = '\\';
            break;
        `}`

​        switch(*s) `{`
​            case 'n':
​                *t++ = '\n';
​                break;
​            case 'r':
​                *t++ = '\r';
​                break;
​            case 't':
​                *t++ = '\t';
​                break;
​            case 'f':
​                *t++ = '\f';
​                break;
​            case 'v':
​                *t++ = '\v';
​                break;
​            case 'e':

#ifdef ZEND_WIN32
                    *t++ = VK_ESCAPE;
#else
                    *t++ = '\e';
#endif
                    break;
                case '"':
                case '`':
                    if (*s != quote_type) `{`
                        *t++ = '\\';
                        *t++ = *s;
                        break;
                    `}`
                    ZEND_FALLTHROUGH;
                case '\\':
                case '$':
                    *t++ = *s;
                    break;
                case 'x':
                case 'X':
                    if (ZEND_IS_HEX(*(s+1))) `{`
                        char hex_buf[3] = `{` 0, 0, 0 `}`;

​                    hex_buf[0] = *(++s);
​                    if (ZEND_IS_HEX(*(s+1))) `{`
​                        hex_buf[1] = *(++s);
​                    `}`
​                    *t++ = (char) ZEND_STRTOL(hex_buf, NULL, 16);
​                `}` else `{`
​                    *t++ = '\\';
​                    *t++ = *s;
​                `}`
​                break;
​            /* UTF-8 codepoint escape, format: /\\u\`{`\x+\`}`/ */
​            case 'u':
​                `{`
​                    /* cache where we started so we can parse after validating */
​                    char *start = s + 1;
​                    size_t len = 0;
​                    bool valid = 1;
​                    unsigned long codepoint;

​                    if (*start != '`{`') `{`
​                        /* we silently let this pass to avoid breaking code

   * with JSON in string literals (e.g. "\"\u202e\""
                          */
                         *t++ = '\\';
                         *t++ = 'u';
                         break;
                     `}` else `{`
                         /* on the other hand, invalid \u`{`blah`}` errors */
                         s++;
                         len++;
                         s++;
                         while (*s != '`}`') `{`
                             if (!ZEND_IS_HEX(*s)) `{`
                                 valid = 0;
                                 break;
                             `}` else `{`
                                 len++;
                             `}`
                             s++;
                         `}`
                         if (*s == '`}`') `{`
                             valid = 1;
                             len++;
                         `}`
                     `}`

     ​                /* \u`{``}` is invalid */
     ​                if (len &lt;= 2) `{`
     ​                    valid = 0;
     ​                `}`

     ​                if (!valid) `{`
     ​                    zend_throw_exception(zend_ce_parse_error,
     ​                        "Invalid UTF-8 codepoint escape sequence", 0);
     ​                    zval_ptr_dtor(zendlval);
     ​                    ZVAL_UNDEF(zendlval);
     ​                    return FAILURE;
     ​                `}`

     ​                errno = 0;
     ​                codepoint = strtoul(start + 1, NULL, 16);

     ​                /* per RFC 3629, UTF-8 can only represent 21 bits */
     ​                if (codepoint &gt; 0x10FFFF || errno) `{`
     ​                    zend_throw_exception(zend_ce_parse_error,
     ​                        "Invalid UTF-8 codepoint escape sequence: Codepoint too large", 0);
     ​                    zval_ptr_dtor(zendlval);
     ​                    ZVAL_UNDEF(zendlval);
     ​                    return FAILURE;
     ​                `}`

     ​                /* based on https://en.wikipedia.org/wiki/UTF-8#Sample_code */
     ​                if (codepoint &lt; 0x80) `{`
     ​                    *t++ = codepoint;
     ​                `}` else if (codepoint &lt;= 0x7FF) `{`
     ​                    *t++ = (codepoint &gt;&gt; 6) + 0xC0;
     ​                    *t++ = (codepoint &amp; 0x3F) + 0x80;
     ​                `}` else if (codepoint &lt;= 0xFFFF) `{`
     ​                    *t++ = (codepoint &gt;&gt; 12) + 0xE0;
     ​                    *t++ = ((codepoint &gt;&gt; 6) &amp; 0x3F) + 0x80;
     ​                    *t++ = (codepoint &amp; 0x3F) + 0x80;
     ​                `}` else if (codepoint &lt;= 0x10FFFF) `{`
     ​                    *t++ = (codepoint &gt;&gt; 18) + 0xF0;
     ​                    *t++ = ((codepoint &gt;&gt; 12) &amp; 0x3F) + 0x80;
     ​                    *t++ = ((codepoint &gt;&gt; 6) &amp; 0x3F) + 0x80;
     ​                    *t++ = (codepoint &amp; 0x3F) + 0x80;
     ​                `}`
     ​            `}`
     ​            break;
     ​        default:
     ​            /* check for an octal */
     ​            if (ZEND_IS_OCT(*s)) `{`
     ​                char octal_buf[4] = `{` 0, 0, 0, 0 `}`;

     ​                octal_buf[0] = *s;
     ​                if (ZEND_IS_OCT(*(s+1))) `{`
     ​                    octal_buf[1] = *(++s);
     ​                    if (ZEND_IS_OCT(*(s+1))) `{`
     ​                        octal_buf[2] = *(++s);
     ​                    `}`
     ​                `}`
     ​                if (octal_buf[2] &amp;&amp; (octal_buf[0] &gt; '3') &amp;&amp; !SCNG(heredoc_scan_ahead)) `{`
     ​                    /* 3 octit values must not overflow 0xFF (\377) */
     ​                    zend_error(E_COMPILE_WARNING, "Octal escape sequence overflow \\%s is greater than \\377", octal_buf);
     ​                `}`

     ​                *t++ = (char) ZEND_STRTOL(octal_buf, NULL, 8);
     ​            `}` else `{`
     ​                *t++ = '\\';
     ​                *t++ = *s;
     ​            `}`
     ​            break;
     ​    `}`
     `}` else `{`
     ​    *t++ = *s;
     `}`

     if (*s == '\n' || (*s == '\r' &amp;&amp; (*(s+1) != '\n'))) `{`
         CG(zend_lineno)++;
     `}`
     s++;
     `}`
     *t = 0;
     Z_STRLEN_P(zendlval) = t - Z_STRVAL_P(zendlval);

skip_escape_conversion:
    if (SCNG(output_filter)) `{`
        size_t sz = 0;
        unsigned char *str;
        // TODO: avoid realocation ???
        s = Z_STRVAL_P(zendlval);
        SCNG(output_filter)(&amp;str, &amp;sz, (unsigned char *)s, (size_t)Z_STRLEN_P(zendlval));
        zval_ptr_dtor(zendlval);
        ZVAL_STRINGL(zendlval, (char *) str, sz);
        efree(str);
    `}`
    return SUCCESS;
`}`
```

lex_scan首先对LNUM之类的数据使用正则定义其结构。再分别对exit之类的关键词定义其分析方法。

由于这一段的代码过于长，所以仅作出部分粘贴。

lex_scan是根据re2c得到语法分析

其定义了

```
LNUM    [0-9]+(_[0-9]+)*
DNUM    (`{`LNUM`}`?"."`{`LNUM`}`)|(`{`LNUM`}`"."`{`LNUM`}`?)
EXPONENT_DNUM    ((`{`LNUM`}`|`{`DNUM`}`)[eE][+-]?`{`LNUM`}`)
HNUM    "0x"[0-9a-fA-F]+(_[0-9a-fA-F]+)*
BNUM    "0b"[01]+(_[01]+)*
ONUM    "0o"[0-7]+(_[0-7]+)*
LABEL    [a-zA-Z_\x80-\xff][a-zA-Z0-9_\x80-\xff]*
WHITESPACE [ \n\r\t]+
TABS_AND_SPACES [ \t]*
TOKENS [;:,.|^&amp;+-/*=%!~$&lt;&gt;?@]
ANY_CHAR [^]
NEWLINE ("\r"|"\n"|"\r\n")
```

作为基础结构单元的正则表达式。

```
&lt;ST_IN_SCRIPTING&gt;"exit" `{`
    RETURN_TOKEN_WITH_IDENT(T_EXIT);
`}`

&lt;ST_IN_SCRIPTING&gt;"die" `{`
    RETURN_TOKEN_WITH_IDENT(T_EXIT);
`}`

&lt;ST_IN_SCRIPTING&gt;"fn" `{`
    RETURN_TOKEN_WITH_IDENT(T_FN);
`}`

&lt;ST_IN_SCRIPTING&gt;"function" `{`
    RETURN_TOKEN_WITH_IDENT(T_FUNCTION);
`}`

&lt;ST_IN_SCRIPTING&gt;"const" `{`
    RETURN_TOKEN_WITH_IDENT(T_CONST);
`}`

&lt;ST_IN_SCRIPTING&gt;"return" `{`
    RETURN_TOKEN_WITH_IDENT(T_RETURN);
`}`

&lt;ST_IN_SCRIPTING&gt;"#[" `{`
    enter_nesting('[');
    RETURN_TOKEN(T_ATTRIBUTE);
`}`

&lt;ST_IN_SCRIPTING&gt;"yield"`{`WHITESPACE`}`"from"[^a-zA-Z0-9_\x80-\xff] `{`
    yyless(yyleng - 1);
    HANDLE_NEWLINES(yytext, yyleng);
    RETURN_TOKEN_WITH_IDENT(T_YIELD_FROM);
`}`
```

对exit，die，fn做出分别定义，执行RETURN_TOKEN_WITH_IDENT

```
#define RETURN_TOKEN_WITH_IDENT(_token) do `{` \
        token = _token; \
        goto emit_token_with_ident; \
    `}` while (0)
```

emit_token_with_ident

```
emit_token_with_ident:
    if (PARSER_MODE()) `{`
        elem-&gt;ident = SCNG(yy_text);
    `}`
    if (SCNG(on_event)) `{`
        SCNG(on_event)(ON_TOKEN, token, start_line, yytext, yyleng, SCNG(on_event_context));
    `}`
    return token;
```

这一部分就是将代码抽象化后存储。

上面这一部分是对基本代码结构即一个表达式的组成元素，变量及其类型，命令式函数及其组成部分和类型进行分析。

下面我们对特殊语法结构进行分析

zend对特殊结构使用BNF进行分析，代码在zend_ini_parser中。

首先是对基本组成单元进行划分

```
%expect 0
%define api.prefix `{`ini_`}`
%define api.pure full
%define api.value.type `{`zval`}`
%define parse.error verbose

%token END 0 "end of file"
%token TC_SECTION
%token TC_RAW
%token TC_CONSTANT
%token TC_NUMBER
%token TC_STRING
%token TC_WHITESPACE
%token TC_LABEL
%token TC_OFFSET
%token TC_DOLLAR_CURLY
%token TC_VARNAME
%token TC_QUOTED_STRING
%token BOOL_TRUE
%token BOOL_FALSE
%token NULL_NULL
%token END_OF_LINE
%token '=' ':' ',' '.' '"' '\'' '^' '+' '-' '/' '*' '%' '$' '~' '&lt;' '&gt;' '?' '@' '`{`' '`}`'
%left '|' '&amp;' '^'
%precedence '~' '!'

%destructor `{` zval_ini_dtor(&amp;$$); `}` TC_RAW TC_CONSTANT TC_NUMBER TC_STRING TC_WHITESPACE TC_LABEL TC_OFFSET TC_VARNAME BOOL_TRUE BOOL_FALSE NULL_NULL cfg_var_ref constant_literal constant_string encapsed_list expr option_offset section_string_or_value string_or_value var_string_list var_string_list_section

%%
```

随后对语句进行抽象描述并一步一步划分成更小的单元。

```
statement_list:
        statement_list statement
    |    %empty
;

statement:
        TC_SECTION section_string_or_value ']' `{`
#if DEBUG_CFG_PARSER
            printf("SECTION: [%s]\n", Z_STRVAL($2));
#endif
            ZEND_INI_PARSER_CB(&amp;$2, NULL, NULL, ZEND_INI_PARSER_SECTION, ZEND_INI_PARSER_ARG);
            zend_string_release(Z_STR($2));
        `}`
    |    TC_LABEL '=' string_or_value `{`
#if DEBUG_CFG_PARSER
            printf("NORMAL: '%s' = '%s'\n", Z_STRVAL($1), Z_STRVAL($3));
#endif
            ZEND_INI_PARSER_CB(&amp;$1, &amp;$3, NULL, ZEND_INI_PARSER_ENTRY, ZEND_INI_PARSER_ARG);
            zend_string_release(Z_STR($1));
            zval_ini_dtor(&amp;$3);
        `}`
    |    TC_OFFSET option_offset ']' '=' string_or_value `{`
#if DEBUG_CFG_PARSER
            printf("OFFSET: '%s'[%s] = '%s'\n", Z_STRVAL($1), Z_STRVAL($2), Z_STRVAL($5));
#endif
            ZEND_INI_PARSER_CB(&amp;$1, &amp;$5, &amp;$2, ZEND_INI_PARSER_POP_ENTRY, ZEND_INI_PARSER_ARG);
            zend_string_release(Z_STR($1));
            zval_ini_dtor(&amp;$2);
            zval_ini_dtor(&amp;$5);
        `}`
    |    TC_LABEL    `{` ZEND_INI_PARSER_CB(&amp;$1, NULL, NULL, ZEND_INI_PARSER_ENTRY, ZEND_INI_PARSER_ARG); zend_string_release(Z_STR($1)); `}`
    |    END_OF_LINE
;
```

我们以switchcase为例

在zend_language_parser中，定义了switchcase的结构，如下图

```
switch_case_list:
  669:         '`{`' case_list '`}`'                    `{` $$ = $2; `}`
  670:     |    '`{`' ';' case_list '`}`'                `{` $$ = $3; `}`
  671:     |    ':' case_list T_ENDSWITCH ';'        `{` $$ = $2; `}`
  672:     |    ':' ';' case_list T_ENDSWITCH ';'    `{` $$ = $3; `}`
  673  ;
```

switchcase可能存在单个case或者多个case。1是对单case的正则。2是对多个的正则。3是单case的结束判断，4是多case的结束判断。

其中T_ENDSWITCH在zend_language_parser定义，是关键词endswitch

case_list定义如下

```
case_list:
  676:         %empty `{` $$ = zend_ast_create_list(0, ZEND_AST_SWITCH_LIST); `}`
  677      |    case_list T_CASE expr case_separator inner_statement_list
  678:             `{` $$ = zend_ast_list_add($1, zend_ast_create(ZEND_AST_SWITCH_CASE, $3, $5)); `}`
  679      |    case_list T_DEFAULT case_separator inner_statement_list
  680:             `{` $$ = zend_ast_list_add($1, zend_ast_create(ZEND_AST_SWITCH_CASE, NULL, $4)); `}`
  681  ;
```

根据结构empty case_list T_CASE expr case_separator inner_statement_list case_list T_DEFAULT case_separator inner_statement_list分别进行存储。

其中expr case_separator inner_statement_list分别在后面有定义，其中case_separator是对：；进行匹配。其他也是类似。分析就到此结束，lexical scanner的抽象化方式是使用了re2c的正则匹配



## 最后

水平有限，欢迎指教

**作者：DR[@03](https://github.com/03)@星盟**
