#!/bin/bash

# ═══════════════════════════════════════════════════════════════
#  TaskMaster AI - Installer Script
# ═══════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Configuration
REPO_URL="https://github.com/MilanSaric011/todo-app"
INSTALL_DIR="$HOME/.local/share/taskmaster"
BIN_DIR="$HOME/.local/bin"
CONFIG_FILE="$HOME/.bashrc"
ZSH_CONFIG_FILE="$HOME/.zshrc"
ALIAS_LINE="alias td='python3 $INSTALL_DIR/taskmaster.py'"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}     ${BOLD}TaskMaster AI - Professional TUI Task Manager${NC}     ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════
#  Check Python Version
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}▸ Checking Python version...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed!${NC}"
    echo "  Please install Python 3.7+ first:"
    echo "    • Arch: sudo pacman -S python"
    echo "    • Ubuntu/Debian: sudo apt install python3"
    echo "    • macOS: brew install python"
    exit 1
fi

PY_VERSION=$(python3 -c 'import sys; print(sys.version_info.major + sys.version_info.minor / 10)')
if (( $(echo "$PY_VERSION >= 3.7" | bc -l) )); then
    echo -e "${GREEN}✓ Python 3.${PY_VERSION} detected${NC}"
else
    echo -e "${RED}✗ Python 3.7+ required (found 3.$PY_VERSION)${NC}"
    exit 1
fi

# ═══════════════════════════════════════════════════════════════
#  Detect Shell
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}▸ Detecting shell...${NC}"

if [ "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$ZSH_CONFIG_FILE"
    SHELL_NAME="Zsh"
elif [ "$BASH_VERSION" ]; then
    SHELL_CONFIG="$CONFIG_FILE"
    SHELL_NAME="Bash"
else
    SHELL_CONFIG="$CONFIG_FILE"
    SHELL_NAME="Bash"
fi

echo -e "${GREEN}✓ Detected ${SHELL_NAME}${NC}"

# ═══════════════════════════════════════════════════════════════
#  Create Installation Directory
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}▸ Creating installation directory...${NC}"

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo -e "${GREEN}✓ Installation directory: $INSTALL_DIR${NC}"

# ═══════════════════════════════════════════════════════════════
#  Clone or Copy Repository
# ═══════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}▸ Installing TaskMaster AI...${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if we're in the project directory
if [ -f "$SCRIPT_DIR/taskmaster.py" ]; then
    # Copy from current directory
    cp "$SCRIPT_DIR/taskmaster.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/models.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/constants.py" "$INSTALL_DIR/"
    cp "$SCRIPT_DIR/__main__.py" "$INSTALL_DIR/"

    # Copy README for reference
    if [ -f "$SCRIPT_DIR/README.md" ]; then
        cp "$SCRIPT_DIR/README.md" "$INSTALL_DIR/"
    fi

    echo -e "${GREEN}✓ Copied project files${NC}"
else
    # Clone from GitHub
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo -e "${YELLOW}▸ Updating existing installation...${NC}"
        cd "$INSTALL_DIR"
        git pull origin main
    else
        echo -e "${YELLOW}▸ Cloning from GitHub...${NC}"
        rm -rf "$INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
    echo -e "${GREEN}✓ Cloned from GitHub${NC}"
fi

chmod +x "$INSTALL_DIR/taskmaster.py"

# ═══════════════════════════════════════════════════════════════
#  Add Alias to Shell Config
# ═══════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}▸ Setting up alias...${NC}"

add_alias() {
    local config_file="$1"
    local alias_marker="# TaskMaster AI"

    # Check if alias already exists
    if grep -q "alias td=" "$config_file" 2>/dev/null; then
        echo -e "${YELLOW}▸ Alias already exists in ${config_file}${NC}"
        return 0
    fi

    # Add alias to config file
    if [ -f "$config_file" ]; then
        echo "" >> "$config_file"
        echo "$alias_marker" >> "$config_file"
        echo "$ALIAS_LINE" >> "$config_file"
        echo -e "${GREEN}✓ Added alias to ${config_file}${NC}"
    else
        # Create new config file
        echo "# TaskMaster AI" > "$config_file"
        echo "$ALIAS_LINE" >> "$config_file"
        echo -e "${GREEN}✓ Created ${config_file} with alias${NC}"
    fi
}

