# 1、request库的练习：
# 尝试爬取百度网页、京东商品网页或亚马逊商品网页中的任意两个网页，并展示网页的前200个字符。
import requests
url='https://www.baidu.com'
response=requests.get(url)
print(response.text[:200])

print('-------------------')
url='https://jd.com'
response=requests.get(url)
print(response.text[:200])

# Output:<!DOCTYPE html>
# <!--STATUS OK--><html> <head><meta http-equiv=content-type content=text/html;charset=utf-8><meta http-equiv=X-UA-Compatible content=IE=Edge><meta content=always name=referrer><link re
# -------------------
# <!DOCTYPE html>
# <html>
#
# <head>
#     <meta charset="utf8" version='1'/>
#     <title>京东(JD.COM)-正品低价、品质保障、配送及时、轻松购物！</title>
#     <meta name="viewport" content="width=device-width, initial-scale=1.0, maxim