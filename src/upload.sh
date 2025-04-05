#!/bin/bash
# ==============================================
# File Synchronization Script for LAR Project
#
# This script:
# 1. Copies .py files from SOURCE to DEST
# 2. Transfers them to a remote server via scp
#
# Configuration:
#   SOURCE      - Local dev directory
#   DEST        - Staging directory
#   EXTENSION   - File type to copy (default: py)
#
# Security Note:
#   - Uses sshpass (consider SSH keys instead)
#   - Password file should be chmod 600
# ==============================================

SOURCE="/home/papouc/Desktop/LAR_Messi/src"      # Source dir
DEST="/home/papouc/Desktop/LAR_CACHE"        # Staging dir
EXTENSION="py"                               # File extension

# Create DEST if missing
if [ ! -d "$DEST" ]; then
    mkdir -p "$DEST"
    echo "[STATUS] Created directory: $DEST"
fi

# Copy files (silence 'no matches' errors)
echo "[STATUS] Copying .$EXTENSION files..."
cp "$SOURCE"/*."$EXTENSION" "$DEST" 2>/dev/null

# Transfer to remote server
echo "[STATUS] Starting secure transfer..."
sshpass -f "/home/papouc/Documents/NothingInteresting/LAR_PASS.txt" \
    scp -r "$DEST" hendrad2@192.168.65.31:~/ && \
    echo "[SUCCESS] Transfer complete!" || \
    echo "[ERROR] Transfer failed!" >&2