add_alias "$SHELL_CONFIG"

# Also add to zshrc if different
if [ "$SHELL_CONFIG" != "$ZSH_CONFIG_FILE" ] && [ -n "$ZSH_VERSION" ]; then
    add_alias "$ZSH_CONFIG_FILE"
fi

# ═══════════════════════════════════════════════════════════════
#  Create Launcher Script
# ═══════════════════════════════════════════════════════════════
echo ""
echo -e "${YELLOW}▸ Creating launcher script...${NC}"

LAUNCHER="$BIN_DIR/taskmaster"

cat > "$LAUNCHER" << 'EOF'
#!/bin/bash
# TaskMaster AI - Launcher Script
# Generated by installer

INSTALL_DIR="$HOME/.local/share/taskmaster"

if [ ! -f "$INSTALL_DIR/taskmaster.py" ]; then
    echo "Error: TaskMaster AI not found at $INSTALL_DIR"
    echo "Please reinstall: https://github.com/MilanSaric011/todo-app"
    exit 1
fi

exec python3 "$INSTALL_DIR/taskmaster.py" "$@"
EOF

chmod +x "$LAUNCHER"
echo -e "${GREEN}✓ Launcher script: $LAUNCHER${NC}"

# Ensure BIN_DIR is in PATH
if ! echo "$PATH" | grep -q "$BIN_DIR"; then
    echo ""
    echo -e "${YELLOW}▸ Adding $BIN_DIR to PATH...${NC}"
    echo ""
    echo -e "${RED}IMPORTANT: Add this line to your shell config:${NC}"
    echo ""
    echo -e "  ${BOLD}export PATH=\"$BIN_DIR:\$PATH\"${NC}"
    echo ""
    echo -e "Then run: ${GREEN}source $SHELL_CONFIG${NC}"
    echo ""
fi

# ═══════════════════════════════════════════════════════════════
#  Create Desktop Entry (Optional)
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}▸ Creating desktop entry...${NC}"

DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_DIR/taskmaster.desktop" << EOF
[Desktop Entry]
Name=TaskMaster AI
Comment=Professional TUI Task Manager
Exec=$INSTALL_DIR/taskmaster.py
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Utility;Tasks;
Keywords=task;todo;manager;terminal;tui;
EOF

chmod +x "$DESKTOP_DIR/taskmaster.desktop"
echo -e "${GREEN}✓ Desktop entry created${NC}"

# ═══════════════════════════════════════════════════════════════
#  Summary
# ═══════════════════════════════════════════════════════════════
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                    ${GREEN}Installation Complete!${NC}                      ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}Quick Start:${NC}"
echo -e "    Run: ${GREEN}td${NC}"
echo ""
echo -e "  ${BOLD}Or:${NC}"
echo -e "    $LAUNCHER"
echo -e "    python3 $INSTALL_DIR/taskmaster.py"
echo ""
echo -e "  ${BOLD}Controls:${NC}"
echo -e "    n=New | d=Del | e=Edit | p=Priority | Space=Toggle"
echo -e "    s=Search | r=Sort | ↑↓=Navigate | Tab=Filter"
echo -e "    M=Archive | Home/End | q=Quit"
echo ""
echo -e "  ${BOLD}To activate alias immediately:${NC}"
echo -e "    ${GREEN}source $SHELL_CONFIG${NC}"
echo ""
echo -e "  ${BOLD}For updates:${NC}"
echo -e "    cd $INSTALL_DIR && git pull"
echo ""
echo -e "  ${BOLD}Documentation:${NC}"
echo -e "    $INSTALL_DIR/README.md"
echo ""
