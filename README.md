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
  同是，您也可以非常方便地构建一个Statement：
  ```python
  from pbf.statement import Statement
  class AudioStatement(Statement):
    cqtype = 'audio'
    url: str = None
    file: str = None
    def __init__(self, url, file):
      self.url = url
      self.file = file
  ```
  然后就可以：
  ```python
  self.client.msg(AudioStatement('https://audio.com/audio.mp3', 'audio.mp3')).send()
  ```
  这样就会发送如下的CQ码：
  ```json
  {"type":"audio","url":"https://audio.com/audio.mp3","file":"audio.mp3"}
  ```
- 引入了Model，使数据储存读取更加便捷，易于维护。您无需再接触繁琐的SQL代码，只需要实现一个简单的Model类，然后便可轻松操作
  ```python
  from pbf.model import DictModel
  class Model(DictModel):
    db_table = 'users
    map = ['uid']
    def id(self):
      return 'int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY'
    def uid(self):
      return 'int(11) NOT NULL'
    def name(self):
      return 'varchar(255) NOT NULL'
  ```
  然后可以通过便捷的方法修改数据或读取
  ```python
  model = Model(uid=114514)
  print(model._get('name'))
  model._set(name='homo')
  print(model.existsFlag)
  model._delete()
  ```
  您无需处理数据表的创建，因为`ModelBase`会帮你完成。同时，Model还与Cache模块高度联动。所有数据均在Cache中缓存，在调用`__del__`时同步到数据库，因此您无需担心效率问题。
- 便捷的指令注册。现在插件注册指令肥肠简单，假设我有一个插件叫`foo`，需要实现一个指令`test`：
  ```python
  from pbf.controller.PBF import PBF
  from pbf.utils.RegCmd import RegCmd

  class foo(PBF):
    @RegCmd(
      name = "test",
      usage = "test",
      permission = "anyone",
      function = "foo@test",
      alias = ["别名1", "别名2"],
      description = "test",
      mode = "分类",
      hidden = 0,
      type = "command"
    )
    def test(self):
      print('test')
      self.send('test')
  ```
  只需要添加一个RegCmd注解，然后传入需要的参数即可。

  
## PBFv4新架构
PBFv4将采用`MSC（Model-Statement-Controller）`模式编写插件，与`MVC`不同之处在于将`View`更改为了`Statement`，不过其作用基本相同。  
与`MVC`相同，`Model`部分主要控制数据的存取等。插件需要实现一个model类，来实现数据存取。自建的`Model`类需要继承`model.ModelBase`类，并可以轻松实现数据存取。具体详见开发文档。
自建的`Statement`类也需要继承`statement.Statement`类，具体详见开发文档。