function main() {
  const name = process.env.APP_NAME || 'me';
  console.log(`Hello from ${name}!`);
  console.log('Project initialized successfully.');
}

if (require.main === module) {
  main();
}

module.exports = { main };
