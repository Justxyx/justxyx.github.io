import matplotlib.pyplot as plt
from pylab import *                                 #支持中文
mpl.rcParams['font.sans-serif'] = ['SimHei']

names = ['0.0','0.1', '0.2', '0.3', '0.4', '0.5','0.6','0.7','0.8','0.9','1.0']
x = range(len(names))
# y = [0.855, 0.84, 0.835, 0.815, 0.81]
y=[84.6,84.8,85.0,85.2,85.4,85.6,85.8,86.0,86.2,86.4,86.6]



y1=[85,85.14,85.56,85.59,85.98,85.72,86.21,85.17,86.08,85.59,85.17]
#plt.plot(x, y, 'ro-')
#plt.plot(x, y1, 'bo-')
#pl.xlim(-1, 11)  # 限定横轴的范围
#pl.ylim(-1, 110)  # 限定纵轴的范围
# plt.plot(x, y, marker='o', mec='r', mfc='w',label=u'111')
plt.plot(x, y1, marker='*', ms=10,label=u'acc')
plt.legend()  # 让图例生效
plt.xticks(x, names, rotation=45)
plt.margins(0)
plt.subplots_adjust(bottom=0.15)
# plt.xlabel(u"time(s)邻居") #X轴标签
plt.ylabel("RMSE") #Y轴标签
plt.title("The effects of  parameters  for accuracy") #标题

plt.show()


y1=[84.6,84.8,85.0,85.2,85.4,85.6,85.8,86.0,86.2,86.4,86.6] 
x1=range(0.1,1.0) 

| 0.1 | -   | 85.14 |
| 0.2 | -   | 85.56 |
| 0.3 | -   | 85.59 |
| 0.4 | -   | 85.98 |
| 0.5 | -   | 85.72 |
| 0.6 | -   | 86.21 |
| 0.7 | -   | 85.17 |
| 0.8 | -   | 86.08 |
| 0.9 | -   | 85.59 |
| 1.0 | -   | 85.17 |