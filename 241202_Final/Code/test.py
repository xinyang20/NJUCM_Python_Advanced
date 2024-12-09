from tensorflow.keras.applications.vgg16 import VGG16, preprocess_input, decode_predictions

# 测试模型加载
model = VGG16(weights='imagenet')
print("VGG16 模型加载成功")
