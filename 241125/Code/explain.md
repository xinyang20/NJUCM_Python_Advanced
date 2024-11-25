### **1. 导入必要的库**
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, classification_report
```

- `pandas`：用于数据加载、清洗和操作。
- `train_test_split`：用于将数据划分为训练集和验证集。
- `MinMaxScaler`：将数值特征归一化到[0, 1]范围。
- `PCA`：主成分分析，用于特征降维。
- `LogisticRegression`：逻辑回归模型。
- `KNeighborsClassifier`：K近邻分类器。
- `DecisionTreeClassifier`：决策树分类器。
- `RandomForestClassifier`：随机森林分类器。
- `accuracy_score`：用于计算模型预测的准确率。
- `recall_score`：用于计算模型预测的召回率。
- `classification_report`：生成分类指标的报告。

---

### **2. 加载数据**
```python
train_file_path = '../实验7科学计算实验2/train.csv'
test_file_path = '../实验7科学计算实验2/test.csv'
train_data = pd.read_csv(train_file_path)
test_data = pd.read_csv(test_file_path)
```

- `pd.read_csv`：加载训练集和测试集，分别存储在 `train_data` 和 `test_data`。

---

### **3. 去掉列名中的多余空格**
```python
train_data.columns = train_data.columns.str.strip()
test_data.columns = test_data.columns.str.strip()
```

- `str.strip`：去除列名中可能存在的前后多余空格，避免后续引用列名时报错。

---

### **4. 定义数据预处理函数**
```python
def preprocess_data(data):
    data = data.copy()
```

- 创建数据副本，避免修改原始数据。

#### **删除 Cabin 列**
```python
    data.drop(columns=['Cabin'], inplace=True, errors='ignore')
```
- `drop`：删除 `Cabin` 列，因为该列的缺失值过多。
- `errors='ignore'`：即使列不存在也不会报错。

#### **处理缺失值**
```python
    data['Age'] = data['Age'].fillna(data['Age'].median())
    data['Fare'] = data['Fare'].fillna(data['Fare'].median())
    data['Embarked'] = data['Embarked'].fillna(data['Embarked'].mode()[0])
```
- `fillna`：用中位数填充数值特征 `Age` 和 `Fare` 的缺失值，用众数填充类别特征 `Embarked` 的缺失值。

#### **数值化特征**
```python
    data['Sex'] = data['Sex'].map({'male': 1, 'female': 0})
    data['Embarked'] = data['Embarked'].map({'S': 0, 'Q': -1, 'C': 1})
```
- `map`：将 `Sex` 和 `Embarked` 列中的文本值转化为数值。

#### **生成新特征**
```python
    data['FamilySize'] = data['SibSp'] + data['Parch'] + 1
```
- 计算家庭成员总数作为新特征 `FamilySize`。

#### **归一化数值特征**
```python
    scaler = MinMaxScaler()
    data[['Age', 'Fare']] = scaler.fit_transform(data[['Age', 'Fare']])
```
- `MinMaxScaler`：将数值特征 `Age` 和 `Fare` 缩放到[0, 1]范围。

---

### **5. 预处理训练集和测试集**
```python
train_data = preprocess_data(train_data)
test_data = preprocess_data(test_data)
```

- 调用 `preprocess_data` 函数对训练集和测试集进行预处理。

---

### **6. 数据划分**
```python
features = ['Pclass', 'Sex', 'Age', 'Fare', 'Embarked', 'FamilySize']
X = train_data[features]
y = train_data['Survived']
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
```

- `features`：特征列名称。
- `X`：特征数据。
- `y`：目标数据（是否生存）。
- `train_test_split`：划分训练集（80%）和验证集（20%）。

---

### **7. 检查并填充缺失值**
```python
X_train = X_train.fillna(X_train.mean())
X_val = X_val.fillna(X_val.mean())
```

- `fillna`：用均值填充训练集和验证集中的任何缺失值。

---

### **8. 定义模型字典**
```python
models = {
    "逻辑回归": LogisticRegression(),
    "K近邻": KNeighborsClassifier(),
    "决策树": DecisionTreeClassifier(),
    "随机森林": RandomForestClassifier()
}
```

- 包含所有模型的字典，以便后续循环训练和评估。

---

### **9. 模型训练和评估**
```python
results = []
for model_name, model in models.items():
    model.fit(X_train, y_train)
    y_pred = model.predict(X_val)
    acc = accuracy_score(y_val, y_pred)
    rec = recall_score(y_val, y_pred)
    report = classification_report(y_val, y_pred, output_dict=True)
    results.append({"模型": model_name, "准确率": acc, "召回率": rec, "分类报告": report})
```

- `model.fit`：在训练集上训练模型。
- `model.predict`：在验证集上进行预测。
- `accuracy_score`：计算准确率。
- `recall_score`：计算召回率。
- `classification_report`：生成分类指标的详细报告。

---

### **10. 展示结果**
```python
results_df = pd.DataFrame([{"模型": r["模型"], "准确率": r["准确率"], "召回率": r["召回率"]} for r in results])
print(results_df)
results_df.to_csv("model_evaluation_results.csv", index=False)
```

- 将模型评估结果转换为 DataFrame，并保存为 CSV 文件。

---

### **11. 对测试集进行预测**
```python
best_model = RandomForestClassifier()
best_model.fit(X, y)
test_predictions = best_model.predict(test_data[features])
test_data['Survived'] = test_predictions
test_data[['PassengerId', 'Survived']].to_csv("titanic_predictions.csv", index=False)
```

- 使用随机森林模型重新在完整训练集上训练，并对测试集进行预测。
- 将预测结果保存到 CSV 文件。
