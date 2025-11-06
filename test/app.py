from flask import Flask, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///register.db'
db = SQLAlchemy(app)


class NameGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    kids = db.relationship('Kids', backref='group', lazy=True)


class Kids(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    age = db.Column(db.String(1), nullable=False)
    name_mother = db.Column(db.Text)
    name_father = db.Column(db.Text)
    number_mother = db.Column(db.String(15))
    number_father = db.Column(db.String(15))
    group_id = db.Column(db.Integer, db.ForeignKey('name_group.id'), nullable=False)

    attendance = db.relationship('Attendance', backref='name', lazy=True)

#авторизация за воспитателя
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False) 


#авторизация за родителя
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(40), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    #group = db.Column(db.Text, nullable=False)


class News(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    news = db.Column(db.Text, nullable=False)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kid = db.Column(db.Text, db.ForeignKey('kids.name'), nullable=False)
    data = db.Column(db.Date, nullable=False)
    attendance = db.Column(db.Boolean, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        users = Users(
            login = login,
            password = generate_password_hash(password)
        )

        db.session.add(users)
        db.session.commit()
    return render_template('sing_in.html')


if __name__ == '__main__':
    app.run(debug=True)