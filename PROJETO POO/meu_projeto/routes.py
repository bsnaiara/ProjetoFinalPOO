from flask import Flask, render_template
from flask import request, redirect, url_for, request, session, flash, jsonify
from models import db, Usuario, ListaDeCompras, Produto, ProdutosLista
import secrets



app = Flask(__name__)

app.secret_key = secrets.token_hex(32)  
app.config['SESSION_TYPE'] = 'filesystem'



# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para a página principal
@app.route('/principal')
def principal():
    return render_template('telaPrincipal.html')

# Rota para a página de produtos
@app.route('/produtos')
def produtos():
    return render_template('telaProdutos.html')

# Rota para a página de detalhes
@app.route('/detalhes')
def detalhes():
    return render_template('telaDetalhes.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    usuario = Usuario.query.filter_by(email=email).first()

    if usuario and usuario.senha == password:  # Em produção, use hash para senhas!
        session['usuario_id'] = usuario.id  # 🔴 GARANTA QUE A SESSÃO ESTÁ SENDO DEFINIDA
        print(f"Usuário {usuario.id} logado!")  # Log para depuração
        return redirect(url_for('principal'))
    else:
        return "Credenciais inválidas", 401

    


# ✅ Exibir todas as listas do usuário logado
@app.route('/listas', methods=['GET'])
def listar_listas():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    usuario_id = session['usuario_id']
    listas = ListaDeCompras.query.filter_by(usuario_id=usuario_id).all()

    return jsonify({'listas': [{'id': l.id, 'nome': l.nome, 'orcamento': float(l.orcamento)} for l in listas]})



# ✅ Criar uma nova lista de compras
@app.route('/listas/criar', methods=['POST'])
def criar_lista():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    data = request.get_json()
    try:
        nova_lista = ListaDeCompras(
            nome=data.get('nome'),
            orcamento=data.get('orcamento'),
            usuario_id=session['usuario_id']
        )
        db.session.add(nova_lista)
        db.session.commit()
        return jsonify({'message': 'Lista criada com sucesso!', 'id': nova_lista.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ✅ Editar uma lista existente
@app.route('/listas/editar/<int:lista_id>', methods=['PUT'])
def editar_lista(lista_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    lista = ListaDeCompras.query.get(lista_id)
    if not lista or lista.usuario_id != session['usuario_id']:
        return jsonify({'error': 'Lista não encontrada'}), 404

    data = request.get_json()
    lista.nome = data.get('nome', lista.nome)
    lista.orcamento = data.get('orcamento', lista.orcamento)

    db.session.commit()
    return jsonify({'message': 'Lista atualizada com sucesso!'})

# ✅ Excluir uma lista
@app.route('/listas/excluir/<int:lista_id>', methods=['DELETE'])
def excluir_lista(lista_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    lista = ListaDeCompras.query.get(lista_id)
    if not lista or lista.usuario_id != session['usuario_id']:
        return jsonify({'error': 'Lista não encontrada'}), 404

    db.session.delete(lista)
    db.session.commit()
    return jsonify({'message': 'Lista excluída com sucesso!'})


from sqlalchemy import text  # ✅ Import necessário

@app.route('/listas/<int:lista_id>')
def detalhes_lista(lista_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    # Carregar a lista
    lista = ListaDeCompras.query.get(lista_id)

    if not lista or lista.usuario_id != session['usuario_id']:
        return "Lista não encontrada ou acesso negado", 403

    # Consulta para obter os produtos associados à lista
    produtos = db.session.query(Produto).join(ProdutosLista).filter(ProdutosLista.lista_id == lista_id).all()

    return render_template('telaDetalhes.html', lista=lista, produtos=produtos)




@app.route('/listas/<int:lista_id>/remover-produto/<int:produto_id>', methods=['DELETE'])
def remover_produto(lista_id, produto_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    db.session.execute(
        "DELETE FROM produtos_lista WHERE lista_id = :lista_id AND produto_id = :produto_id",
        {"lista_id": lista_id, "produto_id": produto_id}
    )
    db.session.commit()

    return jsonify({'message': 'Produto removido com sucesso!'})

@app.route('/produtos/adicionar', methods=['POST'])
def adicionar_produto():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    # Pega os dados do formulário
    nome = request.form.get('product-name')
    preco = request.form.get('product-price')
    categoria = request.form.get('product-category')
    quantidade_estoque = request.form.get('product-stock')
    descricao = request.form.get('product-description')

    # Verifica se todos os campos necessários estão preenchidos
    if not nome or not preco or not categoria or not quantidade_estoque or not descricao:
        return jsonify({'error': 'Todos os campos devem ser preenchidos'}), 400

    try:
        # Tenta converter os campos para os tipos apropriados
        preco = float(preco)  # Converte o preço para float
        quantidade_estoque = int(quantidade_estoque)  # Converte a quantidade em estoque para inteiro
    except ValueError as e:
        return jsonify({'error': f'Erro na conversão de dados: {str(e)}'}), 400

    # Criar o produto
    novo_produto = Produto(
        nome=nome,
        preco=preco,
        categoria=categoria,
        quantidade_estoque=quantidade_estoque,
        descricao=descricao
    )

    db.session.add(novo_produto)
    db.session.commit()

    # Agora, associar o produto à lista
    lista_id = request.form.get('lista_id')  # Vamos assumir que a lista_id será passada no formulário
    if lista_id:
        produto_lista = ProdutosLista(lista_id=lista_id, produto_id=novo_produto.id)
        db.session.add(produto_lista)
        db.session.commit()

    return redirect(url_for('principal'))  # Redireciona de volta para os detalhes da lista

