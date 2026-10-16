#!/usr/bin/env bash
set -euo pipefail

REPO="https://github.com/alilograda/LOGRADA_TIME.git"
DIR="$HOME/.local/opt/LOGRADA_TIME"
BIN="$HOME/.local/bin"

echo "[+] Installing LOGRADA_TIME..."

command -v python3 >/dev/null || {
    echo "Error: Python 3 is required."
    exit 1
}

command -v git >/dev/null || {
    echo "Error: Git is required. Install it with: sudo apt install git"
    exit 1
}

mkdir -p "$HOME/.local/opt" "$BIN"

if [ -d "$DIR/.git" ]; then
    git -C "$DIR" pull --ff-only
elif [ -e "$DIR" ]; then
    echo "Error: $DIR exists but is not a Git repository."
    echo "Move or rename that directory before installing."
    exit 1
else
    git clone "$REPO" "$DIR"
fi

python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/python" -m pip install "$DIR"

cat > "$BIN/lograda_time" <<'LAUNCHER'
#!/usr/bin/env bash
exec "$HOME/.local/opt/LOGRADA_TIME/.venv/bin/lograda_time" "$@"
LAUNCHER

chmod +x "$BIN/lograda_time"

echo
echo "[+] Installation completed!"
echo "Run: $BIN/lograda_time status"
