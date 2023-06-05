# xc-qq-robot

一个python萌新写的对接go-cqhttp的屎山玩意

本项目仅使用main.py即可运行，会自动初始化

使用方法：

1， 克隆本项目

2, 在项目根目录输入

```pip install -r requirements.txt```

安装所需库

3, 配置go-cqhttp,这个go-cqhttp有教程，端口地址什么的在config/config.ini里面可以更改 默认是go-cqhttp的默认端口 需要正向websocket和http api

4, 即可使用，可以自己按照示例的插件 qqbot.py 编写

但是应为我是个傻逼 一开始用了多线程加载插件，导致现在没法在插件里面使用异步只能 多线程+线程锁或者干脆不写线程直接写
