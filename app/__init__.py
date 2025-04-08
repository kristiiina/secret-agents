from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'the_secret_key'

# Указываем путь к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем предупреждения
# Создаем объект базы данных
db = SQLAlchemy(app)


from app import routes, utils