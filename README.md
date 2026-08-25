# Guess the Number

A quick, friendly terminal game built with Node.js. The game secretly chooses a
number from 1 to 100, and your job is to find it in as few guesses as possible.
After every valid guess, you get a useful hint telling you whether to search
higher or lower. Invalid input is handled without costing a guess, so you can
focus on the puzzle.

## How to play

Start the game with `npm run game`, enter a whole number between 1 and 100, and
keep narrowing the range until you find the answer. The game reports how many
guesses you needed when you win. Use `Ctrl+C` to leave at any time.

## Coming in the next update

- **Play again:** start a fresh round without restarting the command.
- **Difficulty levels:** choose smaller or larger number ranges for a quicker
	challenge or a harder hunt.
- **Best score tracking:** keep your lowest guess count during the session.
- **Smarter feedback:** show the remaining range and warn when a guess repeats.
- **Polished terminal flow:** add a welcome screen, clearer prompts, and a
	graceful end-of-game option.

## Scripts

- `npm start` — run the app
- `npm run game` — play Guess the Number in the terminal
- `npm run build:windows` — build `dist/DungeonRPG.exe`
- `npm test` — run the test suite

## Structure

- [package.json](package.json) — project config and scripts
- [src/index.js](src/index.js) — application entry point
- [test/index.test.js](test/index.test.js) — example test

## Quick start

```bash
npm install
npm start
```

To play:

```bash
npm run game
```

## Build the Windows version

After installing dependencies, create a standalone Windows executable with:

```bash
npm run build:windows
```

The output is written to `dist/DungeonRPG.exe`. It is a console application,
so it should be launched from Command Prompt or PowerShell.
