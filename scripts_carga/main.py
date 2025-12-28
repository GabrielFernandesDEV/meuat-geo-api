import sys
from pathlib import Path

from download_data import download_data
from load_data import load_data


def main():
    """Função principal que executa download e carregamento dos dados."""
    # Caminho relativo ao working_dir (/app/scripts)
    data_path = str(Path(__file__).parent.parent / "data")
    
    # Passo 1: Download dos dados
    print("=" * 50)
    print("📥 Passo 1: Download dos dados")
    print("=" * 50)
    try:
        if not download_data(data_path):
            print("❌ Falha no download dos dados")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao baixar dados: {e}")
        sys.exit(1)
    
    # Passo 2: Carregar dados no banco
    print("\n" + "=" * 50)
    print("💾 Passo 2: Carregar dados no banco")
    print("=" * 50)
    try:
        if not load_data(data_path, "AREA_IMOVEL_1.shp"):
            print("❌ Falha ao carregar dados no banco")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao carregar dados no banco: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✅ Processo concluído com sucesso!")
    print("=" * 50)


if __name__ == "__main__":
    main() 