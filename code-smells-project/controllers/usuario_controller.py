from flask import jsonify, request

from models import usuario_model
from services import usuario_service
from utils.errors import AppError, NotFoundError
from utils.validators import validar_login, validar_usuario


def listar_usuarios():
    return jsonify({"dados": usuario_model.listar(), "sucesso": True}), 200


def buscar_usuario(id):
    usuario = usuario_model.buscar_por_id(id)
    if not usuario:
        raise NotFoundError("Usuário não encontrado")
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar_usuario():
    dados = validar_usuario(request.get_json(silent=True))
    usuario_id = usuario_service.criar_usuario(**dados)
    return jsonify({"dados": {"id": usuario_id}, "sucesso": True}), 201


def login():
    email, senha = validar_login(request.get_json(silent=True))
    usuario = usuario_service.autenticar(email, senha)
    if not usuario:
        raise AppError("Email ou senha inválidos", 401)
    return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
