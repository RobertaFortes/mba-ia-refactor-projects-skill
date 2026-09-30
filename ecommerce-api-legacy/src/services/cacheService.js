const logger = require('../utils/logger');

// Cache em memória encapsulado (antes era um objeto global mutável exportado).
class CacheService {
  constructor() {
    this.store = new Map();
  }

  set(key, value) {
    logger.info(`Salvando no cache: ${key}`);
    this.store.set(key, value);
  }

  get(key) {
    return this.store.get(key);
  }
}

module.exports = CacheService;
