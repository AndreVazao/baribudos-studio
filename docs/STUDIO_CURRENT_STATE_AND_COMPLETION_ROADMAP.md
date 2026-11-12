# Baribudos Studio — estado real, auditoria inicial e plano de conclusão

**Data de referência:** 2026-11-12  
**Branch/base auditada:** main — commit 0caa6a780293e642bebfe148673fbe205115388d  
**Tipo:** inventário estrutural e revisão estática orientada a evidência. Não é certificação de produção nem teste end-to-end.

> Regra de leitura: existir no repositório não significa funcionar de ponta a ponta. Os estados distinguem documentação, código presente, implementação parcial e validação operacional real.

## 1. Resumo executivo

O Baribudos Studio não é um projeto vazio. É um monorepo com backend FastAPI, frontend React/Vite, empacotamento Tauri/Capacitor, serviços de domínio, uma superfície API extensa e módulos reais para produção editorial, IP/canon, áudio, imagem, publicação e controlo do Website.

Mas a dimensão do código e o número de painéis não provam que o produto esteja pronto. A revisão confirma blocos úteis e fronteiras críticas incompletas:

1. **Segurança familiar P0:** autenticação atual por nome/PIN, credenciais em texto simples, sessão restaurada pelo cliente sem validação no servidor e autorização que historicamente aceita identidade/função fornecidas pelo cliente. A montagem estática da raiz de storage exige prova HTTP e correção.
2. **Operação real P0:** não foi demonstrado um percurso completo e repetível com dados reais, desde o arranque local e login até produção, pacote, publicação e recuperação após falha.
3. **Website autónomo P0/P1:** issue Website #30 permanece aberta; a ingestão não demonstra materialização durável dos bytes dos assets no Website.
4. **Produção editorial P1:** existem serviços para história, layout, ilustração, e-book, audiobook e vídeo, mas os estados de conclusão/readiness precisam de validação de artefactos. A geração narrativa principal ainda é baseada em templates.
5. **Multilinguismo P1:** os dez idiomas configurados estão identificados, mas as traduções encontradas são simuladas.
6. **Modelo editorial P1:** a relação persistente livro → audiobook → minissérie → episódios → temporadas/séries → coleções ainda precisa de confirmação e consolidação.
7. **Créditos, vozes e direitos P1:** existem componentes parciais para perfis vocais, AudioCast, créditos e patrocínios; falta provar atribuição completa e enforcement em cada asset e no gate final.
8. **UX e rotina familiar P1/P2:** existem muitos painéis, mas o fluxo de operador, estados, mensagens, permissões e experiência infantil precisam de ensaio com utilizadores e conteúdos reais.

**Conclusão atual:** base técnica substancial, mas não há evidência suficiente para declarar o Studio pronto para uso familiar diário seguro e fiável. A primeira missão é fechar o inventário e os gates de segurança/operação; só depois ampliar funcionalidades.

## 2. Objetivo funcional que governa a implementação

### 2.1 Studio

O Studio é o núcleo privado/doméstico e autoridade editorial interna. Deve correr no computador familiar, com acesso restrito à família autorizada, e permitir:
- gerir a produtora **Baribudo Estúdio** e várias propriedades intelectuais;
- criar, importar, editar, rever e aprovar histórias;
- gerir IPs, sagas, canons narrativos/pedagógicos/visuais, personagens e continuidade;
- produzir e-books, ilustrações, audiobooks, vídeos/minisséries e séries;
- gerir pessoas, créditos, vozes, consentimentos e patrocínios;
- controlar catálogo, metadados, preços e publicação;
- controlar o Website através de um único dashboard operacional;
- acompanhar encomendas, clientes, vendas, métricas, distribuição e incidentes;
- manter memória operacional local e contexto técnico duradouro.

### 2.2 Website

O Website é a camada pública, comercial e de distribuição. Deve continuar a apresentar catálogo, servir assets, vender e permitir acesso a compras mesmo quando o computador doméstico/Studio está desligado.

O Studio inicia sincronização outbound autenticada; não deve ser exposto diretamente à Internet. O Website persiste os bytes dos conteúdos públicos aprovados e gere os estados externos observados.

