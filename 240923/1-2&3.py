# 1-2
import numpy as np
from random import randint
# 使用np.random库创建一个10*10的整型ndarray对象，并打印出最大最小元素;

arr=np.random.randint(low=randint(0,50), high=randint(50,100),size=(10,10))

print("最大值为：",arr.max())
print("最小值为：",arr.min())

# 1-3
# 对第2题中的矩阵，计算最后两列的和;
sum_last_two_column=arr[:,-2:].sum()
print("最后两列的和：",sum_last_two_column)