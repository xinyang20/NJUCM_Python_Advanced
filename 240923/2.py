import pandas as pd
# 创建一个包含以下数据的 DataFrame：
# Name	Age	City	Salary	Department	Years_of_work
# Alice	27	Nanjing	8000	IT	3
# Bob	24	New York	5000	HR	2
# Charlie	22	Los Angeles	6500	IT	2
# David	35	Chicago	5200	Finance	6
# Ouki	39	Beijing	20000	Finance	10
# Rose	25	Xian	6500	HR	3
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Ouki', 'Rose'],
    'Age': [27, 24, 22, 35, 39, 25],
    'City': [None, 'New York', 'Los Angeles', 'Chicago', 'Beijing', 'Xian'],
    'Salary': [8000, 5000, 6500, 5200, 20000, 6500],
    'Department': ['IT', 'HR', 'IT', 'Finance', 'Finance', 'HR'],
    'Years_of_work': [3, 2, 2, 6, 10, 3]
}
df = pd.DataFrame(data)
print("problem 2-1 result:\n",df)

# 2-2
# 基于上述数据，找出所有年龄大于 25 且工资大于 6000 的员工的姓名和工资
result = df[(df['Age'] > 25) & (df['Salary'] > 6000)]
print("problem 2-2 result:\n",result)

# 2-3
# 基于题(1)计算每个部门的平均工资，并找出哪个部门的总工资最高。
avg_salary = df.groupby('Department')['Salary'].mean()
max_salary = avg_salary.idxmax()
print("problem 2-3 result:\n",avg_salary)