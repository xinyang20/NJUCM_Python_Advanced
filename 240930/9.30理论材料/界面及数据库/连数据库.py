import tkinter as tk
from tkinter import messagebox
import webbrowser
from PIL import Image, ImageTk  # 使用PIL支持更多图片格式
import mysql.connector  # MySQL 连接器

# 创建主窗口
root = tk.Tk()
root.title("注册与登录界面")

# 设置窗口大小和居中显示函数
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()  # 获取屏幕宽度
    screen_height = window.winfo_screenheight()  # 获取屏幕高度
    x = (screen_width // 2) - (width // 2)  # 计算窗口左上角的x坐标
    y = (screen_height // 2) - (height // 2)  # 计算窗口左上角的y坐标
    window.geometry(f'{width}x{height}+{x}+{y}')  # 设置窗口大小和位置

# 调用函数将窗口大小设置为800x600并居中
center_window(root, 800, 600)

# 背景图片
bg_image = Image.open("background.png")  # 替换为你的背景图片路径
bg_image = bg_image.resize((800, 600))  # 调整背景图片大小以适应窗口
bg_photo = ImageTk.PhotoImage(bg_image)

# 使用Label设置背景图片
bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)  # 将背景图片填满整个窗口

# 创建 MySQL 数据库连接
def connect_db():
    connection = mysql.connector.connect(
        host="localhost",  # MySQL 服务器地址
        user="root",  # MySQL 用户名
        password="20050317",  # MySQL 密码
        database="PyGame230930"  # MySQL 数据库名称
    )
    return connection

# 注册功能
def register():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("错误", "请输入用户名和密码！")
        return

    # 连接数据库
    conn = connect_db()
    cursor = conn.cursor()

    # 检查用户名是否已存在
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()

    if result:
        messagebox.showerror("错误", "用户名已存在！")
    else:
        # 插入新用户
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        messagebox.showinfo("注册成功", "注册成功！")

    # 关闭数据库连接
    cursor.close()
    conn.close()

# 登录功能
def login():
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("错误", "请输入用户名和密码！")
        return

    # 连接数据库
    conn = connect_db()
    cursor = conn.cursor()

    # 查询用户
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    result = cursor.fetchone()

    if result:
        messagebox.showinfo("登录成功", f"欢迎，{username}！")
        root.withdraw()  # 隐藏登录窗口
        open_video_window()  # 登录成功后打开视频界面
    else:
        messagebox.showerror("错误", "用户名或密码错误！")

    # 关闭数据库连接
    cursor.close()
    conn.close()

# 打开锻炼视频窗口
def open_video_window():
    # 创建新窗口
    video_window = tk.Toplevel(root)
    video_window.title("中医锻炼视频")
    center_window(video_window, 800, 600)  # 将新窗口大小设置为800x600并居中

    # 视频界面的背景图片
    video_bg_image = Image.open("background.png")  # 替换为你的视频界面背景图片路径
    video_bg_image = video_bg_image.resize((800, 600))  # 调整背景图片大小
    video_bg_photo = ImageTk.PhotoImage(video_bg_image)

    # 使用Label设置视频界面的背景图片
    video_bg_label = tk.Label(video_window, image=video_bg_photo)
    video_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    # 保存图片引用，防止图片被垃圾回收
    video_bg_label.image = video_bg_photo

    # 创建视频列表标签
    label_videos = tk.Label(video_window, text="请选择一个锻炼视频观看:", bg="white")
    label_videos.pack(pady=10)

    # 创建按钮，点击后在浏览器中打开视频链接
    btn_video1 = tk.Button(video_window, text="中医气功锻炼视频",
        command=lambda: open_video_link("https://www.bilibili.com/video/BV185411K7nx/?spm_id_from=333.337.search-card.all.click&vd_source=85d692aa67f6f261f67a8cdbaec8db2d"))
    btn_video1.pack(padx=10,pady=10)

    btn_video2 = tk.Button(video_window, text="中医养生太极视频",
        command=lambda: open_video_link("https://example.com/taichi"))
    btn_video2.pack(padx=10,pady=10)

    btn_video3 = tk.Button(video_window, text="中医八段锦锻炼视频",
        command=lambda: open_video_link("https://example.com/baduanjin"))
    btn_video3.pack(padx=10,pady=10)


# 打开指定视频链接
def open_video_link(url):
    webbrowser.open(url)


# 创建用户名和密码的标签和输入框
frame_form = tk.Frame(root)  # 使用frame让控件居中
frame_form.place(relx=0.5, rely=0.4, anchor=tk.CENTER)  # 设置frame的位置在界面中央

label_username = tk.Label(frame_form, text="用户名:", bg="white")
label_username.grid(row=0, column=0, padx=10, pady=10)
entry_username = tk.Entry(frame_form)
entry_username.grid(row=0, column=1, padx=10, pady=10)

label_password = tk.Label(frame_form, text="密码:", bg="white")
label_password.grid(row=1, column=0, padx=10, pady=10)
entry_password = tk.Entry(frame_form, show='*')  # 使用 '*' 来隐藏密码输入
entry_password.grid(row=1, column=1, padx=10, pady=10)

# 创建注册和登录按钮
frame_buttons = tk.Frame(root)  # 使用frame让按钮水平排列
frame_buttons.place(relx=0.5, rely=0.6, anchor=tk.CENTER)  # 设置frame的位置在界面中央

btn_register = tk.Button(frame_buttons, text="注册", command=register)
btn_register.grid(row=0, column=0, padx=20, pady=10)

btn_login = tk.Button(frame_buttons, text="登录", command=login)
btn_login.grid(row=0, column=1, padx=20, pady=10)

# 运行主循环
root.mainloop()
