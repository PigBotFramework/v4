# 新版本预告： 
**PBFv4即将崭新推出**  
  
## PBFv4将分为以下几个组件：  
- PBF核心。PBF核心包含PBF基类、utils、statement、以及各种其他的基础类
- PBF处理器。PBF处理器由FastAPI构建，负责功能较多，例如：启动时加载所有所需数据到cache模块、加载所有插件、提供一些数据结构、处理上报消息（分发监听器）、负责定时任务等等
- PBF进程守护。负责实时监视各处理器的运行状态，必要时启动或重启处理器
- PBF控制面板。网页控制面板（预计使用Flask编写），可以总控以上四个组件 此外还有官网、开发文档、使用文档等业务  
  
  
## PBFv4新特性：
- 重新引入了类似于PBFv2的缓存方案，将需要频繁读写的数据缓存到内存中，由Python维护一个字典
- PBF核心API命名及所处包优化。PBFv3将所有API都堆在了bot类，而PBFv4分散了，例如CallApi和发送消息等移动到了.client包中
- 引入Statement，更易维护。现在可以使用Statement构建消息，例如： 
  ```python
  self.client.msg(
      TextStatement('我爱猪比'),
      FaceStatement(151),
      ImageStatemant(file='abab'),
      Statement('poke', qq=3558267090)
  ).send()
  ```
- 插件编写更加容易。PBFv2/3需要使用data.json及commands.json注册指令及其他信息，而在PBFv4中，只需要插件主类实现__enter__、__exit__方法，并在__enter__方法中返回List[ utils.RegCmd]即可实现注册指令