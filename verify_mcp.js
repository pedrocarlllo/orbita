import fs from 'fs';
const s = fs.readFileSync('/c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/.mcp.json', 'utf8');
const j = JSON.parse(s);
console.log('JSON OK');
console.log('keys:', Object.keys(j));
console.log('type:', j.mcpServers.orbita-local.type);
console.log('command:', j.mcpServers.orbita-local.command);
console.log('args:', JSON.stringify(j.mcpServers.orbita-local.args));
console.log('cwd:', j.mcpServers.orbita-local.cwd);
