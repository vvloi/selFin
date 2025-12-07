# Running the selFin API (keep it always running)

This guide provides simple commands to start the FastAPI app and keep it running on macOS (development and production options).

Important: make sure your virtual environment is created and activated before running these commands.

## Quick development start

Activate venv and run Uvicorn with auto-reload (for development):

```bash
cd /path/to/selFin
source .venv/bin/activate
.venv/bin/uvicorn app.main:app --reload
```

Open: http://127.0.0.1:8000/docs

## Keep the server running in background (nohup)

Start in background and write logs to `uvicorn.log`:

```bash
cd /path/to/selFin
source .venv/bin/activate
nohup .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &
echo $! > uvicorn.pid
```

Stop server:

```bash
kill $(cat uvicorn.pid) && rm -f uvicorn.pid
```

Tail logs:

```bash
tail -f uvicorn.log
```

## Use tmux (recommended for interactive sessions)

Create a persistent tmux session and run the server inside it:

```bash
tmux new -s selFin -d
tmux send-keys -t selFin "source .venv/bin/activate" C-m
tmux send-keys -t selFin ".venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" C-m
tmux attach -t selFin
```

Detach the session with `Ctrl+B` then `D` — the server keeps running.

## Production: Gunicorn with Uvicorn workers

Install `gunicorn` (in your venv):

```bash
pip install gunicorn
```

Run with multiple workers and access logs to stdout:

```bash
.venv/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app \
  --bind 0.0.0.0:8000 --workers 4 --log-level info --access-logfile -
```

You can combine Gunicorn with `nohup`, `tmux` or `launchd` to keep it running.

## macOS LaunchAgent (auto-start on login)

Create a plist file `~/Library/LaunchAgents/com.yourname.selfin.plist` with content like:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.yourname.selfin</string>
    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>-lc</string>
      <string>cd /path/to/selFin && source .venv/bin/activate && .venv/bin/gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000 --workers 2</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/path/to/selFin/launch.out.log</string>
    <key>StandardErrorPath</key>
    <string>/path/to/selFin/launch.err.log</string>
  </dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.yourname.selfin.plist
# Unload: launchctl unload ~/Library/LaunchAgents/com.yourname.selfin.plist
```

## Helpful tips

- Use `--host 127.0.0.1` if you don't want the server exposed on the network.
- For production, use a reverse-proxy (nginx) in front of Gunicorn/Uvicorn.
- Keep secrets out of the repo; set them in `.env` or in your environment.

## Quick checklist

1. Activate venv: `source .venv/bin/activate`
2. Set environment variables (or copy `.env.example` to `.env`)
3. Run migrations: `alembic upgrade head`
4. Start server using one of the methods above

---

This file gives multiple options — pick the one that fits your workflow. If you want, I can add a small helper script (`scripts/start.sh`) to encapsulate the preferred method.
