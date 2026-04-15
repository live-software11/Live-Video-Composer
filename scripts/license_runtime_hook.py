# PyInstaller runtime hook — Live Video Composer Installer build
# Imposta LIVEWORKS_LICENSE_ENABLED=true nell'eseguibile installer.
# Questo file viene eseguito prima di main.py da PyInstaller.
import os
os.environ["LIVEWORKS_LICENSE_ENABLED"] = "true"
