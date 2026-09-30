// Toda configuração vem do ambiente (ver .env.example). Nenhum segredo fica no código.
module.exports = {
  port: Number(process.env.PORT || 3000),
  dbPath: process.env.DB_PATH || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
  // Sem ADMIN_TOKEN definido, os endpoints administrativos ficam bloqueados.
  adminToken: process.env.ADMIN_TOKEN || '',
};
