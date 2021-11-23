2021.11.11

# 1.market1501

- 初始实验结果
![p1](/assets/ims/2021.11/p1.png)

- 改进1
            m1 = imgs[:,:,:,0:64]
            m2 = imgs[:,:,:,0:128]
![p2](/assets/ims/2021.11/p2.png)
- 改进2
            m1 = imgs[:,:,:,0:32]
            m2 = imgs[:,:,:,33:64]
            m3 = imgs[:,:,:,65:96]
            m4 = imgs[:,:,:,97:128]
效果稀烂

- 改进3
            m1 = imgs[:,:,0:128,:]
            m2 = imgs[:,:,129:256,:]
![p2](/assets/ims/2021.11/p3.png)

- 改进4
             m1 = imgs[:,:,:,0:32]
            m2 = imgs[:,:,:,0:64]
            m3 = imgs[:,:,:,0:128]
![p2](/assets/ims/2021.11/p4.png)


- 改机5
  调参
![p2](/assets/ims/2021.11/p5.png)

- 改机6
  调参
![p2](/assets/ims/2021.11/p6.png)


# dukemtmcreid

- 原始结果
![p2](/assets/ims/2021.11/p7.png)
- 模型改进