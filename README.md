<p align="center">
  <img src="https://img.icons8.com/fluency/96/000000/microphone.png" alt="Transcripter Logo"/>
</p>

<h1 align="center">Transcripter</h1>

<p align="center">
  <strong>Transforme sua voz em texto instantaneamente!</strong>
</p>

<p align="center">
  <a href="https://github.com/klaus-deor/Transcripter/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"/>
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python"/>
  </a>
  <a href="https://github.com/klaus-deor/Transcripter">
    <img src="https://img.shields.io/badge/platform-Linux-orange.svg" alt="Platform"/>
  </a>
</p>

---

## O que é o Transcripter?

O **Transcripter** é uma ferramenta de transcrição de áudio para Linux que converte sua fala em texto usando a poderosa API Groq Whisper.

Com apenas um atalho de teclado, você pode:
1. Gravar sua voz
2. Ter o áudio transcrito automaticamente
3. Receber o texto pronto na área de transferência

Simples assim!

---

## Demonstração Rápida

```
1. Pressione Ctrl+Alt+R → Começa a gravar
2. Fale o que quiser
3. Pressione Ctrl+Alt+R novamente → Para de gravar
4. Aguarde 2-3 segundos
5. Use Ctrl+V em qualquer lugar → Texto transcrito!
```

---

## Funcionalidades

| Recurso | Descrição |
|---------|-----------|
| **Atalho Global** | Grave áudio de qualquer lugar com `Ctrl+Alt+R` |
| **Transcrição Rápida** | Usa Groq Whisper API (extremamente rápida) |
| **Clipboard Automático** | Texto copiado automaticamente |
| **Histórico** | Acesse transcrições anteriores |
| **Multi-idioma** | Suporta Português, Inglês, Espanhol e mais |
| **System Tray** | Ícone discreto na bandeja do sistema |
| **Notificações** | Feedback visual do status |
| **Configurável** | Personalize atalhos, idioma e mais |

---

## Requisitos

### Sistema Operacional
- Linux (Ubuntu, Debian, Fedora, Arch, etc.)

### Dependências
- Python 3.8 ou superior
- GTK 3
- Conexão com internet (para API Groq)

---

## Instalação

### Passo 1: Clone o Repositório

```bash
git clone https://github.com/klaus-deor/Transcripter.git
cd Transcripter
```

### Passo 2: Instale as Dependências do Sistema

**Ubuntu/Debian:**
```bash
./install_system_deps.sh
```

