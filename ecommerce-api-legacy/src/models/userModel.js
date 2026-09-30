module.exports = (db) => ({
  findByEmail: (email) => db.get('SELECT id FROM users WHERE email = ?', [email]),

  async create({ name, email, passwordHash }) {
    const { lastID } = await db.run('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, passwordHash]);
    return lastID;
  },

  // Remove o usuário e seus dados dependentes (pagamentos e matrículas) na mesma transação.
  removeWithDependents: (id) =>
    db.transaction(async () => {
      await db.run('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [id]);
      await db.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
      await db.run('DELETE FROM users WHERE id = ?', [id]);
    }),
});
