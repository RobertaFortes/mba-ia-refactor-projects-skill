const logger = require('../utils/logger');
const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');

// Gateway de pagamento simulado. Nunca registra o número do cartão nem a chave do gateway.
module.exports = (gatewayKey) => ({
  charge(card, amount) {
    const status = card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    logger.info(`Pagamento ${status} (cartão final ${card.slice(-4)}, valor ${amount}, gateway ${gatewayKey ? 'configurado' : 'sem chave'})`);
    return { status, amount };
  },
});