### 2.3 Produtora e IP

- **Baribudo Estúdio:** produtora/plataforma de criação e gestão de múltiplas IPs.
- **Baribudos:** uma IP/universo específico, atualmente a primeira em desenvolvimento.
- Canons e personagens pertencem ao âmbito de cada IP. Partilha entre IPs exige relação explícita, autorizada e rastreável.

A especificação aprovada está em docs/BARIBUDOS_PRODUCT_VISION_AND_ACCEPTANCE.md; requisitos de produtora, IP, créditos e vozes em docs/STUDIO_PRODUCER_IP_VOICE_CREDITS_REQUIREMENTS.md; requisitos multilingues em docs/MULTILINGUAL_FIRST_GLOBAL_LAUNCH_REQUIREMENTS.md.

## 3. Inventário estrutural do repositório

Snapshot do Git tree de main no commit acima:

| Elemento | Quantidade / tecnologia | Leitura |
|---|---:|---|
| Ficheiros versionados | 403 | Monorepo de dimensão relevante |
| Documentos em docs/ | 67 | Documentação extensa; alguns documentos antigos/TBD carecem de reconciliação |
| Routers API em studio_core/api/routes/ | 78 módulos Python | Superfície HTTP extensa; permissões têm de ser inventariadas |
| Serviços em studio_core/services/ | 85 módulos Python | Muitos domínios já têm implementação |
| Testes Python em tests/ | 4 ficheiros | Cobertura visível pequena face à superfície |
| Componentes React em client/mobile-app/src/components/ | 49 componentes JSX | Dashboard abrangente; qualidade não inferida pelo número |
| Backend | FastAPI / Pydantic | API Python |
| Frontend | React 18 / Vite | Cliente web também usado no desktop/mobile |
| Desktop | Tauri 2 | Empacotamento declarado |
| Android | Capacitor 7 | Integração Android declarada |
| Persistência de domínio | JSON em storage local | Não foi identificado ORM/DB central no Studio |
| Memória | Markdown local + integração Obsidian | Separada da memória técnica de desenvolvimento |

### 3.1 Domínios de backend já presentes

- API, utilizadores, settings, health, diagnostics, jobs e memória persistente.
- Projetos, story source, story layout, geração de histórias e traduções.
- IPs, sagas, canons, personagens, branding, paletas e visual sets.
- Ilustração, providers, assets e pipeline visual.
- Perfis de voz, biblioteca, preview, casting e AudioCast.
- E-books, audiobooks, vídeos, final media render e produção editorial.
- Publication package, freeze, readiness, credits, sponsors e commercial metadata.
- Distribution Hub, Website contract, publisher, bundles, reconcile e controlo.
- Operações locais: instalação/gestão de engines, updater, secret control, DB/deploy control.

### 3.2 Clientes e UX existentes

A aplicação React contém painéis de dashboard, criação de projeto, story source/layout, pipeline de ilustração, perfis vocais, AudioCast, outputs, pipeline de produção, pacote/readiness, publicação e controlo Website, IP/canon/personagens, créditos, updater, vault e diagnóstico.

**Não está demonstrado:** que todos os botões e fluxos estejam ligados a operações completas, que erros sejam tratados consistentemente, que o dashboard guie bem uma pessoa não técnica ou que permissões server-side correspondam ao que a UI apresenta.

### 3.3 Testes e validação

Existem quatro ficheiros de testes Python no diretório tests/ no snapshot:
- test_audiobook_fallbacks.py
- test_project_factory_video_sequence.py
- test_route_audit.py
- test_website_publish_retry.py

Os workflows GitHub Actions incluem Studio CI, Distribution Hub smoke, publish ops, Website visibility e builds desktop/Android. CI verde valida apenas os passos efetivamente executados pelo workflow; não substitui testes de hardware, browser, rede familiar, providers, qualidade de áudio/vídeo ou compras sandbox.

## 4. Idiomas pré-configurados no arranque

A constante SUPPORTED_LANGUAGES em studio_core/services/language_service.py define atualmente:

