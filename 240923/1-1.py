import numpy as np

arr=np.zeros(shape=(5,6))
arr[1:3,1:4]=1
for row in range(0,5,1):
    for col in range(0,6,1):
        print(arr[row][col],end=' ')
    print()