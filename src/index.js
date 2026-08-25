const readline = require('node:readline');

function createGame(secret = Math.floor(Math.random() * 100) + 1) {
  let attempts = 0;

  return {
    guess(value) {
      const guess = Number(value);
      if (!Number.isInteger(guess) || guess < 1 || guess > 100) {
        return { message: 'Enter a whole number from 1 to 100.', won: false };
      }

      attempts += 1;
      if (guess === secret) {
        return { message: `You got it in ${attempts} ${attempts === 1 ? 'guess' : 'guesses'}!`, won: true };
      }

      return {
        message: guess < secret ? 'Too low. Try again.' : 'Too high. Try again.',
        won: false,
      };
    },
  };
}

async function playGame(input = process.stdin, output = process.stdout) {
  const game = createGame();
  const reader = readline.createInterface({ input, output });

  output.write('\nGuess the Number\n');
  output.write('I am thinking of a number from 1 to 100.\n');

  for await (const line of reader) {
    const result = game.guess(line.trim());
    output.write(`${result.message}\n`);
    if (result.won) {
      reader.close();
      break;
    }
  }
}

function main() {
  const name = process.env.APP_NAME || 'me';
  console.log(`Hello from ${name}!`);
  console.log('Project initialized successfully.');
}

if (require.main === module) {
  if (process.argv.includes('--game')) {
    playGame().catch((error) => {
      console.error(error.message);
      process.exitCode = 1;
    });
  } else {
    main();
  }
}

module.exports = { createGame, main, playGame };