| Código | Nome |
|---|---|
| pt-PT | Português (Portugal) |
| pt-BR | Português (Brasil) |
| en | Inglês |
| es | Espanhol |
| fr | Francês |
| de | Alemão |
| it | Italiano |
| nl | Neerlandês |
| zh | Chinês |
| ja | Japonês |

Esta é a lista existente a preservar como ponto de partida. Não acrescentar nem retirar idiomas por iniciativa técnica sem decisão editorial.

**Estado real:** a lista existe como constante, mas get_supported_languages() devolve a lista mutável diretamente. Os modelos de projeto e bootstrap usam pt-PT como default; não foi demonstrado que todas as dez línguas estejam ativas em todas as IPs, formatos ou providers.

**Gap crítico:** language_service.py acrescenta um prefixo [idioma] ao texto para destinos diferentes de pt-PT; story_translation_service.py acrescenta uma etiqueta de tradução e mantém o texto original. Isto é simulação, não tradução. Não marcar estas variantes como tradução concluída/aprovada/publicável.

## 5. Estado por domínio — classificação inicial

Legenda:
- **RED / P0:** risco ou bloqueio que impede utilização real segura.
- **RED / P1:** capacidade central não comprovada ou comportamento enganador.
- **AMARELO:** há código/documentação útil, mas falta integração/validação.
- **VERDE:** apenas quando existe evidência suficiente de operação real; não atribuir verde por mera presença de ficheiros.

| Domínio | Estado inicial | Evidência / gap principal | Prioridade |
|---|---|---|---|
| Visão e arquitetura Studio/Website | AMARELO | Especificação funcional aprovada; implementação tem de ser reconciliada | P1 |
| Arranque/instalação local | AMARELO | Scripts e guias existem; falta ensaio limpo, reinício e recuperação | P0/P1 |
| Login familiar | RED | Nome/PIN em vez de e-mail pré-registado; PIN simples; troca obrigatória não provada | P0 |
| Sessão e RBAC API | RED | Cliente persiste utilizador em localStorage; sessão central/deny-by-default não demonstrada | P0 |
| Storage privado | RED | /storage monta raiz que contém JSON internos; confirmar por HTTP isolado e fechar | P0 |
| CORS/rede doméstica | RED | Configuração observada usa origins wildcard com credenciais e host default 0.0.0.0 | P0 |
| Perfis e permissões infantis | AMARELO/RED | Papéis existem no modelo, mas enforcement por endpoint e experiência guiada não demonstrados | P0 |
| IPs/sagas/canons | AMARELO | Serviços e ficheiros canónicos; validar isolamento multi-IP e uso efetivo | P1 |
| Criação de histórias | AMARELO/RED | Templates determinísticos na via principal; provider generativo real não comprovado | P1 |
| Story source/layout | AMARELO | Serviços e painéis existem; falta ensaio de edição, persistência, versionamento e UX | P1 |
| Ilustração/consistência visual | AMARELO | Pipeline e visual sets existem; falta validação em outputs reais | P1 |
| E-book | AMARELO | Serviço existe; falta validar EPUB, TOC, fontes, imagens, metadados e leitura | P1 |
| Audiobook | AMARELO | PR #33 removeu fallback silencioso; falta validação técnica/editorial de ficheiros reais | P1 |
| Vídeo/minissérie | AMARELO/RED | PR #32 corrigiu passagem de frames; renderer continua slideshow/animatic | P1 |
| Modelo livro/série/episódio/coleção | RED/AMARELO | Entidades/linhagem persistente não comprovadas na via principal | P1 |
| Tradução/localização | RED | Implementação atual é fake translation; lista de dez idiomas não significa capacidade | P1 |
| Vozes, clones e consentimentos | AMARELO | Perfis/casting parciais; enforcement por língua/IP/mercado/uso não provado | P1 |
| Créditos finais | AMARELO | Serviço/painel existe; falta derivação completa e gate obrigatório | P1 |
| Patrocínios | AMARELO | Serviço/escopos documentados; falta comprovar composição e gate por IP/produto/campanha | P2 |
| Package freeze/readiness | AMARELO/RED | Serviços existem; checks têm de validar artefactos, direitos, créditos e locale | P1 |
| Studio → Website | AMARELO | Contrato/publisher/bundle/reconcile existem; provar auth, idempotência, hashes e recuperação | P0/P1 |
| Website assets duráveis/offline | RED | Website issue #30 aberta; materialização dos bytes não provada | P0/P1 |
| Dashboard Website único | AMARELO | Painéis e endpoints existem; validar ações com Website real | P1 |
| Distribuição externa | AMARELO/RED | Roadmap/adapters e estados existem; APIs, contas e fluxos reais não demonstrados | P2 |
| Memória persistente | AMARELO | Serviço Markdown/Obsidian existe; confirmar segurança das rotas e fluxo de consulta | P1 |
| Builds desktop/Android | AMARELO | Workflows/scripts existem; instalação e smoke em dispositivos não comprovados | P1 |
| Observabilidade/backup/restore | AMARELO/RED | Logs/jobs/smokes existem; falta prova de backup automático e restore | P0/P1 |

