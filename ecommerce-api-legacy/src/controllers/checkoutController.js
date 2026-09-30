const { AppError } = require('../utils/errors');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+$/;

module.exports = (checkoutService) => ({
  async checkout(req, res) {
    // O contrato externo (usr, eml, pwd, c_id, card) é preservado; internamente usamos nomes claros.
    const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body || {};

    const valid =
      typeof name === 'string' && name &&
      typeof email === 'string' && EMAIL_PATTERN.test(email) &&
      courseId && typeof card === 'string' && card;
    if (!valid) throw new AppError('Bad Request', 400);

    const result = await checkoutService.checkout({ name, email, password, courseId, card });
    res.status(200).json(result);
  },
});
