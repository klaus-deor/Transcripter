#!/bin/bash
# ============================================
# Transcripter - macOS Build Script
# Cria o .app e .dmg automaticamente
# ============================================

set -e

echo ""
echo "========================================"
echo "   TRANSCRIPTER - Build para macOS"
echo "========================================"
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "[ERRO] Python3 não encontrado!"
    echo ""
    echo "Instale com:"
    echo "  brew install python3"
    echo ""
    echo "Ou baixe de: https://www.python.org/downloads/"
    exit 1
fi

echo "[OK] Python encontrado"
python3 --version

# Verificar Homebrew e dependências
if command -v brew &> /dev/null; then
    echo "[OK] Homebrew encontrado"

    # Instalar portaudio se necessário
    if ! brew list portaudio &> /dev/null; then
        echo "Instalando portaudio..."
        brew install portaudio
    fi

    # Instalar create-dmg se necessário
    if ! command -v create-dmg &> /dev/null; then
        echo "Instalando create-dmg..."
        brew install create-dmg
    fi
else
    echo "[AVISO] Homebrew não encontrado. Algumas funcionalidades podem não funcionar."
fi

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

# Gerar ícones
echo ""
echo "[4/5] Gerando ícones..."
python scripts/generate_icons.py

# Criar .icns se iconutil disponível
if command -v iconutil &> /dev/null; then
    if [ -d "packaging/macos/transcripter.iconset" ]; then
        echo "Criando transcripter.icns..."
        iconutil -c icns packaging/macos/transcripter.iconset -o packaging/macos/transcripter.icns
    fi
fi

# Compilar executável
echo ""
echo "[5/5] Compilando executável..."
echo ""
python scripts/build.py --clean

# Criar DMG se create-dmg disponível
if command -v create-dmg &> /dev/null; then
    echo ""
    echo "Criando DMG..."
    ./packaging/macos/create_dmg.sh || echo "[AVISO] Falha ao criar DMG"
fi

echo ""
echo "========================================"
echo "   BUILD CONCLUÍDO!"
echo "========================================"
echo ""
echo "Arquivos criados em dist/:"
ls -lh dist/
echo ""
echo "Para executar:"
echo "  open dist/Transcripter.app"
echo ""
