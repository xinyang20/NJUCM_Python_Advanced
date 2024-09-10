def f(x):
    i = 1
    sum = 0
    while i <= x:
        sum += i
        i += 1
    return sum
def g(n):
    i = 1
    sum = 0
    while i <= n:
        sum += f(i)
        i += 1
    return sum

n = 10
print("1到10的阶乘求和结果：", g(int(n)))
# Output:
# 1到10的阶乘求和结果： 220