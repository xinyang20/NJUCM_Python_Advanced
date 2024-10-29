import pygame

# 初始化
pygame.init()
screen = pygame.display.set_mode([800, 600])
ico = pygame.image.load('./image/fish_1.png')
pygame.display.set_caption('抓鱼游戏')
pygame.display.set_icon(ico)
font = pygame.font.Font('./font/simhei.ttf', 50)
bg = pygame.image.load('./image/background.png')
fish = pygame.image.load('./image/fish_2.png')
playerimg = pygame.image.load('./image/wang.png')
const_time = 60
time = const_time
record = False

# 精灵定义
scale = 120
pic = pygame.transform.scale(fish, (scale, scale))
colorkey = pic.get_at((0, 0))
pic.set_colorkey(colorkey)
picx = picy = 0
timer = pygame.time.Clock()
speedX = speedY = 5
paddleW, paddleH = 200, 25
paddleX, paddleY = 300, 550
yellow = (255, 255, 0)
picW = picH = 100
points = 0
lives = 5

# 音乐加载
pygame.mixer.init()
pygame.mixer.music.load('./music/天空之城.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)
sound = pygame.mixer.Sound('./music/shot.wav')  # 加载音效

history_points = [20, 40, 30, 1]
# 主游戏循环
while True:
    if time > 0:
        time -= timer.get_time() / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # 游戏计分
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1 and (lives == 0 or time <= 0):
                points = 0
                lives = 5
                picx = picy = 0
                speedX = speedY = 5
                time = const_time
                record = False

    # 精灵坐标计算
    picx += speedX
    picy += speedY
    x, y = pygame.mouse.get_pos()
    x -= playerimg.get_width() / 2
    y = 400
    pygame.mouse.set_visible(False)

    # 精灵速度 - 边界检测
    if picx <= 0 or picx + pic.get_width() >= 800:
        pic = pygame.transform.flip(pic, True, False)
        speedX = -speedX * 1.1
    if picy <= 0:
        speedY = -speedY + 1
    if picy >= 500:
        lives -= 1
        speedY = -5
        speedX = 5
        picy = 500

    # 精灵动画
    screen.blit(bg, (0, 0))
    screen.blit(pic, (picx, picy))
    paddleX = pygame.mouse.get_pos()[0]
    paddleX -= paddleW / 2

    # 精灵碰撞检测
    pygame.draw.rect(screen, yellow, (paddleX, paddleY, paddleW, paddleH))
    if picy + picH >= paddleY and picy + picH <= paddleY + paddleH and speedY > 0:
        if picx + picW / 2 >= paddleX and picx + picW / 2 <= paddleX + paddleW:
            sound.play()
            points += 1
            speedY = -speedY
    screen.blit(playerimg, (x, y))
    draw_string = '生命值：' + str(lives) + '积分：' + str(points)
    if lives < 1 or time <= 0:
        speedX = speedY = 0
        draw_string = '游戏结束，你的成绩是：' + str(points)
        if points > 0 and record == False:
            history_points.append(int(points))
            record = True

    # 历史分数记录显示
    font = pygame.font.Font('./font/simhei.ttf', 20)
    history_points.sort(reverse=True)
    points_string = '排名\t分数'
    text = font.render(points_string, True, yellow)
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx + 280
    text_rect.y = 100
    screen.blit(text, text_rect)
    i = 0
    text_rect.centerx += 10
    for point in history_points:
        i += 1
        points_string = str(i) + '\t\t ' + str(point)  # +'\t\t '+str(point[1])
        text = font.render(points_string, True, yellow)

        text_rect.y = text_rect.y + 20
        screen.blit(text, text_rect)
        if (i >= 10):
            break

    time_string = '倒计时：' + str(int(time)) + '秒'
    text = font.render(time_string, True, yellow)
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx - 200
    text_rect.y = 100
    screen.blit(text, text_rect)

    font = pygame.font.Font('./font/simhei.ttf', 50)

    # 图形文字显示
    text = font.render(draw_string, True, yellow)
    text_rect = text.get_rect()
    text_rect.centerx = screen.get_rect().centerx
    text_rect.y = 50
    screen.blit(text, text_rect)
    pygame.display.update()
    timer.tick(60)

# 增加功能：
# ① 设置倒计时功能，到时间，游戏结束。
# ② 创建一个记分板，显示历史最高得分。
