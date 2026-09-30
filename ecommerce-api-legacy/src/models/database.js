const sqlite3 = require('sqlite3');

// Wrapper com Promises sobre o sqlite3. Uma instância é criada no entry point e injetada nos models.
class Database {
  constructor(path) {
    this.conn = new sqlite3.Database(path);
    this.queue = Promise.resolve();
  }

  run(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.conn.run(sql, params, function onDone(err) {
        if (err) return reject(err);
        return resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  }

  get(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.conn.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
    });
  }

  all(sql, params = []) {
    return new Promise((resolve, reject) => {
      this.conn.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows)));
    });
  }

  // Transações são serializadas: a conexão é única, então BEGIN/COMMIT não podem se sobrepor.
  transaction(work) {
    const task = this.queue.then(async () => {
      await this.run('BEGIN');
      try {
        const result = await work();
        await this.run('COMMIT');
        return result;
      } catch (err) {
        await this.run('ROLLBACK');
        throw err;
      }
    });
    this.queue = task.catch(() => {});
    return task;
  }

  close() {
    return new Promise((resolve, reject) => this.conn.close((err) => (err ? reject(err) : resolve())));
  }
}

module.exports = Database;
