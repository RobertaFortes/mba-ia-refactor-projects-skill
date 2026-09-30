const crypto = require('crypto');
const { AppError } = require('../utils/errors');
const { ADMIN_TOKEN_HEADER } = require('../config/constants');

// Exige o header X-Admin-Token igual a ADMIN_TOKEN (comparação em tempo constante).
module.exports = (adminToken) => (req, res, next) => {
  const received = Buffer.from(String(req.get(ADMIN_TOKEN_HEADER) || ''));
  const expected = Buffer.from(adminToken);
  const allowed = expected.length > 0 && received.length === expected.length && crypto.timingSafeEqual(received, expected);
  if (!allowed) return next(new AppError('Acesso negado', 403));
  return next();
};
