# 🎯 MapaLeads PRO - Prospecção Inteligente no Google Maps

O **MapaLeads PRO** é uma plataforma moderna em **tema Light minimalista** (com paleta estrita de 5 cores harmoniosas) para mapear empresas locais no **Google Maps** que **NÃO possuem site oficial** ou utilizam apenas redes sociais, com **CRM de Vendas integrado** e **Automação de WhatsApp**.

---

## 🚀 Como Iniciar

Dê dois cliques no arquivo:
```bat
iniciar.bat
```
Ou via terminal:
```bash
python server.py
```
O painel abrirá automaticamente em: **`http://127.0.0.1:5055`**

---

## 💎 Novidades & Melhorias Desta Versão

### 1. Autocomplete com Classificação Precisa: Cidade, Bairro ou Rua
- **Classificação Visual em Tempo Real**: Exibe badges distintos com ícones para **Cidade** (🏙️ roxo), **Bairro** (🏘️ verde) e **Rua / Avenida** (🛣️ azul).
- **Calibração Inteligente de Zoom no Google Maps**:
  - **Cidade**: Zoom calibrado em `12z` (ou enquadramento do polígono municipal) para varrer todos os estabelecimentos da cidade inteira.
  - **Bairro**: Zoom calibrado em `14z` para cobrir todo o perímetro do bairro.
  - **Rua / Avenida**: Zoom calibrado em `16z` para cobrir a extensão comercial da via sem vincular a número de porta.
- **Formulação Natural de Busca**: Constrói queries em português nativo adequadas a cada nível geográfico (ex: *"Psicólogos em Belo Horizonte"*, *"Clínicas Médicas em Copacabana, Rio de Janeiro"*, *"Oficinas Mecânicas na Av. Paulista, São Paulo"*).

### 2. Catálogo de Segmentos Expandido (+80 Nichos B2C & B2B)
- **Saúde & Medicina**: Psicólogos, Médicos Especialistas, Dentistas, Fisioterapeutas, Nutricionistas, Fonoaudiólogos, Veterinárias, Laboratórios, Clínicas Oftalmológicas e Podologia.
- **Serviços B2B & Corporativos**: Contabilidade, Escritórios de Advocacia, Consultorias, Agências de Marketing/Tráfego, Suporte de TI, Segurança e Monitoramento, Limpeza e Conservação, Logística/Transportadoras, Coworking, Engenharia/Arquitetura e Gráficas.
- **Outras 9 Categorias Completas**: Beleza & Estética, Construção & Reformas, Automotivo, Gastronomia, Educação & Idiomas, Fitness & Esportes, Imobiliário & Finanças, Eventos & Festas e Comércio & Varejo.
- **Barra de Ferramentas com Filtros & Busca Instantânea**: Filtre por categoria com 1 clique ou busque qualquer nicho por digitação (com remoção automática de acentos).

### 2. Design Clean & Tema Light (5 Cores)
- **Branco & Slate Puro**: Visual estilo Linear / Stripe / Notion.
- **Azul Royal (#2563eb)**: Ações principais e navegação.
- **Verde Esmeralda (#10b981)**: WhatsApp e Vendas Fechadas.
- **Âmbar Ouro (#f59e0b)**: Destaque de oportunidades "Sem Site".
- Tipografia limpa com fontes Google Inter e Outfit.

### 3. CRM Completo de Vendas (Kanban por Funil)
- **Etapas do Funil**:
  1. `1. Novos Leads` (Ainda não contatados)
  2. `2. Mensagem Enviada` (Abordagem realizada com data/hora registrada)
  3. `3. Respondeu / Em Negociação` (Cliente interessado)
  4. `4. Reunião / Proposta` (Apresentação de portfólio de site)
  5. `5. Venda Fechada 🚀` (Registra o valor em R$ do site e soma no faturamento do topo)
- **Tags Dinâmicas**: Adicione marcadores como `#SemSite`, `#Quente`, `#RetornarAmanha`.
- **Métricas em Tempo Real**: Taxa de resposta de prospecção e faturamento acumulado de vendas.

### 4. Automação WhatsApp & Agendamento
- **Copy 1 (Abordagem com Gatilhos)**: Substituição automática de `{nome}`, `{categoria}`, `{rua}`, `{bairro}`, `{avaliacao}`.
- **Copy 2 (Follow-up de Agendamento)**: Resposta pronta com opções de horários para reunião ou envio de modelo de site.
- **Modo 1-Clique Seguro**: Abre o WhatsApp Web já com a mensagem preenchida sem nenhum risco de bloqueio.
- **Estrutura Modular para Baileys**: Configuração de delay humanizado de segurança (45 a 90s) e detector de resposta para agendamento.
