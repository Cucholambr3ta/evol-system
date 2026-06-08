#!/usr/bin/env node

const { execSync } = require('child_process');

try {
  execSync(`python3 -c "from evol_cli import main; main()" ${process.argv.slice(2).join(' ')}`, {
    stdio: 'inherit',
    shell: true
  });
} catch (error) {
  process.exit(error.status || 1);
}