Ou manualmente:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 portaudio19-dev xclip
```

### Passo 3: Configure o Ambiente Python

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Passo 4: Obtenha sua API Key

1. Acesse [console.groq.com](https://console.groq.com/)
2. Crie uma conta (gratuita)
3. Gere uma API Key
4. Guarde a chave

### Passo 5: Execute o Transcripter

```bash
transcripter
```

Na primeira execução, configure sua API Key na janela de Settings.

---

## Como Usar

### Método 1: Atalho de Teclado (Recomendado)

| Ação | Atalho Padrão |
|------|---------------|
| Iniciar/Parar Gravação | `Ctrl + Alt + R` |

### Método 2: Menu da Bandeja

Clique com botão direito no ícone:

```
┌─────────────────────┐
│ Status: Idle        │
├─────────────────────┤
│ Start Recording     │
├─────────────────────┤
│ History             │
│ Settings            │
│ About               │
├─────────────────────┤
│ Quit                │
└─────────────────────┘
```

---

## Formas de Executar

### Opção A: Como Aplicativo (Recomendado)

```bash
./install_desktop.sh
```

Depois, encontre "Transcripter" no menu de aplicativos.

### Opção B: Em Background

```bash
./run_background.sh    # Iniciar
./stop_transcripter.sh # Parar
```

### Opção C: No Terminal

```bash
source venv/bin/activate
transcripter
```

---

## Configurações

### Acessando as Configurações

1. Clique com botão direito no ícone da bandeja
2. Selecione "Settings"

### Opções Disponíveis

| Aba | Configurações |
|-----|---------------|
| **General** | Notificações, Idioma, Autostart |
| **Audio** | Dispositivo de entrada (microfone) |
| **Groq API** | API Key, Modelo Whisper |
| **Hotkeys** | Atalho de gravação |
| **History** | Tamanho máximo do histórico |

### Arquivo de Configuração

As configurações são salvas em:
```
~/.config/transcripter/config.toml
```

---

## Solução de Problemas

### Ícone não aparece na bandeja (GNOME)

```bash
sudo apt install gnome-shell-extension-appindicator
```
Depois, ative a extensão em "Extensões" ou "Tweaks".

### Hotkeys não funcionam no Wayland

O Wayland bloqueia hotkeys globais por segurança. Soluções:

**Opção 1:** Mude para X11 na tela de login

**Opção 2:** Configure atalho nas configurações do sistema:
- Comando: `/caminho/para/Transcripter/toggle_recording.sh`

Veja mais detalhes em [WAYLAND_FIX.md](WAYLAND_FIX.md)

### Erro de API Key

1. Verifique se a API Key está correta
2. Confirme que tem créditos na conta Groq
3. Teste sua conexão com internet

### Diagnóstico Completo

```bash
./diagnose_hotkeys.sh
```

---

## Estrutura do Projeto

```
Transcripter/
├── transcripter/           # Código fonte principal
│   ├── __init__.py         # Informações do pacote
│   ├── main.py             # Ponto de entrada
│   ├── config.py           # Gerenciamento de configurações
│   ├── audio.py            # Gravação de áudio
│   ├── transcription.py    # Integração com Groq API
│   ├── clipboard.py        # Operações de clipboard
│   ├── hotkeys.py          # Captura de atalhos globais
│   ├── tray.py             # Ícone da bandeja do sistema
│   └── gui/
│       ├── settings.py     # Janela de configurações
│       └── history.py      # Janela de histórico
├── config/
│   └── default_config.toml # Configuração padrão
├── requirements.txt        # Dependências Python
├── setup.py                # Script de instalação
├── run_background.sh       # Script para rodar em background
├── stop_transcripter.sh    # Script para parar
├── install_desktop.sh      # Integração com desktop
└── README.md               # Este arquivo
```

---

## Tecnologias Utilizadas

| Tecnologia | Uso |
|------------|-----|
| **Python 3** | Linguagem principal |
| **GTK 3** | Interface gráfica |
| **Groq API** | Transcrição com Whisper |
| **pynput** | Captura de hotkeys |
| **sounddevice** | Gravação de áudio |
| **keyring** | Armazenamento seguro de API Key |

---

## Contribuindo

Contribuições são bem-vindas!

1. Faça um Fork do projeto
2. Crie uma branch (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFeature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abra um Pull Request

---

## Desenvolvedores

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/klaus-deor">
        <img src="https://github.com/klaus-deor.png" width="100px;" alt="Klaus Deor"/><br />
        <sub><b>Klaus Deor</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://claude.ai">
        <img src="https://img.icons8.com/fluency/100/000000/artificial-intelligence.png" width="100px;" alt="Claude Code"/><br />
        <sub><b>Claude Code</b></sub>
      </a>
      <br />
      <sub>Anthropic AI Assistant</sub>
    </td>
  </tr>
</table>

---

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## Links Úteis

- [Repositório GitHub](https://github.com/klaus-deor/Transcripter)
- [Groq Console](https://console.groq.com/) - Obter API Key
- [Reportar Bug](https://github.com/klaus-deor/Transcripter/issues)
- [Solicitar Feature](https://github.com/klaus-deor/Transcripter/issues)

---

<p align="center">
  Feito com ❤️ por <a href="https://github.com/klaus-deor">Klaus Deor</a> e <a href="https://claude.ai">Claude Code</a>
</p>

<p align="center">
  <a href="#transcripter">⬆️ Voltar ao topo</a>
</p>
