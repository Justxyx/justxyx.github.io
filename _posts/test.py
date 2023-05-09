 # -*- coding: utf-8 -*

f=open("./task07测试.txt",'a+')
for i in range(1,195):
    f.write('xyx_' + str(i))
    f.write("\n")                               #每个数字一行
f.close()

