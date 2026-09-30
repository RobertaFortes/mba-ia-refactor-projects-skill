module.exports = {
  PAYMENT_STATUS: { PAID: 'PAID', DENIED: 'DENIED' },
  // Regra do gateway simulado: cartões que começam com "4" são aprovados.
  APPROVED_CARD_PREFIX: '4',
  ADMIN_TOKEN_HEADER: 'x-admin-token',
};
