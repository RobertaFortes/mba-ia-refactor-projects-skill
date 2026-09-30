const logger = require('../utils/logger');

// Middleware final do Express: única saída de erros da API (mantém respostas em texto, como antes).
// eslint-disable-next-line no-unused-vars
module.exports = (err, req, res, next) => {
  const status = err.status || 500;
  if (status >= 500) logger.error(err);
  res.status(status).send(status >= 500 ? 'Erro interno' : err.message);
};
