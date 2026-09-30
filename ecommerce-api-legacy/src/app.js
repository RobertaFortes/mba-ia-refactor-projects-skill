const express = require('express');
const settings = require('./config/settings');
const logger = require('./utils/logger');
const Database = require('./models/database');
const { initSchema } = require('./models/schema');
const passwordService = require('./services/passwordService');
const CacheService = require('./services/cacheService');
const createPaymentService = require('./services/paymentService');
const createCheckoutService = require('./services/checkoutService');
const createReportService = require('./services/reportService');
const createCheckoutController = require('./controllers/checkoutController');
const createAdminController = require('./controllers/adminController');
const createCheckoutRoutes = require('./routes/checkoutRoutes');
const createAdminRoutes = require('./routes/adminRoutes');
const createAdminAuth = require('./middlewares/adminAuth');
const errorHandler = require('./middlewares/errorHandler');

// Composition root: cria as dependências uma única vez e as injeta nas camadas.
async function createApp(config = settings) {
  const db = new Database(config.dbPath);
  await initSchema(db, passwordService);

  const models = {
    userModel: require('./models/userModel')(db),
    courseModel: require('./models/courseModel')(db),
    enrollmentModel: require('./models/enrollmentModel')(db),
    paymentModel: require('./models/paymentModel')(db),
    auditLogModel: require('./models/auditLogModel')(db),
    reportModel: require('./models/reportModel')(db),
  };

  const checkoutService = createCheckoutService({
    db,
    ...models,
    passwordService,
    paymentService: createPaymentService(config.paymentGatewayKey),
    cacheService: new CacheService(),
  });
  const reportService = createReportService(models);

  const app = express();
  app.use(express.json());
  app.use(createCheckoutRoutes(createCheckoutController(checkoutService)));
  app.use(createAdminRoutes(createAdminController({ reportService, userModel: models.userModel }), createAdminAuth(config.adminToken)));
  app.use(errorHandler);

  return { app, db };
}

if (require.main === module) {
  createApp().then(({ app }) => {
    app.listen(settings.port, () => logger.info(`Frankenstein LMS rodando na porta ${settings.port}...`));
  });
}

module.exports = { createApp };
