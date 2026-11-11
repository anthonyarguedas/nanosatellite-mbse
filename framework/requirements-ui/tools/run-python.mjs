// Command transport only. Native Python owns study construction and storage.
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export function runPython(command, args = process.argv.slice(2)) {
  const source = fileURLToPath(new URL('../../python/cli.py', import.meta.url));
  const result = spawnSync(process.env.VERIFICATION_PYTHON || 'python3', ['-I', '-B', source, command, ...args], { stdio: 'inherit' });
  if (result.error) {
    console.error(`Could not start Python: ${result.error.message}. Set VERIFICATION_PYTHON to the selected interpreter.`);
    process.exitCode = 1;
  } else process.exitCode = result.status ?? 1;
}
