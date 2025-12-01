# 🔧 Solução de Problemas - Gemini API

## Problema: Erro 404 com modelo Gemini

Se você ainda estiver vendo o erro:
```
Erro ao gerar insights: 404 models/gemini-1.5-flash is not found
```

Mesmo após atualizar o código, isso acontece porque o **Streamlit está usando cache antigo**.

---

## ✅ Solução Rápida

### Opção 1: Limpar Cache pelo Menu (Recomendado)
1. Na aplicação Streamlit, clique no **menu ☰** (três barrinhas) no canto superior direito
2. Selecione **"Clear cache"**
3. Recarregue a página (F5)

### Opção 2: Reiniciar Servidor
1. Pare o servidor Streamlit (Ctrl+C no terminal)
2. Reinicie com:
```powershell
py -m streamlit run app.py
```

### Opção 3: Forçar Recarga Completa
No terminal, execute:
```powershell
# Windows PowerShell
Remove-Item -Recurse -Force $env:USERPROFILE\.streamlit\cache
py -m streamlit run app.py
```

---

## 🔍 Verificação

O modelo correto configurado em `ai_models.py`:
- ✅ Linha 20: `model="gemini-2.5-flash"`
- ✅ Linha 48: `genai.GenerativeModel('gemini-2.5-flash')`

Nenhuma referência a `gemini-1.5-flash` existe no código atual.

---

## 📝 Modelos Gemini Disponíveis

Use um destes modelos na sua API Key:
- **gemini-2.5-flash** (Recomendado - mais recente)
- gemini-2.0-flash-exp
- gemini-1.5-pro
- gemini-1.5-flash-latest

---

## 🎯 Após Limpar Cache

1. Vá para **🤖 AI Insights**
2. Insira sua API Key
3. Teste com **"🔄 Gerar Insights"**
4. Deve funcionar perfeitamente! ✅

---

*Última atualização: 01/12/2025*
