# task-manager-api

API de Task Manager em Python/Flask, refatorada para MVC com a skill `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py     # popula tasks.db com usuários, categorias e tasks de exemplo
python app.py
```

A aplicação sobe em `http://localhost:5000` (ajuste com `PORT`). Configuração por variáveis de ambiente: veja `.env.example` (`SECRET_KEY`, `DATABASE_URI`, `DEBUG`, `HOST`, `PORT`).

Autenticação: `POST /login` devolve um token assinado; envie-o em `Authorization: Bearer <token>`. `DELETE /users/<id>` e a definição/alteração de `role` exigem um usuário admin (o seed cria `joao@email.com` / `1234` como admin).

## Estrutura

```
app.py            composition root (create_app)
config/           settings (env) e constants
models/           Task, User, Category (regras de domínio: is_overdue, hash de senha, serialização)
controllers/      validação de entrada e orquestração por domínio
routes/           mapeamento URL -> controller (task, user, category, report, system)
services/         regras e consultas (task, user, category, report, auth)
middlewares/      auth (Bearer token / admin) e error_handler global
utils/            validators, errors, time
```
