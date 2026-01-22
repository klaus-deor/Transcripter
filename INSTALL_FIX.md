# Guia de Instalação - Correção de Erros

Se você recebeu erros durante a instalação do PyGObject, siga estes passos:

## Solução Rápida

O problema ocorreu porque o PyGObject precisa de bibliotecas do sistema que não podem ser instaladas via pip. A solução é usar os pacotes do sistema.

### Passo 1: Instalar dependências do sistema

Execute o script de instalação (isso instalará Cairo e outras dependências):

```bash
./install_system_deps.sh
```

Se preferir instalar manualmente:

```bash
sudo apt update
sudo apt install -y \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 \
    gir1.2-notify-0.7 \
    libcairo2-dev \
    libgirepository1.0-dev \
    portaudio19-dev \
    python3-dev \
    pkg-config \
    xclip
```

### Passo 2: Remover o ambiente virtual antigo

```bash
deactivate  # Se ainda estiver ativado
rm -rf venv
```

### Passo 3: Criar um novo ambiente virtual COM acesso aos pacotes do sistema

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

**IMPORTANTE:** Note o parâmetro `--system-site-packages` - ele permite que o venv acesse o python3-gi instalado no sistema.

### Passo 4: Instalar os pacotes Python

```bash
pip install -r requirements.txt
```

### Passo 5: Instalar o aplicativo

```bash
pip install -e .
```

### Passo 6: Verificar grupo audio

```bash
groups | grep audio
```

Se não aparecer "audio", adicione seu usuário ao grupo:

```bash
sudo usermod -a -G audio $USER
```

Depois, faça logout e login novamente.

### Passo 7: Executar o aplicativo

```bash
transcripter
```

Ou:

```bash
python -m transcripter.main
```

## Por que isso aconteceu?

PyGObject é uma biblioteca que faz binding com GTK, que é uma biblioteca C. No Linux, é melhor usar a versão instalada pelo gerenciador de pacotes do sistema (apt) em vez de tentar compilar via pip, porque:

1. A versão do apt já vem pré-compilada
2. Está otimizada para sua distribuição
3. Tem todas as dependências corretas
4. É mais estável

## Verificar se PyGObject está funcionando

Depois de instalar, teste:

```python
python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print('PyGObject OK!')"
```

Se não houver erros, está tudo certo!

## Problemas Comuns

### Erro: "No module named 'gi'"

Você não criou o venv com `--system-site-packages`. Recrie o venv:

```bash
deactivate
rm -rf venv
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

### Erro: "cairo" not found

Instale as bibliotecas de desenvolvimento do Cairo:

```bash
sudo apt install libcairo2-dev libgirepository1.0-dev pkg-config
```

### Ícone não aparece na bandeja (GNOME)

Instale a extensão AppIndicator:

```bash
sudo apt install gnome-shell-extension-appindicator
```

Depois ative em "Extensões" ou "Ajustes".
