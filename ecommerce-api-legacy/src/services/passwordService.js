const crypto = require('crypto');

const KEY_LENGTH = 64;

// Hash com scrypt e salt aleatório; formato "salt:hash" (hex).
module.exports = {
  hash(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    return `${salt}:${crypto.scryptSync(password, salt, KEY_LENGTH).toString('hex')}`;
  },

  verify(password, stored) {
    const [salt, key] = String(stored).split(':');
    if (!salt || !key) return false;
    const expected = Buffer.from(key, 'hex');
    const actual = crypto.scryptSync(password, salt, KEY_LENGTH);
    return expected.length === actual.length && crypto.timingSafeEqual(expected, actual);
  },

  // Senha aleatória para contas criadas sem senha informada (sem senha padrão previsível).
  randomPassword: () => crypto.randomBytes(16).toString('hex'),
};
