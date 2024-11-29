# Trabalho devops


### Alunos
- Otavio Marques Ra: 23.9797-4
- Gustavo Aparecido da Silva Ra: 23.9361-9
- Gabriel Monteiro Ricardo Ra: 22.8636-7

####  Inicio
O arquivo docker-compose.yml foi criado na raiz do projeto para configurar os contêineres necessários.

```bash
vim docker-compose.yml
```
Após isso adicionei o seguinte código dentro do arquivo:

``` yml
version: '3.7'

services:
  mariadb:
    build:
      context: ./mariadb
      dockerfile: Dockerfile_mariadb
    ports:
      - "3306:3306"
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: school_db
      MYSQL_USER: flask_user
      MYSQL_PASSWORD: flask_password

  flask:
    build:
      context: ./flask
      dockerfile: Dockerfile_flask
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=mysql+pymysql://flask_user:flask_password@mariadb:3306/school_db
    depends_on:
      - mariadb

  test:
    build:
      context: ./flask
      dockerfile: Dockerfile_flask
    command: ["pytest", "/app/test_app.py"]  # Roda os testes no arquivo test_app.py
    depends_on:
      - mariadb
      - flask
    environment:
      - DATABASE_URL=mysql+pymysql://flask_user:flask_password@mariadb:3306/school_db
    networks:
      - default  # Conecta o contêiner aos mesmos serviços de rede
```

Após, foi-se criada um novo diretório na raiz do projeto chamado flask, onde dentro criou-se o arquivo `app.py`.
```
vim app.py 
```
em seguinda, dentro deste adicionei o seguinte código:
``` python
# Código principal do Flask (app.py)
import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics
import logging

app = Flask(__name__)

metrics = PrometheusMetrics(app)
# Configuração da chave secreta para sessões
app.config['SECRET_KEY'] = 'minha_chave_secreta_super_secreta'  # Substitua por uma chave segura

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@mariadb/school_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados e o AppBuilder
db = SQLAlchemy(app)
appbuilder = AppBuilder(app, db.session)

# Configuração do log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelo de Aluno - Definição da tabela 'Aluno' no banco de dados
class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    disciplinas = db.Column(db.String(200), nullable=False)
    ra = db.Column(db.String(200), nullable=False)


# Tentar conectar até o MariaDB estar pronto
attempts = 5
for i in range(attempts):
    try:
        with app.app_context():
            db.create_all()  # Inicializa o banco de dados
            # Criar um usuário administrador padrão
            if not appbuilder.sm.find_user(username='admin'):
                appbuilder.sm.add_user(
                    username='admin',
                    first_name='Admin',
                    last_name='User',
                    email='admin@admin.com',
                    role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
                    password='admin'
                )
        logger.info("Banco de dados inicializado com sucesso.")
        break
    except OperationalError:
        if i < attempts - 1:
            logger.warning("Tentativa de conexão com o banco de dados falhou. Tentando novamente em 5 segundos...")
            time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
        else:
            logger.error("Não foi possível conectar ao banco de dados após várias tentativas.")
            raise

# Visão do modelo Aluno para o painel administrativo
class AlunoModelView(ModelView):
    datamodel = SQLAInterface(Aluno)
    list_columns = ['id', 'nome', 'sobrenome', 'turma', 'disciplinas', 'ra']

# Adicionar a visão do modelo ao AppBuilder
appbuilder.add_view(
    AlunoModelView,
    "Lista de Alunos",
    icon="fa-folder-open-o",
    category="Alunos",
)

# Rota para listar todos os alunos - Método GET
@app.route('/alunos', methods=['GET'])
def listar_alunos():
    alunos = Aluno.query.all()
    output = [{'id': aluno.id, 'nome': aluno.nome, 'sobrenome': aluno.sobrenome, 'turma': aluno.turma, 'disciplinas': aluno.disciplinas, 'ra': aluno.ra} for aluno in alunos]
    return jsonify(output)

# Rota para adicionar um aluno - Método POST
@app.route('/alunos', methods=['POST'])
def adicionar_aluno():
    data = request.get_json()
    novo_aluno = Aluno(nome=data['nome'], sobrenome=data['sobrenome'], turma=data['turma'], disciplinas=data['disciplinas'], ra=data['ra'])
    db.session.add(novo_aluno)
    db.session.commit()
    logger.info(f"Aluno {data['nome']} {data['sobrenome']} adicionado com sucesso!")
    return jsonify({'message': 'Aluno adicionado com sucesso!'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

Após adicionei nossas dependencias da aplicação por meio do arquivo requirements, este ficou dentro da pasta flask também.

```bash
vim requirements.txt
```

e adicionei o seguinte código dentro:
```txt
Flask==1.1.4  # Versão compatível com Flask-AppBuilder
Flask-SQLAlchemy==2.4.4  # Extensão do Flask para integração com SQLAlchemy
PyMySQL==0.9.3  # Biblioteca para conexão do Python com o banco de dados MariaDB
Flask-AppBuilder==3.3.0  # Versão compatível com Flask 1.x
Werkzeug==1.0.1  # Versão compatível do Werkzeug para evitar erros de importação
MarkupSafe==2.0.1  # Versão compatível com Jinja2 e Flask
WTForms==2.3.3  # Versão compatível com Flask-AppBuilder que contém o módulo 'compat'
prometheus-flask-exporter==0.18.3
pytest==6.2.5
pytest-flask==1.2.0
Flask-Testing==0.8.0
```
Após criei o Dockerfile_flask dentro da pasta flask também, ele vai determinar o diretorio de trabalho e rodar a instalação das dependencias

``` bash
vim Dockerfile_flask
```

e em seguida o seguinte código foi adicionado dentro:

``` yml
# Dockerfile (Flask AppBuilder)
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#COPY . .
COPY app.py /app/

