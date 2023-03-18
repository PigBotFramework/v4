# 新版本预告： 
**PBFv4即将崭新推出**  
  
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

## PBFv4新架构
PBFv4现已投入生产一段时间，得到了较好的改进，但同时反映出了一些问题。  
  
PBFv4将采用`MSC（Model-Statement-Controller）`模式编写插件，与`MVC`不同之处在于将`View`更改为了`Statement`，不过其作用基本相同。  
与`MVC`相同，`Model`部分主要控制数据的存取等。插件需要实现一个model类，来实现数据存取。自建的`Model`类需要继承`model.ModelBase`类，并可以轻松实现数据存取。具体详见开发文档。
自建的`Statement`类也需要继承`statement.Statement`类，具体详见开发文档。