Esta matriz é um ponto de partida. Cada linha deve evoluir para estado, evidência, teste, PR e critério de aceitação próprios.

## 6. Achados técnicos concretos que exigem prioridade

### 6.1 Segurança de acesso — P0

A auditoria existente docs/security/2026-11-09-authentication-and-storage-exposure-audit.md descreve os riscos. A revisão adicional do snapshot confirma:

- auth_service.py compara nome e PIN diretamente contra data/users.json.
- O modelo User ainda contém pin: str; modelos de criação/alteração aceitam PIN.
- LoginPanel.jsx apresenta defaults de nome André e PIN 1234.
- client/mobile-app/src/api/core.js guarda o utilizador completo em localStorage e não acrescenta bearer token aos helpers HTTP.
- App.jsx restaura o utilizador guardado sem validar sessão server-side.
- config.py define host default 0.0.0.0.
- A auditoria de main.py identificou a montagem estática da raiz de storage. A prova HTTP continua pendente; tratar como exposição potencial até fechar.

**Objetivo de correção:** e-mail pré-registado; primeiro acesso temporário com troca obrigatória; hash forte; sessão assinada/expirada/revogável; revogação em alteração/reset; RBAC central server-side; negação por defeito; rate-limit; CORS explícito; storage privado por defeito; allowlist apenas para assets publicados; migração coordenada desktop/móvel.

Não aplicar patch isolado que remova o PIN da UI sem proteger todos os endpoints e sem plano de migração/rollback.

### 6.2 Geração narrativa — P1

A via principal usa generate_canon_story() e templates em português, selecionando personagens/temas/estrutura. Isto é útil como fallback ou protótipo, mas não equivale a geração generativa de histórias completas. O provider deve ser configurável e o resultado validado contra canon narrativo, pedagógico, personagens, idade e locale.

### 6.3 Áudio — P1

A PR Studio #33 foi integrada e removeu o comportamento que podia devolver WAV silencioso como fallback válido. Corrige um falso sucesso conhecido, mas não prova qualidade de audiobooks reais. Faltam gates para ficheiro válido, duração, silêncio, clipping, integridade, pronúncia, completude, capítulos, língua e aprovação humana.

### 6.4 Vídeo — P1

A PR Studio #32 foi integrada e passou a sequência de frames aprovados para o renderer. É uma correção útil, mas o serviço atual monta vídeo a partir de imagens estáticas e áudio. Não chamar a isto animação/minissérie animada com movimento de personagens ou sincronização labial.

### 6.5 Website autónomo — P0/P1

A issue AndreVazao/baribudos-studio-website#30 continua aberta. O contrato tem de garantir que os bytes dos assets aprovados são enviados e persistidos em storage durável controlado pelo Website, com hash/MIME/tamanho, idempotência, rollback e URLs finais sem dependência do PC doméstico. Não assumir fornecedor de object storage ou credenciais sem inspecionar configuração e decisão existente.

### 6.6 Estado de PRs Website conhecidos

Na última pesquisa do Website estavam abertas:
- PR #26 — sync atómico/idempotente; testes de integração, checksum recalculado e concorrência ainda pendentes segundo a descrição da PR.
- PR #27 — invalidação de sessões de utilizadores desativados; teste runtime com cookie existente pendente.
- PR #28 — captura PayPal; validação sandbox pendente.
- PR #29 — webhook Stripe; validação sandbox pendente.

