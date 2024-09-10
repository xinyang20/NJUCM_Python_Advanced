import numpy as np
import PIL.Image as img

img_njucm = img.open('njucm.jpg')
img_array = np.array(img_njucm)

# Red_Channel
red_channel = img_array.copy()
red_channel[:, :, 1] = 0
red_channel[:, :, 2] = 0

# Green_Channel
green_channel = img_array.copy()
green_channel[:, :, 0] = 0
green_channel[:, :, 2] = 0

# Blue_Channel
blue_channel = img_array.copy()
blue_channel[:, :, 0] = 0
blue_channel[:, :, 1] = 0

# 转换图像
red_image = img.fromarray(red_channel)
green_image = img.fromarray(green_channel)
blue_image = img.fromarray(blue_channel)
gray_image = img_njucm.convert('L')

# 保存修改后的图像
red_image.save('red_channel_njucm.jpg')
green_image.save('green_channel_njucm.jpg')
blue_image.save('blue_channel_njucm.jpg')
gray_image.save('gray_njucm.jpg')