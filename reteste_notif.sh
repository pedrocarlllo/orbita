#!/bin/bash
# ORBITA RETESTE NOTIFICATIONS
# Sequence:
# 1. initialize (id=1)
# 2. notifications/initialized (NO id - correct notification)
# 3. tools/list (id=3)
# 4. tools/call orbita_status (id=4)

cd "/c/ORBITA-Universal-Plugin-Windows-0.1.0/orbita-agent/server"

# Send messages via heredoc (without id for notification)
cat > /tmp/reteste_msgs.json << 'EOF'
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}
{"jsonrpc":"2.0","method":"notifications/initialized"}
{"jsonrpc":"2.0","id":3,"method":"tools/list"}
{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"orbita_status"}}
EOF

node src/index.mjs < /tmp/reteste_msgs.json 2>/tmp/reteste.err > /tmp/reteste.out
RC=$?
echo "EXIT_CODE: $RC"
echo "=== STDOUT ==="
cat /tmp/reteste.out
echo "=== STDERR ==="
cat /tmp/reteste.err
