import pandas as pd
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Ouki', 'Rose'],
    'Age': [27, 24, 22, 35, 39, 25],
    'City': [None, 'New York', 'Los Angeles', 'Chicago', 'Beijing', 'Xian'],
    'Salary': [8000, 5000, 6500, 5200, 20000, 6500],
    'Department': ['IT', 'HR', 'IT', 'Finance', 'Finance', 'HR'],
    'Years_of_work': [3, 2, 2, 6, 10, 3]
}
df = pd.DataFrame(data)
avg_salary = df.groupby('Department')['Salary'].mean()
# 3-1
# 绘制题2中每个部门的平均工资条形图，展示不同部门的工资水平差异。
# 要求：
# X 轴表示部门名称，Y 轴表示平均工资。
# 条形图上每根柱子显示具体的平均工资数值。
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
avg_salary.plot(kind='bar', title='平均薪资表')
for x, y in enumerate(avg_salary):
    plt.text(x, y, '%.2f' % y, ha='center', va='bottom')
plt.show()

# 3-2
# 绘制一个热力图，显示每个部门与员工工作年限和工资之间的关系。
# 要求：
# 横轴表示 "Department"（部门），纵轴表示 "Years_of_work"（工作年限），每个方格的颜色深浅代表工资的高低。
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
df = pd.DataFrame(data)
df = df.pivot_table(index='Department', columns='Years_of_work', values='Salary', aggfunc=np.mean)
sns.heatmap(df, cmap='YlGnBu', annot=True)
plt.show()