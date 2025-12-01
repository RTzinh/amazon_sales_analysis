# 📊 Amazon Sales Analytics Dashboard

Plataforma profissional de análise de vendas com **IA integrada** usando Google Gemini e LangChain.

## 🌟 Características Principais

### 📊 Dashboards Interativos
- **Dashboard Executivo**: KPIs principais, tendências e quick wins em uma página
- **Overview**: Métricas de conversão e resumo executivo
- **Sales Analytics**: Análise temporal, tendências e padrões sazonais
- **Product Performance**: Top produtos, categorias e análise de margem
- **Customer Insights**: Segmentação RFM e clustering ML
- **Geographic Analysis**: Mapas de calor e distribuição regional
- **Performance Comercial**: Ranking de vendedores e análise de descontos
- **Eficiência Comercial**: Gargalos operacionais e quick wins
- **Plano de Ação**: Recomendações estratégicas com ROI calculado
- **AI Insights**: Análises com Google Gemini AI

### 🤖 Recursos de Inteligência Artificial
- ✨ **Google Gemini AI**: Geração automática de insights de negócio
- 💬 **LangChain Agents**: Chat com dados em linguagem natural
- 🎯 **Machine Learning**: Clustering de clientes e segmentação RFM
- 🚨 **Anomaly Detection**: Identificação de transações incomuns
- 📈 **Análise Preditiva**: Insights qualitativos sobre tendências

