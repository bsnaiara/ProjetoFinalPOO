from flask import Flask
from config import Config
from models import db
from routes import app  # Importa o app já configurado no routes.py

app.config.from_object(Config)
db.init_app(app)

# Criar tabelas no banco de dados ao iniciar o app
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
