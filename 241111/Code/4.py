import re
reg=r"\d"
m=re.search(reg,"abc123cd")
print(m)

reg=r"b\d+"
m=re.search(reg,"a12b123c")
print(m)

reg=r"ab+"
m=re.search(reg,"acabc")
print(m)
reg=r"ab*"
m=re.search(reg,"acabc")
print(m)

reg=r"ab?"
m=re.search(reg,"abbcabc")
print(m)

s="xaxby"
m=re.search(r"a.b",s)
print(m)

s="xaabababy"
m=re.search(r"ab|ba",s)
print(m)

reg=r"a\nb?"
m=re.search(reg,"ca\nbcabc")
print(m)

reg=r"car\b"
m=re.search(reg,"The car is black")
print(m)

reg=r"x[0-9]y"
m=re.search(reg,"xyx2y")
print(m)

reg=r"x[^ab0-9]y"
m=re.search(reg,"xayx2yxcy")
print(m)
