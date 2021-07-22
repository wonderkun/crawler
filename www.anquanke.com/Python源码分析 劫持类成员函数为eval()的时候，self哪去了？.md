> 原文链接: https://www.anquanke.com//post/id/213414 


# Python源码分析 劫持类成员函数为eval()的时候，self哪去了？


                                阅读量   
                                **194311**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01680a0faa934e1a53.png)](https://p0.ssl.qhimg.com/t01680a0faa934e1a53.png)



在Python题的getshell途中，我们可以把某个类的成员函数劫持成`eval`。看起来一切都没有问题，但仔细想想，调用类的成员函数的时候传参不是会传递`self`也就是`func(clazz.self, paramter)`吗？那为什么没有`self`没有被作为`eval`的第一个参数呢，而且还没有报错？

知其然更要知其所以然，我们今天就来以python3.7.8源码为例进行分析。调试python的源码的环境配置步骤和调试php源码的时候差不多，所以可以参考php源码调试环境搭建的相关文章。

小贴士：python源码中Doc文件夹里的存放着官方文档（一些`.rst`文件），不知道源码里的函数的作用时，可以在Doc中进行搜索查看，在clion中可以按Ctrl+Shift+F进行全部搜索，搜索范围可达整个项目乃至库函数的源码）。



## 引例

来看下面的这份代码，我们知道[eval()](https://docs.python.org/3.8/library/functions.html?highlight=eval#eval)的定义是`eval(expression[, globals[, locals]])`。

如果把`eval()`放在`__eq__`里，在执行`a=="bb"`的时候`expression`应该传入的是`self`，然而`globals`应该传的是`"bb"`，如果这样的话一定是会报错没法继续执行的。：

```
class A():
    pass

if __name__ == "__main__":
    a = A()
    a.__class__.__eq__ = eval
    print(a)
    print(eval)
    a == "bb"
```

那实际中，在`__eq__`里用`a.__class__.__eq__ = eval`放进`eval()`，为什么没有报错，反而正常执行了呢？



## 分析

### <a class="reference-link" name="0x01%20builtin_eval"></a>0x01 builtin_eval

python语言里的`eval()`是属于`python`的`builtin_function`，它的实现是在`builtin_eval`

```
static PyObject *
builtin_eval(PyObject *module, PyObject *const *args, Py_ssize_t nargs)
`{`
    PyObject *return_value = NULL;
    PyObject *source;
    PyObject *globals = Py_None;
    PyObject *locals = Py_None;

    if (!_PyArg_UnpackStack(args, nargs, "eval",
        1, 3,
        &amp;source, &amp;globals, &amp;locals)) `{`
        goto exit;
    `}`
    return_value = builtin_eval_impl(module, source, globals, locals);

exit:
    return return_value;
`}`
```

所以对这个函数下断点，看看调用链。

可以看到在解释`a == 'bb'`的时候，因为在进行`==`比较`do_richcompare`发挥了作用，参数中的`op=2`意思是正在进行`==`

在python语言的设计理念里，一个对象拥有诸多个`slots`，比如`__str__`就是一个槽函数，你可以Override它。包括`__eq__`也是

[https://docs.python.org/3.8/c-api/typeobj.html?highlight=slots](https://docs.python.org/3.8/c-api/typeobj.html?highlight=slots)

`a.__class__.__eq__=eval`，所以可以理解为将`eval`就放在了这个eq对应的`slot`里，这样就进入到了`slot_tp_richcompare`。

如果没有放`eval`，那么python在进行`richcompare`的时候就按照正常的流程进行比较。

```
static PyObject *
slot_tp_richcompare(PyObject *self, PyObject *other, int op)
`{`
    int unbound;
    PyObject *func, *res;

    func = lookup_maybe_method(self, &amp;name_op[op], &amp;unbound);
    if (func == NULL) `{`
        PyErr_Clear();
        Py_RETURN_NOTIMPLEMENTED;
    `}`

    PyObject *args[1] = `{`other`}`;
    res = call_unbound(unbound, func, self, args, 1);
    Py_DECREF(func);
    return res;
`}`

static _Py_Identifier name_op[] = `{`
    `{`0, "__lt__", 0`}`,
    `{`0, "__le__", 0`}`,
    `{`0, "__eq__", 0`}`,
    `{`0, "__ne__", 0`}`,
    `{`0, "__gt__", 0`}`,
    `{`0, "__ge__", 0`}`
`}`;
```

`lookup_maybe_method`取出放在`__eq__`里的eval，用然后`call_unbound`执行eval

但是注意到`call_unbound`里还是传入了`self`，那`self`是在哪被丢掉的？

因为`unbound=0`，所以`self`在这里被丢掉了

```
static PyObject*
call_unbound(int unbound, PyObject *func, PyObject *self,
             PyObject **args, Py_ssize_t nargs)
`{`
    if (unbound) `{` //unbound = 0
        return _PyObject_FastCall_Prepend(func, self, args, nargs);
    `}`
    else `{`
        return _PyObject_FastCall(func, args, nargs);
    `}`
`}`
```

现在知道了`self`在哪被丢掉的，那么`unbound = 0`又是怎么来的，让我们刨根问底，继续接着看：

### <a class="reference-link" name="0x02%20unbound"></a>0x02 unbound

继续跟踪可以发现`_PyObject_FastCallDict()`，调用了`_PyCFunction_FastCallDict()`，这个`CFunction`当然就是我们的eval，后面就进入到了`builtin_eval()`的执行当中

```
PyObject *
_PyObject_FastCallDict(PyObject *callable, PyObject *const *args, Py_ssize_t nargs,
                       PyObject *kwargs)
`{`
    /* _PyObject_FastCallDict() must not be called with an exception set,
       because it can clear it (directly or indirectly) and so the
       caller loses its exception */
    assert(!PyErr_Occurred());

    assert(callable != NULL);
    assert(nargs &gt;= 0);
    assert(nargs == 0 || args != NULL);
    assert(kwargs == NULL || PyDict_Check(kwargs));

    if (PyFunction_Check(callable)) `{`
        return _PyFunction_FastCallDict(callable, args, nargs, kwargs);
    `}`
    else if (PyCFunction_Check(callable)) `{`
        return _PyCFunction_FastCallDict(callable, args, nargs, kwargs);
    `}`
```

所以呢？`unbound=0`是怎么来的？让我们看下`lookup_maybe_method`干了什么。

```
static PyObject *
lookup_maybe_method(PyObject *self, _Py_Identifier *attrid, int *unbound)
`{`
    PyObject *res = _PyType_LookupId(Py_TYPE(self), attrid);
    //res = eval()
    //这里就是把eval从__eq__里取出来，这里的attrid就是__eq__
    if (res == NULL) `{`
        return NULL;
    `}`

    if (PyFunction_Check(res)) `{`
        /* Avoid temporary PyMethodObject */
        *unbound = 1;
        Py_INCREF(res);
    `}`
    else `{`
        *unbound = 0;
        descrgetfunc f = Py_TYPE(res)-&gt;tp_descr_get;
        // descr descriptor tp_descr_get是获取新式类里的__get__方法
        // 在python中，如果一个新式类定义了__get__, __set__, __delete__方法中的一个或者多个，那么这里的descriptor指的是所定义__get__, __set__, __delete__
        if (f == NULL) `{`
            Py_INCREF(res);
            //引用计数器 +1
        `}`
        else `{`
            res = f(res, self, (PyObject *)(Py_TYPE(self)));
        `}`
    `}`
    return res;
`}`
```

`PyFunction_Check`相关宏定义：

```
#define PyFunction_Check(op) (Py_TYPE(op) == &amp;PyFunction_Type)
#define Py_TYPE(ob)             (((PyObject*)(ob))-&gt;ob_type)
```

`&amp;PyFunction_Type`可以理解为`PyFunction_Type[0]`，PyFunction_Type数组：

```
PyTypeObject PyFunction_Type = `{`
    PyVarObject_HEAD_INIT(&amp;PyType_Type, 0)
    "function",
    sizeof(PyFunctionObject),
    0,
    (destructor)func_dealloc,                   /* tp_dealloc */
    0,                                          /* tp_print */
    0,                                          /* tp_getattr */
    0,                                          /* tp_setattr */
    0,                                          /* tp_reserved */
    (reprfunc)func_repr,                        /* tp_repr */
    0,                                          /* tp_as_number */
    0,                                          /* tp_as_sequence */
    0,                                          /* tp_as_mapping */
    0,                                          /* tp_hash */
    function_call,                              /* tp_call */
    0,                                          /* tp_str */
    0,                                          /* tp_getattro */
    0,                                          /* tp_setattro */
    0,                                          /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,    /* tp_flags */
    func_new__doc__,                            /* tp_doc */
    (traverseproc)func_traverse,                /* tp_traverse */
    0,                                          /* tp_clear */
    0,                                          /* tp_richcompare */
    offsetof(PyFunctionObject, func_weakreflist), /* tp_weaklistoffset */
    0,                                          /* tp_iter */
    0,                                          /* tp_iternext */
    0,                                          /* tp_methods */
    func_memberlist,                            /* tp_members */
    func_getsetlist,                            /* tp_getset */
    0,                                          /* tp_base */
    0,                                          /* tp_dict */
    func_descr_get,                             /* tp_descr_get */
    0,                                          /* tp_descr_set */
    offsetof(PyFunctionObject, func_dict),      /* tp_dictoffset */
    0,                                          /* tp_init */
    0,                                          /* tp_alloc */
    func_new,                                   /* tp_new */
`}`;
```

`PyVarObject_HEAD_INIT(&amp;PyType_Type, 0) "function"`前面的那堆是类型转换，不管他。

这里的意思是`ob_type`得是`"function"`才能让`PyFunction_Check`返回`1`，因为`eval`的`ob_type`是`builtin_function_or_method`，所以会返回`0`

可以通过如下简单测试验证，如下例子中的`ob_type`为`function`，并且返回的`unbound = 1`：

```
def hello(aa, bb):
    print(aa, bb)
a.__class__.__eq__ = hello
```

然后我们明显没有定义`class A`的`__get__`，所以`descrgetfunc = NULL`，之后`lookup_maybe_method`结束，就把`eval`返回过来了顺带确定`unbound = 0`



## 总结

在web安全的学习当中，很多语言的小trick看似普通，但是，我们要弄明白它的原理，因为了解trick背后的原理更有收获比起光光记住小trick，往往来得更有收获。

阅读源码时往往可以参考官方的文档，这样便于理解其设计理念，知道了整体架构，也便于后续的分析。
