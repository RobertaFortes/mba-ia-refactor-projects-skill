const { Router } = require('express');
const asyncHandler = require('../utils/asyncHandler');

module.exports = (checkoutController) => {
  const router = Router();
  router.post('/api/checkout', asyncHandler(checkoutController.checkout));
  return router;
};
