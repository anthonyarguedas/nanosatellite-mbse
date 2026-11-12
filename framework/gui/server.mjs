// Compatibility entry point for npm start and existing local launch commands.
import { pathToFileURL } from 'node:url';
import { startServer } from './server/server.mjs';
export { createServer } from './server/server.mjs';

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) startServer();
