# Solução para Hotkeys no Wayland

## O Problema

Você está usando **Wayland** como servidor de display. O Wayland **bloqueia hotkeys globais por motivos de segurança** - isso é por design, não é um bug.

Por isso, aplicativos não conseguem capturar atalhos de teclado globalmente no Wayland.

---

## Soluções Disponíveis

Existem **3 soluções** para fazer os atalhos funcionarem:

---

### **Solução 1: Mudar para X11** (Mais Simples - Recomendado)

Esta é a solução mais simples e faz tudo funcionar perfeitamente.

#### Passos:

1. **Faça logout** do sistema
2. **Na tela de login**, procure por um **ícone de engrenagem** ou **"\u2699"** (geralmente perto do botão "Entrar")
3. **Clique no ícone** e selecione:
   - **"Ubuntu on Xorg"** (se você usa Ubuntu/GNOME)
   - **"Plasma (X11)"** (se você usa KDE)
   - Ou qualquer opção que mencione **"X11" ou "Xorg"**
4. **Faça login** normalmente
5. **Reinicie o Transcripter**:
   ```bash
   ./stop_transcripter.sh
   ./run_background.sh
   ```

Pronto! Os hotkeys vão funcionar perfeitamente agora.

#### Como verificar se está no X11:

```bash
echo $XDG_SESSION_TYPE
```

Se mostrar `x11`, você está no X11
Se mostrar `wayland`, ainda está no Wayland

---

### **Solução 2: Usar Atalhos do Desktop Environment** (Funciona no Wayland)

Se você quiser continuar usando Wayland, pode configurar o atalho nas configurações do sistema.

#### Para GNOME (Ubuntu padrão):

1. Abra **Configurações** (Settings)
2. Vá em **Teclado** (Keyboard)
3. Role até o final e clique em **"Adicionar atalho personalizado"** ou **"Custom Shortcuts"**
4. Configure:
   - **Nome:** Transcripter Toggle
   - **Comando:** `/home/klaus/Documentos/Saas/Transcripter/toggle_recording.sh`
   - **Atalho:** Pressione as teclas que quer usar (ex: Ctrl+Alt+R)
5. Clique em **Adicionar**

#### Para KDE Plasma:

1. Abra **Configurações do Sistema**
2. Vá em **Atalhos** -> **Atalhos Personalizados**
3. Clique em **Editar** -> **Novo** -> **Comando Global**
4. Configure:
   - **Nome:** Transcripter Toggle
   - **Comando:** `/home/klaus/Documentos/Saas/Transcripter/toggle_recording.sh`
   - **Gatilho:** Defina seu atalho
5. Aplique

Agora o atalho vai funcionar!

---

### **Solução 3: Testar o Script Manualmente**

Para testar se a solução está funcionando, você pode executar o script manualmente:

```bash
./toggle_recording.sh
```

Isso deve iniciar/parar a gravação, mesmo no Wayland.

---

## Diagnóstico

Execute o script de diagnóstico para ver informações detalhadas:

```bash
./diagnose_hotkeys.sh
```

Este script vai:
- Verificar se o Transcripter está rodando
- Detectar se você está no Wayland ou X11
- Verificar logs de erro
- Testar se pynput está funcionando
- Mostrar recomendações específicas

---

## Resumo das Soluções

| Solução | Dificuldade | Funciona no Wayland? | Recomendação |
|---------|-------------|----------------------|--------------|
| **Mudar para X11** | Fácil | N/A (usa X11) | Melhor |
| **Atalhos do DE** | Fácil | Sim | Boa alternativa |
| **Script manual** | Muito fácil | Sim | Para testes |

---

## FAQ

### Por que o Wayland bloqueia hotkeys?

Por segurança. Imagine um malware capturando todas as suas teclas digitadas (incluindo senhas). O Wayland previne isso não permitindo que aplicativos capturem teclas globalmente.

### Posso usar os dois (X11 e Wayland)?

Sim! Você pode alternar entre X11 e Wayland sempre que fizer login. É só escolher na tela de login.

### O X11 é seguro?

Sim, o X11 ainda é amplamente usado e seguro. O Wayland é mais moderno e tem algumas vantagens de segurança, mas o X11 funciona perfeitamente para a maioria dos casos.

### Meu desktop funciona melhor no Wayland

Se você precisa do Wayland por outros motivos (melhor suporte a HiDPI, melhor performance em certos hardwares, etc.), use a **Solução 2** (atalhos do DE).

---

## Ainda não funciona?

1. Execute o diagnóstico:
   ```bash
   ./diagnose_hotkeys.sh
   ```

2. Verifique os logs:
   ```bash
   tail -f ~/.config/transcripter/transcripter.log
   ```

3. Reinicie o Transcripter:
   ```bash
   ./stop_transcripter.sh
   ./run_background.sh
   ```

4. Teste o script manualmente:
   ```bash
   ./toggle_recording.sh
   ```

Se ainda assim não funcionar, abra uma issue no GitHub com a saída do `diagnose_hotkeys.sh`.
