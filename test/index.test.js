const test = require('node:test');
const assert = require('node:assert/strict');
const { main } = require('../src/index.js');

test('main prints greeting and success message', () => {
  const original = process.env.APP_NAME;
  process.env.APP_NAME = 'demo';

  const originalWrite = process.stdout.write;
  let output = '';
  process.stdout.write = (chunk) => {
    output += chunk;
    return true;
  };

  try {
    main();
  } finally {
    process.stdout.write = originalWrite;
    if (original === undefined) {
      delete process.env.APP_NAME;
    } else {
      process.env.APP_NAME = original;
    }
  }

  assert.match(output, /Hello from demo!/);
  assert.match(output, /Project initialized successfully\./);
});
