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

- ### 2, 安装所需库
  
  > 以后如果对接上icqq，可能会使用一些可以在py中运行js的库，到时候可能会有一些改动

  在项目根目录输入 ```pip install -r requirements.txt``` 安装所需库

- ### 3, 配置go-cqhttp
  这个go-cqhttp有教程，端口地址什么的在config/config.ini里面可以更改 默认是go-cqhttp的默认端口 需要正向websocket和http api

- ### 4, 现在就可以使用拉！

  >可以自己按照示例的插件 qqbot.py 编写

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