Reconsultar estado, head SHA, draft e CI antes de qualquer decisão. Não fazer merge apenas por CI/Vercel verdes quando testes sandbox/integração fazem parte do critério.

## 7. Sequência de execução — do princípio ao fim

A ordem é deliberada. Não começar por traduzir, gerar vídeos ou acrescentar painéis enquanto a fronteira de segurança e a persistência não estiverem controladas.

### Fase 0 — Baseline e preservação
- [ ] Confirmar branch/main, PRs abertas, workflows e issues dos dois repositórios.
- [ ] Inventariar dados persistentes, canons, assets, contratos, endpoints e configurações.
- [ ] Identificar ficheiros de dados locais e política de backup/restore.
- [ ] Comparar funcionalidades únicas dos repositórios históricos sem apagar nem substituir históricos.
- [ ] Produzir matriz de rotas: endpoint → público/privado → permissão → serviço chamado → dados/side effects → teste.
- [ ] Confirmar os dez idiomas predefinidos e a origem de configuração usada por frontend/backend.

**Saída:** baseline técnico versionado e plano de migração com rollback.

### Fase 1 — Segurança e acesso familiar (P0)
- [ ] Provar em ambiente isolado os caminhos HTTP de storage e retirar a raiz privada da superfície estática.
- [ ] Separar assets publicados de dados, uploads privados, vozes, logs, backups e exports.
- [ ] Implementar login por e-mail pré-registado e credencial temporária/primeiro acesso.
- [ ] Hash de credenciais e sessão server-side.
- [ ] Bloquear endpoints normais antes da troca obrigatória da credencial.
- [ ] Implementar reset pelo owner, must_change_password e revogação de sessões.
- [ ] Implementar RBAC deny-by-default em todas as rotas e serviços sensíveis.
- [ ] Separar capacidades de criança, colaborador, editor, administrador e owner.
- [ ] Migrar cliente React/Tauri/Capacitor para sessão real.
- [ ] Restringir CORS e configurar rede privada doméstica.
- [ ] Testes 401/403, role forgery, utilizador desativado, sessão expirada/revogada, CORS e storage.

**Gate:** nenhum acesso sem autorização; nenhum dado privado servido; nenhum papel controlado pelo cliente; fluxos desktop/móvel funcionais.

### Fase 2 — Operação local e fiabilidade (P0/P1)
- [ ] Instalação limpa em PC Windows alvo.
- [ ] Arranque, health, logs, restart e shutdown controlados.
- [ ] Configuração explícita de storage, backups e recuperação.
- [ ] Verificar serviços externos/locais necessários e respetiva deteção.
- [ ] Testar falta de espaço, provider indisponível, rede desligada e reinício durante job.
- [ ] Jobs duráveis, estados e retries seguros; evitar tarefas duplicadas.
- [ ] Executar builds e smoke tests em ambiente real; registar artefactos e versões.

**Gate:** o Studio instala, arranca, recupera e mantém dados sem intervenção de programador.

### Fase 3 — Modelo de dados editorial (P1)
- [ ] Formalizar IP, saga, canonical work, story version e language edition.
- [ ] Formalizar Book/Publication, Audiobook, MiniSeries, Episode, Season/Series e Collection/Volume.
- [ ] Relacionar outputs com a mesma versão editorial aprovada e canon usado.
- [ ] Definir versionamento, lineage, imutabilidade de versões aprovadas e tarefas de revisão.
- [ ] Tornar agrupamento configurável por IP/saga; não fixar cinco livros por volume sem decisão.
- [ ] Migrar dados atuais com backup e compatibilidade.

**Gate:** reconstruir a proveniência e a relação de todos os produtos e edições.

