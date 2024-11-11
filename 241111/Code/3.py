import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from urllib.parse import urljoin

# 目标网页的 URL
url = "https://xxgk.njucm.edu.cn/"

# 发送 GET 请求获取网页内容
response = requests.get(url)
response.encoding = 'utf-8'  # 确保编码正确

# 使用 BeautifulSoup 解析 HTML 内容
soup = BeautifulSoup(response.text, "html.parser")

# 初始化列表存储提取的信息
department_data = []

# 查找每个信息公开表格
tables = soup.find_all('table', {'background': '/_upload/tpl/01/c0/448/template448/images/sliderbg.png'})

for table in tables:
    # 提取部门信息
    dept_info = {}
    header = table.find('td', style="font-size:12px; font-weight:bold;")
    dept_info['部门名称'] = header.get_text(strip=True) if header else ""

    # 提取详细信息
    p = table.find('p')
    if p:
        # 获取所有行
        lines = p.get_text(separator='\n', strip=True).split('\n')
        for line in lines:
            # 按冒号分割每行，提取键值对
            if '：' in line:
                key, value = line.split('：', 1)
                key = key.strip()
                value = value.strip()
                dept_info[key] = value

    # 添加到列表中
    department_data.append(dept_info)

# 将数据保存到 Excel
df = pd.DataFrame(department_data)
df.to_excel('南京中医药大学信息公开部门信息.xlsx', index=False)
print("信息已保存到 '南京中医药大学信息公开部门信息.xlsx' 文件中。")

# 下载相关图片
image_tags = soup.find_all('img')  # 查找所有图片标签
image_urls = [img['src'] for img in image_tags if 'src' in img.attrs]

# 创建保存图片的目录
os.makedirs('images', exist_ok=True)

for i, img_url in enumerate(image_urls):
    # 处理相对 URL
    img_url = urljoin(url, img_url)

    # 发送 GET 请求获取图片
    img_response = requests.get(img_url, stream=True)
    if img_response.status_code == 200:
        # 获取图片扩展名
        ext = os.path.splitext(img_url)[1]
        # 将图片保存到 'images' 目录
        with open(f'images/image_{i + 1}{ext}', 'wb') as f:
            for chunk in img_response.iter_content(1024):
                f.write(chunk)
        print(f"已下载 image_{i + 1}{ext}")
    else:
        print(f"下载 {img_url} 失败")
