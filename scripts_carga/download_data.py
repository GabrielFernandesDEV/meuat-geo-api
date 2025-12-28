#!/usr/bin/env python3
"""
Script para baixar os dados do Google Drive (ZIP) e descompactar.
"""

import sys
import zipfile
from pathlib import Path
import gdown

def download_data(path: str):
    """Baixa o arquivo ZIP do Google Drive e descompacta."""
    file_id = "15ghpnwzdDhFqelouqvQwXlbzovtPhlFe"
    zip_file = Path(path) / "fazendas_sp.zip"
    
    print("📥 Baixando dados...")
    try:
        gdown.download(f"https://drive.google.com/uc?id={file_id}", str(zip_file), quiet=False)
        
        if not zip_file.exists() or zip_file.stat().st_size == 0:
            print("❌ Erro ao baixar arquivo")
            return False
        
        print("📦 Descompactando...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(path)
        
        zip_file.unlink()
        print("✅ Download e extração concluídos!")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

