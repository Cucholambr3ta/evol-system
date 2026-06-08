#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

const scriptsDir = path.join(__dirname, '..', 'scripts');

try {
  execSync(`PYTHONPATH=${scriptsDir} python3 -c "from evol_cli import main; main()" agent ${process.argv.slice(2).join(' ')}`, {
    stdio: 'inherit',
    shell: true
  });
} catch (error) {
  process.exit(error.status || 1);
}