### Fase 4 — Pipeline editorial real (P1)
- [ ] Provider generativo configurável (local/remoto) com timeouts, schema, logs e custos.
- [ ] Contexto inclui canon, personagens, idade, pedagogia, arco e locale.
- [ ] Revisão humana: editar, aprovar, rejeitar, regenerar e versionar.
- [ ] Paginação, storyboard, ilustrações, capa e visual canon.
- [ ] E-book com validação EPUB e leitura real.
- [ ] Audiobook com validação técnica e editorial.
- [ ] Vídeo com cenas, duração, montagem e áudio; distinguir animatic de animação.
- [ ] Readiness por artefacto e etapa; completed só quando outputs obrigatórios passaram validação.
- [ ] Gate impede outputs incompletos, incorretos ou sem aprovação.

**Gate:** produção de um livro completo com outputs rastreáveis, reproduzíveis e aprovados.

### Fase 5 — Multilinguismo (P1)
- [ ] Centralizar os dez idiomas existentes sem os alterar.
- [ ] Definir catálogo locale, nomes nativos, convenções regionais, estado por IP/formato e reviewers.
- [ ] Obra canónica + edições localizadas com source lineage e versionamento.
- [ ] Provider real de tradução/localização e glossário por IP.
- [ ] Validar texto, humor, pedagogia, continuidade e adequação etária.
- [ ] Não marcar IA como aprovada sem revisão humana.
- [ ] TTS/dobragem por locale com qualidade, pronúncia e consentimento.
- [ ] Legendas, closed captions, créditos, metadados, thumbnails e copy localizados.
- [ ] Release matrix por idioma/formato; coordenado ou faseado por decisão do owner.
- [ ] Falha de uma língua não invalida edições publicadas noutras línguas.

**Gate:** projeto piloto com as dez línguas configuradas, estados reais por etapa e sem falsas traduções.

### Fase 6 — Direitos, pessoas, vozes, créditos e patrocínios (P1/P2)
- [ ] Registo central de pessoas separado de contas de login.
- [ ] Contribuições por asset e produto, com origem, titular, papel e aprovação.
- [ ] Perfis de voz original, clones e variantes com lineage imutável.
- [ ] Consentimento por língua, IP, mercado, canal e uso comercial.
- [ ] Salvaguardas reforçadas e autorização parental para menores.
- [ ] Créditos derivados dos assets efetivamente usados na versão final.
- [ ] Patrocínios por escopo global/IP/saga/product/campaign sem herança não autorizada.
- [ ] Gate bloqueia publicação quando faltam atribuições, consentimentos ou decisão de exceção.

**Gate:** pacote publicado contém créditos corretos e consentimentos comprovados.

### Fase 7 — Website independente e dashboard único (P0/P1)
- [ ] Resolver Website #30 com storage durável de bytes.
- [ ] Contrato Studio → Website versionado, autenticado, checksum verificado, idempotente e reprocessável.
- [ ] Publicação transacional: nenhum catálogo ativo com assets por materializar.
- [ ] URLs públicos finais nunca dependem do PC doméstico.
- [ ] Testar downloads, biblioteca, checkout e páginas públicas com Studio desligado.
- [ ] Studio apresenta catálogo, clientes, encomendas, vendas, métricas, canais, estados e divergências.
- [ ] Reconcile oferece diagnóstico e ação corretiva clara.
- [ ] Separar auth de família e auth de clientes Website.

**Gate:** desligar o PC não afeta Website, vendas, downloads ou biblioteca.

### Fase 8 — Distribuição externa e lançamento (P2)
- [ ] Validar capacidade/API oficial por plataforma e direitos.
- [ ] Preparar primeiro canal externo com submissão assistida se não houver API.
- [ ] Aprovação por IP, idioma, mercado, produto e canal.
- [ ] Registar IDs/recibos/estados reais, não simular publicação ou royalties.
- [ ] Testar recuperação, duplicados, replays e falhas de provider.
- [ ] Lançar piloto controlado e só depois ampliar.

### Fase 9 — Aceitação final
- [ ] Testes com proprietário, adulto editor e perfil infantil supervisionado.
- [ ] Fluxo completo real: criar IP/saga/projeto → história → aprovação → e-book → audiobook → minissérie → pacote → Website → compra/download → reconcile.
- [ ] Testar dez línguas com estados de qualidade verdadeiros.
- [ ] Testar Studio offline depois da publicação.
- [ ] Testar backup/restore e atualização.
- [ ] Segurança e permissões verificadas por endpoint.
- [ ] Documentação, runbooks, métricas e suporte familiar concluídos.

