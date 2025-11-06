# PURE Quick Start

- Install and bootstrap:
  curl -fsSL https://raw.githubusercontent.com/Slave88/pure/main/install.sh | bash

- Run in separate terminals:
  # terminal 1
  source ~/.pure/.venv/bin/activate
  python3 protocol/server.py

  # terminal 2
  source ~/.pure/.venv/bin/activate
  python3 search/server.py

- Test protocol:
  python3 protocol/client.py 127.0.0.1 9000

- Test search:
  http://127.0.0.1:8888/search?q=hello

- UI:
  open browser/index.html in a normal browser
