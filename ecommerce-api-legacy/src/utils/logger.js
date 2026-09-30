const log = (level, args) => console[level === 'ERROR' ? 'error' : 'log'](`[${level}]`, ...args);

module.exports = {
  info: (...args) => log('INFO', args),
  warn: (...args) => log('WARN', args),
  error: (...args) => log('ERROR', args),
};
