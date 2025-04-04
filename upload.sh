#! /bin/bash

SOURCE="/home/papouc/Desktop/LAR_Messi"
DEST="/home/papouc/Desktop/LAR_CACHE"
EXTENSION="py"

# Check, whether destination folder exists
if [ ! -d "$DEST" ]; then
    mkdir -p "$DEST"
fi

# Copy files
cp "$SOURCE"/*."$EXTENSION" "$DEST" 2>/dev/null

sshpass -f "/home/papouc/Documents/NothingInteresting/LAR_PASS.txt" scp -r /home/papouc/Desktop/LAR_CACHE hendrad2@192.168.65.28:~/