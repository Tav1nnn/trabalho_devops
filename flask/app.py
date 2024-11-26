import time
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@mariadb/school_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de Aluno
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)

# Tentar conectar ao banco de dados
attempts = 5
for i in range(attempts):
    try:
        with app.app_context():
            db.create_all()  # Cria tabelas
        break
    except OperationalError:
        if i < attempts - 1:
            time.sleep(5)  # Tenta novamente após 5 segundos
        else:
            raise

@app.route('/')
def home():
    return jsonify({"message": "Hello, Flask com MariaDB!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

