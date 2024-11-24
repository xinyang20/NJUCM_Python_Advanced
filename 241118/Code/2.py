import cv2


def detect_faces(image, output="output.jpg"):
    # 加载预训练的 Haar 特征分类器（人脸检测）
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # 读取图像
    image = cv2.imread(image)
    if image is None:
        print("无法加载图像，请检查路径！")
        return

    # 转换为灰度图像（人脸检测通常在灰度图上完成）
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(160, 160))

    print(f"检测到 {len(faces)} 张人脸。")

    # 如果检测到人脸，绘制矩形框
    for (x, y, w, h) in faces:
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 保存标注后的图像
    cv2.imwrite(output, image)
    print(f"标注后的图像已保存至 {output}")

    # # 显示结果（可选）
    # cv2.imshow("Detected Faces", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()



input_image = "../test_image.jpg"
detect_faces(input_image)
