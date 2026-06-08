#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

const scriptPath = path.join(__dirname, '..', 'scripts', 'evol-memory.py');

try {
  execSync(`python3 "${scriptPath}" ${process.argv.slice(2).join(' ')}`, {
    stdio: 'inherit',
    shell: true
  });
} catch (error) {
  process.exit(error.status || 1);
}
