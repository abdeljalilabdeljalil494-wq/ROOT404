const text = require('fs').readFileSync(0, 'utf8').trim();
console.log(text ? text.split(/\s+/).reduce((sum, value) => sum + Number(value), 0) : 0);
