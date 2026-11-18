# -*- coding: utf-8 -*-
"""
Currículo Completo da Academia de Vendas PRO — MapaLeads PRO.
Contém 6 cursos completos de estratégias comerciais B2B locais, cada um com:
- 5 aulas aprofundadas passo a passo (lessons)
- Manual técnico de entrega e fornecedores (delivery_guide)
- 3 pacotes de precificação com cálculo de custo, setup, recorrência e margem (pricing_tiers)
- Checklist interativo de auditoria e entrega (checklist)
- 4 roteiros copiáveis: Abordagem Inicial, Cadência de Follow-up + Áudio, Matriz de Objeções e Proposta Comercial / Contrato (script_approach, script_followup, script_objections, proposal_script)
"""

SALES_ACADEMY_CURRICULUM = [
    # =========================================================================
    # CURSO 1 — GOOGLE MEU NEGÓCIO (GBP) & SEO LOCAL TOP 3
    # =========================================================================
    {
        "slug": "estrategia-gmn",
        "strategy_key": "gmn",
        "badge_label": "Curso 01 • Google Meu Negócio & SEO Local",
        "title": "Domínio do Google Meu Negócio & Posicionamento Top 3 Local",
        "subtitle": "Aprenda a auditar, vender, precificar e otimizar fichas do Google Business Profile para colocar empresas locais nas 3 primeiras posições do Google Maps em 30 dias.",
        "ticket_range": "R$ 350 a R$ 800 setup + R$ 250 a R$ 500/mês",
        "thumbnail_url": "/static/img/academy/gmn-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-gmn.mp4",
        "course_duration": "5 Aulas • ~45 min",
        "vsl_video_url": "/static/video/sales-academy/vsl-gmn.mp4",
        "vsl_title": "VSL Pronta: Seu Concorrente Está Roubando Seus Clientes no Google Maps",
        "vsl_duration": "00:29",
        "target_opp": "gmn",
        "sort_order": 1,
        "lessons": [
            {
                "num": 1,
                "module": "Módulo 1 • Fundamentos & Garimpagem",
                "title": "A Mina de Ouro do Google Local Pack e Como Filtrar os Melhores Alvos",
                "duration": "10 min",
                "summary": "Entenda como funciona o algoritmo do Google Maps (Relevância, Distância e Proeminência) e como encontrar empresas que estão perdendo vendas todos os dias.",
                "content_html": """
<h4>1. Por que o Google Meu Negócio é o serviço mais fácil de vender para empresas locais?</h4>
<p>Diferente do Instagram (onde o usuário está rolando o feed por entretenimento), quem pesquisa <em>"dentista perto de mim"</em>, <em>"oficina mecânica em [Bairro]"</em> ou <em>"clínica de estética em [Cidade]"</em> no Google já está com o <strong>cartão de crédito na mão e urgência de compra</strong>. Estudos de SEO Local comprovam que <strong>68% de todos os cliques e ligações</strong> ficam concentrados nas <strong>3 primeiras empresas do bloco do mapa (Google Local Pack)</strong>.</p>

<div class="sa-callout sa-callout-emerald">
  <strong><i class="fa-solid fa-bolt"></i> Os 3 Pilares Oficiais do Algoritmo do Google Maps:</strong>
  <ul>
    <li><strong>1. Relevância (35% do peso):</strong> O quão bem a ficha responde à busca do usuário. Depende diretamente da <strong>Categoria Principal</strong>, das Categorias Secundárias, dos Serviços cadastrados e das palavras-chave na descrição e nas avaliações.</li>
    <li><strong>2. Proeminência / Autoridade (40% do peso):</strong> Volume total de avaliações, nota média (acima de 4.6⭐), frequência de novas avaliações (recência), taxa de resposta do proprietário, fotos atualizadas e consistência NAP (Nome, Endereço e Telefone idênticos no site e diretórios).</li>
    <li><strong>3. Distância (25% do peso):</strong> Proximidade física do pesquisador ou menção explícita dos bairros atendidos na aba de Áreas de Cobertura e Serviços.</li>
  </ul>
</div>

<h4>2. Como filtrar os alvos perfeitos dentro do MapaLeads PRO</h4>
<ol>
  <li>Vá em <strong>Buscar Empresas</strong> e escolha nichos de <strong>alto ticket médio</strong> (Clínicas Odontológicas, Estética, Advocacia, Energia Solar, Oficinas Mecânicas, Dedetizadoras, Veterinárias, Imobiliárias). Um único cliente novo para essas empresas paga o seu serviço 3 vezes!</li>
  <li>No <strong>CRM Kanban</strong>, selecione o filtro de oportunidade <strong>"Google Meu Negócio"</strong> ou ordene pelo <strong>Score IA ≥ 70</strong>.</li>
  <li>Priorize empresas que tenham: <strong>menos de 30 avaliações</strong>, <strong>nota abaixo de 4.6</strong>, ou que tenham boa estrutura física mas <strong>não apareçam no Top 3</strong> quando você pesquisa o nicho + bairro.</li>
</ol>
"""
            },
            {
                "num": 2,
                "module": "Módulo 2 • Diagnóstico Raio-X",
                "title": "Auditoria Prática em 2 Minutos: Os 7 Erros que Afundam uma Ficha",
                "duration": "12 min",
                "summary": "Aprenda a bater o olho em qualquer perfil do Google Maps e encontrar imediatamente 3 a 5 falhas graves para apresentar ao dono do negócio.",
                "content_html": """
<h4>O Roteiro de Auditoria Rápida (2 Minutos por Lead)</h4>
<p>Antes de mandar mensagem para o empresário, clique no botão <strong>Ver no Google Maps</strong> dentro da gaveta do lead no MapaLeads PRO e verifique estes 7 pontos:</p>

<div class="sa-lesson-grid">
  <div class="sa-lesson-card">
    <strong>1. Categoria Principal Genérica ou Errada</strong>
    <p>Ex: Uma clínica especializada em implantes cadastrada apenas como "Dentista" em vez de "Periodontista de implantes dentários", ou uma hamburgueria artesanal cadastrada como "Lanchonete".</p>
  </div>
  <div class="sa-lesson-card">
    <strong>2. Ausência de Categorias Secundárias</strong>
    <p>O Google permite até 9 categorias adicionais. 90% das empresas locais preenchem apenas 1 e perdem buscas específicas de alta conversão.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>3. Avaliações Sem Resposta do Proprietário</strong>
    <p>Quando o cliente avalia e o dono não responde, o algoritmo do Google interpreta que o perfil está abandonado e reduz sua entrega no mapa.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>4. Falta de Catálogo de Produtos e Serviços</strong>
    <p>Fichas sem a vitrine de Produtos/Serviços preenchida ocupam metade do espaço visual na tela do celular e não ranqueiam para buscas de serviços específicos.</p>
  </div>
</div>

<h4>A Técnica do "Print Comparativo de Choque"</h4>
<p>Abra o Google Maps em uma aba anônima e digite: <code>[Nicho do Lead] em [Bairro/Cidade]</code> (ex: <em>"Clínica de estética em Moema"</em>). Tire um print das <strong>3 primeiras empresas que aparecem no topo</strong> (onde o seu lead NÃO está). Circule em vermelho os 3 concorrentes e anote quantas avaliações eles têm. Esse print será sua arma secreta na abordagem!</p>
"""
            },
            {
                "num": 3,
                "module": "Módulo 3 • Prospecção & Fechamento",
                "title": "Abordagem Magnética no WhatsApp + Uso da VSL White-Label",
                "duration": "08 min",
                "summary": "A sequência exata de mensagens, print e vídeo VSL que gera taxa de resposta acima de 45% com donos de empresas locais.",
                "content_html": """
<h4>Regra de Ouro: Nunca mande "textão de agência" na primeira mensagem</h4>
<p>Donos de empresas ignoram mensagens longas que começam com <em>"Olá, somos uma agência de marketing digital..."</em>. Em vez disso, faça uma <strong>abordagem consultiva dividida em 2 passos</strong>:</p>

<ol>
  <li><strong>Mensagem 1 (Quebra-gelo de Curiosidade):</strong> Pergunte se é o responsável e avise que encontrou uma falha no posicionamento da empresa no Google Maps da cidade.</li>
  <li><strong>Mensagem 2 (Assim que ele responder "Qual falha?" ou "Pode falar"):</strong> Envie o <strong>Print Comparativo</strong> + a <strong>VSL Pronta desta estratégia (<code>vsl-gmn.mp4</code>)</strong> + um áudio curto de 30 segundos falando o nome da empresa dele e dos 2 concorrentes que estão capturando as ligações no lugar dele.</li>
</ol>

<div class="sa-callout sa-callout-amber">
  <strong><i class="fa-solid fa-microphone"></i> Estrutura do Áudio Matador de 30 Segundos:</strong>
  <p><em>"Fala [Nome], tudo bem? Te mandei esse vídeo rápido de 25 segundos e o print acima porque fiz o teste buscando por [Nicho] aqui em [Cidade]. Hoje quem aparece no Top 3 recebendo os cliques diretos de WhatsApp são a [Concorrente A] e a [Concorrente B], mesmo a sua estrutura sendo excelente. Eu já mapeei os 4 ajustes técnicos na sua ficha do Google para puxar sua empresa para o topo ainda este mês. Posso te mandar aqui em 3 linhas o que precisa ser corrigido?"</em></p>
</div>
"""
            },
            {
                "num": 4,
                "module": "Módulo 4 • Execução Técnica Passo a Passo",
                "title": "Como Entregar o Serviço na Prática em 90 Minutos (Manual Operacional)",
                "duration": "15 min",
                "summary": "O passo a passo completo desde como solicitar acesso de gerente na ficha do cliente até a otimização avançada de SEO Local.",
                "content_html": """
<h4>Passo 1: Como receber acesso à ficha SEM pedir a senha do Gmail do cliente</h4>
<ol>
  <li>Peça para o cliente abrir o Google logado no e-mail da empresa e digitar <strong>"Minha Empresa"</strong> na busca (ou acessar <code>business.google.com</code>).</li>
  <li>Ele clica nos <strong>3 pontinhos (⋮)</strong> no canto superior direito do painel → <strong>Configurações do Perfil da Empresa</strong> → <strong>Pessoas e acesso</strong> → <strong>Adicionar (+)</strong>.</li>
  <li>Ele digita o <strong>seu e-mail Gmail</strong>, seleciona o nível <strong>Administrador (Gerente)</strong> e clica em Convidar. Você aceita no seu e-mail e já pode trabalhar!</li>
</ol>

<h4>Passo 2: Os 8 Ajustes Técnicos de Otimização Top 3</h4>
<ol>
  <li><strong>Categoria Principal Cirúrgica:</strong> Instale a extensão gratuita <em>PlePer</em> ou <em>GMB Everywhere</em> no Chrome para ver qual é a categoria exata usada pelos 3 primeiros colocados da cidade e aplique a mesma categoria principal + 4 a 6 categorias secundárias relevantes.</li>
  <li><strong>Nome Semântico (Sem Spam):</strong> Use o formato <code>Nome da Marca - Especialidade Principal</code> (ex: <em>Clínica Sorriso - Implantes e Odontologia</em>). Não encha de bairros ou palavras repetidas para evitar suspensão.</li>
  <li><strong>Descrição Otimizada (750 caracteres):</strong> Escreva 3 parágrafos incluindo os serviços principais, diferenciais, tempo de mercado e os 5 principais bairros/regiões atendidos.</li>
  <li><strong>Consistência NAP &amp; Link de WhatsApp com Rastreio:</strong> No campo "Website" ou "Agendamento", coloque o Biossite do cliente ou o link direto para o WhatsApp com mensagem pré-preenchida: <code>https://wa.me/55DD999999999?text=Ol%C3%A1%2C+encontrei+voc%C3%AAs+no+Google+e+gostaria+de+um+or%C3%A7amento</code>.</li>
  <li><strong>Vitrine de Produtos e Serviços (O Segredo Visual):</strong> Cadastre de 8 a 15 Produtos/Serviços com foto (1200×900px), título contendo a palavra-chave (ex: <em>Limpeza de Pele Profunda em [Cidade]</em>), descrição persuasiva e botão levando para o WhatsApp.</li>
  <li><strong>Upload de 15 Fotos Reais Nomeadas:</strong> Renomeie os arquivos das fotos antes de subir (ex: <code>clinica-odontologica-centro-fachada.jpg</code>). Suba 3 fotos da fachada, 4 do interior, 4 da equipe trabalhando e 4 de serviços/resultados.</li>
  <li><strong>Seção de Perguntas e Respostas (FAQ Nativo):</strong> Use sua conta para fazer as 5 perguntas mais comuns dos clientes (ex: <em>"Vocês atendem convênio ou parcelam?", "Tem estacionamento no local?", "Como agendar pelo WhatsApp?"</em>) e responda oficialmente pelo perfil da empresa.</li>
  <li><strong>Resposta Semântica a Todas as Avaliações:</strong> Responda as últimas 20 avaliações agradecendo pelo nome e inserindo naturalmente o serviço + cidade (ex: <em>"Muito obrigado pela avaliação, Carlos! Ficamos felizes que tenha gostado do nosso serviço de [Palavra-Chave] aqui em [Cidade]!"</em>).</li>
</ol>
"""
            },
            {
                "num": 5,
                "module": "Módulo 5 • Escala & Recorrência Mensal",
                "title": "Como Fechar Mensalidades de R$ 250 a R$ 500/mês e Reter por 12 Meses",
                "duration": "10 min",
                "summary": "Como não viver apenas de setups únicos: estruture o plano de manutenção mensal que leva 40 minutos por mês para entregar.",
                "content_html": """
<h4>Por que o cliente precisa de manutenção mensal no Google Meu Negócio?</h4>
<p>Explique ao cliente: <em>"O Google Maps não é uma placa estática na rua; é um ranking vivo. Se arrumarmos sua ficha hoje e ela ficar 3 meses sem novas fotos, sem postagens semanais e sem respostas estratégicas às avaliações, os concorrentes voltam a te ultrapassar."</em></p>

<h4>O Que Entregar na Mensalidade (Custo de Tempo: 40 min/mês por cliente)</h4>
<ul>
  <li><strong>1 Postagem Semanal na aba "Atualizações / Ofertas" do Google:</strong> Pode reaproveitar a melhor foto que o cliente já postou no Instagram da semana, adicionando um texto com palavras-chave locais e botão "Ligar agora" ou "Saiba mais".</li>
  <li><strong>Resposta Profissional a 100% das Novas Avaliações:</strong> Com inserção de palavras-chave de SEO Local.</li>
  <li><strong>Upload de 4 Novas Fotos por Mês:</strong> Mantém o sinal de "frescor" (freshness) ativo no algoritmo do Google.</li>
  <li><strong>Relatório Mensal no WhatsApp (Todo dia 05):</strong> Tire 1 print da aba <strong>Desempenho (Performance)</strong> do Google Meu Negócio mostrando quantas pessoas visualizaram a ficha, clicaram em "Rotas" e clicaram em "Ligar / Website" nos últimos 30 dias. Quando o dono vê 80 ligações geradas, ele renova sua mensalidade sorrindo!</li>
</ul>
"""
            }
        ],
        "delivery_guide": """PASSO A PASSO TÉCNICO DE ENTREGA (CHECKLIST DE BASTIDORES — 90 MINUTOS)

1. ACESSO SEGURO (GERENTE DA FICHA)
   • Solicite ao cliente que adicione seu Gmail em: business.google.com → Menu (⋮) → Configurações do Perfil da Empresa → Pessoas e acesso → Adicionar Administrador.
   • Caso a empresa ainda não tenha reivindicado a ficha, clique em "É proprietário desta empresa?" no Google Maps e faça a verificação por vídeo curto ou SMS junto com o cliente.

2. PESQUISA DE CATEGORIAS DOS LÍDERES (EXTENSÃO GRATUITA)
   • Instale no Google Chrome a extensão gratuita "PlePer Local SEO Tools" ou "GMB Everywhere".
   • Pesquise a palavra-chave principal na cidade do cliente e anote a Categoria Primária e as Categorias Secundárias dos 3 primeiros colocados.
   • Atualize a Categoria Primária do seu cliente e adicione de 4 a 7 Categorias Secundárias coerentes.

3. OTIMIZAÇÃO DE DADOS CADASTRAIS & NAP
   • Nome: [Marca do Cliente] - [Especialidade Principal] (Evite excesso de palavras-chave para não violar diretrizes).
   • Descrição (750 caracteres): Inclua especialidades, diferenciais, bairros vizinhos atendidos e chamada para ação.
   • Horários: Preencha todos os dias da semana + feriados próximos (o Google prioriza fichas com horários de feriados confirmados).
   • Atributos: Marque todas as comodidades (Acessibilidade, Wi-Fi, Formas de Pagamento, Estacionamento, Atendimento com hora marcada).

4. VITRINE DE PRODUTOS E SERVIÇOS (CONVERSÃO DIRETA)
   • Na aba "Editar Produtos", crie de 3 a 4 categorias e cadastre os 10 principais serviços/produtos do cliente.
   • Em cada produto, suba uma foto nítida (1200x900px), coloque o preço (ou "A partir de R$ X") e no link do botão cole o link direto do WhatsApp do cliente com mensagem personalizada.

5. BATERIA DE FOTOS + FAQ + RESPOSTAS A REVIEWS
   • Suba pelo menos 12 fotos reais e bem iluminadas (Fachada, Recepção, Equipe, Produtos/Serviços).
   • Cadastre 5 Perguntas e Respostas (Q&A) estratégicas na ficha.
   • Responda as últimas 20 avaliações do perfil utilizando o nome do avaliador + o serviço prestado + o nome da cidade.

6. ENTREGA DO LINK CURTO DE AVALIAÇÃO + RELATÓRIO "ANTES E DEPOIS"
   • Copie o link direto "Pedir avaliações" (g.page/r/.../review) no painel do Google.
   • Monte um PDF ou mensagem no WhatsApp com o print do Perfil Antes vs. Perfil Depois + o link curto para o cliente enviar aos consumidores pelo WhatsApp.""",
        "pricing_tiers": [
            {
                "name": "Plano Setup Express",
                "badge": "Porta de Entrada",
                "cost": "R$ 0,00 (1h30 do seu tempo)",
                "setup_price": "R$ 350 a R$ 490",
                "monthly_price": "Sem mensalidade",
                "profit_margin": "100% de margem líquida",
                "deliverables": [
                    "Auditoria completa + Correção de Categoria Principal e Secundárias",
                    "Descrição otimizada com SEO Local (750 caracteres)",
                    "Cadastro de até 8 Produtos/Serviços com botão direto para WhatsApp",
                    "Upload de 10 fotos otimizadas + Resposta às últimas 15 avaliações",
                    "Entrega do Link Curto Oficial para captar novas avaliações 5 estrelas"
                ]
            },
            {
                "name": "Plano Top 3 + Gestão Mensal",
                "badge": "Mais Vendido ★",
                "cost": "R$ 0,00 (40 min/mês)",
                "setup_price": "R$ 497 a R$ 697",
                "monthly_price": "R$ 250 a R$ 397/mês",
                "profit_margin": "100% de margem + Receita Recorrente",
                "deliverables": [
                    "Tudo do Setup Express + Cadastro de até 15 Produtos/Serviços na vitrine",
                    "Estruturação de 5 Perguntas & Respostas (FAQ nativo no Google)",
                    "4 Postagens mensais de Ofertas/Novidades no perfil do Google",
                    "Resposta profissional com palavras-chave a 100% das novas avaliações",
                    "Relatório mensal de Ligações, Cliques de WhatsApp e Rotas geradas"
                ]
            },
            {
                "name": "Plano Dominância Local + NFC",
                "badge": "Ticket Alto / VIP",
                "cost": "R$ 18,00 (1 Placa NFC)",
                "setup_price": "R$ 897 a R$ 1.290",
                "monthly_price": "R$ 397 a R$ 597/mês",
                "profit_margin": "98% de margem líquida",
                "deliverables": [
                    "Otimização Completa Google Meu Negócio + Gestão Mensal Contínua",
                    "1 Plaquinha Física em Acrílico com Chip NFC + QR Code para o balcão",
                    "Script e treinamento de 5 min para a equipe multiplicar avaliações 5⭐",
                    "Monitoramento mensal de concorrentes no Google Maps da região"
                ]
            }
        ],
        "checklist": [
            "Filtrar no MapaLeads empresas com nota < 4.6 ou menos de 35 avaliações no nicho escolhido",
            "Tirar o Print Comparativo mostrando os 3 concorrentes que aparecem no topo do Google Maps",
            "Enviar a Mensagem 1 de quebra-gelo e, após resposta, enviar o Print + VSL (vsl-gmn.mp4)",
            "Solicitar acesso de Administrador/Gerente em business.google.com (sem pedir senha do cliente)",
            "Ajustar Categoria Principal e adicionar 4 a 6 Categorias Secundárias usando PlePer/GMB Everywhere",
            "Reescrever Descrição (750 caracteres) com palavras-chave do serviço e bairros atendidos",
            "Cadastrar 10 Produtos/Serviços com fotos nítidas e link direto para o WhatsApp do cliente",
            "Subir 12+ fotos reais, criar 5 Perguntas & Respostas (FAQ) e responder às últimas 20 avaliações",
            "Agendar no calendário o envio do Print de Desempenho (Ligações/Rotas) após 30 dias para garantir a renovação"
        ],
        "script_approach": """[MENSAGEM 1 — QUEBRA-GELO DE ALTA RESPOSTA]
Olá, tudo bem? Aqui é o [Seu Nome].
Estou falando com o responsável pela *[Nome da Empresa]*?
Fiz uma busca rápida por *[Nicho da Empresa]* aqui em *[Cidade]* no Google Maps e notei um erro técnico na ficha de vocês que está entregando os clientes prontos para comprar direto para 2 concorrentes da região. Posso te mandar o print aqui rapidinho?

[MENSAGEM 2 — APÓS O CLIENTE RESPONDER "PODE MANDAR" (ENVIE O PRINT + A VSL MP4)]
Olha só esse print e esse vídeo rápido de 28 segundos que te mandei acima 👆
Quando um cliente pesquisa pelo seu serviço hoje em *[Cidade]*, o Google destaca apenas as 3 primeiras empresas do mapa (que concentram quase 70% das ligações e cliques no WhatsApp).
Hoje a *[Nome da Empresa]* está ficando de fora desse bloco principal porque:
1️⃣ A categoria secundária e o catálogo de serviços não estão indexados;
2️⃣ Faltam palavras-chave locais nas respostas de avaliações e na vitrine da ficha.

Eu trabalho especificamente corrigindo e otimizando o Perfil do Google para posicionar empresas de *[Cidade]* no Top 3 local.
Se eu deixar toda a sua estrutura otimizada em 48 horas por um valor único acessível, faz sentido eu te mostrar como funciona?""",
        "script_followup": """[FOLLOW-UP 1 — 24 HORAS DEPOIS (GATILHO DE VALOR)]
Oi, responsável pela *[Nome da Empresa]*! Imagino que a rotina aí esteja corrida.
Só para não deixar passar: além da correção das categorias, também notei que a ficha de vocês no Google ainda não tem o botão direto de orçamento para o WhatsApp na vitrine de serviços.
Quer que eu te mande as 3 correções e o valor do pacote de otimização rápida aqui pelo WhatsApp mesmo?

[FOLLOW-UP 2 — 72 HORAS DEPOIS (GATILHO DE PROVA / ESCASSEZ LOCAL)]
Fala! Passando para avisar que esta semana estou fechando a otimização de Google Maps de apenas 2 empresas do segmento de *[Nicho]* aqui em *[Cidade]* (para não gerar conflito de posicionar muitos concorrentes do mesmo bairro).
Como abri o diagnóstico para vocês primeiro, tenho 1 vaga disponível para entregar até sexta-feira. Ainda tem interesse em colocar a *[Nome da Empresa]* no topo das buscas locais?

[ROTEIRO DE ÁUDIO DE 30 SEGUNDOS]
"Fala, tudo bem? Te mandei mensagem porque quando a gente pesquisa por [Nicho] aí em [Cidade], a sua empresa tem uma estrutura excelente, mas o Google está jogando os clientes no colo da concorrência por falta de configuração técnica na ficha. É um ajuste que eu entrego pronto em 48h e que traz ligação orgânica o ano inteiro sem você precisar pagar anúncio para o Google. Dá uma olhada na proposta acima e me diz se consegue separar 2 minutinhos hoje!" """,
        "script_objections": """• "Mas o Google Meu Negócio é gratuito, eu mesmo posso mexer!"
Resposta: "Sim, a ferramenta é 100% gratuita! O problema é que apenas criar a ficha não posiciona no Top 3. Existe uma engenharia técnica por trás do algoritmo: escolha das categorias ocultas de maior peso, indexação semântica de serviços, parâmetros de conversão para o WhatsApp e resposta otimizada de reviews. Eu entrego tudo isso pronto em 48h para você focar no seu negócio enquanto o Google traz clientes."

• "Em quanto tempo vejo resultado?"
Resposta: "A mudança visual na ficha (vitrine de serviços, fotos profissionais, botões de WhatsApp e FAQ) fica pronta em 48 horas e já aumenta a conversão de quem te procura pelo nome. Já a subida de posições no ranking do Google Maps para buscas do seu nicho costuma ocorrer entre 15 e 35 dias conforme o algoritmo reindexa sua ficha."

• "Já invisto em Instagram / Tráfego Pago, preciso disso?"
Resposta: "No Instagram você interrompe pessoas que estão vendo vídeos de humor. No Google Maps você captura quem acabou de digitar exatamente o que você vende na sua cidade, com intenção imediata de compra. E o melhor: depois de otimizada, a ficha gera chamadas e mensagens no WhatsApp todos os dias de forma 100% orgânica, sem custo por clique."

• "Achei caro / Vou pensar."
Resposta: "Qual é o ticket médio de um único cliente novo na *[Nome da Empresa]* hoje? Geralmente apenas 1 ou 2 clientes que te encontrarem pelo Google Maps neste mês já pagam 100% dessa otimização, e a estrutura continua gerando chamadas pelos próximos 12 meses. Além disso, fazemos 50% na entrada e 50% só depois que você ver a ficha toda pronta!" """,
        "proposal_script": """📋 *PROPOSTA COMERCIAL — OTIMIZAÇÃO GOOGLE MEU NEGÓCIO & SEO LOCAL TOP 3*
Empresa: *[Nome da Empresa]* | Cidade: *[Cidade]*

🎯 *OBJETIVO DO PROJETO:*
Reestruturar e otimizar 100% do Perfil da Empresa no Google Maps para aumentar a autoridade visual, capturar clientes com alta intenção de compra na região e impulsionar o posicionamento rumo ao Top 3 local.

✅ *O QUE SERÁ ENTREGUE EM ATÉ 48 HORAS:*
1. Auditoria e configuração da Categoria Principal + Categorias Secundárias de alto volume de busca;
2. Redação estratégica da Descrição Oficial (750 caracteres) com palavras-chave locais e bairros atendidos;
3. Criação da Vitrine Visual com até 12 Produtos/Serviços cadastrados com foto e botão direto para o seu WhatsApp;
4. Tratamento e upload de até 15 fotos estratégicas do negócio;
5. Estruturação de 5 Perguntas & Respostas frequentes (FAQ nativo no Google);
6. Resposta otimizada com SEO Local às últimas 20 avaliações de clientes;
7. Geração do Link Curto Oficial + Roteiro para multiplicar novas avaliações 5 estrelas.

💰 *INVESTIMENTO & CONDIÇÃO ESPECIAL:*
• *Opção 1 (Setup Completo Único):* R$ 497,00 (50% no início + 50% na entrega em 48h via Pix)
• *Opção 2 (Setup + Gestão Mensal Contínua Top 3):* R$ 397,00 de implantação + R$ 250,00/mês (inclui 4 postagens mensais no Google, resposta contínua às avaliações, novas fotos e relatório mensal de chamadas/rotas).

🚀 *PARA INICIARMOS HOJE:*
Basta responder *"Quero a Opção 1"* ou *"Quero a Opção 2"* e te envio o passo a passo de 1 minuto para liberar meu acesso de gerente na ficha!"""
    },

    # =========================================================================
    # CURSO 2 — PLAQUINHAS NFC + QR CODE DE AVALIAÇÕES 5⭐, PIX & WI-FI
    # =========================================================================
    {
        "slug": "estrategia-nfc",
        "strategy_key": "nfc",
        "badge_label": "Curso 02 • Plaquinhas NFC & QR Code 5⭐",
        "title": "Fábrica de Lucro com Plaquinhas NFC + QR Code de Avaliações, Pix & Wi-Fi",
        "subtitle": "Aprenda onde comprar insumos por R$ 15, como gravar o chip NTAG215 pelo celular em 30 segundos e vender kits de balcão por R$ 150 a R$ 490 com 800% de lucro.",
        "ticket_range": "R$ 150 a R$ 490 (Custo R$ 15 a R$ 35)",
        "thumbnail_url": "/static/img/academy/nfc-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-nfc.mp4",
        "course_duration": "5 Aulas • ~40 min",
        "vsl_video_url": "/static/video/sales-academy/vsl-nfc.mp4",
        "vsl_title": "VSL Pronta: Multiplique suas Avaliações 5 Estrelas no Balcão por Aproximação",
        "vsl_duration": "00:25",
        "target_opp": "nfc",
        "sort_order": 2,
        "lessons": [
            {
                "num": 1,
                "module": "Módulo 1 • Oportunidade & Margem",
                "title": "Por que Todo Comércio Físico Compra Plaquinhas NFC na Hora",
                "duration": "08 min",
                "summary": "Entenda a psicologia do produto físico palpável, a dor da falta de avaliações e como lucrar até 800% por peça vendida.",
                "content_html": """
<h4>1. O Poder do Produto Físico + Tecnologia por Aproximação</h4>
<p>Muitos donos de comércios tradicionais têm resistência a comprar "serviços digitais invisíveis", mas quando veem um <strong>Display de Acrílico Premium em cima do balcão</strong> onde o cliente encosta o celular (igual ao Apple Pay / cartão por aproximação) e a tela de 5 estrelas do Google abre em 1 segundo, <strong>o desejo de compra é instantâneo</strong>.</p>

<div class="sa-callout sa-callout-emerald">
  <strong><i class="fa-solid fa-calculator"></i> A Matemática Real da Operação NFC:</strong>
  <ul>
    <li><strong>Custo do Display de Acrílico L ou T (10×15cm) + Arte Impressa/Adesivo Vinil:</strong> R$ 10,00 a R$ 15,00</li>
    <li><strong>Custo da Tag Adesiva NFC (Chip NXP NTAG215 - 25mm):</strong> R$ 1,50 a R$ 2,50</li>
    <li><strong>Custo Total de Produção por Placa:</strong> <strong>R$ 12,00 a R$ 18,00</strong></li>
    <li><strong>Preço de Venda Unitário (Comércio Local):</strong> <strong>R$ 147,00 a R$ 197,00</strong></li>
    <li><strong>Preço do Kit 3 Placas (Google 5⭐ + Pix Balcão + Wi-Fi Automático):</strong> <strong>R$ 347,00 a R$ 490,00</strong></li>
  </ul>
</div>

<h4>2. Quais nichos compram mais rápido?</h4>
<p>Filtre no MapaLeads PRO pelo filtro <strong>"Plaquinha NFC / QR"</strong> focando em negócios com <strong>alto fluxo presencial no balcão ou recepção</strong>:</p>
<ul>
  <li>Clínicas Odontológicas, Médicas e Estéticas (paciente espera na recepção com o celular na mão);</li>
  <li>Barbearias, Salões de Beleza e Esmalterias (cliente feliz logo após cortar o cabelo/fazer a unha);</li>
  <li>Restaurantes, Cafeterias, Padarias e Hamburguerias (placa no caixa ou em cada mesa);</li>
  <li>Oficinas Mecânicas, Lava-Rápidos, Pet Shops e Lojas de Ótica.</li>
</ul>
"""
            },
            {
                "num": 2,
                "module": "Módulo 2 • Fornecedores & Insumos",
                "title": "Chips NTAG213 vs NTAG215 e Onde Comprar Acrílicos e Tags Baratos no Brasil",
                "duration": "10 min",
                "summary": "Saiba exatamente qual chip comprar para nunca ter erro de leitura em iPhones e Androids e como montar seu estoque inicial gastando menos de R$ 90.",
                "content_html": """
<h4>1. Qual Chip NFC escolher: NTAG213 ou NTAG215?</h4>
<p>Sempre utilize chips originais da família <strong>NXP NTAG (frequência 13.56 MHz)</strong>, que são 100% compatíveis com qualquer iPhone (iPhone XR ou superior lê nativamente sem abrir nenhum app) e qualquer Android com NFC:</p>
<ul>
  <li><strong>NTAG213 (144 bytes de memória):</strong> Suporta URLs curtas (até ~130 caracteres). Funciona bem para links curtos <code>g.page/r/.../review</code>.</li>
  <li><strong>NTAG215 (504 bytes de memória — RECOMENDADO ★):</strong> Custa quase a mesma coisa (R$ 1,50 a R$ 2,50 em pacotes de 20 a 50 unidades), tem mais que o triplo de memória e permite gravar URLs longas, códigos Pix Copia e Cola ou credenciais completas de Wi-Fi sem risco de faltar espaço.</li>
  <li><strong>ATENÇÃO — Tags Anti-Metal:</strong> Se for colar a tag em balcão de inox ou superfície metálica, compre a versão <em>"Tag NFC NTAG215 Anti-Metal (com camada de ferrite)"</em>, pois o metal comum bloqueia o campo magnético de tags normais. Para acrílico, PVC ou madeira, a tag adesiva comum (Wet Inlay ou PVC 25mm) funciona perfeitamente!</li>
</ul>

<h4>2. As 2 Formas de Produzir suas Plaquinhas</h4>
<div class="sa-lesson-grid">
  <div class="sa-lesson-card">
    <strong>Opção A: Produção Própria Express (Menor Custo — R$ 14/unid)</strong>
    <p>1. Compre no Mercado Livre ou Shopee um <em>"Kit 10 Displays Acrílico L ou T 10x15cm Cristal"</em> (~R$ 75 o kit com 10) + <em>"Kit 20 Tags Adesivas NFC NTAG215 25mm"</em> (~R$ 35).<br>
    2. Crie a arte no Canva (10×15cm) com a logo do cliente, o ícone de aproximação NFC e o QR Code.<br>
    3. Imprima em papel fotográfico glossy 180g ou vinil adesivo em qualquer gráfica rápida por R$ 2,50, cole a tag NFC atrás do símbolo de aproximação e insira no display de acrílico!</p>
  </div>
  <div class="sa-lesson-card">
    <strong>Opção B: Placa Rígida PVC ou Acrílico Preto com Impressão UV (Premium — R$ 25/unid)</strong>
    <p>Busque no Mercado Livre/Shopee ou gráfica de comunicação visual da sua cidade por <em>"Display Placa Acrílico Preto QR Code NFC Personalizado"</em>. Você compra as bases prontas ou terceiriza a impressão UV e apenas grava o chip NFC pelo seu celular antes de entregar ao cliente por R$ 197!</p>
  </div>
</div>
"""
            },
            {
                "num": 3,
                "module": "Módulo 3 • Gravação Técnica no NFC Tools",
                "title": "Como Gravar o Chip em 30 Segundos pelo App Gratuito NFC Tools",
                "duration": "10 min",
                "summary": "Tutorial clique a clique no aplicativo NFC Tools (iOS e Android) para gravar Avaliação Google, Chave Pix e Conexão Wi-Fi Automática.",
                "content_html": """
<h4>Passo 1: Como pegar o Link Direto de Avaliação 5 Estrelas do Cliente</h4>
<ol>
  <li>Se o cliente já te deu acesso ao Google Meu Negócio, clique no botão <strong>"Pedir avaliações"</strong> no painel do Google e copie o link curto oficial (formato <code>https://g.page/r/CODIGO/review</code>).</li>
  <li><strong>Dica Ninja (Sem precisar de acesso à conta do cliente!):</strong> Você pode gerar o link direto de avaliação de QUALQUER empresa pública do Google Maps usando o <em>Place ID Finder</em> oficial do Google Developers: basta digitar o nome e endereço da empresa no mapa do Place ID Finder, copiar o código <code>ChIJ...</code> e montar o link: <code>https://search.google.com/local/writereview?placeid=COLE_O_PLACE_ID_AQUI</code>.</li>
</ol>

<h4>Passo 2: Gravando a Tag no App Gratuito "NFC Tools" (Wakdev)</h4>
<ol>
  <li>Baixe gratuitamente o app <strong>NFC Tools</strong> na App Store (iPhone) ou Google Play (Android).</li>
  <li>Abra o app e toque na aba <strong>"Escrever" (Write)</strong>.</li>
  <li>Toque em <strong>"Adicionar um registro" (Add a record)</strong> → escolha <strong>"URL / URI"</strong> (ou <em>URL Personalizada</em>).</li>
  <li>Cole o link completo (com <code>https://</code>) da avaliação do Google do cliente e toque em <strong>OK</strong>.</li>
  <li>Toque no botão <strong>"Escrever / X Bytes" (Write)</strong> e encoste a tag NFC na traseira do seu celular (no iPhone fica no topo, ao lado da câmera; no Android fica no centro da traseira).</li>
  <li>Ouviu o apito e apareceu <strong>"Gravação concluída!"</strong>? Pronto! Sua placa já está funcionando!</li>
</ol>

<div class="sa-callout sa-callout-amber">
  <strong><i class="fa-solid fa-triangle-exclamation"></i> Regra Crítica: NUNCA clique em "Bloquear Tag" (Lock Tag) de forma permanente!</strong>
  <p>Se você usar a função <em>Lock Tag</em>, o chip fica somente-leitura para sempre. Em vez disso, deixe desbloqueado (ou use proteção por senha na aba <em>Outros → Definir Senha</em>), assim você pode regravar a tag caso o cliente mude de link ou se quiser usar uma placa de demonstração para vários clientes!</p>
</div>

<h4>Passo 3: Sempre inclua o QR Code impresso junto com o NFC</h4>
<p>Gere um QR Code apontando para o mesmo link (no próprio Canva ao montar a arte da placa). Assim, 85% dos clientes usam a aproximação NFC e os 15% com celulares antigos apontam a câmera para o QR Code!</p>
"""
            },
            {
                "num": 4,
                "module": "Módulo 4 • Venda no WhatsApp & Balcão",
                "title": "Abordagem à Distância com VSL vs. Demonstração Presencial Matadora",
                "duration": "06 min",
                "summary": "Duas formas de fechar vendas todos os dias: pelo WhatsApp enviando a VSL pronta ou entrando no estabelecimento com uma placa de amostra.",
                "content_html": """
<h4>Estratégia 1: Venda 100% pelo WhatsApp usando o MapaLeads + VSL</h4>
<p>Filtre empresas com menos de 40 avaliações na sua cidade ou em cidades vizinhas. Envie a mensagem de diagnóstico mostrando quantas avaliações o concorrente líder tem e anexe a <strong>VSL Pronta (<code>vsl-nfc.mp4</code>)</strong>. O vídeo mostra visualmente o celular encostando na placa de acrílico e as 5 estrelas abrindo na tela. Você fecha pelo WhatsApp, recebe 50% no Pix e envia a placa por Motoboy (na sua cidade) ou Correios/Mini Envios (para todo o Brasil)!</p>

<h4>Estratégia 2: A Técnica Presencial do "Teste no Celular do Dono" (Conversão de 70%)</h4>
<p>Leve <strong>1 plaquinha de amostra</strong> na mochila. Antes de entrar na clínica, barbearia ou restaurante, abra o app <em>NFC Tools</em> na calçada e <strong>grave em 10 segundos o link de avaliação daquela empresa específica</strong> na sua placa de amostra. Entre, peça para falar com o gerente/dono e diga:</p>
<p><em>"Oi [Nome], fiz um protótipo configurado para a sua empresa testar. Desbloqueia seu celular rapidinho e encosta ele aqui nessa placa."</em></p>
<p>Quando o celular dele vibra e abre a tela de avaliação 5 estrelas da própria empresa dele em 1 segundo, os olhos dele brilham e a única pergunta que ele faz é: <strong>"Quanto custa pra deixar essa aqui comigo?"</strong></p>
"""
            },
            {
                "num": 5,
                "module": "Módulo 5 • Kits Multi-Placas & Upsell",
                "title": "Como Triplicar o Ticket Vendendo o Kit Balcão 3 em 1 (Google + Pix + Wi-Fi)",
                "duration": "06 min",
                "summary": "Aprenda a oferecer o Kit de 3 placas para o mesmo cliente e elevar o pedido de R$ 150 para R$ 390 com custo adicional de apenas R$ 28.",
                "content_html": """
<h4>Por que vender 1 placa de R$ 150 se você pode vender o Kit de 3 Placas por R$ 350 a R$ 450?</h4>
<p>No app <strong>NFC Tools</strong> (aba <em>Escrever → Adicionar Registro</em>), além de links do Google, você pode gravar:</p>
<ul>
  <li><strong>Placa 1 — Avalie-nos no Google 5⭐:</strong> Fica na recepção ou mesa de atendimento.</li>
  <li><strong>Placa 2 — Wi-Fi Automático para Clientes:</strong> No NFC Tools, escolha o registro <strong>"Rede Wi-Fi"</strong>, digite o nome do Wi-Fi (SSID) e a senha da loja. Quando o cliente encosta o celular, ele conecta no Wi-Fi sem precisar perguntar a senha para a atendente!</li>
  <li><strong>Placa 3 — Instagram + Catálogo WhatsApp (ou Pix):</strong> Quando o cliente encosta, abre o Biossite com chave Pix, Instagram e WhatsApp da loja.</li>
</ul>
<p><strong>Ancoragem de Preço na Proposta:</strong><br>
• 1 Placa Individual Google 5⭐ = <strong>R$ 150,00</strong><br>
• 2 Placas (Google 5⭐ + Instagram/WhatsApp) = <strong>R$ 247,00</strong><br>
• Kit Balcão Completo 3 Placas (Google + Wi-Fi Automático + Pix/Instagram) + Otimização Express da Ficha = <strong>R$ 397,00</strong> (70% dos empresários escolhem a opção de R$ 247 ou R$ 397!)</p>
"""
            }
        ],
        "delivery_guide": """MANUAL TÉCNICO DE PRODUÇÃO E ENTREGA — PLAQUINHAS NFC + QR CODE

1. LISTA DE MATERIAIS PARA COMEÇAR (INVESTIMENTO INICIAL < R$ 100)
   • 10 Displays de Acrílico em L ou T (medida 10x15cm ou 10x10cm, espessura 2mm) — Mercado Livre / Shopee.
   • 20 Etiquetas Adesivas NFC Chip NXP NTAG215 (25mm redonda, 13.56 MHz) — Mercado Livre / Shopee / AliExpress.
   • Impressão da arte em Papel Fotográfico Glossy 180g ou Vinil Adesivo (gráfica rápida local: ~R$ 2,50 por folha A4 que cabe 2 artes 10x15cm).

2. EXTRAÇÃO DO LINK DIRETO DE AVALIAÇÃO (SEM ERRO)
   • Opção 1 (Pelo painel do cliente): business.google.com → Botão "Pedir avaliações" → Copiar link (https://g.page/r/.../review).
   • Opção 2 (Pública via Place ID): Acesse developers.google.com/maps/documentation/javascript/examples/places-placeid-finder → busque o nome e endereço da empresa → copie o Place ID → monte a URL: https://search.google.com/local/writereview?placeid=PLACE_ID

3. GRAVAÇÃO DO CHIP NO APP "NFC TOOLS" (ANDROID OU IPHONE)
   • Abra o NFC Tools → Aba "Escrever" (Write) → "Adicionar um registro" (Add a record) → "URL / URI".
   • Cole a URL completa da avaliação do Google (certifique-se de que começa com https://) e confirme em OK.
   • Clique em "Escrever" e encoste o verso do celular na etiqueta NFC até exibir "Gravação concluída com sucesso!".
   • Teste imediatamente fechando o app e encostando o celular desbloqueado na tag para confirmar que a tela das 5 estrelas do Google abre direto.

4. CRIAÇÃO DA ARTE NO CANVA (10x15cm)
   • Topo: Logotipo da empresa do cliente + Chamada "Gostou do nosso atendimento? Avalie-nos em 5 segundos!".
   • Centro: Ícone de Aproximação Contactless ("Encoste seu celular aqui") + QR Code gerado com o mesmo link ("Ou aponte a câmera").
   • Base: 5 Estrelas Douradas + Logo do Google.
   • Cole a etiqueta adesiva NFC no verso do papel exatamente atrás do ícone de aproximação e insira no display de acrílico.

5. ENTREGA COM "SCRIPT DE BALCÃO" PARA A EQUIPE DO CLIENTE
   • Entregue junto um cartãozinho com a frase para os funcionários falarem no fim do atendimento:
     "Fulano, se você gostou do meu atendimento hoje, encosta seu celular aqui nessa plaquinha por 2 segundos pra me dar 5 estrelas no Google? Me ajuda demais aqui na empresa!" (Isso multiplica por 5x o número de avaliações diárias!).""",
        "pricing_tiers": [
            {
                "name": "Placa Unitária Google 5⭐",
                "badge": "Venda Rápida",
                "cost": "R$ 15,00 (Acrílico + NTAG215 + Impressão)",
                "setup_price": "R$ 147 a R$ 179",
                "monthly_price": "Venda única",
                "profit_margin": "~90% de margem (R$ 132 a R$ 164 líquido)",
                "deliverables": [
                    "1 Display de Acrílico 10x15cm personalizado com a logo da empresa",
                    "Chip NFC NXP NTAG215 configurado + QR Code espelho de alta leitura",
                    "Redirecionamento direto para a janela de 5 estrelas do Google Maps",
                    "Cartão com Script de Balcão para a recepção/atendentes"
                ]
            },
            {
                "name": "Kit Duplo Recepção & Caixa",
                "badge": "Mais Vendido ★",
                "cost": "R$ 29,00 (2 Placas Completas)",
                "setup_price": "R$ 247 a R$ 297",
                "monthly_price": "Venda única",
                "profit_margin": "~89% de margem (R$ 218 a R$ 268 líquido)",
                "deliverables": [
                    "2 Displays de Acrílico NFC + QR Code (Ex: 1 para Avaliação Google + 1 para Instagram/Pix ou 2 guichês)",
                    "Personalização com as cores e logotipo do estabelecimento",
                    "Configuração do Link Oficial de Avaliação + Teste presencial/vídeo",
                    "Garantia de funcionamento vitalício do chip sem precisar de bateria"
                ]
            },
            {
                "name": "Kit Balcão PRO (3 Placas + Setup GMN)",
                "badge": "Lucro Máximo",
                "cost": "R$ 44,00 (3 Placas Completas)",
                "setup_price": "R$ 447 a R$ 590",
                "monthly_price": "Opcional R$ 197/mês (Gestão GMN)",
                "profit_margin": "~91% de margem (R$ 403 a R$ 546 líquido)",
                "deliverables": [
                    "3 Displays NFC + QR Code (Avaliação Google 5⭐ + Wi-Fi Automático + Pix/Catálogo)",
                    "Otimização Express da Ficha do Google Meu Negócio (Categorias + Fotos + Respostas)",
                    "Treinamento prático de 5 minutos para a equipe bater recorde de avaliações em 30 dias"
                ]
            }
        ],
        "checklist": [
            "Filtrar no MapaLeads empresas com atendimento presencial (clínicas, barbearias, restaurantes, lojas) e poucas avaliações",
            "Verificar quantas avaliações o concorrente nº 1 da cidade possui para usar como gancho na abordagem",
            "Enviar mensagem de abordagem + Vídeo VSL (vsl-nfc.mp4) demonstrando a placa funcionando na prática",
            "Oferecer as 3 opções de pacote (1 Placa R$ 147 | 2 Placas R$ 247 | Kit 3 Placas + Setup GMN R$ 447)",
            "Receber 50% de sinal via Pix + logotipo do cliente pelo WhatsApp",
            "Extrair o link direto de avaliação 5 estrelas do Google Maps da empresa e testar no navegador",
            "Montar a arte personalizada no Canva (10x15cm) incluindo o QR Code espelho e imprimir",
            "Gravar a tag NTAG215 pelo app NFC Tools (Aba Escrever → URL/URI) e testar aproximando o celular",
            "Entregar a placa + Cartão com o Script de Balcão para a equipe e receber os 50% restantes"
        ],
        "script_approach": """[MENSAGEM 1 — ABORDAGEM DIRETA COM GATILHO DE CURIOSIDADE]
Olá, tudo bem? Aqui é o [Seu Nome].
Estou falando com o responsável pela *[Nome da Empresa]*?
Vi que o atendimento de vocês aqui em *[Cidade]* é muito elogiado, mas muitas vezes o cliente vai embora satisfeito e esquece de avaliar vocês no Google (hoje vocês estão com *[X]* avaliações, enquanto outros locais da região já passaram de 120).
Posso te mostrar em um vídeo de 25 segundos a Plaquinha por Aproximação que faz o cliente te avaliar com 5 estrelas em 3 segundos ainda no balcão?

[MENSAGEM 2 — ENVIE A VSL (vsl-nfc.mp4) + A OFERTA]
Olha que prático o funcionamento nesse vídeo acima 👆
Nós produzimos o *Display em Acrílico Personalizado com a Logo da [Nome da Empresa]* equipado com Chip NFC + QR Code:
📲 O cliente só encosta o celular na placa (ou aponta a câmera) e já abre *direto na tela de 5 estrelas do Google de vocês*, sem precisar digitar nada!
⚡ Não usa bateria, não tem mensalidade e dura para sempre.

Estamos entregando aqui em *[Cidade]* com condição especial:
• *1 Placa Personalizada:* R$ 147,00
• *Kit 2 Placas (Ex: Avaliação Google + Pix ou Instagram):* R$ 247,00
Quer que eu monte uma prévia da arte com a logo da *[Nome da Empresa]* sem compromisso para você ver como fica linda no balcão?""",
        "script_followup": """[FOLLOW-UP 1 — 24 HORAS DEPOIS (GATILHO DA PRÉVIA VISUAL)]
Oi! Peguei a logo da *[Nome da Empresa]* e montei o rascunho de como fica o Display NFC de Avaliação 5 Estrelas do Google personalizado nas cores de vocês.
Posso te mandar a imagem aqui para você dar uma nota de 0 a 10?

[FOLLOW-UP 2 — 72 HORAS DEPOIS (FECHAMENTO DE LOTE DA SEMANA)]
Fala! Estou fechando o lote de produção e gravação das Plaquinhas NFC desta semana aqui da região.
Consegui segurar o valor promocional (1 placa por R$ 147 ou o par por R$ 247 com frete/entrega inclusa).
Quer que eu inclua a da *[Nome da Empresa]* nesse lote para você já colocar no balcão nos próximos dias?

[ROTEIRO DE ÁUDIO DE 25 SEGUNDOS]
"Fala, tudo bem? Cara, todo cliente que sai satisfeito aí da sua empresa e não deixa avaliação no Google é dinheiro que fica na mesa, porque quem pesquisa no Google Maps sempre escolhe o local com mais estrelas. Com essa plaquinha no balcão, a sua atendente só fala 'encosta o celular aqui 2 segundinhos' e pronto, já abre nas 5 estrelas. Me manda sua logo aqui que eu monto a prévia pra você ver agora!" """,
        "script_objections": """• "Eu mesmo posso imprimir um QR Code numa folha sulfite de graça!"
Resposta: "Com certeza! O problema é que papel colado com durex no balcão passa uma imagem amadora e o cliente tem preguiça de abrir a câmera, focar e clicar no link. O Display em Acrílico com chip NFC desperta a curiosidade ('encoste o celular aqui') — em 1 segundo a tela já abre sozinha e valoriza o visual da sua recepção."

• "Tem alguma mensalidade ou precisa carregar na tomada?"
Resposta: "Zero mensalidade e não usa bateria nem tomada! O chip NFC funciona por indução magnética do próprio celular quando encosta (a mesma tecnologia dos cartões de banco por aproximação). Você paga uma única vez e a placa funciona por anos."

• "Funciona tanto em iPhone quanto em Android?"
Resposta: "Sim, 100%! Todos os iPhones (a partir do XR) e celulares Android com NFC leem por aproximação instantaneamente sem precisar baixar nenhum aplicativo. E a placa também leva o QR Code impresso junto para atender qualquer modelo de celular."

• "E se meus clientes não souberem usar?"
Resposta: "Por isso entregamos junto o 'Script de Balcão' para sua equipe! Quando o atendente diz no final: 'Se gostou do meu atendimento, encosta seu celular aqui 2 segundinhos para me dar 5 estrelas?', 8 em cada 10 clientes fazem na hora com um sorriso no rosto." """,
        "proposal_script": """📋 *PEDIDO & ORÇAMENTO — DISPLAY ACRÍLICO INTELIGENTE NFC + QR CODE*
Cliente: *[Nome da Empresa]* | Cidade: *[Cidade]*

✨ *ESPECIFICAÇÕES DO PRODUTO:*
• Display de Balcão em Acrílico Cristal com arte em alta definição personalizada com a identidade visual da sua empresa;
• Chip Original NXP NTAG215 integrado (leitura instantânea por aproximação em iPhone e Android, sem bateria e sem mensalidade);
• QR Code espelho de alta precisão integrado ao design;
• Configuração direta para a página oficial de Avaliação 5 Estrelas do Google Maps da sua empresa;
• Bônus: Cartão com Roteiro de Abordagem de Balcão para sua equipe multiplicar as avaliações na primeira semana.

💰 *OPÇÕES DE PACOTE:*
1️⃣ *1 Placa NFC Google 5 Estrelas:* R$ 147,00
2️⃣ *Kit Duplo (2 Placas — Ex: Google 5⭐ + Instagram/Pix ou 2 Balcões):* R$ 247,00 *(Mais Vendido)*
3️⃣ *Kit Balcão Completo (3 Placas: Google 5⭐ + Wi-Fi Automático + Pix/Instagram) + Otimização Express da Ficha Google:* R$ 397,00

💳 *FORMA DE PAGAMENTO E PRAZO:*
• 50% na aprovação da arte via Pix e 50% na entrega/envio com vídeo de teste do chip gravado.
• Prazo de produção e entrega: 48 horas.

Qual das 3 opções fica melhor para o seu balcão hoje? Pode me enviar a sua logo por aqui para eu gerar a arte de aprovação!"""
    },

    # =========================================================================
    # CURSO 3 — ESTRUTURAÇÃO DE WHATSAPP BUSINESS PRO & CATÁLOGO
    # =========================================================================
    {
        "slug": "estrategia-whatsapp",
        "strategy_key": "whatsapp",
        "badge_label": "Curso 03 • WhatsApp Business PRO & Funil",
        "title": "Estruturação de WhatsApp Business PRO, Catálogo & Funil de Atendimento",
        "subtitle": "Transforme o WhatsApp amador de clínicas, lojas e prestadores de serviço em uma máquina de vendas com Catálogo Nativo, Etiquetas de CRM e Respostas Rápidas.",
        "ticket_range": "R$ 250 a R$ 697 setup + R$ 197/mês opcional",
        "thumbnail_url": "/static/img/academy/whatsapp-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-whatsapp.mp4",
        "course_duration": "5 Aulas • ~42 min",
        "vsl_video_url": "/static/video/sales-academy/vsl-whatsapp.mp4",
        "vsl_title": "VSL Pronta: Pare de Perder Orçamentos por Demora no WhatsApp",
        "vsl_duration": "00:25",
        "target_opp": "whatsapp",
        "sort_order": 3,
        "lessons": [
            {
                "num": 1,
                "module": "Módulo 1 • Diagnóstico da Dor",
                "title": "Por que Empresas Locais Perdem 40% das Vendas Dentro do Próprio WhatsApp",
                "duration": "08 min",
                "summary": "Entenda os 4 gargalos fatais no atendimento de pequenas e médias empresas e por que o dono paga na hora para organizar.",
                "content_html": """
<h4>O Ralo Invisível de Dinheiro no Atendimento Local</h4>
<p>Quase toda empresa local investe tempo ou dinheiro para fazer o cliente chamar no WhatsApp, mas quando o cliente manda <em>"Olá, qual o valor?"</em>, acontecem 4 erros fatais:</p>
<ol>
  <li><strong>Demora na Primeira Resposta:</strong> Pesquisas mostram que responder em até 5 minutos aumenta em <strong>9 vezes</strong> a chance de fechamento. Passou de 30 minutos, o cliente já fechou com o concorrente do Google Maps.</li>
  <li><strong>Falta de Catálogo Visual Nativo:</strong> A atendente digita preços soltos sem foto ou manda um PDF pesado de 25MB que o cliente não consegue abrir no 4G.</li>
  <li><strong>Atendente Digitando Tudo do Zero:</strong> Perde 3 horas por dia repetindo as mesmas explicações sobre endereço, formas de pagamento, preparo e garantias.</li>
  <li><strong>Zero Controle de Follow-up (O Cemitério de Orçamentos):</strong> O cliente pergunta o preço, diz <em>"Vou ver com meu marido e te aviso"</em>, a conversa desce na tela do WhatsApp e <strong>ninguém nunca mais cobra aquele orçamento</strong>!</li>
</ol>
"""
            },
            {
                "num": 2,
                "module": "Módulo 2 • Prospecção no MapaLeads",
                "title": "Como Filtrar e Auditar o WhatsApp do Lead Antes de Abordar",
                "duration": "08 min",
                "summary": "Como usar os filtros do MapaLeads PRO e checar em 15 segundos se o perfil comercial do cliente está amador.",
                "content_html": """
<h4>Como encontrar os leads ideais no MapaLeads PRO</h4>
<ol>
  <li>No <strong>CRM Kanban</strong>, filtre pela oportunidade <strong>"WhatsApp Business"</strong> ou filtre empresas com WhatsApp Verificado.</li>
  <li>Quando abrir a conversa do lead no WhatsApp, clique na foto de perfil dele para ver os dados da conta comercial.</li>
  <li>Verifique:
    <ul>
      <li>Ele usa WhatsApp comum (pessoal) em vez do WhatsApp Business?</li>
      <li>Se usa WhatsApp Business, o <strong>Catálogo está vazio</strong>?</li>
      <li>Falta horário de funcionamento, endereço clicável no mapa ou descrição profissional?</li>
      <li>Quando você manda a primeira mensagem, ele NÃO tem mensagem automática de saudação configurada?</li>
    </ul>
  </li>
</ol>
<p>Qualquer um desses 4 sinais é o gancho perfeito para você enviar a <strong>VSL Pronta (<code>vsl-whatsapp.mp4</code>)</strong> e oferecer a Estruturação Comercial em 24 horas!</p>
"""
            },
            {
                "num": 3,
                "module": "Módulo 3 • Catálogo & Perfil Blindado",
                "title": "Como Construir um Catálogo Nativo que Vende Sozinho no WhatsApp",
                "duration": "10 min",
                "summary": "A engenharia visual e de copy para cadastrar os 10 a 15 serviços/produtos principais dentro do WhatsApp Business.",
                "content_html": """
<h4>1. Configuração do Perfil Comercial de Autoridade</h4>
<ul>
  <li><strong>Foto de Perfil com Margem de Segurança:</strong> Logo centralizada com fundo limpo (1080×1080px).</li>
  <li><strong>Descrição Comercial em 3 Linhas:</strong> Especialidade + Prova Social/Diferencial + Chamada para o Catálogo abaixo.</li>
  <li><strong>Endereço com Pino no Mapa &amp; Horário Exato:</strong> Essencial para que a mensagem de ausência dispare automaticamente fora do expediente.</li>
</ul>

<h4>2. Engenharia do Catálogo Nativo (A "Landing Page" dentro do WhatsApp)</h4>
<p>Em <em>Ferramentas Comerciais → Catálogo</em>, organize os produtos/serviços em <strong>Coleções</strong> e cadastre os 10 a 15 itens mais lucrativos:</p>
<ul>
  <li><strong>Imagem Quadrada (1080×1080px):</strong> Com foto real do serviço/produto e um selo discreto com o benefício principal.</li>
  <li><strong>Título Claro + Preço ou Ancoragem:</strong> Se o preço for fixo, preencha o valor. Se depender de avaliação (ex: clínica/oficina), coloque no título <em>"(Solicite Avaliação)"</em> e detalhe os benefícios na descrição.</li>
  <li><strong>O Segredo no Atendimento:</strong> Ensine o atendente a usar o botão de <strong>Clipe/Anexo → Catálogo</strong> dentro da conversa para enviar o card interativo do serviço específico em 1 clique!</li>
</ul>
"""
            },
            {
                "num": 4,
                "module": "Módulo 4 • Funil de 5 Etiquetas & Atalhos",
                "title": "Implantando o CRM de 5 Etiquetas Coloridas + 12 Atalhos de Resposta Rápida (/)",
                "duration": "10 min",
                "summary": "O método de organização de funil que recupera de 20% a 35% dos orçamentos perdidos já na primeira semana.",
                "content_html": """
<h4>1. O Funil Visual de 5 Etiquetas Coloridas (CRM Gratuito Nativo)</h4>
<p>Configure em <em>Ferramentas Comerciais → Etiquetas</em> exatamente estas 5 etapas na ordem do funil:</p>
<div class="sa-lesson-grid">
  <div class="sa-lesson-card">
    <strong>🟡 1. Novo Lead / Triagem</strong>
    <p>Cliente acabou de chamar e ainda não recebeu orçamento ou explicação completa.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>🔵 2. Orçamento Enviado (Cobrar!)</strong>
    <p>A etiqueta mais lucrativa da empresa! Todo contato que recebeu preço fica azul até fechar ou desistir.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>🟣 3. Aguardando Pix / Agendamento</strong>
    <p>Cliente disse que vai fechar, falta apenas confirmar o pagamento ou horário.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>🟢 4. Cliente Fechado (Pós-Venda)</strong>
    <p>Venda concluída! Usado para pedir avaliação 5 estrelas no Google e fazer campanha de recompra.</p>
  </div>
</div>

<h4>2. Os 12 Atalhos de Resposta Rápida (Tecla <code>/</code>)</h4>
<p>Configure em <em>Ferramentas Comerciais → Respostas Rápidas</em> os atalhos que economizam 2 horas por dia da equipe:</p>
<ul>
  <li><code>/boasvindas</code> — Saudação consultiva + pergunta de qualificação para entender a necessidade do cliente.</li>
  <li><code>/apresentacao</code> — Quem somos, diferenciais e prova social em 4 linhas + áudio gravado.</li>
  <li><code>/orcamento</code> — Estrutura de apresentação de valor (Benefícios primeiro → Preço depois → Pergunta de fechamento).</li>
  <li><code>/pix</code> — Dados bancários, chave Pix e link de parcelamento no cartão.</li>
  <li><code>/endereco</code> — Endereço completo, ponto de referência, estacionamento e link do Google Maps.</li>
  <li><code>/followup1</code> — Mensagem elegante de acompanhamento 24h após o orçamento (<em>"Ficou alguma dúvida sobre o orçamento que te enviei ontem?"</em>).</li>
  <li><code>/followup2</code> — Mensagem de condição especial/escassez 72h após o orçamento.</li>
  <li><code>/avaliacao</code> — Pedido pós-venda com o link direto das 5 estrelas do Google Meu Negócio.</li>
</ul>
"""
            },
            {
                "num": 5,
                "module": "Módulo 5 • Entrega & Upsell",
                "title": "A Rotina das 16h30 que Faz o Cliente Amar Seu Trabalho + Upsell Recorrente",
                "duration": "06 min",
                "summary": "Como entregar o projeto via acesso remoto ou presencialmente em 1 hora e vender acompanhamento mensal.",
                "content_html": """
<h4>A "Rotina das 16h30" que Gera Retorno na Primeira Semana</h4>
<p>Ao finalizar a configuração do WhatsApp Business do seu cliente, ensine um único hábito de 15 minutos para o atendente/vendedor dele:</p>
<p><strong>"Todos os dias às 16h30, clique em Etiquetas → 🔵 Orçamento Enviado, abra os contatos que estão lá desde ontem e envie o atalho <code>/followup1</code>."</strong></p>
<p>Só essa rotina recupera de 3 a 10 vendas por semana que antes morriam esquecidas! Quando o empresário vê dinheiro entrando no caixa em 48 horas graças às suas etiquetas e scripts, você oferece facilmente a <strong>Otimização do Google Meu Negócio</strong> ou a <strong>Plaquinha NFC</strong> como próximo passo!</p>
"""
            }
        ],
        "delivery_guide": """MANUAL TÉCNICO DE ENTREGA — ESTRUTURAÇÃO WHATSAPP BUSINESS PRO (60 A 90 MINUTOS)

1. PREPARAÇÃO & BRIEFING RÁPIDO (15 MIN)
   • Solicite ao cliente: Logotipo, horário de funcionamento, endereço, lista dos 10 serviços/produtos mais vendidos (com foto e preço/descrição), chave Pix e as 5 dúvidas mais comuns dos clientes.
   • Como acessar para configurar: Você pode configurar conectando o WhatsApp Web do cliente temporariamente no seu navegador (via QR Code em web.whatsapp.com — 90% das configurações de Catálogo, Etiquetas e Respostas Rápidas funcionam direto pelo WhatsApp Web!) ou via AnyDesk / presencialmente no celular da empresa.

2. CONFIGURAÇÃO DO PERFIL COMERCIAL
   • Atualize Foto de Perfil, Nome Comercial, Categoria, Descrição persuasiva com CTA, Endereço com pino no mapa, Horário de atendimento por dia da semana, E-mail e Link do site/Instagram.

3. CRIAÇÃO DO CATÁLOGO NATIVO (10 A 15 ITENS)
   • Padronize as fotos em formato quadrado (1080x1080px) no Canva com visual limpo.
   • Cadastre Título, Preço (ou faixa de valor), Descrição estruturada com bullet points de benefícios e link de ação.

4. IMPLANTAÇÃO DO FUNIL DE 5 ETIQUETAS (CRM NATIVO)
   • Crie as etiquetas:
     1. 🟡 Novo Lead / Triagem
     2. 🔵 Orçamento Enviado (Fazer Follow-up)
     3. 🟣 Aguardando Pagamento / Agendamento
     4. 🟢 Cliente Fechado (Pedir Avaliação 5⭐)
     5. 🔴 Reativação / Oferta Futura

5. AUTOMAÇÕES NATIVAS + 10 RESPOSTAS RÁPIDAS (/)
   • Ative a Mensagem de Saudação (para novos contatos ou após 14 dias sem interação).
   • Ative a Mensagem de Ausência (programada para disparar "Fora do horário comercial").
   • Cadastre os 10 atalhos "/" (/boasvindas, /orcamento, /pix, /endereco, /garantia, /followup1, /followup2, /avaliacao, etc.).

6. TREINAMENTO EXPRESS DA EQUIPE (10 MIN)
   • Grave um vídeo curto de 5 minutos (ou mostre ao vivo) ensinando como enviar itens do catálogo na conversa, como usar a tecla "/" e como executar a "Rotina das 16h30" na etiqueta Azul (Orçamento Enviado).""",
        "pricing_tiers": [
            {
                "name": "Setup WhatsApp Express",
                "badge": "Entrada Rápida",
                "cost": "R$ 0,00 (1h do seu tempo)",
                "setup_price": "R$ 250 a R$ 350",
                "monthly_price": "Venda única",
                "profit_margin": "100% de margem líquida",
                "deliverables": [
                    "Configuração completa do Perfil Comercial (Descrição, Mapa, Horários)",
                    "Mensagem de Saudação e Ausência Inteligentes configuradas",
                    "8 Atalhos de Respostas Rápidas (/) personalizados para o negócio",
                    "Implantação do Funil de 5 Etiquetas Coloridas no WhatsApp"
                ]
            },
            {
                "name": "WhatsApp PRO + Catálogo & Funil",
                "badge": "Mais Vendido ★",
                "cost": "R$ 0,00 (1h30 do seu tempo)",
                "setup_price": "R$ 497 a R$ 650",
                "monthly_price": "Venda única",
                "profit_margin": "100% de margem líquida",
                "deliverables": [
                    "Tudo do Setup Express + Criação de Catálogo Nativo com até 12 Produtos/Serviços",
                    "Design padronizado das fotos do catálogo no Canva (1080x1080px)",
                    "12 Scripts de Respostas Rápidas + Roteiro de Follow-up de Orçamentos",
                    "Treinamento prático de 15 min para a equipe/secretária recuperar vendas"
                ]
            },
            {
                "name": "Máquina Comercial (WhatsApp + Biossite + GMN)",
                "badge": "Pacote Completo",
                "cost": "R$ 0,00 (3h do seu tempo)",
                "setup_price": "R$ 997 a R$ 1.290",
                "monthly_price": "R$ 197 a R$ 297/mês",
                "profit_margin": "100% de margem + Recorrência",
                "deliverables": [
                    "Estruturação Completa do WhatsApp Business PRO + Catálogo + Funil de Etiquetas",
                    "Biossite / Página de Captura levando leads qualificados para o WhatsApp",
                    "Otimização da Ficha do Google Meu Negócio integrada ao WhatsApp",
                    "Atualização mensal de campanhas, catálogo e scripts de reativação de base"
                ]
            }
        ],
        "checklist": [
            "Filtrar no MapaLeads empresas com atendimento intenso via WhatsApp (clínicas, oficinas, lojas, estética, serviços)",
            "Abrir o perfil do WhatsApp do lead e verificar se falta catálogo, mensagem automática ou descrição",
            "Enviar a abordagem consultiva + VSL Pronta (vsl-whatsapp.mp4) focando nos orçamentos perdidos",
            "Coletar o briefing rápido (logo, horários, 10 serviços principais, preços, Pix e dúvidas frequentes)",
            "Conectar via WhatsApp Web (ou AnyDesk) para configurar Perfil Comercial, Horários e Mensagens Automáticas",
            "Criar e subir as artes quadradas (1080x1080px) dos 10 a 12 serviços principais no Catálogo Nativo",
            "Configurar as 5 Etiquetas Coloridas do Funil e os 10+ Atalhos de Resposta Rápida (/)",
            "Entregar o guia da 'Rotina das 16h30' para cobrança diária da etiqueta Azul (Orçamento Enviado)",
            "Fazer pós-venda após 7 dias perguntando quantos orçamentos foram recuperados e oferecer a Plaquinha NFC"
        ],
        "script_approach": """[MENSAGEM 1 — DIAGNÓSTICO DO ATENDIMENTO]
Olá, tudo bem? Aqui é o [Seu Nome].
Estou falando com o responsável pela *[Nome da Empresa]*?
Cliquei no contato de vocês pelo Google e notei que o WhatsApp da empresa ainda não está com a *Vitrine de Catálogo Nativo* nem com a *Triagem Automática de Orçamentos* ativadas.
Posso te mandar um vídeo de 25 segundos mostrando como empresas de *[Cidade]* estão recuperando até 30% dos clientes que pedem preço e somem no WhatsApp?

[MENSAGEM 2 — ENVIE A VSL (vsl-whatsapp.mp4) + EXPLICAÇÃO PRÁTICA]
Dá uma olhada nesse vídeo rápido acima 👆
Hoje, quando o cliente pede orçamento no WhatsApp e diz *"vou pensar"*, a conversa desce na tela e acaba esquecida.
Nós fazemos a *Estruturação Comercial Completa do seu WhatsApp Business em 24 horas* (no seu próprio número atual, sem perder nenhuma conversa):
✅ *Catálogo Visual Nativo:* Seus principais serviços/produtos com fotos e botões dentro do chat;
✅ *Atalhos de 1 Clique (/):* Sua equipe responde orçamentos, endereço, Pix e dúvidas em 3 segundos;
✅ *Funil de 5 Etiquetas Coloridas:* Separa quem recebeu orçamento para cobrar automaticamente todo fim de tarde.

O investimento é único (sem mensalidade de robô caro). Posso te mandar os detalhes de como entregamos aí na *[Nome da Empresa]*?""",
        "script_followup": """[FOLLOW-UP 1 — 24 HORAS DEPOIS]
Oi! Passando para te fazer uma pergunta rápida: hoje, de cada 10 pessoas que chamam no WhatsApp da *[Nome da Empresa]* perguntando preço, quantas acabam parando de responder depois que recebem o valor?
Nosso Funil de Etiquetas + Scripts de Follow-up resolve exatamente esse buraco no atendimento em 24 horas. Quer ver o escopo?

[FOLLOW-UP 2 — 72 HORAS DEPOIS]
Fala! Estou com horário na agenda amanhã à tarde para fazer a configuração remota do WhatsApp Business PRO (leva cerca de 1 hora e você não fica sem usar o aparelho).
Se fecharmos hoje, incluo de bônus o design de 10 cards profissionais para o seu Catálogo Nativo do WhatsApp. Vamos deixar seu atendimento redondo esta semana?

[ROTEIRO DE ÁUDIO DE 30 SEGUNDOS]
"Fala, tudo bem? Cara, o maior desperdício de qualquer empresa hoje é o cliente que chama no WhatsApp, pergunta o preço, visualiza e some porque ninguém faz o acompanhamento certo. Eu configuro dentro do seu próprio WhatsApp Business um catálogo visual profissional, atalhos de resposta em 1 clique e um funil de etiquetas coloridas que mostra exatamente quem precisa ser cobrado todo dia às 16h. É um serviço rápido, barato e que se paga na primeira semana!" """,
        "script_objections": """• "Vou precisar trocar de número ou pagar mensalidade de plataforma de chatbot?"
Resposta: "Nenhum dos dois! Nós estruturamos tudo 100% dentro do seu próprio aplicativo oficial do WhatsApp Business e no seu número atual. Você não perde nenhuma conversa antiga e não fica preso a mensalidades de sistemas externos."

• "Não quero robô engessado que irrita o cliente com digite 1, digite 2..."
Resposta: "Perfeito, nós também somos contra aqueles robôs frios que afastam o cliente! Nossa estrutura humaniza e acelera o atendimento: a saudação acolhe na hora, o catálogo mostra seus serviços com fotos reais e os atalhos '/' permitem que você ou sua atendente enviem respostas completas e persuasivas em 2 segundos."

• "Minha secretária/equipe não entende muito de tecnologia."
Resposta: "Fique tranquilo, justamente por ser dentro do próprio WhatsApp que ela já usa todo dia, é super simples! Além de deixar tudo configurado, eu entrego um vídeo de 5 minutos ensinando a usar a tecla '/' e as etiquetas coloridas." """,
        "proposal_script": """📋 *PROPOSTA COMERCIAL — ESTRUTURAÇÃO WHATSAPP BUSINESS PRO & FUNIL DE VENDAS*
Empresa: *[Nome da Empresa]* | Cidade: *[Cidade]*

🎯 *OBJETIVO:*
Profissionalizar o atendimento no WhatsApp, eliminar a demora nas respostas e implantar um funil visual de acompanhamento para recuperar orçamentos que hoje são perdidos.

✅ *O QUE ENTREGAMOS CONFIGURADO NO SEU NÚMERO ATUAL:*
1. *Perfil Comercial Blindado:* Descrição persuasiva, horários automáticos, localização no mapa e links;
2. *Catálogo Nativo de Alta Conversão:* Design e cadastro de até 12 serviços/produtos com fotos quadradas padronizadas e copy de vendas;
3. *Automação de Recepção:* Mensagem de Saudação imediata e Mensagem de Ausência inteligente fora do expediente;
4. *Arsenal de 12 Respostas Rápidas (/):* Atalhos prontos para orçamento, apresentação, Pix, endereço, quebra de objeções e pós-venda;
5. *CRM de 5 Etiquetas Coloridas + Rotina de Follow-up:* Método prático para acompanhar e fechar todos os orçamentos abertos.

💰 *INVESTIMENTO ÚNICO (SEM MENSALIDADE DE SISTEMA):*
• *Pacote Completo WhatsApp PRO + Catálogo + Treinamento:* R$ 497,00 (50% no início + 50% na entrega em 24h via Pix).

Posso te enviar o checklist rápido de 5 itens para começarmos a configuração hoje?"""
    },

    # =========================================================================
    # CURSO 4 — CARDÁPIO DIGITAL SEM TAXAS + QR CODE DE MESA
    # =========================================================================
    {
        "slug": "estrategia-cardapio",
        "strategy_key": "cardapio",
        "badge_label": "Curso 04 • Cardápio Digital Sem Taxas",
        "title": "Cardápio Digital Sem Taxas + Engenharia de Menu & QR Code de Mesa",
        "subtitle": "Mostre a restaurantes, pizzarias, hamburguerias e açaí como economizar até R$ 4.000/mês de comissões de apps com um cardápio próprio integrado ao WhatsApp.",
        "ticket_range": "R$ 350 a R$ 897 setup + R$ 97 a R$ 147/mês",
        "thumbnail_url": "/static/img/academy/cardapio-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-cardapio.mp4",
        "course_duration": "5 Aulas • ~45 min",
        "vsl_video_url": "/static/video/sales-academy/vsl-cardapio.mp4",
        "vsl_title": "VSL Pronta: Pare de Perder até 27% do seu Faturamento em Taxas de Apps",
        "vsl_duration": "00:23",
        "target_opp": "cardapio",
        "sort_order": 4,
        "lessons": [
            {
                "num": 1,
                "module": "Módulo 1 • A Dor do Food Service",
                "title": "A Matemática Sangrenta dos Apps (12% a 27%) vs. Canal Próprio Taxa Zero",
                "duration": "09 min",
                "summary": "Entenda como fazer a conta que deixa qualquer dono de restaurante, pizzaria ou hamburgueria de olhos arregalados.",
                "content_html": """
<h4>1. O Sócio Mais Caro do Restaurante</h4>
<p>Todo dono de restaurante, pizzaria, hamburgueria, sushi ou açaí tem uma dor aguda: <strong>trabalhar 14 horas por dia para entregar de 12% a 27% do faturamento bruto para aplicativos de marketplace</strong>, além de esperar semanas pelo repasse e não ter acesso ao telefone do cliente para fazer remarketing.</p>

<div class="sa-callout sa-callout-emerald">
  <strong><i class="fa-solid fa-sack-dollar"></i> A Conta que Fecha a Venda em 2 Minutos:</strong>
  <ul>
    <li>Se uma hamburgueria ou pizzaria vende <strong>R$ 25.000/mês</strong> pelo marketplace (com taxa média + pagamento online de ~20%), ela paga <strong>R$ 5.000 todo mês (R$ 60.000 por ano!)</strong> em comissões.</li>
    <li>Você NÃO vai pedir para ele sair do iFood! Você vai dizer: <em>"Continue usando o iFood como vitrine para conquistar a 1ª compra do cliente novo, mas vamos converter 30% a 50% dos seus clientes recorrentes para pedirem direto no seu Cardápio Digital Próprio com 0% de comissão!"</em></li>
    <li>Só de migrar 30% dos pedidos para o cardápio próprio, o dono <strong>economiza R$ 1.500 todo mês</strong>. Cobrar R$ 497 de montagem + R$ 97/mês de manutenção parece troco perto dessa economia!</li>
  </ul>
</div>
"""
            },
            {
                "num": 2,
                "module": "Módulo 2 • Prospecção & Horário Certo",
                "title": "Como Filtrar Restaurantes no MapaLeads e o Horário de Ouro para Abordar",
                "duration": "08 min",
                "summary": "Nunca aborde um restaurante às 20h da sexta-feira! Aprenda os horários exatos e os gatilhos que geram resposta imediata.",
                "content_html": """
<h4>1. Filtrando os Melhores Alvos no MapaLeads PRO</h4>
<p>Busque por: <em>Pizzarias, Hamburguerias, Açaí, Sushi / Comida Japonesa, Marmitaria, Doceria, Padaria, Espetinho e Lanchonetes</em>. No CRM Kanban, aplique o filtro <strong>"Cardápio Digital"</strong>.</p>
<p>Os melhores alvos são estabelecimentos que:</p>
<ul>
  <li>Não possuem link de site na ficha do Google Meu Negócio;</li>
  <li>Colocam apenas o link do iFood na bio do Instagram (ou seja, estão pagando até 27% de comissão até sobre os clientes que já são seguidores deles no Instagram!);</li>
  <li>Ainda atendem no WhatsApp mandando foto de cardápio em JPEG/PDF e anotando pedido na mão (o que trava o atendimento na sexta e sábado à noite).</li>
</ul>

<h4>2. O Horário de Ouro para Falar com Donos de Food Service</h4>
<ul>
  <li><strong>Operações Noturnas (Pizzarias, Hamburguerias, Sushi):</strong> Aborde entre <strong>14h00 e 17h15</strong> (quando o dono está fazendo compras/pré-preparo com o celular na mão, antes da correria da cozinha começar às 18h).</li>
  <li><strong>Operações de Almoço (Restaurantes, Marmitarias):</strong> Aborde entre <strong>09h00 e 10h30</strong> ou entre <strong>15h00 e 17h00</strong>.</li>
</ul>
"""
            },
            {
                "num": 3,
                "module": "Módulo 3 • Engenharia de Cardápio",
                "title": "Engenharia de Menu Digital: Como Aumentar o Ticket Médio em 25%",
                "duration": "10 min",
                "summary": "Não entregue apenas uma lista de preços! Aplique os 4 gatilhos psicológicos de engenharia de cardápio que aumentam o valor de cada pedido.",
                "content_html": """
<h4>Os 4 Segredos da Engenharia de Cardápio Aplicada ao Digital</h4>
<ol>
  <li><strong>O Efeito da Primazia (Topo da Categoria):</strong> Os 3 primeiros itens de cada categoria recebem 60% dos cliques. Nunca coloque o item mais barato no topo! Crie a categoria <em>"⭐ Mais Pedidos da Casa (Combos)"</em> no topo com os 3 produtos de maior margem de lucro.</li>
  <li><strong>Trava Inteligente de Opcionais e Adicionais (Cross-Sell Automático):</strong> Ao clicar em um lanche ou pizza, o cardápio digital deve abrir obrigatoriamente as perguntas:
    <ul>
      <li><em>"Deseja turbinar seu pedido?"</em> (+ Bacon crocante R$ 5 | + Cheddar cremoso R$ 6 | + Borda recheada R$ 12)</li>
      <li><em>"Vai uma bebida bem gelada para acompanhar?"</em> (Coca-Cola 2L, Lata, Suco)</li>
      <li><em>"Sobremesa com desconto no combo?"</em> (Brownie / Petit Gateau)</li>
    </ul>
    Um garçom ou atendente ocupado no WhatsApp esquece de oferecer adicional; o Cardápio Digital oferece em <strong>100% dos pedidos</strong>!
  </li>
  <li><strong>Descrições Sensoriais que Dão Água na Boca:</strong> Substitua <em>"X-Bacon: pão, carne, queijo e bacon"</em> por <em>"Pão brioche selado na manteiga, blend artesanal 160g suculento, duplo cheddar derretido e fatias generosas de bacon crocante"</em>.</li>
  <li><strong>Fotos com Fundo Quente e Iluminação:</strong> Você pode melhorar as fotos atuais do cliente em segundos ajustando brilho, contraste e saturação no Canva antes de subir no cardápio.</li>
</ol>
"""
            },
            {
                "num": 4,
                "module": "Módulo 4 • Ferramentas & Execução",
                "title": "Plataformas White-Label / Gratuitas e Como Montar tudo + QR de Mesa em 2h",
                "duration": "10 min",
                "summary": "Quais ferramentas usar para entregar um cardápio digital com carrinho WhatsApp, cálculo de frete por bairro, Pix e QR Code de mesa sem programar.",
                "content_html": """
<h4>Quais plataformas usar para montar o Cardápio Digital do seu cliente?</h4>
<p>Você não precisa programar nada do zero. Existem 3 caminhos excelentes no mercado brasileiro:</p>
<div class="sa-lesson-grid">
  <div class="sa-lesson-card">
    <strong>1. Plataformas Freemium / Sem Comissão (OlaClick, Cardapio.ai, Menudino, Goomer)</strong>
    <p>Possuem planos gratuitos ou muito baratos. Você cria a conta para o restaurante, configura a identidade visual, cadastra todas as categorias, adicionais, taxas de entrega por bairro e chave Pix. O cliente monta o carrinho e o pedido chega formatado no WhatsApp da loja com troco, endereço e código Pix!</p>
  </div>
  <div class="sa-lesson-card">
    <strong>2. Sistemas White-Label de Revenda</strong>
    <p>Se você fechar mais de 5 restaurantes, pode assinar uma plataforma white-label de cardápio digital (custo ~R$ 99/mês para dezenas de lojas) e cobrar R$ 97 a R$ 147/mês de cada restaurante na sua própria marca!</p>
  </div>
</div>

<h4>Como Entregar também o "QR Code de Mesa" (Para Salão)</h4>
<p>Na mesma plataforma do cardápio digital, ative a opção <strong>"Consumo no Local / Informar Número da Mesa"</strong>. Gere no Canva os adesivos de mesa (8×10cm) numerados (<em>Mesa 01, Mesa 02... Mesa 15</em>) com o QR Code do cardápio. O cliente senta, escaneia, escolhe sem esperar o garçom e o pedido sai direto no balcão identificando: <strong>"📍 PEDIDO MESA 04"</strong>!</p>
"""
            },
            {
                "num": 5,
                "module": "Módulo 5 • Migração de Clientes & Recorrência",
                "title": "A Estratégia do 'Cupom Cavalo de Troia' na Sacola do Delivery",
                "duration": "08 min",
                "summary": "O método infalível para fazer os clientes que hoje pedem pelo iFood passarem a pedir direto no Cardápio Próprio do seu cliente.",
                "content_html": """
<h4>A Maior Objeção do Dono de Restaurante: "Mas meus clientes estão acostumados a pedir pelo iFood..."</h4>
<p>Responda com a <strong>Estratégia do Cupom Cavalo de Troia</strong> (e entregue a arte desse cupom pronta como bônus do seu pacote!):</p>
<ol>
  <li>Crie no Canva uma arte de panfleto pequeno (10×14cm) com um QR Code gigante apontando para o novo Cardápio Digital Próprio do restaurante.</li>
  <li>Texto do Panfleto: <strong>"🎁 GANHE R$ 10 DE DESCONTO (OU REFRI GRÁTIS) NO SEU PRÓXIMO PEDIDO! Sabia que os aplicativos cobram taxas altas da gente? Peça direto pelo nosso Cardápio Oficial escaneando o QR Code abaixo e nós repassamos essa economia em forma de desconto ou brinde para você!"</strong></li>
  <li>O restaurante grampeia esse cupom na nota fiscal de <strong>todas as sacolas que saem pelo iFood</strong>!</li>
</ol>
<p>Em 30 dias, centenas de clientes fiéis do bairro salvam o link do Cardápio Próprio no celular, o restaurante economiza milhares de reais em taxas e você garante sua mensalidade de manutenção/suporte por anos!</p>
"""
            }
        ],
        "delivery_guide": """MANUAL TÉCNICO DE ENTREGA — CARDÁPIO DIGITAL SEM TAXAS + QR CODE DE MESA

1. COLETA DE DADOS DO RESTAURANTE (15 MIN)
   • Peça ao cliente o link atual dele no iFood (ou foto do cardápio impresso), logotipo, horário de funcionamento, chave Pix e tabela de taxa de entrega por bairro (ou por km).
   • Dica de Ouro: Se ele já tem iFood, você copia os títulos, preços, descrições e fotos diretamente da página pública dele no iFood em 30 minutos!

2. ESTRUTURAÇÃO DO CARDÁPIO E ENGENHARIA DE MENU (60 MIN)
   • Crie as categorias na ordem estratégica: 1º Destaques / Combos da Casa → 2º Pratos Principais / Pizzas / Burgers → 3º Porções / Acompanhamentos → 4º Bebidas → 5º Sobremesas.
   • Configure os Grupos de Complementos (Ex: Ponto da Carne, Escolha de Sabores Meio a Meio, Adicionais Pagos de Alta Margem, Sugestão de Bebida).
   • Configure métodos de pagamento: Pix (com chave Copia e Cola), Cartão na Entrega (crédito/débito) e Dinheiro (com campo automático "Precisa de troco para quanto?").
   • Configure modalidades: Delivery (com cálculo automático da taxa por bairro), Retirada no Balcão e Pedido na Mesa.

3. INTEGRAÇÃO COM INSTAGRAM, GOOGLE MEU NEGÓCIO E WHATSAPP
   • Substitua o link do iFood na Bio do Instagram pelo link do novo Cardápio Digital Próprio (ou um Biossite com botão principal "🍔 Fazer Pedido Sem Taxa").
   • Adicione o link do cardápio no campo "Cardápio / Fazer Pedido" da ficha do Google Meu Negócio do restaurante.
   • Configure a Mensagem de Saudação do WhatsApp Business do restaurante para já enviar o link do cardápio automaticamente assim que o cliente disser "Boa noite".

4. ENTREGA DOS BÔNUS DE ALTO VALOR (ARTE DO CUPOM DE SACOLA + QR CODE DE MESA)
   • Entregue em PDF pronto para impressão a arte do "Cupom Cavalo de Troia" (10x14cm) com QR Code para o restaurante grampear nas sacolas de delivery.
   • Se tiver salão, entregue o arquivo PDF com os Displays/Adesivos de QR Code de Mesa.""",
        "pricing_tiers": [
            {
                "name": "Cardápio Digital Express",
                "badge": "Entrada Rápida",
                "cost": "R$ 0,00 (2h do seu tempo)",
                "setup_price": "R$ 350 a R$ 490",
                "monthly_price": "Opcional R$ 67/mês",
                "profit_margin": "100% de margem líquida",
                "deliverables": [
                    "Montagem completa do Cardápio Digital Responsivo (até 40 itens)",
                    "Carrinho inteligente que envia o pedido pronto e somado para o WhatsApp",
                    "Configuração de taxas de entrega por bairro + Chave Pix Copia e Cola",
                    "Configuração do link na Bio do Instagram e na mensagem automática do WhatsApp"
                ]
            },
            {
                "name": "Sistema Delivery Próprio + Migração",
                "badge": "Mais Vendido ★",
                "cost": "R$ 0,00 (2h30 do seu tempo)",
                "setup_price": "R$ 597 a R$ 790",
                "monthly_price": "R$ 97 a R$ 147/mês",
                "profit_margin": "100% de margem + Recorrência Mensal",
                "deliverables": [
                    "Tudo do Cardápio Express + Engenharia de Adicionais para subir o ticket médio",
                    "Arte pronta do 'Cupom de Sacola com QR Code' para migrar clientes do iFood",
                    "Inclusão do link de pedido direto na ficha do Google Meu Negócio",
                    "Manutenção mensal inclusa (alterações de preços, fotos e promoções da semana)"
                ]
            },
            {
                "name": "Ecossistema Delivery + Salão QR + NFC",
                "badge": "Pacote Premium",
                "cost": "R$ 30,00 (Placas/Adesivos)",
                "setup_price": "R$ 997 a R$ 1.490",
                "monthly_price": "R$ 147 a R$ 247/mês",
                "profit_margin": "~97% de margem + Recorrência",
                "deliverables": [
                    "Cardápio Digital Completo (Delivery + Retirada + Pedido por QR Code nas Mesas)",
                    "Arte e geração dos QR Codes numerados para todas as mesas do salão",
                    "1 Plaquinha Acrílico NFC + QR Code no caixa para captar Avaliações 5⭐ no Google",
                    "Suporte prioritário e atualização mensal de cardápio e combos promocionais"
                ]
            }
        ],
        "checklist": [
            "Filtrar no MapaLeads pizzarias, hamburguerias, restaurantes, sushi e açaí sem site próprio",
            "Verificar no Instagram ou Google do lead se ele joga os próprios seguidores para o link do iFood ou atende no manual",
            "Abordar no horário fora de pico (14h30 às 17h15) enviando a conta da economia de taxas + VSL (vsl-cardapio.mp4)",
            "Coletar o link atual do iFood (ou foto do cardápio), tabela de taxas de entrega por bairro e chave Pix",
            "Cadastrar as categorias aplicando Engenharia de Menu (combos mais lucrativos no topo + adicionais obrigatórios)",
            "Testar um pedido completo do início ao fim verificando a formatação da mensagem que chega no WhatsApp",
            "Gerar a arte do 'Cupom Cavalo de Troia' com QR Code para grampear nas sacolas de delivery",
            "Colocar o link do Cardápio Próprio na Bio do Instagram, no Google Meu Negócio e na Saudação do WhatsApp",
            "Oferecer o plano mensal de R$ 97 a R$ 147/mês para gerenciar alterações de preços e promoções da semana"
        ],
        "script_approach": """[MENSAGEM 1 — ABORDAGEM NO HORÁRIO FORA DE PICO (14h30 ÀS 17h15)]
Olá, tudo bem? Aqui é o [Seu Nome].
Falo com o proprietário(a) da *[Nome da Empresa]*?
Vi o perfil de vocês aqui em *[Cidade]* e notei que muitos clientes que já conhecem a sua marca acabam pedindo pelo aplicativo (onde vocês perdem de 12% a 27% de taxa em cada pedido) ou precisam esperar atendimento manual no WhatsApp.
Posso te mandar um vídeo de 23 segundos mostrando como instalar o seu *Cardápio Digital Próprio com 0% de comissão por pedido*?

[MENSAGEM 2 — ENVIE A VSL (vsl-cardapio.mp4) + A MATEMÁTICA DO LUCRO]
Dá uma olhada nesse vídeo rápido acima 👆
Quando o cliente clica no seu Cardápio Digital Próprio (no Instagram, Google ou na mensagem automática do WhatsApp):
🍔 Ele vê suas fotos, escolhe adicionais/bebidas sozinho, seleciona o bairro (já soma a taxa de entrega) e escolhe Pix, Cartão ou Troco;
📲 O pedido já chega *100% pronto, somado e formatado no seu WhatsApp* direto para a cozinha;
💰 *Zero comissão por pedido:* Se você migrar apenas R$ 10.000 em pedidos recorrentes do app para o seu link próprio, são *R$ 1.500 a R$ 2.500 de lucro líquido a mais no seu bolso todo mês*!

E nós ainda entregamos a arte do *Cupom de Sacola com QR Code* para você converter os clientes do iFood para o seu link próprio na próxima compra.
Posso te mostrar uma demonstração no celular de como fica o cardápio da *[Nome da Empresa]*?""",
        "script_followup": """[FOLLOW-UP 1 — DIA SEGUINTE ÀS 15h00]
Fala! Tudo tranquilo no pré-preparo de hoje?
Fiz uma simulação rápida: com apenas 2 pedidos por noite migrando do app para o seu Cardápio Digital Próprio, a economia de taxas já paga 100% da implantação no primeiro mês — e todo o resto é lucro limpo no caixa da *[Nome da Empresa]*.
Se você já tiver cardápio no iFood ou em PDF, eu puxo todas as fotos e preços de lá para você não ter trabalho nenhum. Vamos montar o seu para já rodar neste fim de semana?

[FOLLOW-UP 2 — 72 HORAS DEPOIS]
Oi! Estou finalizando a implantação do Cardápio Digital Sem Taxas de um restaurante aqui da região e tenho vaga para entregar mais 1 cardápio completo até sexta-feira (já com os adicionais configurados e a arte do cupom fidelidade com QR Code).
Quer que eu reserve essa entrega para a *[Nome da Empresa]*?

[ROTEIRO DE ÁUDIO DE 30 SEGUNDOS]
"Fala, tudo bem? Sei que a correria aí na cozinha é grande, então vou ser bem direto: a ideia não é você sair do iFood, é parar de pagar 20% de taxa para o cliente fiel que já te conhece e pede toda semana! Eu monto o seu Cardápio Digital Próprio onde o cliente escolhe tudo sozinho, calcula a entrega por bairro e o pedido cai pronto no seu WhatsApp com zero comissão. Você só me manda o link atual ou foto do cardápio e eu entrego tudo pronto em 48 horas!" """,
        "script_objections": """• "Não quero sair do iFood porque lá vem muito cliente novo!"
Resposta: "E você não deve sair! O segredo dos restaurantes mais lucrativos é usar o iFood como vitrine para a 1ª compra e colocar dentro da sacola o nosso Cupom com QR Code ('Peça direto no nosso Cardápio Oficial na próxima vez e ganhe 10% OFF ou refri grátis'). Assim o cliente novo vem pelo iFood, mas da 2ª compra em diante pede no seu link próprio com Taxa Zero!"

• "Não tenho tempo para cadastrar produto por produto e tirar foto..."
Resposta: "Você não vai precisar cadastrar nada! Nossa equipe puxa todos os seus pratos, preços, descrições e fotos diretamente do seu iFood atual (ou do seu PDF) e entrega o cardápio 100% pronto para uso em 48 horas."

• "E como fica o cálculo da taxa de entrega?"
Resposta: "Já deixamos toda a sua tabela de bairros (ou raio por km) cadastrada no sistema! Quando o cliente digita o endereço, o cardápio soma o frete exato automaticamente antes de enviar o pedido para o seu WhatsApp." """,
        "proposal_script": """📋 *PROPOSTA COMERCIAL — CARDÁPIO DIGITAL PRÓPRIO SEM TAXAS + SISTEMA DE MIGRAÇÃO*
Estabelecimento: *[Nome da Empresa]* | Cidade: *[Cidade]*

🎯 *OBJETIVO:*
Criar o canal próprio de vendas online do seu restaurante (0% de comissão por pedido), automatizar a recepção de pedidos no WhatsApp e aumentar o ticket médio com adicionais inteligentes.

✅ *O QUE ENTREGAMOS PRONTO EM 48 HORAS:*
1. *Cadastro Completo do Cardápio:* Importação de todas as categorias, pratos, fotos, descrições e preços (você não tem trabalho nenhum);
2. *Engenharia de Adicionais (Cross-Sell):* Configuração de complementos, bordas, adicionais e sugestão automática de bebidas/sobremesas;
3. *Cálculo Automático de Entrega & Pagamento:* Tabela de frete por bairro, opção de Retirada, Pix Copia e Cola e cálculo de troco;
4. *Integração Total:* Pedido chega formatado e somado no seu WhatsApp + Link configurado na Bio do Instagram e no Google Maps;
5. *Bônus — Arte do Cupom "Cavalo de Troia":* Arte pronta com QR Code para colocar nas sacolas do delivery e migrar clientes dos apps para o seu canal próprio.

💰 *INVESTIMENTO:*
• *Implantação Completa (Chave na Mão):* R$ 497,00 (50% no início + 50% na entrega em 48h)
• *Plano com Suporte & Atualizações Mensais de Preços/Promoções:* + R$ 97,00/mês (opcional, a partir do 2º mês).

Me envie o link do seu iFood (ou foto do cardápio) + tabela de entrega por bairro e já deixamos tudo pronto para rodar neste fim de semana!"""
    },

    # =========================================================================
    # CURSO 5 — BIOSSITES & LANDING PAGES EXPRESS (48H)
    # =========================================================================
    {
        "slug": "estrategia-biossite",
        "strategy_key": "biossite",
        "badge_label": "Curso 05 • Biossites & Landing Pages 48h",
        "title": "Biossites & Landing Pages Locais de Alta Conversão (Entrega em 48h)",
        "subtitle": "Venda páginas mobile-first ultra rápidas por R$ 300 a R$ 900 para os 70% de empresas locais que não têm site ou usam um Linktree amador.",
        "ticket_range": "R$ 300 a R$ 900 setup + R$ 67 a R$ 97/mês",
        "thumbnail_url": "/static/img/academy/biossite-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-biossite.mp4",
        "course_duration": "5 Aulas • ~42 min",
        "vsl_video_url": "/static/video/sales-academy/vsl-biossite.mp4",
        "vsl_title": "VSL Pronta: Transforme Cliques do Instagram e Google em Clientes no WhatsApp",
        "vsl_duration": "00:24",
        "target_opp": "biossite",
        "sort_order": 5,
        "lessons": [
            {
                "num": 1,
                "module": "Módulo 1 • O Mercado dos Sem-Site",
                "title": "Por que 70% das Empresas Locais Não Têm Site e Como Vender a Solução Ideal",
                "duration": "08 min",
                "summary": "Por que sites tradicionais de R$ 3.000 são difíceis de vender, mas Biossites e Landing Pages Locais de R$ 350 a R$ 700 vendem todos os dias.",
                "content_html": """
<h4>A Grande Oportunidade dos Negócios "Sem Site" ou "Só Instagram"</h4>
<p>Quando você faz uma busca no MapaLeads PRO em qualquer cidade brasileira, descobre que <strong>65% a 75% das empresas locais não possuem site próprio</strong> (ou colocam apenas um link do WhatsApp cru ou um Linktree cinza sem graça na bio do Instagram).</p>
<p>Por que esses empresários ainda não compraram um site? Porque agências tradicionais tentam cobrar <strong>R$ 3.000 a R$ 5.000</strong> e pedem 30 dias para entregar um site institucional cheio de abas (<em>"Missão, Visão e Valores"</em>) que ninguém lê no celular!</p>

<div class="sa-callout sa-callout-emerald">
  <strong><i class="fa-solid fa-mobile-screen-button"></i> O Que o Empresário Local Realmente Quer Comprar:</strong>
  <p>Uma <strong>Landing Page Local / Biossite Mobile-First</strong>: uma página única, linda na tela do celular, que carrega em 1 segundo, mostra os serviços com fotos reais, exibe as avaliações 5 estrelas do Google Maps, mostra o mapa de como chegar e tem um botão pulsante que leva o cliente direto para o WhatsApp. Você cria em <strong>60 a 90 minutos</strong> e vende por <strong>R$ 350 a R$ 890 + R$ 67/mês de hospedagem</strong>!</p>
</div>
"""
            },
            {
                "num": 2,
                "module": "Módulo 2 • Filtragem & Técnica da Prévia",
                "title": "Filtrando Alvos no MapaLeads & A Técnica da 'Prévia de 10 Minutos'",
                "duration": "09 min",
                "summary": "Como usar o filtro de Biossite no CRM e a técnica matadora de mandar um print da primeira dobra já com a logo do cliente.",
                "content_html": """
<h4>1. Como encontrar os melhores compradores no MapaLeads PRO</h4>
<p>No <strong>CRM Kanban</strong>, selecione o filtro de oportunidade <strong>"Biossite / Landing Page"</strong>. O sistema já filtra automaticamente empresas cujo campo de site está vazio ou aponta apenas para redes sociais (Instagram/Facebook/Linktree).</p>
<p>Os nichos que pagam mais rápido por páginas de alta conversão são:</p>
<ul>
  <li><strong>Saúde &amp; Beleza:</strong> Dentistas, Clínicas de Estética, Psicólogos, Nutricionistas, Fisioterapeutas, Barbearias VIP e Salões;</li>
  <li><strong>Serviços &amp; Profissionais Liberais:</strong> Advogados, Contadores, Arquitetos, Imobiliárias, Energia Solar;</li>
  <li><strong>Automotivo &amp; Casa:</strong> Estética Automotiva, Oficinas Especializadas, Marcenarias, Dedetizadoras, Climatização.</li>
</ul>

<h4>2. A Técnica da "Prévia da Primeira Dobra" (70% de Fechamento)</h4>
<p>Para leads com Score IA ≥ 80 (empresas que têm boas avaliações e Instagram ativo, mas não têm site), pegue a logo e 1 foto do Instagram deles, jogue no seu template base e tire um <strong>print da tela do celular mostrando como ficaria o Biossite deles</strong>. Quando o empresário vê a própria marca em uma página moderna ao lado da VSL (<code>vsl-biossite.mp4</code>), a venda está 80% fechada!</p>
"""
            },
            {
                "num": 3,
                "module": "Módulo 3 • Anatomia da Página",
                "title": "Os 5 Blocos Obrigatórios de uma Landing Page Local que Converte 3x Mais",
                "duration": "10 min",
                "summary": "O wireframe exato validado para negócios locais que transforma visitantes curiosos em orçamentos no WhatsApp.",
                "content_html": """
<h4>A Estrutura dos 5 Blocos de Alta Conversão (De Cima para Baixo)</h4>
<div class="sa-lesson-grid">
  <div class="sa-lesson-card">
    <strong>Bloco 1: Primeira Dobra (Hero Section)</strong>
    <p>• Logotipo + Badge de localização (Ex: <em>"Referência em Estética Facial em [Bairro/Cidade]"</em>).<br>
    • Headline de Promessa Clara + Subheadline.<br>
    • <strong>Botão Principal Pulsante (Verde Esmeralda):</strong> <em>"Agendar Avaliação pelo WhatsApp"</em> com link <code>wa.me</code> e mensagem pré-preenchida.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>Bloco 2: Vitrine dos 3 a 4 Serviços Carros-Chefe</strong>
    <p>Cards visuais com foto real, nome do procedimento/serviço, 2 linhas explicando o benefício e um botão individual em cada card (<em>"Quero saber mais sobre [Serviço X]"</em>).</p>
  </div>
  <div class="sa-lesson-card">
    <strong>Bloco 3: Prova Social do Google Maps</strong>
    <p>Selo <em>"⭐ Nota 4.9 no Google"</em> + print ou transcrição de 3 avaliações reais de clientes da cidade + fotos do ambiente/equipe para gerar confiança imediata.</p>
  </div>
  <div class="sa-lesson-card">
    <strong>Bloco 4 &amp; 5: Mapa Interativo + FAQ + Rodapé NAP</strong>
    <p>• Botão <em>"Abrir Rota no Google Maps / Waze"</em> + Horário de funcionamento.<br>
    • 3 Perguntas Frequentes (Convênios/Formas de pagamento, estacionamento, horários).<br>
    • Rodapé com Nome, Endereço e Telefone idênticos à ficha do Google Meu Negócio (impulsiona o SEO Local!).</p>
  </div>
</div>
"""
            },
            {
                "num": 4,
                "module": "Módulo 4 • Criação Sem Código em 60 Min",
                "title": "Ferramentas Práticas para Criar e Publicar sem Código em 1 Hora",
                "duration": "09 min",
                "summary": "Como usar Canva Sites, Carrd, Framer, WordPress ou hospedagem gratuita na Cloudflare/Netlify para ter margem próxima de 100%.",
                "content_html": """
<h4>As 3 Melhores Ferramentas para Entregar Rápido e com Custo Quase Zero</h4>
<ol>
  <li><strong>Canva Websites (Mais Rápido para Iniciantes — 40 minutos):</strong> Você monta o design mobile-first usando templates prontos no Canva, insere os links <code>https://wa.me/55...</code> nos botões e clica em <em>Publicar como Site</em> (no subdomínio gratuito <code>.my.canva.site</code> ou conectando o domínio <code>.com.br</code> do cliente).</li>
  <li><strong>Carrd.co Pro / Framer (Visual Ultra Moderno):</strong> O plano anual do Carrd Pro custa menos de R$ 100/ano para até 25 sites com domínio personalizado! Permite criar Biossites e Landing Pages responsivas com animações suaves em 45 minutos.</li>
  <li><strong>HTML Estático + Cloudflare Pages / Netlify (Custo R$ 0,00 e Nota 100 no Google PageSpeed):</strong> Tenha 3 templates HTML/Tailwind prontos (1 para Clínicas/Saúde, 1 para Serviços/Oficinas, 1 para Gastronomia/Lojas). Basta trocar cores, textos, fotos e o número do WhatsApp e publicar gratuitamente na Cloudflare Pages ou Netlify com SSL automático!</li>
</ol>
"""
            },
            {
                "num": 5,
                "module": "Módulo 5 • Hospedagem & Sinergia SEO",
                "title": "Como Conectar o Biossite ao Google Meu Negócio e Cobrar R$ 67 a R$ 97/mês",
                "duration": "06 min",
                "summary": "Por que conectar o Biossite na ficha do Google Maps faz a empresa subir no ranking local e garante sua mensalidade.",
                "content_html": """
<h4>O Duplo Benefício que Justifica a Mensalidade</h4>
<p>Assim que publicar o Biossite/Landing Page do cliente:</p>
<ol>
  <li>Coloque o link na <strong>Bio do Instagram</strong> do cliente;</li>
  <li>Coloque o link no botão <strong>"Website" da ficha do Google Meu Negócio</strong> dele!</li>
</ol>
<p>Quando o algoritmo do Google vê que a ficha do Google Maps agora aponta para uma página rápida que contém o <strong>mesmo Nome, Endereço e Telefone (consistência NAP)</strong> no rodapé, a relevância da ficha sobe no ranking local! Ofereça o plano de <strong>Hospedagem VIP + SSL + Até 2 Atualizações Mensais de Fotos/Promoções por R$ 67 a R$ 97/mês</strong>.</p>
"""
            }
        ],
        "delivery_guide": """MANUAL TÉCNICO DE ENTREGA — BIOSSITE & LANDING PAGE LOCAL EM 48H

1. BRIEFING EXPRESS (10 MINUTOS)
   • Extraia da própria ficha do Google Maps e do Instagram do cliente: Logotipo, paleta de 2 cores principais, endereço, horário, telefone WhatsApp, 3 avaliações reais de 5 estrelas e fotos do local/equipe.
   • Pergunte ao cliente apenas: "Quais são os 3 ou 4 serviços/produtos principais que você mais quer receber orçamentos no WhatsApp?"

2. MONTAGEM DOS 5 BLOCOS DE CONVERSÃO (45 A 60 MIN)
   • Bloco 1 (Hero): Logo + Headline ("Especialistas em [Serviço] em [Cidade]") + Subtítulo + Botão CTA Verde com link personalizado:
     https://wa.me/55DD999999999?text=Ol%C3%A1%21+Vim+pelo+site+e+gostaria+de+solicitar+um+or%C3%A7amento
   • Bloco 2 (Serviços): 3 a 4 cards com foto, título, benefício e botão individual para o WhatsApp com o nome daquele serviço na mensagem.
   • Bloco 3 (Autoridade & Prova Social): "Quem Somos" enxuto + Selo da nota do Google Maps + 3 depoimentos reais de clientes.
   • Bloco 4 (Localização): Endereço completo + Horário + Botão direto "Como Chegar (Google Maps)".
   • Bloco 5 (Rodapé NAP): Nome Comercial, Endereço completo, Telefone e CNPJ idênticos ao Google Meu Negócio.

3. OTIMIZAÇÃO DE VELOCIDADE E PUBLICAÇÃO
   • Comprima as imagens para WebP ou JPG leve (< 200KB por imagem) para carregar instantaneamente no 4G.
   • Publique com certificado HTTPS (SSL) ativo e teste a abertura no celular vertical.

4. INSTALAÇÃO NOS CANAIS DO CLIENTE
   • Atualize o link na Bio do Instagram do cliente e no campo "Website" do Google Meu Negócio.""",
        "pricing_tiers": [
            {
                "name": "Biossite Mobile Express",
                "badge": "Entrada Rápida",
                "cost": "R$ 0,00 (45 min no Canva/Carrd)",
                "setup_price": "R$ 297 a R$ 390",
                "monthly_price": "Opcional R$ 49/mês",
                "profit_margin": "100% de margem líquida",
                "deliverables": [
                    "Biossite Mobile-First personalizado com as cores e logo da empresa",
                    "Botões inteligentes para WhatsApp (com mensagem pronta), Google Maps e Instagram",
                    "Destaque para os 3 principais serviços/produtos e horário de atendimento",
                    "Ideal para substituir o Linktree amador na Bio do Instagram"
                ]
            },
            {
                "name": "Landing Page Local 5 Blocos",
                "badge": "Mais Vendido ★",
                "cost": "R$ 0,00 (1h30 do seu tempo)",
                "setup_price": "R$ 597 a R$ 790",
                "monthly_price": "R$ 67 a R$ 97/mês (Hospedagem + Suporte)",
                "profit_margin": "100% de margem + Recorrência",
                "deliverables": [
                    "Landing Page Completa em 5 Blocos de Alta Conversão (Mobile e Desktop)",
                    "Vitrine de Serviços com fotos reais + Seção de Avaliações 5⭐ do Google",
                    "Mapa interativo 'Como Chegar' + Botão Flutuante de WhatsApp",
                    "Integração com a ficha do Google Meu Negócio (Consistência NAP para SEO Local)"
                ]
            },
            {
                "name": "Landing Page PRO + Domínio + GMN",
                "badge": "Autoridade Máxima",
                "cost": "R$ 40,00/ano (Domínio .com.br)",
                "setup_price": "R$ 997 a R$ 1.290",
                "monthly_price": "R$ 97 a R$ 147/mês",
                "profit_margin": "~96% de margem + Recorrência",
                "deliverables": [
                    "Landing Page Local Completa + Registro/Configuração de Domínio Próprio (.com.br)",
                    "Instalação de Pixel da Meta / Google Tag para campanhas de anúncios",
                    "Otimização Completa do Perfil da Empresa no Google Meu Negócio",
                    "Hospedagem rápida com SSL + Até 2 atualizações mensais de conteúdo"
                ]
            }
        ],
        "checklist": [
            "Filtrar no MapaLeads empresas com oportunidade 'Biossite / Landing Page' (sem site ou usando Linktree/Instagram)",
            "Priorizar clínicas, dentistas, estética, advogados, oficinas e serviços com boa nota no Google",
            "Enviar mensagem apontando a ausência do site na ficha do Google + Vídeo VSL (vsl-biossite.mp4)",
            "Para leads quentes, montar em 10 minutos uma prévia da 1ª dobra com a logo deles e enviar o print no WhatsApp",
            "Coletar os 3 a 4 serviços carros-chefe, fotos reais do local e depoimentos do Google Maps",
            "Construir a página seguindo a anatomia dos 5 Blocos (Hero + Serviços + Prova Social + Mapa + Rodapé NAP)",
            "Configurar todos os botões com link wa.me/55... contendo mensagem personalizada por serviço",
            "Testar carregamento no celular (4G) e instalar o link na Bio do Instagram e no botão Website do Google Maps",
            "Ativar o plano mensal de R$ 67 a R$ 97/mês de hospedagem e atualizações"
        ],
        "script_approach": """[MENSAGEM 1 — DIAGNÓSTICO DE AUTORIDADE NO GOOGLE & INSTAGRAM]
Olá, tudo bem? Aqui é o [Seu Nome].
Falo com o responsável pela *[Nome da Empresa]*?
Encontrei vocês pesquisando por *[Nicho]* aqui em *[Cidade]* no Google Maps. Vi que a empresa tem ótimas avaliações, mas o botão de *Website* na ficha do Google está vazio (ou leva apenas para um link simples na bio).
Posso te mostrar em um vídeo de 24 segundos o modelo de *Biossite / Página Express* que estamos criando para empresas de *[Cidade]* converterem cliques em agendamentos no WhatsApp?

[MENSAGEM 2 — ENVIE A VSL (vsl-biossite.mp4) + A OFERTA]
Dá uma olhada nesse vídeo rápido acima 👆
Hoje 92% dos seus clientes abrem o seu perfil pelo celular. Quando eles encontram um *Biossite / Landing Page Local* com a sua identidade visual:
✅ Veem seus principais serviços com fotos reais logo na primeira tela;
✅ Conferem suas avaliações 5 estrelas do Google e o mapa de como chegar em 1 clique;
✅ Clicam no botão direto do WhatsApp já informando exatamente qual serviço desejam orçar!

Nós entregamos a página 100% pronta e configurada no seu Google e Instagram em *48 horas*, por uma fração do valor de um site tradicional.
Quer que eu monte uma prévia gratuita da primeira tela com a logo da *[Nome da Empresa]* para você ver como fica no celular?""",
        "script_followup": """[FOLLOW-UP 1 — 24 HORAS DEPOIS (GATILHO DA PRÉVIA)]
Oi! Peguei a logo e as cores da *[Nome da Empresa]* e montei um rascunho de como ficaria a primeira tela da sua nova Página Express para o Instagram e Google Maps.
Ficou muito profissional! Posso te mandar o print aqui para você dar uma olhada sem compromisso?

[FOLLOW-UP 2 — 72 HORAS DEPOIS]
Fala! Estou encerrando as entregas da semana aqui em *[Cidade]*.
Consegui manter a condição especial do Biossite / Landing Page Local completa (entrega em 48h, já integrada ao seu Google Meu Negócio e Bio do Instagram).
Vamos colocar a página da *[Nome da Empresa]* no ar esta semana?

[ROTEIRO DE ÁUDIO DE 25 SEGUNDOS]
"Fala, tudo bem? Cara, quando o cliente te acha no Google ou no Instagram e não vê uma página profissional mostrando seus serviços, suas avaliações e o botão direto pro WhatsApp, você perde autoridade pro concorrente. Você não precisa gastar 3 mil reais num site pesado: eu monto uma página mobile ultra rápida com a cara da sua empresa em 48h por um valor super acessível. Me diz aqui se posso te mandar o print da prévia que separei pra vocês!" """,
        "script_objections": """• "Já tenho Instagram, preciso mesmo de uma página/site?"
Resposta: "O Instagram é excelente para atrair atenção, mas o feed distrai o cliente. A Landing Page / Biossite é o seu 'fechador de vendas': quando o cliente clica no link da sua Bio ou no botão Website do Google Maps, ele cai em uma tela limpa, vê seus serviços principais, sua nota no Google, sua localização e clica direto para chamar no WhatsApp já decidido a comprar."

• "Site costuma demorar semanas e dá dor de cabeça para atualizar..."
Resposta: "Esse é o modelo antigo! Nossa Página Express é focada 100% em conversão no celular e nós fazemos tudo por você: pegamos suas melhores fotos e avaliações e entregamos 100% pronta no ar em 48 horas."

• "Adicionar a página ajuda a minha empresa a subir no Google Maps?"
Resposta: "Sim! Ter um site ativo vinculado à sua ficha do Google Meu Negócio com o mesmo nome, endereço e telefone no rodapé é um dos fatores oficiais de autoridade do algoritmo do Google para ranquear melhor a sua empresa na cidade." """,
        "proposal_script": """📋 *PROPOSTA COMERCIAL — BIOSSITE & LANDING PAGE LOCAL DE ALTA CONVERSÃO*
Empresa: *[Nome da Empresa]* | Cidade: *[Cidade]*

🎯 *OBJETIVO:*
Criar uma página profissional ultra rápida (Mobile & Desktop) para transformar visitantes do Instagram e do Google Maps em clientes chamando no seu WhatsApp.

✅ *ESTRUTURA COMPLETA ENTREGUE EM 48 HORAS:*
1. *Primeira Dobra de Impacto:* Design personalizado com sua logo, promessa principal e botão de ação imediata para o WhatsApp;
2. *Vitrine Visual de Serviços/Produtos:* Cards com fotos reais, benefícios e botão de orçamento individual por serviço;
3. *Bloco de Prova Social:* Destaque da sua nota e avaliações 5 estrelas do Google Maps + Sobre a Empresa;
4. *Localização & Horários:* Mapa interativo "Como Chegar" em 1 clique + Horário de atendimento;
5. *Integração Completa:* Instalação do link na Bio do Instagram e no botão "Website" do Google Meu Negócio.

💰 *OPÇÕES DE INVESTIMENTO:*
• *Opção 1 — Biossite Mobile Express:* R$ 297,00 (pagamento único: 50% no início + 50% na entrega)
• *Opção 2 — Landing Page Local Completa 5 Blocos:* R$ 597,00 (+ R$ 67/mês opcional para hospedagem VIP e atualizações mensais).

Qual das duas opções atende melhor o momento da *[Nome da Empresa]* hoje?"""
    },

    # =========================================================================
    # CURSO 6 (NOVO!) — COMBO PRESENÇA LOCAL 360° & RECORRÊNCIA MENSAL
    # =========================================================================
    {
        "slug": "estrategia-combo",
        "strategy_key": "combo",
        "badge_label": "Curso 06 • Combo 360° & Recorrência",
        "title": "Combo Presença Local 360° & Fechamento de Contratos Recorrentes",
        "subtitle": "Como empacotar Google Meu Negócio + Biossite + Plaquinha NFC + WhatsApp PRO em contratos de R$ 1.200 a R$ 2.500 + mensalidade de R$ 297 a R$ 597/mês.",
        "ticket_range": "R$ 997 a R$ 2.500 setup + R$ 297 a R$ 597/mês",
        "thumbnail_url": "/static/img/academy/combo-hero.jpg",
        "course_video_url": "/static/video/sales-academy/curso-combo.mp4",
        "course_duration": "5 Aulas • ~50 min",
        "vsl_video_url": "/static/video/sales-academy/vsl-combo.mp4",
        "vsl_title": "VSL Pronta: A Estrutura Completa Presença Local 360° em 48 Horas",
        "vsl_duration": "00:28",
        "target_opp": "",
        "sort_order": 6,
        "lessons": [
            {
                "num": 1,
                "module": "Módulo 1 • A Psicologia da Ancoragem B2B",
                "title": "Por que é Mais Fácil Vender um Pacote de R$ 1.297 do que um Serviço Isolado",
                "duration": "10 min",
                "summary": "Aprenda como sair da comparação de preços e construir uma carteira de 10 a 20 clientes recorrentes que geram R$ 5.000 a R$ 15.000/mês.",
                "content_html": """
<h4>1. A Armadilha do Vendedor de Serviço Único vs. O Consultor 360°</h4>
<p>Quando você oferece apenas um serviço isolado, o empresário pensa: <em>"Legal, mas só arrumar o Google ou só ter uma plaquinha resolve todo o meu problema?"</em>. Agora, quando você apresenta o <strong>Ecossistema Completo de Vendas Locais (Atração + Conversão + Atendimento + Prova Social)</strong>, ele percebe que está diante de uma solução definitiva para a empresa dele.</p>

<div class="sa-callout sa-callout-amber">
  <strong><i class="fa-solid fa-crown"></i> O Efeito da Ancoragem de Preço na Prática:</strong>
  <p>Na sua proposta comercial, você lista o preço real de cada serviço vendido separadamente:</p>
  <ul>
    <li>1. Otimização Completa Google Meu Negócio Top 3 = <s>R$ 597,00</s></li>
    <li>2. Landing Page / Biossite de Alta Conversão = <s>R$ 597,00</s></li>
    <li>3. Estruturação WhatsApp Business PRO + Catálogo + Funil = <s>R$ 497,00</s></li>
    <li>4. Display Acrílico Físico NFC + QR Code Google 5⭐ = <s>R$ 197,00</s></li>
    <li><strong>Valor Total Separado: <s>R$ 1.888,00</s></strong></li>
    <li><strong>Investimento no Combo Presença Local 360°: R$ 1.197,00 (ou 3x no cartão / 50% entrada + 50% na entrega) + R$ 297/mês de Gestão Contínua!</strong></li>
  </ul>
  <p>O empresário sente que está <strong>ganhando quase R$ 700 de desconto imediato</strong> e levando até uma placa física de acrílico para o balcão!</p>
</div>
"""
            },
            {
                "num": 2,
                "module": "Módulo 2 • A Escada de Valor (Pé na Porta)",
                "title": "Como Entrar com um Serviço de R$ 150 a R$ 350 e Fazer Upsell para o Combo em 7 Dias",
                "duration": "10 min",
                "summary": "O plano B infalível: se o cliente achar o Combo alto logo de cara, feche 1 pilar rápido e suba ele para o contrato completo na entrega.",
                "content_html": """
<h4>As 2 Portas de Entrada para Conquistar Qualquer Empresário</h4>
<div class="sa-lesson-grid">
  <div class="sa-lesson-card">
    <strong>Porta 1: Top-Down (Apresenta o Combo 360° Primeiro)</strong>
    <p>Para empresas estruturadas (clínicas médicas/odontológicas, escritórios, estética, restaurantes grandes, oficinas grandes): apresente sempre a proposta de 3 colunas com o <strong>Combo 360° (R$ 1.197 + R$ 297/mês)</strong> em destaque no centro. Se o orçamento dele estiver apertado, você desce para o <strong>Combo Start (R$ 697)</strong> sem perder a venda!</p>
  </div>
  <div class="sa-lesson-card">
    <strong>Porta 2: Bottom-Up ("Pé na Porta" em 7 Dias)</strong>
    <p>Se o cliente for desconfiado, venda primeiro a <strong>Plaquinha NFC de R$ 147</strong> ou o <strong>Setup Express do Google de R$ 350</strong>. Entregue em 24 horas com perfeição! No momento em que ele vê a placa funcionando ou a ficha linda, a desconfiança desaparece e você diz: <em>"Como você já pagou R$ 350, eu abato 100% desse valor para a gente completar o seu Biossite + WhatsApp PRO + Gestão Mensal!"</em></p>
  </div>
</div>
"""
            },
            {
                "num": 3,
                "module": "Módulo 3 • Cronograma de Entrega em 48h",
                "title": "Como Entregar os 4 Pilares do Combo 360° em 4 horas de Trabalho Líquido",
                "duration": "12 min",
                "summary": "A linha de montagem otimizada para que você aproveite o mesmo briefing para entregar GMN, Biossite, Plaquinha NFC e WhatsApp PRO sem retrabalho.",
                "content_html": """
<h4>Por que o Combo 360° dá quase o mesmo trabalho de 1 serviço isolado?</h4>
<p>Porque <strong>80% do trabalho de qualquer serviço digital é coletar o briefing (logo, fotos, textos dos serviços e acessos)</strong>! Uma vez que você coletou as fotos e os 10 serviços principais do cliente, você usa exatamente o mesmo material nos 4 pilares:</p>
<ol>
  <li><strong>Hora 1 (Google Meu Negócio):</strong> Ajusta categorias, descrição de 750 caracteres, cadastra os 10 serviços na vitrine do Google, sobe as fotos e responde às avaliações.</li>
  <li><strong>Hora 2 (Biossite / Landing Page 5 Blocos):</strong> Duplica seu template base, insere a mesma logo, os mesmos textos dos serviços e as mesmas avaliações do Google, e publica o link.</li>
  <li><strong>Hora 3 (WhatsApp Business PRO):</strong> Usa as mesmas fotos quadradas dos serviços para subir no Catálogo Nativo do WhatsApp Web, cria as 5 etiquetas coloridas e cola os 10 atalhos <code>/</code>.</li>
  <li><strong>Hora 4 (Plaquinha NFC):</strong> Pega o link curto de avaliação do Google Meu Negócio, grava a tag NTAG215 no app <em>NFC Tools</em> em 30 segundos, imprime a arte no Canva e encaixa no display de acrílico!</li>
</ol>
<p>Resultado: <strong>4 horas de execução organizada = R$ 1.197 a R$ 1.897 no bolso + R$ 297 a R$ 497/mês de recorrência!</strong></p>
"""
            },
            {
                "num": 4,
                "module": "Módulo 4 • Cobrança Recorrente & Contrato",
                "title": "Como Configurar Assinatura Automática (Pix/Boleto/Cartão) e Formalizar Sem Burocracia",
                "duration": "10 min",
                "summary": "Nunca perca tempo cobrando mensalidade manualmente no WhatsApp: automatize tudo e use o Termo de Prestação de Serviços simplificado.",
                "content_html": """
<h4>1. Como Automatizar a Cobrança das suas Mensalidades</h4>
<p>O maior erro de consultores iniciantes é mandar mensagem todo dia 10 perguntando: <em>"Oi cliente, consegue fazer o Pix da mensalidade deste mês?"</em>. Isso gera atrito e faz o cliente repensar toda vez.</p>
<ul>
  <li>Crie uma conta gratuita no <strong>Asaas</strong>, <strong>Mercado Pago</strong> ou <strong>Efí Bank</strong>.</li>
  <li>Cadastre o cliente na modalidade <strong>Assinatura / Cobrança Recorrente Mensal</strong> (via Cartão de Crédito recorrente que não ocupa o limite total do cartão, ou Boleto/Pix Automático com lembrete por WhatsApp/E-mail enviado pela própria plataforma).</li>
</ul>

<h4>2. Contrato Simples de 1 Página ou Aceite por WhatsApp</h4>
<p>Para tickets de R$ 500 a R$ 2.500, um contrato longo de 10 páginas assusta o pequeno empresário. Utilize o <strong>Termo de Escopo e Prestação de Serviços de 1 Página</strong> (disponível na aba de Proposta deste curso) enviado em PDF ou com aceite direto no WhatsApp, sem multa abusiva de fidelidade — quem retém o cliente é o <strong>Relatório Mensal de Resultados</strong>!</p>
"""
            },
            {
                "num": 5,
                "module": "Módulo 5 • Retenção de 12+ Meses",
                "title": "O Relatório Mensal de 1 Página no WhatsApp que Blinda Contra Cancelamentos",
                "duration": "08 min",
                "summary": "Como provar para o seu cliente todo dia 05 do mês que a mensalidade de R$ 297 gerou R$ 4.000+ em novos negócios para ele.",
                "content_html": """
<h4>Por que clientes cancelam agências comuns, mas NUNCA cancelam quem envia este relatório?</h4>
<p>Clientes só cancelam uma mensalidade quando acham que <em>"ninguém está fazendo nada lá"</em>. Todo dia 05 do mês, dedique 15 minutos ao cliente e envie no WhatsApp o <strong>Print de Desempenho do Google Meu Negócio + Resumo Mensal</strong>:</p>

<div class="sa-callout sa-callout-emerald">
  <strong>📊 Modelo de Mensagem de Relatório Mensal (Todo Dia 05):</strong>
  <p><em>"Bom dia, [Nome]! Segue o balanço da sua Estrutura Presença Local 360° nos últimos 30 dias:<br>
  📍 <strong>Visualizações da sua empresa no Google Maps:</strong> 1.840 pessoas (+34%)<br>
  📞 <strong>Cliques em Ligar / Website / WhatsApp:</strong> 112 contatos diretos<br>
  🚗 <strong>Solicitações de Rota até a sua porta:</strong> 78 clientes<br>
  ⭐ <strong>Novas Avaliações 5 Estrelas captadas pela Plaquinha NFC:</strong> +19 avaliações (sua nota subiu para 4.9!)<br>
  ✅ Já publicamos as 4 atualizações do mês no Google, atualizamos o Biossite e respondemos 100% dos reviews com SEO Local. Vamos com tudo para este novo mês!"</em></p>
</div>
"""
            }
        ],
        "delivery_guide": """ROTEIRO OPERACIONAL DE ENTREGA — COMBO PRESENÇA LOCAL 360° (CRONOGRAMA DE 48 HORAS)

ETAPA 1 — ONBOARDING ÚNICO (15 MINUTOS APÓS O PIX DE ENTRADA)
• Envie o Checklist Único de Boas-Vindas pedindo:
  1. Liberação do seu Gmail como Administrador no Google Meu Negócio (business.google.com);
  2. Logotipo em boa qualidade + 10 a 15 fotos reais do local, equipe e serviços;
  3. Lista dos 10 principais serviços/produtos + horários + chave Pix;
  4. Escolha do modelo da Plaquinha Acrílico NFC (aprovação da arte enviada por você).

ETAPA 2 — DIA 1: GOOGLE MEU NEGÓCIO + BIOSSITE (2 HORAS)
• Configure Categorias (Principal + 5 Secundárias), Descrição de 750 caracteres, Horários, Atributos e 5 Perguntas & Respostas no Google Meu Negócio.
• Cadastre a Vitrine de Produtos/Serviços no Google e responda às últimas 20 avaliações com palavras-chave locais.
• Monte o Biossite / Landing Page Local em 5 Blocos usando exatamente as mesmas fotos, serviços e avaliações do Google, e vincule o link no botão "Website" do Google Maps e na Bio do Instagram.

ETAPA 3 — DIA 2: WHATSAPP BUSINESS PRO + PLAQUINHA NFC (2 HORAS)
• Conecte via WhatsApp Web (ou acesso remoto) e suba o Catálogo Nativo com os mesmos 10 serviços e fotos quadradas (1080x1080px).
• Configure o Funil de 5 Etiquetas Coloridas, Mensagem de Saudação/Ausência e os 12 Atalhos de Resposta Rápida (/).
• Grave o chip NTAG215 da Plaquinha Acrílico com o link direto de avaliação 5 estrelas do Google pelo app NFC Tools e entregue ao cliente com o Cartão de Script de Balcão.

ETAPA 4 — ROTINA MENSAL DE RETENÇÃO (40 MINUTOS POR MÊS)
• Publique 1 postagem semanal de Atualização/Oferta no Google Meu Negócio.
• Responda às novas avaliações recebidas pela Plaquinha NFC com palavras-chave da cidade.
• Todo dia 05, envie no WhatsApp o Print de Desempenho (Visualizações, Ligações, Rotas e Novas Avaliações).""",
        "pricing_tiers": [
            {
                "name": "Combo Start (Google + WhatsApp)",
                "badge": "Entrada Consultiva",
                "cost": "R$ 0,00 (2h30 do seu tempo)",
                "setup_price": "R$ 697 a R$ 890",
                "monthly_price": "R$ 197/mês",
                "profit_margin": "100% de margem líquida",
                "deliverables": [
                    "Otimização Completa do Google Meu Negócio para o Top 3 Local",
                    "Estruturação do WhatsApp Business PRO (Catálogo + 5 Etiquetas + 10 Atalhos)",
                    "Link direto de avaliações + Resposta otimizada aos reviews",
                    "Manutenção mensal do Google Meu Negócio + Relatório de Chamadas"
                ]
            },
            {
                "name": "Combo Presença Local 360° (4 em 1)",
                "badge": "Mais Vendido ★",
                "cost": "R$ 16,00 (1 Placa Acrílico NFC)",
                "setup_price": "R$ 1.197 a R$ 1.497",
                "monthly_price": "R$ 297 a R$ 397/mês",
                "profit_margin": "~98% de margem + Alta Recorrência",
                "deliverables": [
                    "1. Otimização Completa do Perfil da Empresa no Google Maps (SEO Local Top 3)",
                    "2. Criação de Biossite / Landing Page Local de Alta Conversão (5 Blocos)",
                    "3. Estruturação do WhatsApp Business PRO (Catálogo Nativo + Funil de Etiquetas)",
                    "4. 1 Display Físico em Acrílico com Chip NFC + QR Code Google 5⭐ para o balcão",
                    "Gestão Mensal Contínua (Posts semanais no Google, Hospedagem VIP e Relatório)"
                ]
            },
            {
                "name": "Combo Dominância Local VIP",
                "badge": "Ticket Premium",
                "cost": "R$ 45,00 (3 Placas NFC + Domínio)",
                "setup_price": "R$ 1.897 a R$ 2.500",
                "monthly_price": "R$ 497 a R$ 597/mês",
                "profit_margin": "~97% de margem líquida",
                "deliverables": [
                    "Todos os 4 Pilares do Combo Presença Local 360° com Domínio Próprio (.com.br)",
                    "Kit Completo com 3 Displays NFC de Acrílico (Google 5⭐ + Wi-Fi Automático + Pix/Catálogo)",
                    "Treinamento da equipe comercial para recuperação diária de orçamentos no WhatsApp",
                    "Gestão Mensal Completa de SEO Local, Atualizações de Landing Page e Relatório Executivo"
                ]
            }
        ],
        "checklist": [
            "Selecionar no MapaLeads empresas com Score IA ≥ 75 que acumulem 2 ou mais oportunidades (ex: GMN + Sem Site + Poucos Reviews)",
            "Utilizar o botão 'Gerar Diagnóstico e Mensagem IA' na gaveta do lead para mapear todas as lacunas da empresa",
            "Abordar o decisor enviando o Diagnóstico Visual + VSL do Combo 360° (vsl-combo.mp4)",
            "Apresentar a Proposta de 3 Colunas ancorando o valor avulso (R$ 1.888) contra o Combo 360° (R$ 1.197 + R$ 297/mês)",
            "Se o cliente hesitar no valor total, aplicar a 'Escada de Valor': fechar 1 pilar de entrada e abater no upgrade em 7 dias",
            "Coletar o Briefing Único (acesso gerente GMN, logo, 12 fotos reais e 10 serviços principais)",
            "Executar o Cronograma de 48h: Dia 1 (Google Meu Negócio + Biossite) e Dia 2 (WhatsApp PRO + Plaquinha NFC)",
            "Cadastrar a assinatura mensal de R$ 297/mês no Asaas/Mercado Pago para cobrança automática sem atrito",
            "Enviar todo dia 05 o Relatório Mensal de 1 Página no WhatsApp com os prints de chamadas, rotas e novas avaliações"
        ],
        "script_approach": """[MENSAGEM 1 — DIAGNÓSTICO EXECUTIVO 360°]
Olá, tudo bem? Aqui é o [Seu Nome], consultor de posicionamento local.
Falo com o responsável pela *[Nome da Empresa]*?
Fiz uma auditoria rápida na presença digital de vocês aqui em *[Cidade]* (Google Maps, página de conversão e atendimento no WhatsApp) e identifiquei 3 pontos onde clientes prontos para comprar estão escapando para a concorrência.
Posso te mandar um vídeo de 28 segundos mostrando o diagnóstico que preparei para a *[Nome da Empresa]*?

[MENSAGEM 2 — ENVIE A VSL (vsl-combo.mp4) + OS 4 PILARES]
Veja esse resumo rápido de 28 segundos acima 👆
Para uma empresa local dominar as vendas na cidade hoje sem depender de gastar fortunas em anúncios, ela precisa de 4 pilares integrados que nós entregamos prontos em *48 horas*:
1️⃣ *Google Meu Negócio Otimizado (Top 3):* Para ser encontrado por quem pesquisa seu serviço em *[Cidade]*;
2️⃣ *Biossite / Landing Page Express:* Para transformar cliques do Google e Instagram em autoridade imediata;
3️⃣ *WhatsApp Business PRO Estruturado:* Com catálogo visual, atalhos de 1 clique e etiquetas para não perder nenhum orçamento;
4️⃣ *Display Físico NFC + QR Code no Balcão:* Para seus clientes satisfeitos encostarem o celular e multiplicarem suas avaliações 5 estrelas no Google.

Em vez de contratar 4 fornecedores separados, nós implementamos o *Combo Presença Local 360°* completo com quase 40% de economia. Posso te enviar a proposta resumida aqui pelo WhatsApp para você avaliar?""",
        "script_followup": """[FOLLOW-UP 1 — 24 HORAS DEPOIS]
Oi! Tudo bem por aí?
Só para complementar o diagnóstico da *[Nome da Empresa]*: nós podemos tanto implementar o *Combo 360° Completo* de uma vez em 48 horas, quanto começar por *1 pilar prioritário* (como a Otimização do Google Maps + Plaquinha NFC de balcão) para você já sentir o aumento de avaliações e chamadas na primeira semana.
Qual formato faz mais sentido para o momento de vocês hoje?

[FOLLOW-UP 2 — 72 HORAS DEPOIS]
Fala! Estou fechando o cronograma de implantações 360° desta semana aqui em *[Cidade]*.
Para quem fecha o pacote completo esta semana, estou incluindo o Display Físico de Acrílico NFC + QR Code personalizado com a sua logo 100% bonificado no projeto.
Consegue olhar a proposta que te enviei acima para reservarmos a vaga da *[Nome da Empresa]*?

[ROTEIRO DE ÁUDIO DE 35 SEGUNDOS]
"Fala, tudo bem? Olha só, a maioria das empresas locais tenta arrumar uma coisinha solta no marketing e não vê resultado porque o funil fica furado: não adianta aparecer no Google se não tem uma página que passa confiança, se o WhatsApp demora pra responder o orçamento e se o cliente vai embora sem deixar avaliação 5 estrelas. No nosso Combo Presença Local 360, a gente entrega esses 4 pilares 100% prontos em 48 horas, inclusive a plaquinha física de acrílico com chip por aproximação pro seu balcão. Dá uma olhada nas opções que te mandei acima e me diz qual delas encaixa melhor pra você!" """,
        "script_objections": """• "Gostei muito de tudo, mas R$ 1.197 agora pesa no meu fluxo de caixa..."
Resposta: "Entendo perfeitamente! Podemos fazer de duas formas super leves: 1) Parcelar em até 3x ou 4x no cartão (onde uma única venda extra por mês já paga a parcela com sobra), OU 2) Começarmos hoje pelo nosso 'Passo 1' (Otimização do Google Meu Negócio + Plaquinha NFC por apenas R$ 447) e, na semana que vem, quando você já estiver colhendo os resultados, abatemos 100% desse valor para concluir o Biossite e o WhatsApp PRO. Qual prefere?"

• "Por que tem a mensalidade de R$ 297/mês depois?"
Resposta: "A mensalidade cobre toda a manutenção ativa para você não precisar contratar funcionário de marketing: inclui a hospedagem VIP da sua página, 4 postagens mensais de ofertas/atualizações na sua ficha do Google Maps, resposta profissional com palavras-chave a todas as novas avaliações de clientes, atualizações de preços no seu catálogo do WhatsApp e o Relatório Mensal de Ligações e Rotas geradas. E não tem multa de fidelidade: você continua porque vê o retorno todo mês!" """,
        "proposal_script": """📋 *PROPOSTA COMERCIAL — COMBO PRESENÇA LOCAL 360° (4 PILARES EM 48 HORAS)*
Empresa: *[Nome da Empresa]* | Cidade: *[Cidade]*

🎯 *OBJETIVO:*
Implementar a estrutura completa de Atração, Conversão, Atendimento e Autoridade Local para posicionar sua empresa à frente da concorrência na cidade.

✅ *OS 4 PILARES INCLUSOS NO PROJETO (CHAVE NA MÃO):*
1️⃣ *Otimização Google Meu Negócio Top 3* _(Valor avulso: R$ 597)_
   Categorias estratégicas, descrição SEO Local, vitrine de 12 serviços, 15 fotos, FAQ e resposta a avaliações.
2️⃣ *Landing Page / Biossite de Alta Conversão* _(Valor avulso: R$ 597)_
   Página mobile-first em 5 blocos integrada ao Google Maps e à Bio do Instagram com botões diretos para o WhatsApp.
3️⃣ *Estruturação WhatsApp Business PRO* _(Valor avulso: R$ 497)_
   Catálogo nativo com até 12 serviços, 12 atalhos de resposta rápida (/) e funil de 5 etiquetas para recuperar orçamentos.
4️⃣ *Display Físico Acrílico NFC + QR Code Google 5⭐* _(Valor avulso: R$ 197)_
   Placa personalizada com a sua logo para o cliente avaliar com 5 estrelas por aproximação no balcão.

💰 *ANCORAGEM & CONDIÇÃO ESPECIAL DO COMBO:*
• Valor total dos 4 serviços contratados separadamente: ~R$ 1.888,00~
• *Investimento no Combo Presença Local 360°:* **R$ 1.197,00** (50% no início + 50% na entrega em 48h via Pix, ou em até 4x no cartão).
• *Plano de Gestão & Manutenção Mensal (a partir do 2º mês):* **R$ 297,00/mês** (inclui hospedagem da página, 4 posts mensais no Google, resposta contínua de avaliações com SEO Local, atualizações de catálogo e Relatório Mensal de Chamadas/Rotas).

🚀 *TERMO DE GARANTIA & INÍCIO:*
Sem fidelidade forçada. Entrega completa dos 4 pilares em até 48 horas úteis após o envio da logo e fotos.
Qual forma de pagamento (Pix 50/50 ou Cartão) fica melhor para darmos o start hoje?"""
    }
]
