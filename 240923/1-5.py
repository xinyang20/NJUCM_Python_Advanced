import numpy as np
# 创建一个一维长度为15的随机矩阵和一个9随机矩阵，
# 将前者使用reshape改为5*3的矩阵，与3*3的矩阵，求矩阵积
a = np.random.rand(15)
b = np.random.rand(9)
a = a.reshape(5, 3)
b = b.reshape(3, 3)
c = np.dot(a, b)
print(c)