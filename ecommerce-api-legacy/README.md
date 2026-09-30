# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express, refatorada para MVC com a skill `refactor-arch`.

## Como rodar

```bash
npm install
ADMIN_TOKEN=um-token-secreto npm start
```

A aplicação sobe em `http://localhost:3000` (ajuste com `PORT`). O banco SQLite é em memória e já carrega seeds no boot. Configuração por variáveis de ambiente: veja `.env.example`.

Os endpoints administrativos (`GET /api/admin/financial-report` e `DELETE /api/users/:id`) exigem o header `X-Admin-Token` igual a `ADMIN_TOKEN`. Exemplos de requisições em `api.http`.

## Estrutura

```
src/app.js            composition root (createApp)
src/config/           settings (env) e constants
src/models/           database (Promises), schema/seed e um model por entidade
src/services/         checkout, pagamento, cache, senha, relatório
src/controllers/      validação de entrada e orquestração
src/routes/           mapeamento URL -> controller
src/middlewares/      adminAuth e errorHandler
src/utils/            errors, asyncHandler, logger
```
