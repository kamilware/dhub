#!/bin/bash

set -e

ZIP_URL="https://github.com/kamilware/dhub/archive/refs/heads/master.zip"
ZIP_FILE="dhub-master.zip"
DIR_NAME="dhub-master"
FINAL_DIR_NAME="src"

if command -v curl >/dev/null 2>&1; then
    echo "Downloading with curl..."
    curl -L "$ZIP_URL" -o "$ZIP_FILE"
elif command -v wget >/dev/null 2>&1; then
    echo "Downloading with wget..."
    wget -O "$ZIP_FILE" "$ZIP_URL"
else
    echo "Neither curl nor wget found. Cannot download. Install one and try again."
    exit 1
fi

if command -v unzip >/dev/null 2>&1; then
    echo "Extracting $ZIP_FILE ..."
    unzip -o "$ZIP_FILE"
else
    echo "'unzip' not found. Please install unzip and re-run."
    exit 1
fi

cd "$DIR_NAME"
pip install -r requirements.txt
cd ..

mv "$DIR_NAME" "$FINAL_DIR_NAME"

EXPORTS_PATH="$(pwd)/$FINAL_DIR_NAME/exports.sh"
if [ ! -f "$EXPORTS_PATH" ]; then
    echo "Cannot find $EXPORTS_PATH, did extraction fail?"
    exit 1
fi

echo "Sourcing $EXPORTS_PATH ..."
. "$EXPORTS_PATH"

echo "✅ Setup complete!"
echo "Now you can use 'dhub-cli' and 'dhub-server' from any directory in this shell."
echo "Try:"
echo "    dhub-cli --help"

echo "Removing downloaded .zip"
rm "$ZIP_FILE"
