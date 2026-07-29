import os
import re
import shutil
import subprocess
import sys

def get_version(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'^__version__\s*=\s*["\']([^"\']+)["\']', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "v0.0"

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(root_dir, 'main.py')
    
    version = get_version(main_script)
    print(f"Building version: {version}")

    output_dir = os.path.join(root_dir, 'dist', version)
    os.makedirs(output_dir, exist_ok=True)
    
    # Esegui PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--noconsole",
        "--onefile",
        "--name", "Presentatore_Immagini",
        "--distpath", output_dir,
        main_script
    ]
    
    print("Avvio PyInstaller...")
    try:
        subprocess.run(cmd, cwd=root_dir, check=True)
        print(f"\nCompilazione completata con successo! L'eseguibile si trova in:\n{output_dir}")
    except subprocess.CalledProcessError as e:
        print(f"\nErrore durante la compilazione. Assicurati di avere PyInstaller installato ('pip install pyinstaller').\nDettagli errore: {e}")

if __name__ == "__main__":
    main()
