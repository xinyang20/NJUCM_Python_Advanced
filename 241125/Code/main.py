import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, precision_score, classification_report

# 加载数据集
train_file_path = '../实验7科学计算实验2/train.csv'
train_data = pd.read_csv(train_file_path)

# 去掉列名中的多余空格
train_data.columns = train_data.columns.str.strip()


# 数据预处理函数
def preprocess_data(data):
    data = data.copy()
    data.drop(columns=['Cabin'], inplace=True, errors='ignore')  # 删除缺失值过多的列
    data['Age'] = data['Age'].fillna(data['Age'].median())  # 用中位数填充年龄缺失值
    data['Fare'] = data['Fare'].fillna(data['Fare'].median())  # 用中位数填充票价缺失值
    data['Embarked'] = data['Embarked'].fillna(data['Embarked'].mode()[0])  # 用众数填充登船口缺失值
    data['Sex'] = data['Sex'].map({'male': 1, 'female': 0})  # 将性别转换为数值型
    data['Embarked'] = data['Embarked'].map({'S': 0, 'Q': -1, 'C': 1})  # 将登船口转换为数值型
    data['FamilySize'] = data['SibSp'] + data['Parch'] + 1  # 创建新特征：家庭成员总数
    scaler = MinMaxScaler()  # 初始化归一化工具
    data[['Age', 'Fare']] = scaler.fit_transform(data[['Age', 'Fare']])  # 归一化年龄和票价
    return data


# 数据预处理
train_data = preprocess_data(train_data)

# 定义特征和目标
features = ['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'FamilySize']
X = train_data[features]  # 特征
y = train_data['Survived']  # 目标值

# 按7:3划分数据集为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 检查并填充可能的缺失值
X_train = X_train.fillna(X_train.mean())
X_test = X_test.fillna(X_test.mean())

# 定义模型
models = {
    "逻辑回归": LogisticRegression(),
    "K近邻": KNeighborsClassifier(),
    "决策树": DecisionTreeClassifier(),
    "随机森林": RandomForestClassifier()
}

# 训练与评估，并保存预测结果
results = []
for model_name, model in models.items():
    # 训练模型
    model.fit(X_train, y_train)

    # 预测测试集
    y_pred = model.predict(X_test)

    # 保存预测结果到 CSV 文件
    predictions_df = X_test.copy()
    predictions_df['真实值'] = y_test.values
    predictions_df['预测值'] = y_pred
    predictions_file = f"{model_name}_predictions.csv"
    predictions_df.to_csv(predictions_file, index=False)
    print(f"{model_name} 的预测结果已保存为 {predictions_file}")

    # 计算评价指标
    acc = accuracy_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # 保存结果
    results.append({
        "模型": model_name,
        "准确率": acc,
        "召回率": rec,
        "精确率": precision,
        "分类报告": report
    })

# 将结果转换为 DataFrame 并展示
results_df = pd.DataFrame(
    [{"模型": r["模型"], "准确率": r["准确率"], "召回率": r["召回率"], "精确率": r["精确率"]} for r in results])
print("模型评估结果：")
print(results_df)

# 保存评估结果到 CSV 文件
results_df.to_csv("model_evaluation_results.csv", index=False)
print("模型评估结果已保存为 model_evaluation_results.csv")
