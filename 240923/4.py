# 4-1
# 缺失值处理：鸢尾花数据集共150个样本，每个样本5个字段，其中四个是特征变量，
# 即萼片长度(Sepal_len)、萼片宽度(Sepal_with)、花瓣长度(Petal_len)、花瓣宽度(Petal_wid)，
# 还有一个字段是其所属的品种的类别变量(species)。
# 下表是鸢尾花数据集的前15个样本数据，其中有一个缺失值。
# 要求分别使用均值、中位数或某种算法填充缺失值。
# 并与原来的真实值4.8进行比较（通过方差、标准差等方法）。
import numpy as np
import pandas as pd

# 方差
def variance(data):
    mean = np.mean(data)
    return np.mean((data - mean) ** 2)
# 标准差
def standard_deviation(data):
    return np.sqrt(variance(data))

data = {
    'Sepal_len': [5.1, 4.9, np.nan, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9, 5.4, 4.8, 4.8, 4.3, 5.8],
    'Sepal_with': [3.5, 3.0, 3.2, 3.1, 3.6, 3.9, 3.4, 3.4, 2.9, 3.1, 3.7, 3.4, 3.0, 3.0, 4.0],
    'Petal_len': [1.4, 1.4, 1.3, 1.5, 1.4, 1.7, 1.4, 1.5, 1.4, 1.5, 1.5, 1.6, 1.4, 1.1, 1.2],
    'Petal_wid': [0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.3, 0.2, 0.2, 0.1, 0.2, 0.2, 0.1, 0.1, 0.2]
}
true_data=4.8
df = pd.DataFrame(data)
# 均值
df.fillna(df.mean(), inplace=True)
print("补充值：", df['Sepal_len'][3], "方差：", variance(df['Sepal_len']), "标准差：", standard_deviation(df['Sepal_len']))
# 中位数
df.fillna(df.median(), inplace=True)
print("补充值：", df['Sepal_len'][3], "方差：", variance(df['Sepal_len']), "标准差：", standard_deviation(df['Sepal_len']))
# 众数
df.fillna(df.mode().iloc[0], inplace=True)
print("补充值：", df['Sepal_len'][3], "方差：", variance(df['Sepal_len']), "标准差：", standard_deviation(df['Sepal_len']))


# 4-2
# 对上述填充后的数据进行探索，画出各个属性对应的散点图及箱线图。分析上限、下限、异常值等。
import matplotlib.pyplot as plt
import seaborn as sns
# 散点图
sns.pairplot(df)
plt.show()
# 箱线图
df.boxplot()
plt.show()
# 通过箱线图可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid都存在异常值，其中Petal_wid的异常值最多。
# 通过散点图可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid之间存在一定的相关性。
# 通过上限、下限可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid的上限、下限分别为：
print("Sepal_len上限：", df['Sepal_len'].max(), "Sepal_len下限：", df['Sepal_len'].min())
print("Sepal_with上限：", df['Sepal_with'].max(), "Sepal_with下限：", df['Sepal_with'].min())
print("Petal_len上限：", df['Petal_len'].max(), "Petal_len下限：", df['Petal_len'].min())
print("Petal_wid上限：", df['Petal_wid'].max(), "Petal_wid下限：", df['Petal_wid'].min())
# 通过异常值可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid的异常值分别为：
print("Sepal_len异常值：", df['Sepal_len'][df['Sepal_len'] > df['Sepal_len'].max()])
print("Sepal_with异常值：", df['Sepal_with'][df['Sepal_with'] > df['Sepal_with'].max()])
print("Petal_len异常值：", df['Petal_len'][df['Petal_len'] > df['Petal_len'].max()])
print("Petal_wid异常值：", df['Petal_wid'][df['Petal_wid'] > df['Petal_wid'].max()])


# 4-3
# 对上述填充后的数据进行规范化，可选最大最小规范化、零均值标准化、小数定标规范化等方法。

# 最大最小规范化
def max_min_normalization(data):
    return (data - data.min()) / (data.max() - data.min())
# 零均值标准化
def zero_mean_normalization(data):
    return (data - data.mean()) / data.std()
# 小数定标规范化
def decimal_scaling_normalization(data):
    return data / 10 ** np.ceil(np.log10(data.abs().max()))
df_max_min = df.copy()
df_max_min.iloc[:, :] = max_min_normalization(df_max_min)
print("最大最小规范化：\n", df_max_min)
df_zero_mean = df.copy()
df_zero_mean.iloc[:, :] = zero_mean_normalization(df_zero_mean)
print("零均值标准化：\n", df_zero_mean)
df_decimal_scaling = df.copy()
df_decimal_scaling.iloc[:, :] = decimal_scaling_normalization(df_decimal_scaling)
print("小数定标规范化：\n", df_decimal_scaling)
# 通过规范化后，可以看出，最大最小规范化、零均值标准化、小数定标规范化后的数据都在0-1之间。
# 通过零均值标准化可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid的均值为0，标准差为1。
# 通过小数定标规范化可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid的绝对值最大值为1。
# 通过最大最小规范化可以看出，Sepal_len、Sepal_with、Petal_len、Petal_wid的最大值为1，最小值为0。
# 通过箱线图可以看出，最大最小规范化、零均值标准化、小数定标规范化后的数据都存在异常值，其中最大最小规范化、零均值标准化、小数定标规范化后的数据都存在异常值。