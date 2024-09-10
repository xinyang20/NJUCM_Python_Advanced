str="Hello World"
x=input("请输入一个数字：")
x=int(x)
if x==0:
    print(str)
elif x>0:
    i=0
    while i+1< len(str):
        print(str[i:i+2])
        i+=2
    if i<len(str):
        print(str[i:])
else:
    print(str[0],str[-1])