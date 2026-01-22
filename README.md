# Transcripter

Um aplicativo de transcrição de áudio para Linux que usa a API Groq (Whisper) para converter fala em texto. O aplicativo roda na bandeja do sistema e permite gravar áudio com um atalho de teclado configurável, transcrevendo automaticamente e copiando o texto para a área de transferência.

## Funcionalidades

- Icone na bandeja do sistema (system tray)
- Gravação de áudio com atalho de teclado global configurável
- Transcrição automática usando Groq Whisper API
- Cópia automática do texto transcrito para o clipboard
- Interface de configurações intuitiva
- Suporte a múltiplos idiomas
- Histórico de transcrições
- Notificações desktop
- Seleção de microfone

## Requisitos do Sistema

### Pacotes do Sistema (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 \
    portaudio19-dev \
    libportaudio2 \
    libasound2-dev \
    python3-dev \
    libx11-dev \
    xclip
```

### Para outras distribuições:

**Fedora/RHEL:**
```bash
sudo dnf install python3 python3-pip python3-gobject gtk3 libappindicator-gtk3 portaudio-devel alsa-lib-devel python3-devel libX11-devel xclip
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip python-gobject gtk3 libappindicator-gtk3 portaudio alsa-lib libx11 xclip
```

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/klaus-deor/Transcripter.git
cd Transcripter
```

### 2. Crie um ambiente virtual COM acesso aos pacotes do sistema

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
```

**IMPORTANTE:** Use `--system-site-packages` para acessar o PyGObject instalado no sistema.

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Instale o aplicativo

```bash
pip install -e .
```

## Configuração

### 1. Obtenha uma API Key do Groq

1. Acesse [console.groq.com](https://console.groq.com/)
2. Crie uma conta ou faça login
3. Gere uma nova API key
4. Copie a API key

### 2. Configure o Transcripter

Execute o aplicativo pela primeira vez:

```bash
transcripter
```

Ou, se ainda estiver no diretório do projeto:

```bash
python -m transcripter.main
```

Na primeira execução, a janela de configurações será aberta automaticamente. Configure:

1. **API Key do Groq**: Cole sua API key
2. **Idioma**: Selecione o idioma principal (ou deixe em "Auto-detect")
3. **Atalho de Teclado**: Configure seu atalho preferido (padrão: `Ctrl+Alt+R`)
4. **Microfone**: Selecione o dispositivo de entrada de áudio

Clique em "Save" para salvar as configurações.

## Uso

### Formas de Executar

Existem 3 formas de executar o Transcripter:

#### 1. Como Aplicativo (Recomendado)

Primeiro, instale a integração com desktop:

```bash
./install_desktop.sh
```

Depois, procure "Transcripter" no menu de aplicativos e clique para executar. O programa rodará em background e você pode fechar o terminal.

#### 2. Em Background (sem manter terminal aberto)

```bash
./run_background.sh
```

Para parar:
```bash
./stop_transcripter.sh
```

#### 3. No Terminal (mantém terminal aberto)

```bash
source venv/bin/activate
transcripter
```

**Nota:** Se fechar o terminal, o programa fecha junto.

Para mais detalhes, veja: [COMO_EXECUTAR.md](COMO_EXECUTAR.md)

O ícone do Transcripter aparecerá na bandeja do sistema.

### Gravar e Transcrever

1. Pressione o atalho configurado (padrão: `Ctrl+Alt+R`) para iniciar a gravação
2. Fale no microfone
3. Pressione o atalho novamente para parar a gravação
4. Aguarde alguns segundos enquanto a transcrição é processada
5. O texto transcrito será automaticamente copiado para o clipboard
6. Use `Ctrl+V` para colar o texto em qualquer lugar

### Menu da Bandeja

Clique com o botão direito no ícone da bandeja para acessar:

- **Start/Stop Recording**: Iniciar/parar gravação manualmente
- **History**: Ver histórico de transcrições
- **Settings**: Abrir janela de configurações
- **About**: Informações sobre o aplicativo
- **Quit**: Fechar o aplicativo

## Configurações

### Arquivo de Configuração

As configurações são armazenadas em:
```
~/.config/transcripter/config.toml
```

### Segurança da API Key

A API key é armazenada de forma segura usando o sistema de keyring do Linux, não em texto plano.

## Estrutura do Projeto

```
Transcripter/
├── transcripter/
│   ├── __init__.py          # Inicialização do pacote
│   ├── main.py              # Entry point principal
│   ├── config.py            # Gerenciamento de configurações
│   ├── audio.py             # Gravação de áudio
│   ├── transcription.py     # Integração com API Groq
│   ├── clipboard.py         # Operações de clipboard
│   ├── hotkeys.py           # Captura de hotkeys globais
│   ├── tray.py              # Ícone da system tray
│   └── gui/
│       ├── __init__.py
│       ├── settings.py      # Janela de configurações
│       └── icons/           # Ícones do aplicativo
├── config/
│   └── default_config.toml  # Configuração padrão
├── requirements.txt         # Dependências Python
├── setup.py                 # Script de instalação
└── README.md               # Este arquivo
```

## Solução de Problemas

### O ícone não aparece na bandeja

**GNOME 3+**: Instale a extensão AppIndicator:
```bash
sudo apt install gnome-shell-extension-appindicator
```

Depois, ative a extensão em "Extensões" ou "Tweaks".

### Erro ao capturar áudio

Verifique se seu usuário está no grupo `audio`:
```bash
sudo usermod -a -G audio $USER
```

Faça logout e login novamente.

### Hotkeys não funcionam

Em Wayland, hotkeys globais podem ter limitações. Considere usar X11 ou configurar permissões especiais para o aplicativo.

### Erro de API Key

Certifique-se de que:
1. Sua API key do Groq está correta
2. Você tem créditos disponíveis na sua conta Groq
3. Sua conexão com a internet está funcionando

## Desenvolvimento

### Executar em modo de desenvolvimento

```bash
python -m transcripter.main
```

### Estrutura de Módulos

- `audio.py`: Captura de áudio usando sounddevice
- `transcription.py`: Cliente da API Groq
- `clipboard.py`: Gerenciamento de clipboard
- `hotkeys.py`: Captura de teclas globais com pynput
- `tray.py`: System tray com AppIndicator3
- `config.py`: Gerenciamento de configurações com pydantic
- `gui/settings.py`: Interface de configurações em GTK3

## Licença

MIT License - Veja o arquivo LICENSE para detalhes.

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Agradecimentos

- [Groq](https://groq.com/) pela API de transcrição Whisper
- [GTK](https://gtk.org/) pelo framework de interface
- [SoundDevice](https://python-sounddevice.readthedocs.io/) pela captura de áudio
- [pynput](https://pynput.readthedocs.io/) pela captura de hotkeys

## Suporte

Para reportar bugs ou solicitar features, abra uma issue no GitHub:
https://github.com/klaus-deor/Transcripter/issues
