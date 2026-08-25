const test = require('node:test');
const assert = require('node:assert/strict');
const { createGame, main } = require('../src/index.js');

test('game gives hints and ends on the correct guess', () => {
  const game = createGame(42);

  assert.deepEqual(game.guess('41'), { message: 'Too low. Try again.', won: false });
  assert.deepEqual(game.guess('43'), { message: 'Too high. Try again.', won: false });
  assert.deepEqual(game.guess('42'), { message: 'You got it in 3 guesses!', won: true });
});

test('game rejects guesses outside the range', () => {
  const game = createGame(42);

  assert.deepEqual(game.guess('hello'), {
    message: 'Enter a whole number from 1 to 100.',
    won: false,
  });
});

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
