import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'postgresql://postgres:3258@localhost:5432/gerenciador_produtos'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