### 🎨 Design Moderno
- Interface web responsiva com tema dark elegante
- Visualizações interativas com Plotly
- Animações suaves e efeitos glassmorphism
- Filtros dinâmicos em tempo real
- Exportação de relatórios em PDF

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.8 ou superior
- Chave da API do Google Gemini ([obter aqui](https://makersuite.google.com/app/apikey))

### Instalação

1. **Instale as dependências:**
```powershell
py -m pip install -r requirements.txt
```

2. **Execute a aplicação:**
```powershell
py -m streamlit run app.py
```

3. **Acesse no navegador:**
```
http://localhost:8501
```

## 🔑 Configuração da API Gemini

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma nova API Key (gratuita)
3. Na página **🤖 AI Insights**, insira sua chave
4. Aproveite os recursos de IA!

## 📁 Estrutura do Projeto

```
amazon_sales_analysis/
├── app.py                      # Aplicação principal
├── data_processor.py           # Processamento de dados
├── ai_models.py                # Modelos de IA (Gemini, LangChain, ML)
├── utils.py                    # Componentes UI
├── pdf_generator.py            # Exportação de relatórios PDF
├── Amazon.csv                  # Dataset de vendas
├── requirements.txt            # Dependências Python
├── .streamlit/
│   └── config.toml            # Configuração do tema
└── pages/
    ├── 0_📊_Dashboard_Executivo.py      # ⭐ NOVO
    ├── 1_📊_Overview.py
    ├── 2_📈_Sales_Analytics.py
    ├── 3_🛍️_Product_Performance.py
    ├── 4_👥_Customer_Insights.py
    ├── 5_🗺️_Geographic_Analysis.py
    ├── 6_🤖_AI_Insights.py
    ├── 7_📈_Performance_Comercial.py     # ⭐ NOVO
    ├── 8_⚡_Eficiência_Comercial.py      # ⭐ NOVO
    └── 9_🎯_Plano_de_Ação.py            # ⭐ NOVO
```

## 💡 Funcionalidades Principais

### 1. Dashboard Executivo ⭐
- 6 KPIs principais em cards grandes
- Gráfico de tendência com regressão linear
- 3 Quick Wins com ganho estimado
- Botão para ver plano completo
- **Ideal para apresentações executivas**

### 2. Performance Comercial
- Ranking de vendedores (Top 20)
- Análise de impacto de desconto na margem
- Performance regional
- Funil de conversão comercial
- Quick wins identificados

### 3. Eficiência Comercial
- Identificação de gargalos operacionais
- Análise de cancelamentos por categoria
- Produtos de alto volume e baixa margem
- Eficiência por método de pagamento
- Priorização de ações (Crítico/Importante/Melhoria)

### 4. Plano de Ação Estratégico
- 5 ações priorizadas por ROI
- Cronograma de implementação (90 dias)
- Métricas de sucesso mês a mês
- Projeção de ROI detalhada
- **Exportação em PDF** 📄

### 5. AI Insights
#### 🧠 Insights Automáticos
Gemini analisa dados e gera recomendações acionáveis

#### 💬 Chat com Dados
Faça perguntas em linguagem natural:
- "Qual é o produto mais vendido?"
- "Quanto faturamos em Electronics?"
- "Quais clientes gastaram mais de $10,000?"

#### 🚨 Detecção de Anomalias
Machine Learning identifica transações incomuns

## 📊 Dataset

O dataset **Amazon.csv** contém 100.000 transações com:

- **Pedidos**: OrderID, OrderDate, OrderStatus
- **Clientes**: CustomerID, CustomerName, City, State, Country
- **Produtos**: ProductID, ProductName, Category, Brand
- **Valores**: UnitPrice, Quantity, Discount, Tax, ShippingCost, TotalAmount
- **Outros**: PaymentMethod, SellerID

## 🛠️ Tecnologias Utilizadas

### Core
- **Python 3.13**: Linguagem base
- **Streamlit 1.51**: Framework web
- **Pandas & NumPy**: Processamento de dados

### Visualização
- **Plotly 6.5**: Gráficos interativos
- **Seaborn**: Visualizações estatísticas

### Inteligência Artificial
- **Google Gemini AI**: Insights automáticos
- **LangChain**: Agentes conversacionais
- **Scikit-learn**: Machine Learning

### Exportação
- **FPDF2**: Geração de relatórios PDF

## 📈 Métricas de Performance

- ✅ 100k registros processados instantaneamente
- ⚡ Caching inteligente para performance otimizada
- 📱 Interface responsiva
- 🎨 10 páginas completas de análise
- 🤖 IA integrada em tempo real
- 📄 Exportação de relatórios em PDF

## 🎯 Como Usar

### Para Análise Executiva
1. Inicie pelo **Dashboard Executivo**
2. Identifique KPIs principais e quick wins
3. Acesse **Plano de Ação** para detalhes
4. Exporte relatório em PDF

### Para Análise Detalhada
1. **Performance Comercial** → Vendedores e margem
2. **Eficiência Comercial** → Gargalos e oportunidades
3. **Customer Insights** → Segmentação e clusters
4. **AI Insights** → Perguntas e anomalias

### Para Gestores
1. Dashboard Executivo (visão geral)
2. Quick Wins (ações rápidas)
3. Plano de Ação (estratégia 90 dias)
4. Baixar PDF para apresentação

## 💎 Diferenciais

### Análise Comercial Completa
- ✅ KPIs comerciais essenciais
- ✅ Análise por vendedor (SellerID)
- ✅ Impacto de desconto calculado
- ✅ Gargalos identificados
- ✅ Quick wins mapeados

### Orientação a Ação
- Cada insight tem **ação prática**
- **ROI calculado** para iniciativas
- Priorização por impacto
- Timeline de 90 dias

### Formato Executivo
- Dashboard resumido
- Métricas de sucesso claras
- Cronograma realista
- Exportação em PDF

## 📄 Exportação de Relatórios

Na página **Plano de Ação**, clique em:
```
📥 Baixar Plano de Ação em PDF
```

O PDF inclui:
- ✅ KPIs principais
- ✅ Quick Wins com ganhos estimados
- ✅ Métricas de performance
- ✅ ROI projetado

## 🎓 Aprendizados Técnicos

### Análise de Dados
- Feature engineering (10+ variáveis derivadas)
- Segmentação RFM
- Clustering K-means
- Anomaly detection (Isolation Forest)

### Desenvolvimento Web
- Streamlit multi-page apps
- Session state management
- Caching strategies
- Custom CSS styling

### IA Generativa
- Prompt engineering
- LangChain agents
- Contextualização de dados
- Tratamento de erros

## 🚀 Melhorias Futuras

- [ ] Forecasting com Prophet
- [ ] Dashboard em tempo real
- [ ] Alertas automáticos
- [ ] App mobile
- [ ] Integração com CRM

## 📝 Licença

Projeto desenvolvido para fins educacionais e demonstração de habilidades em análise de dados aplicada a vendas.

---

**Desenvolvido com ❤️ usando:**
- Python 3.13
- Streamlit
- Google Gemini AI
- LangChain
- Plotly

🚀 **Versão**: 2.0.0  
📅 **Atualização**: Dezembro 2025  
💼 **Foco**: Performance Comercial com IA
