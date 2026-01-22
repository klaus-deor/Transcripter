# Como Executar o Transcripter

Existem **3 formas** de executar o Transcripter. Escolha a que preferir!

---

## Opção 1: No Terminal (precisa manter aberto)

**Quando usar:** Para testes rápidos ou desenvolvimento.

```bash
source venv/bin/activate
transcripter
```

ou

```bash
source venv/bin/activate
python -m transcripter.main
```

**ATENÇÃO:** Se você fechar o terminal, o programa fecha junto!

---

## Opção 2: Em Background (pode fechar o terminal)

**Quando usar:** Uso normal do dia a dia, sem precisar manter o terminal aberto.

### Iniciar:
```bash
./run_background.sh
```

### Parar:
```bash
./stop_transcripter.sh
```

**VANTAGEM:** Você pode fechar o terminal e o programa continua rodando!

O programa fica rodando em segundo plano e salva logs em:
- `~/.config/transcripter/transcripter.log`

---

## Opção 3: Como Aplicativo (menu de aplicativos)

**Quando usar:** Melhor opção! Rodar como um aplicativo normal do Linux.

### Instalação (faça apenas uma vez):

```bash
./install_desktop.sh
```

Este comando vai:
1. Adicionar "Transcripter" no menu de aplicativos
2. Perguntar se você quer que inicie automaticamente no login

### Depois de instalar:

1. **Procure "Transcripter" no menu de aplicativos** (como qualquer outro app)
2. **Clique para executar** - não precisa de terminal!
3. O ícone aparece na bandeja do sistema

**MELHOR OPÇÃO:** Funciona como qualquer outro aplicativo Linux!

---

## Autostart (Iniciar automaticamente)

Se você escolheu "sim" durante a instalação, o Transcripter vai iniciar automaticamente quando você fizer login no sistema.

### Habilitar autostart manualmente:
```bash
cp transcripter.desktop ~/.config/autostart/
```

### Desabilitar autostart:
```bash
rm ~/.config/autostart/transcripter.desktop
```

---

## Como Parar o Programa

### Se iniciou pelo terminal (Opção 1):
- Pressione `Ctrl + C` no terminal

### Se iniciou em background (Opção 2):
```bash
./stop_transcripter.sh
```

### Se iniciou pelo menu (Opção 3):
- Clique com botão direito no ícone da bandeja
- Selecione "Quit"

Ou use o script:
```bash
./stop_transcripter.sh
```

---

## Verificar se está rodando

```bash
ps aux | grep transcripter
```

ou

```bash
cat ~/.config/transcripter/transcripter.pid
```

---

## Ver Logs

Quando roda em background, os logs ficam em:

```bash
tail -f ~/.config/transcripter/transcripter.log
```

---

## Recomendação

**Para uso diário:**
1. Execute `./install_desktop.sh` (só precisa fazer uma vez)
2. Habilite o autostart quando perguntado
3. Pronto! O Transcripter vai iniciar automaticamente e você usa pelo ícone na bandeja

**Para desenvolvimento/testes:**
- Use a Opção 1 (terminal) para ver os logs em tempo real
