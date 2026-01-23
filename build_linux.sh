#!/bin/bash
# ============================================
# Transcripter - Linux Build Script
# Cria o executável e AppImage automaticamente
# ============================================

set -e

echo ""
echo "========================================"
echo "   TRANSCRIPTER - Build para Linux"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 não encontrado!"
    echo ""
    echo "Instale com:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-venv python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "[OK] Python encontrado"
python3 --version

# Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo ""
    echo "[1/5] Criando ambiente virtual..."
    python3 -m venv venv
fi

# Ativar ambiente virtual
echo ""
echo "[2/5] Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo ""
echo "[3/5] Instalando dependências (pode demorar alguns minutos)..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
pip install pyinstaller pillow

# Gerar ícones se necessário
if [ ! -f "packaging/assets/transcripter.png" ]; then
    echo ""
    echo "Gerando ícones..."
    python scripts/generate_icons.py
fi

# Compilar executável
echo ""
echo "[4/5] Compilando executável..."
echo ""
python scripts/build.py --clean

# Criar AppImage
echo ""
echo "[5/5] Criando AppImage..."
./packaging/linux/build_appimage.sh

echo ""
echo "========================================"
echo "   BUILD CONCLUÍDO!"
echo "========================================"
echo ""
echo "Arquivos criados em dist/:"
ls -lh dist/
echo ""
echo "Para executar:"
echo "  ./dist/Transcripter"
echo "  ou"
echo "  ./dist/Transcripter-1.0.0-x86_64.AppImage"
echo ""