**O Studio só é considerado pronto quando estes gates forem demonstrados com evidência, não quando a lista de tarefas estiver implementada em código.**

## 8. Regras de execução e governação

1. Trabalhar em branches dedicadas e PRs pequenas, com âmbito coeso.
2. Fazer diff review, CI e testes específicos antes de merge.
3. CI verde não substitui testes manuais/sandbox/real hardware quando necessários.
4. Não fazer alterações destrutivas a dados nem migrações sem backup, ensaio e rollback.
5. Não remover serviços ou ficheiros históricos sem mapear consumidores.
6. Preservar canons e assets existentes; não os regenerar/substituir sem aprovação.
7. Não expor o Studio à Internet para resolver sincronização.
8. Não simular tradução, áudio, vídeo, publicação, pagamento ou vendas como sucesso.
9. Cada funcionalidade tem estado explícito: não iniciado, em curso, implementado, validado, bloqueado.
10. Cada finding liga-se a evidência, issue/PR, teste e critério de aceitação.
11. Atualizar este documento e a memória AndreOS no fim de cada marco importante.
12. Continuar a partir do estado registado, sem pedir ao proprietário para repetir contexto.

## 9. Documentos de referência e autoridade

### Visão e produto
- docs/BARIBUDOS_PRODUCT_VISION_AND_ACCEPTANCE.md
- docs/STUDIO_PRODUCER_IP_VOICE_CREDITS_REQUIREMENTS.md
- docs/MULTILINGUAL_FIRST_GLOBAL_LAUNCH_REQUIREMENTS.md
- docs/MULTI_IP_SAGA_PRINCIPLE.md

### Auditorias técnicas
- docs/security/2026-11-09-authentication-and-storage-exposure-audit.md
- docs/2026-11-12-editorial-pipeline-gap-audit.md
- docs/TRUE_PRODUCTION_FLOW_AUDIT_V1.md
- docs/OPERATIONAL_AUDIT_CHECKLIST_V1.md
- docs/OPERATIONAL_EXECUTION_MATRIX_V1.md

### Operação e Website
- docs/LOCAL_PACKAGING_AND_RUN.md
- docs/RUNBOOK.md
- docs/STUDIO_WEBSITE_OPERATIONAL_HANDOFF_V1.md
- docs/EXTERNAL_CHANNELS_ROADMAP.md
- Repositório Website: AndreVazao/baribudos-studio-website
- Website issue #30: materialização durável de assets.

### Memória
- docs/PERSISTENT_MEMORY.md — memória operacional local do Studio.
- AndreVazao/andreos-memory — memória técnica de longo prazo para desenvolvimento e continuidade.

**Atenção:** a pesquisa de repositórios mostrou que AndreVazao/andreos-memory está atualmente com visibilidade pública, apesar de documentação antiga o descrever como privado. Rever visibilidade e conteúdo antes de guardar informação pessoal, credenciais ou material sensível. Nunca guardar segredos em Git.

## 10. Registo de alterações deste snapshot

- 2026-11-12: inventário estrutural de main, 403 ficheiros, 78 routers, 85 serviços, 4 ficheiros de testes Python, 49 componentes JSX e 67 documentos.
- 2026-11-12: confirmada lista inicial de dez idiomas em language_service.py.
- 2026-11-12: PR Studio #34 integrada — requisitos de produtora/IP, pessoas, créditos, vozes, patrocínios e reset de credencial.
- 2026-11-12: PR Studio #35 integrada — requisitos multilingual-first e lançamento global coordenado.
- 2026-11-12: PR Studio #32 e #33 já integradas — passagem de frames aprovados para renderer e remoção do fallback de audiobook silencioso.
- 2026-11-12: mantidos como bloqueios principais segurança familiar, storage privado, pipeline editorial real, tradução real e autonomia de assets do Website.

**Este documento é um snapshot vivo.** Atualizar estado, evidência, datas, PRs e testes quando novas auditorias ou implementações alterarem a realidade do produto.
