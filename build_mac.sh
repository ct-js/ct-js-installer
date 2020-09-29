#!/bin/sh

cd "$(dirname "$0")"

python3 -m PyInstaller main.py --console --onefile --name="ctjs-installer-mac" --add-data="./assets:./assets" --icon="./assets/icon.icns" --noconfirm --windowed
