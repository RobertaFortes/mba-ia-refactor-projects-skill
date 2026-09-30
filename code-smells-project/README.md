# code-smells-project

API de E-commerce em Python/Flask (refatorada para MVC com a skill `refactor-arch`).

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000` (ajuste com `PORT`). O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, com produtos e usuários de exemplo (senhas armazenadas com hash).

Configuração por variáveis de ambiente: veja `.env.example`.

## Estrutura

```
app.py            composition root (create_app)
config/           settings (env) e constants (regras de negócio)
models/           acesso a dados (SQL parametrizado) e schema/seed
controllers/      orquestração dos casos de uso
routes/           mapeamento URL -> controller (Blueprints)
services/         regras de pedido/relatório, autenticação, notificações
middlewares/      tratamento de erros global e proteção de endpoints admin
utils/            validators e exceções de domínio
```