CMD ["flask", "run", "--host=0.0.0.0"]

```

Em seguida, configurei o banco de dados. Na raiz do projeto, criei a pasta `mariadb` e adicionei o arquivo `Dockerfile_mariadb`, responsável por definir as variáveis de ambiente necessárias para o funcionamento do projeto.

```vim
vim Dockerfile_mariadb
```

código: 

```  yml
# Dockerfile para MariaDB
# Salve este arquivo como Dockerfile.mariadb na raiz do projeto

# Dockerfile (MariaDB)
FROM mariadb:10.5

# Defina as variáveis de ambiente para o banco de dados
ENV MYSQL_ROOT_PASSWORD=root_password
ENV MYSQL_DATABASE=school_db
ENV MYSQL_USER=flask_user
ENV MYSQL_PASSWORD=flask_password

EXPOSE 3306
```

- Após isso rodei o comando para subir os containres 

```bash
docker-compose up --build
```

- Ao confeir no navegador o localhost:5000 obitive a resultado correto:

![alt text](images/image.png)

#### Jenkins
Nesta parte, criamos uma nova tarefa no Jenkins, que será utilizada para gerenciar o pipeline do projeto "trabalho devops". Primeiro, inserimos o nome do item, no caso "trabalho devops". Em seguida, selecionamos o tipo de tarefa como Pipeline, que é ideal para projetos que demandam a execução de atividades complexas e sequenciais, como o fluxo de integração e entrega contínua (CI/CD). Depois de selecionar o tipo de tarefa, clicamos no botão "Tudo certo" para prosseguir com a configuração do pipeline.

![alt text](images/1.jpg)

Em seguida, configuramos o pipeline no Jenkins para conectar ao repositório Git onde está armazenado o código do projeto "trabalho devops".


No campo SCM, selecionamos Git como o sistema de controle de versão.
No campo Repository URL, inserimos o link para o repositório do GitHub: https://github.com/Tav1nn/trabalho_devops.git.
Como não foram configuradas credenciais específicas, deixamos o campo Credentials como - none -. Caso o repositório fosse privado, seria necessário adicionar credenciais para autenticação.
No campo Branches to build, especificamos a branch que será usada para as builds, no caso */main. Isso indica que o pipeline será executado na branch principal.

![alt text](images/2.jpg)