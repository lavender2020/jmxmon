# jmxmon
jmxmon monitor for java tomcat

## jar 
更改java程序启动脚本，程序jar包启动的时候，增加参数:   
 -Dcom.sun.management.jmxremote.port=$MONPORT \  
 -Dcom.sun.management.jmxremote.ssl=false \  
 -Dcom.sun.management.jmxremote.authenticate=false \  

备注:  
  参数直接加载 java 命令后面  
  $MONPORT 为启用的监控端口  
  默认禁用ssl和认证功能  
  
## tomcat
在catalina.sh文件Execute The Requested Command行下面增加:
CATALINA_OPTS="-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.port=$MONPORT -Dcom.sun.management.jmxremote.ssl=false -Dcom.sun.management.jmxremote.authenticate=false"  

备注:
  $MONPORT 为启用的监控端口
  默认禁用ssl和认证功能

## 配置文件

cat conf.properties   
\# the working dir  
workDir=./  
  
\# localhost jmx ports, split by comma  
jmx.ports=18877  \# $MONPORT  

\# agent port url  
agent.posturl=http://localhost  

\#project-name  
port2project=18877@uploadservice  \# MONPORT@service description  


\# 可选项：上报给open-falcon的endpoint，默认值为本机hostname。不建议修改  
hostname=wxyd-ocs-p70-193.hjidc.com  \# monitor host hostname  
 
\# 可选项：上报给open-falcon的上报间隔，默认值60，单位秒。不建议修改  
#step=  


## agent处理程序
### jmxmon-0.0.2-jar-with-dependencies.jar  
负责采集客户端数据，采集间隔1分钟，采集数据保存为jmxmon.jvm.context.json，三次采集并处理后保存到jmxmon.txt  

### zabbixSender.py  
zabbixSender.py 被jmxmon-0.0.2-jar-with-dependencies.jar调用并把数据文件jmxmon.txt数据传送到zabbix    
配置文件中需要更改zabbix proxy地址:  sender = ZabbixSender(u'zabbix-proxy.yeshj.com')   



