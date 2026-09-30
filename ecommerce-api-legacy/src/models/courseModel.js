module.exports = (db) => ({
  findActiveById: (id) => db.get('SELECT * FROM courses WHERE id = ? AND active = 1', [id]),
});
