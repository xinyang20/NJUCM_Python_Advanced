from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 模拟用户数据库
users = {"test_user": "test_password"}

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # 验证用户名和密码
    if username in users and users[username] == password:
        session['username'] = username
        flash('登录成功！', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('用户名或密码错误！', 'danger')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"欢迎，{session['username']}！<br><a href='/logout'>注销</a>"
    else:
        flash('请先登录！', 'warning')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('已注销成功！', 'info')
    return redirect(url_for('home'))

app.run(debug=True)
