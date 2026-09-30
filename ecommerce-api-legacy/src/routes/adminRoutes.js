const { Router } = require('express');
const asyncHandler = require('../utils/asyncHandler');

// Todas as rotas administrativas exigem o token (middleware adminAuth).
module.exports = (adminController, adminAuth) => {
  const router = Router();
  router.get('/api/admin/financial-report', adminAuth, asyncHandler(adminController.financialReport));
  router.delete('/api/users/:id', adminAuth, asyncHandler(adminController.deleteUser));
  return router;
};
