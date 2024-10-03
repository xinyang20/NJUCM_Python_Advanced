# 导入所需的模块
import pygame,sys,time
# 初始化pygame
pygame.init()
# 设置窗口大小
screen = pygame.display.set_mode((600, 400))
# 设置窗口标题
pygame.display.set_caption("钢琴模拟")
# 设置按键时的图像
bgImg = pygame.image.load("piano.png")
bgImg0 = pygame.image.load("piano.png")
bgImg1 = pygame.image.load("piano1.png")
bgImg2 = pygame.image.load("piano2.png")
bgImg3 = pygame.image.load("piano3.png")
bgImg4 = pygame.image.load("piano4.png")
bgImg5 = pygame.image.load("piano5.png")
bgImg6 = pygame.image.load("piano6.png")
bgImg7 = pygame.image.load("piano7.png")
bgImg8 = pygame.image.load("piano8.png")
# 设置音符
sound1 = pygame.mixer.Sound("1.wav")
sound2 = pygame.mixer.Sound("2.wav")
sound3 = pygame.mixer.Sound("3.wav")
sound4 = pygame.mixer.Sound("4.wav")
sound5 = pygame.mixer.Sound("5.wav")
sound6 = pygame.mixer.Sound("6.wav")
sound7 = pygame.mixer.Sound("7.wav")
sound8 = pygame.mixer.Sound("8.wav")
# 设置音量
sound_big = 20
# 设置背景音乐
pygame.mixer.music.load("Minecraft-c418.mp3")
pygame.mixer.music.play(sound_big)
run_thing = True
# 设置主循环
while run_thing:
    # 获取事件
    for event in pygame.event.get():
        # 判断事件是否为退出事件
        if event.type == pygame.QUIT:
                #or event.type == pygame.K_q:
            # 退出pygame
            pygame.quit()
            # 退出系统
            sys.exit()
            # 获得键盘按下的事件
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE: 
                run_thing = False
            elif event.key == pygame.K_1:
                bgImg = bgImg1
                sound1.play()
            elif event.key == pygame.K_2:
                bgImg = bgImg2
                sound2.play()
            elif event.key == pygame.K_3:
                bgImg = bgImg3
                sound3.play()
            elif event.key == pygame.K_4:
                bgImg = bgImg4
                sound4.play()
            elif event.key == pygame.K_5:
                bgImg = bgImg5
                sound5.play()
            elif event.key == pygame.K_6:
                bgImg = bgImg6
                sound6.play()
            elif event.key == pygame.K_7:
                bgImg = bgImg7
                sound7.play()
            elif event.key == pygame.K_8:
                bgImg = bgImg8
                sound8.play()
            elif event.key == pygame.K_0:
                sound_big -= 1
                pygame.mixer.music.play(sound_big)
                # 设置背景为白色
    screen.fill((255, 255, 255))
    # 这里给了2个实参，分别是图像，绘制的位置
    screen.blit(bgImg, (0, 0))
    # 绘制屏幕内容
    pygame.display.update()
    # 推迟执行
    time.sleep(0.05)
    bgImg = bgImg0
    screen.blit(bgImg, (0, 0))
    # 刷新内容
    pygame.display.update()