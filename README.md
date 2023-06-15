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
<summary>开始使用：</summary>

- ### 1, 克隆本项目
  - ```git clone https://github.com/XCWQW1/xc-qq-robot.git```
  - ```cd xc-qq-robot```


- ### 2, 安装所需库

    - ```pip install -r requirements.txt``` 

- ### 3, 配置go-cqhttp
  
    - >go-cqhttp刚开始需要选择正向ws和http api

    - 详见go-cqhttp官方文档(https://docs.go-cqhttp.org/guide/quick_start.html)
  
- ### 4, 编写插件
 - >示例的插件 qqbot.py、qqbot_http_api.py 
- ### 5, 启动
    -  ```python main.py``` 
	
	PS：第一次运行会停止2次初始化配置文件

</details>


有什么bug或者建议可以提Issues

官方群聊：818266207

<details>
<summary>TODO：</summary>

  - #### 对接框架
    - [x] go-cqhttp
    - [ ] icqq
  
  - #### 接口
    - [ ] onebot V12
    - [x] http api （只有一个发送消息的api也算是吧？后面慢慢完善
</details>
