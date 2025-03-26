from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    senha = db.Column(db.Text, nullable=False)

class Loja(db.Model):
    __tablename__ = 'lojas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    endereco = db.Column(db.Text)

    # Relação com os produtos, alterando o nome do backref
    #produtos_na_loja = db.relationship('Produto', backref='loja', lazy=True)

class Produto(db.Model):
    __tablename__ = 'produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    preco = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(255))
    quantidade_estoque = db.Column(db.Integer, nullable=False, default=0)  # Nova coluna
    descricao = db.Column(db.Text)  # Adicionada a coluna descricao

    # Relação com a loja
    #loja = db.relationship('Loja', backref='produtos_na_loja', lazy=True)

class ListaDeCompras(db.Model):
    __tablename__ = 'listas_de_compras'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    orcamento = db.Column(db.Numeric(10, 2))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id', ondelete='CASCADE'))

class ProdutosLista(db.Model):
    __tablename__ = 'produtos_lista'
    id = db.Column(db.Integer, primary_key=True)
    lista_id = db.Column(db.Integer, db.ForeignKey('listas_de_compras.id', ondelete='CASCADE'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produtos.id', ondelete='CASCADE'))
