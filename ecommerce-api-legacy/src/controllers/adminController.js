module.exports = ({ reportService, userModel }) => ({
  async financialReport(req, res) {
    res.json(await reportService.financialReport());
  },

  async deleteUser(req, res) {
    await userModel.removeWithDependents(req.params.id);
    res.send('Usuário deletado com sucesso (matrículas e pagamentos removidos junto).');
  },
});
