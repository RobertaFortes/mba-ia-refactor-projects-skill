from flask import jsonify, request

from models import produto_model
from utils.errors import NotFoundError
from utils.validators import parse_preco, validar_produto


def listar_produtos():
    return jsonify({"dados": produto_model.listar(), "sucesso": True}), 200


def buscar_produto(id):
    produto = produto_model.buscar_por_id(id)
    if not produto:
        raise NotFoundError("Produto não encontrado")
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar_produto():
    dados = validar_produto(request.get_json(silent=True))
    produto_id = produto_model.criar(**dados)
    return jsonify({"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar_produto(id):
    if not produto_model.buscar_por_id(id):
        raise NotFoundError("Produto não encontrado")
    dados = validar_produto(request.get_json(silent=True))
    produto_model.atualizar(id, **dados)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar_produto(id):
    if not produto_model.buscar_por_id(id):
        raise NotFoundError("Produto não encontrado")
    produto_model.remover(id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_produtos():
    termo = request.args.get("q", "")
    categoria = request.args.get("categoria")
    preco_min = parse_preco(request.args.get("preco_min"), "preco_min")
    preco_max = parse_preco(request.args.get("preco_max"), "preco_max")
    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
