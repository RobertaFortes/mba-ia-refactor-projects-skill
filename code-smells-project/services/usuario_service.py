from werkzeug.security import check_password_hash, generate_password_hash

from models import usuario_model


def criar_usuario(nome, email, senha):
    return usuario_model.criar(nome, email, generate_password_hash(senha))


def autenticar(email, senha):
    """Retorna os dados públicos do usuário se as credenciais forem válidas, senão None."""
    row = usuario_model.buscar_credenciais_por_email(email)
    if row is None:
        return None

    armazenada = row["senha"] or ""
    if "$" in armazenada:
        valido = check_password_hash(armazenada, senha)
    else:
        # Bancos antigos guardavam texto puro: aceita uma última vez e migra para hash.
        valido = armazenada == senha
        if valido:
            usuario_model.atualizar_senha(row["id"], generate_password_hash(senha))

    if not valido:
        return None
    return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
