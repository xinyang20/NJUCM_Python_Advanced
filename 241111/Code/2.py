import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.weather.com.cn/weather/101190101.shtml"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36"
}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")
forecast = []
ul = soup.find('ul', class_='t clearfix')
if ul:
    lis = ul.find_all('li')
    for li in lis[:7]:
        date = li.find('h1').get_text()
        weather = li.find('p', class_='wea').get_text()
        temp_high = li.find('p', class_='tem').find('span')
        temp_high = temp_high.get_text().replace('℃', '') if temp_high else ''
        temp_low = li.find('p', class_='tem').find('i').get_text().replace('℃', '')
        wind = li.find('p', class_='win').find('span')['title']
        wind_speed = li.find('p', class_='win').find('i').get_text()

        forecast.append({
            "日期": date,
            "天气": weather,
            "最高温度(℃)": temp_high,
            "最低温度(℃)": temp_low,
            "风向": wind,
            "风速": wind_speed
        })

df = pd.DataFrame(forecast)
df.to_excel("南京未来七天天气预报.xlsx", index=False)
print("数据已保存到文件中")
