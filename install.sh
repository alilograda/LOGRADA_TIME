#!/usr/bin/env bash
set -e

echo "[+] Installing LOGRADA_TIME..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required."
    exit 1
fi

if ! command -v git >/dev/null 2>&1; then
    echo "Please install git first: sudo apt install git"
    exit 1
fi

if ! command -v nmap >/dev/null 2>&1; then
    echo "Installing Nmap..."
    sudo apt update
    sudo apt install -y nmap
fi

INSTALL_DIR="$HOME/.local/opt/LOGRADA_TIME"
mkdir -p "$HOME/.local/bin"

if [ -d "$INSTALL_DIR" ]; then
    echo "Installation directory already exists: $INSTALL_DIR"
    echo "Update it separately rather than overwriting it."
    exit 1
fi

mkdir -p "$INSTALL_DIR"
cp -r . "$INSTALL_DIR/"
cd "$INSTALL_DIR"

python3 -m venv .venv
"$INSTALL_DIR/.venv/bin/pip" install .

cat > "$HOME/.local/bin/lograda_time" <<'LAUNCHER'
#!/usr/bin/env bash
exec "$HOME/.local/opt/LOGRADA_TIME/.venv/bin/lograda_time" "$@"
LAUNCHER

chmod +x "$HOME/.local/bin/lograda_time"

echo
echo "[+] Installation complete!"
echo "Run: ~/.local/bin/lograda_time status"
