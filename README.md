<div align="center">
  
# xc-qq-robot

一个萌新写的多线程垃圾QQ机器人框架

</div>

<p align="center">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/static/v1?label=python&message=3.8&color=blue" alt="python">
  </a>
</P>
  
一个python萌新写的对接大佬们框架的屎山玩意

本项目仅使用main.py即可运行，会自动初始化

<details>
<summary>使用方法：</summary>

- ### 1, 克隆本项目
  
  - 克隆的话请执行 ```cd xc-qqbot-robot```
  
  - 下载的话解压后请执行 ```cd xc-qq-robot-main```

- ### 2, 安装所需库
  
    > 以后如果对接上icqq，可能会使用一些可以在py中运行js的库，到时候可能会有一些改动

    在项目根目录输入 ```pip install -r requirements.txt``` 安装所需库

- ### 3, 配置go-cqhttp
  
    >go-cqhttp刚开始需要选择正向ws和http api
  
    go-cqhttp的话可以可以看go-cqhttp官方的教程 [戳这里！](https://docs.go-cqhttp.org/guide/#go-cqhttp)
  
    http api和websockets的端口和地址在当前目录下的config文件夹下的config.ini文件
  
    里面可以更改http api和websockets的端口和地址
  
    默认的http api和websockets的端口和地址是go-cqhttp的默认http api和websockets的端口地址

- ### 4, 启动
  
    >这一步完成后可以自己按照示例的插件 qqbot.py 或者 qqbot_http_api.py 编写
  
    在当前目录下直接执行 ```python main.py``` 即可运行
    
    PS：第一次运行会停止2次初始化配置文件

</details>

有什么bug或者建议可以提Issues

官方群聊：818266207

<details>
<summary>大饼铺子：</summary>

  - #### 对接框架
    - [x] go-cqhttp
    - [ ] icqq
  
  - #### 接口
    - [ ] onebot V12
    - [x] http api （只有一个发送消息的api也算是吧？后面慢慢完善
</details>
