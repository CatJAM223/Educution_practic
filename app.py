from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Childrengarden.db'
app.config['SECRET_KEY'] = 'childerGarden_KostromaS#@S'
db = SQLAlchemy(app)

class NameGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

class Kids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    age = db.Column(db.String(1), nullable=False)
    name_mother = db.Column(db.Text)
    name_father = db.Column(db.Text)
    number_mother = db.Column(db.String(15))
    number_father = db.Column(db.String(15))
    group_id = db.Column(db.Integer, db.ForeignKey('name_group.id'), nullable=False)
    group = db.relationship('NameGroup', backref='kids')

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news = db.Column(db.Text, nullable=False)
    name_news = db.Column(db.Text, nullable=False, default='Новость')

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kid = db.Column(db.Text, nullable=False)
    data = db.Column(db.Date, nullable=False)
    attendance = db.Column(db.Boolean, nullable=False)

with app.app_context():
    db.create_all()
    existing_admin = Admin.query.filter_by(login='admin').first()
    if not existing_admin:
        admin = Admin(
            login='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def main():
    return render_template('home.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return render_template('registration.html', error="Пароли не совпадают")
        
        existing_user = Users.query.filter_by(login=login).first()
        if existing_user:
            return render_template('registration.html', error="Пользователь с таким логином уже существует")

        users = Users(
            login=login,
            password=generate_password_hash(password)
        )

        db.session.add(users)
        db.session.commit()
        return redirect(url_for('sing_in'))
        
    return render_template('registration.html')

@app.route('/sing_in', methods=['GET', 'POST'])
def sing_in():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        user = Users.query.filter_by(login=login).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('main'))
        else:
            return render_template('login-in.html', error="Неверный логин или пароль")
            
    return render_template('login-in.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('main'))

@app.route('/groups')
def groups():
    if 'user_id' not in session:
        return redirect(url_for('sing_in'))
    groups = NameGroup.query.all()
    return render_template('groups.html', groups=groups)

@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect(url_for('sing_in'))
    return render_template('events.html')

@app.route('/teacher')
def teacher():
    return render_template('teacher.html')

@app.route('/news')
def news():
    if 'user_id' not in session:
        return redirect(url_for('sing_in'))
    news_list = News.query.all()
    return render_template('news.html', news_list=news_list)

@app.route('/attendance')
def attendance():
    if 'user_id' not in session:
        return redirect(url_for('sing_in'))
    attendance_list = Attendance.query.all()
    return render_template('attendance.html', attendance_list=attendance_list)

@app.route('/ogr')
def ogr():
    return render_template('ogr.html')

@app.route('/program')
def program():
    return render_template('program.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(login=login).first()
        
        if admin and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Неверный логин или пароль")
            
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    news_list = News.query.all()
    return render_template('admin_dashboard.html', news_list=news_list)

@app.route('/admin/add_news', methods=['POST'])
def add_news():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    news_text = request.form.get('news_text')
    news_name = request.form.get('news_name')  # Добавляем получение названия новости
    
    if news_text and news_name:  # Проверяем оба поля
        news = News(news=news_text, name_news=news_name)  # Создаем новость с названием
        db.session.add(news)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/journal')
def admin_journal():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    attendance_list = Attendance.query.all()
    return render_template('admin_journal.html', attendance_list=attendance_list)

@app.route('/admin/add_attendance', methods=['POST'])
def add_attendance():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    kid_name = request.form.get('kid_name')
    date_str = request.form.get('date')
    attendance_status = request.form.get('attendance') == 'on'
    
    if kid_name and date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            attendance = Attendance(
                kid=kid_name,
                data=date_obj,
                attendance=attendance_status
            )
            db.session.add(attendance)
            db.session.commit()
        except ValueError:
            pass
    
    return redirect(url_for('admin_journal'))

@app.route('/admin/delete_attendance/<int:attendance_id>')
def delete_attendance(attendance_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    attendance = Attendance.query.get(attendance_id)
    if attendance:
        db.session.delete(attendance)
        db.session.commit()
    
    return redirect(url_for('admin_journal'))

@app.route('/admin/delete_news/<int:news_id>')
def delete_news(news_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    news = News.query.get(news_id)
    if news:
        db.session.delete(news)
        db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    return redirect(url_for('main'))

if __name__ == '__main__':
    app.run(debug=True)