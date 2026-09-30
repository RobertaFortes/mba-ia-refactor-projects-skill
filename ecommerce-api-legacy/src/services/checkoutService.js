const { AppError } = require('../utils/errors');
const { PAYMENT_STATUS } = require('../config/constants');

module.exports = ({ db, userModel, courseModel, enrollmentModel, paymentModel, auditLogModel, paymentService, passwordService, cacheService }) => ({
  async checkout({ name, email, password, courseId, card }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new AppError('Curso não encontrado', 404);

    // O pagamento é decidido ANTES de qualquer escrita: cartão recusado não cria usuário órfão.
    const payment = paymentService.charge(card, course.price);
    if (payment.status === PAYMENT_STATUS.DENIED) throw new AppError('Pagamento recusado', 400);

    const { userId, enrollmentId } = await db.transaction(async () => {
      const existing = await userModel.findByEmail(email);
      const id =
        existing?.id ??
        (await userModel.create({
          name,
          email,
          passwordHash: passwordService.hash(password || passwordService.randomPassword()),
        }));
      const enrollment = await enrollmentModel.create({ userId: id, courseId });
      await paymentModel.create({ enrollmentId: enrollment, amount: course.price, status: payment.status });
      await auditLogModel.record(`Checkout curso ${courseId} por ${id}`);
      return { userId: id, enrollmentId: enrollment };
    });

    cacheService.set(`last_checkout_${userId}`, course.title);
    return { msg: 'Sucesso', enrollment_id: enrollmentId };
  },
});
