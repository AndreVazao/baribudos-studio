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


## 10. Atualização operacional — 12 de novembro de 2026 (execução posterior à baseline)

Esta secção acrescenta evidência operacional recolhida depois do snapshot estrutural acima. Não altera retroativamente os resultados dos testes anteriores.

### 10.1 Website de produção — bloqueio comercial P0

A issue [Website #35](https://github.com/AndreVazao/baribudos-studio-website/issues/35) regista falhas HTTP 500 em `/loja`, `/ips` e `/novidades`; homepage e login respondem HTTP 200. Os logs Vercel associam as falhas a `PrismaClientInitializationError` e `FATAL (ENOTFOUND): tenant/user not found`. O deployment Vercel estar READY não prova conectividade à base de dados.

A consulta read-only ao provider Supabase confirmou que o projeto existente `baribudos-studio-website` está com estado **INACTIVE**, região `eu-west-1`, PostgreSQL 17.6.1. Esta evidência confirma o estado do projeto no provider; não prova isoladamente se o erro de tenant/role decorre apenas da inatividade, de endpoint, role ou configuração de ligação.

**Restrição operacional:** não restaurar, pausar, substituir, criar projeto alternativo, alterar credenciais ou modificar variáveis de produção sem autorização explícita e confirmação do alvo. A recuperação deve preservar a instância e os dados existentes. Depois de autorizada, validar conectividade e as rotas públicas, catálogo, checkout, webhooks e biblioteca.

### 10.2 Website PR #26 — sincronização

A PR continua aberta/draft. O head reportado é `185523816ee1c242431024689221f434790444c0`. A normalização de capa vazia/omitida e os testes de URL absoluta/caminho relativo estão incluídos. CI, Prisma Generate, typecheck, unit tests, build e Vercel Preview foram reportados como sucesso.

Continuam gates obrigatórios antes de merge:
- integração PostgreSQL para concorrência, repetição, remoção de assets e rollback;
- recálculo real do SHA-256 com fixtures partilhadas e normalização idêntica entre Python e Node;
- constraint declarativa que garanta unicidade de `Product.publicationVariantId` por variante, com migração segura e tratamento de duplicados;
- materialização dos bytes dos assets em storage durável controlado pelo Website, que é acompanhada separadamente pela issue #30.

### 10.3 Studio PR #38 — produção audiovisual

A PR continua aberta/draft no head `912ad3746e0444f8c74865105550d1c1f6a53a3e`. Os caminhos manual e direto de exportação passam agora os frames aprovados do storyboard ao gerador de episódios. Studio CI #426 e Distribution Hub Smoke #33 foram reportados como sucesso, incluindo testes Python.

Falta ensaio real com FFmpeg, imagens aprovadas e áudio: confirmar duração, ordem, sincronização, MP4 reproduzível e resultado final. Os testes de encaminhamento não certificam qualidade audiovisual.

### 10.4 Segurança Studio — âmbito da auditoria

O inventário heurístico reportou 78 módulos de rotas, 233 handlers, 233 sem sinal local de autorização, 97 sensíveis/operacionais e 29 com referências a identidade fornecida pelo cliente. Estes números são sinais de triagem, não prova individual de exposição.

A revisão estática confirmou no snapshot consultado:
- CORS com origins wildcard e credenciais;
- montagem de toda a raiz de storage em `/storage`;
- criação automática do owner com PIN previsível `1234`;
- rotas de utilizadores que devolvem o registo completo e comparam PIN em texto simples;
- decisões de acesso a projetos baseadas em parâmetros de identidade/função fornecidos pelo cliente;
- ausência de verificação local visível nos módulos Secret Control, DB Control, Deploy Control e Updater, a exigir rastreio de middleware, dependências e serviços antes de concluir sobre cada endpoint.

Não fazer correções isoladas que deixem rotas ou clientes incompatíveis. Próxima saída técnica: matriz handler → dependências globais/router → principal server-side → autorização/serviço → dados e efeitos → testes 401/403, incluindo fluxos anónimos, sessão inválida/expirada/revogada e tentativa de falsificação de papel.

### 10.5 Ordem de execução atualizada

1. Obter autorização explícita para recuperar a instância Supabase existente; até lá, manter apenas investigação read-only.
2. Preparar e executar a recuperação controlada, com validação do estado do provider e preservação dos dados.
3. Fechar a matriz de segurança dos 233 handlers e desenhar a migração coordenada de autenticação/RBAC.
4. Resolver materialização durável de assets Website sem dependência do Studio doméstico.
5. Fechar os gates de integração, checksum e unicidade da PR Website #26.
6. Executar o ensaio audiovisual real exigido pela PR Studio #38.
7. Atualizar esta auditoria com evidência de runtime, testes e referências às PRs; não declarar conclusão com base apenas em CI verde.


## 11. Atualização de recuperação e sincronização — 12 de novembro de 2026 (posterior à secção 10)

Esta secção **substitui** as afirmações da secção 10.1 que indicavam Supabase INACTIVE e recuperação ainda não autorizada. A autorização explícita foi recebida e a recuperação controlada foi executada na instância original.

### 11.1 Supabase e Website após recuperação

- Projeto original preservado: `rpfyazuejafgxswrlbvw`, `baribudos-studio-website`, região `eu-west-1`, PostgreSQL 17.6.1.
- Restauro do projeto existente concluído; `get_project` confirmou `ACTIVE_HEALTHY`. Não foi criada instância substituta.
- Consulta SQL read-only confirmou ligação ao PostgreSQL 17.6 e existência das 14 tabelas Prisma, mais `public.system_metadata`.
- Migration registada: `20260527185301` (`phase_42_3_lite_stabilization`). Não foi aplicada qualquer migration durante a recuperação.
- Contagens read-only na base de produção: `User=2`; `StudioSettings=0`; `IntellectualProperty=0`; `Series=0`; `Publication=0`; `PublicationVariant=0`; `PublicationAsset=0`; `Product=0`; `Checkout=0`; `CheckoutItem=0`; `CustomerLibrary=0`; `BundleGroup=0`; `BundleGroupItem=0`.
- Smoke público sem autenticação nem writes: `/`, `/login`, `/loja`, `/ips`, `/novidades` responderam HTTP 200. A loja continua sem produtos; novidades declara ausência de novidades públicas. Isto não valida login, checkout, webhooks ou biblioteca.
- `GET /api/catalog/home` respondeu `ok=true`, com arrays `products=[]` e `bundles=[]`.
- Vercel runtime errors/logs na janela consultada (~30 min) sem erros; Supavisor entre 16:00–16:40 UTC sem correspondências ao erro tenant/user. Manter observação.
- `public.system_metadata` continua com RLS desativado e sem policies; Security Advisor reporta `rls_disabled_in_public`. Não ativar RLS antes de desenhar e validar policies.
- `DATABASE_URL` usa pooler transaction (6543); `DIRECT_URL` usa pooler session (5432), não o host direto. Não alterado; validar configuração Prisma/Supabase antes de qualquer mudança.
- Vercel reportou metadados `readable-secret` para algumas variáveis encriptadas. Não prova exposição pública. Nenhum segredo foi exposto, rodado ou alterado.

**Segurança da recuperação:** não foram alterados dados, schema, migrations, credenciais, env vars ou deployments; nenhuma compra, webhook ou write foi executado.

### 11.2 Catálogo vazio e reconciliação Studio → Website

A causa do catálogo vazio ainda não está provada. O publisher do Studio só envia uma publicação quando existe pacote congelado, política elegível e ação explícita de publicação. É necessário reconciliar os recibos locais `website_sync` com os IDs `publication_id`/`variant_id` no Website antes de reenviar qualquer conteúdo. O clone local disponível em `C:\\ProgramasGodMode\\baribudos-studio` está em `main` no commit `3cd6888`, não contém a pasta runtime `storage` e não é evidência do estado de produção do Studio. Não foram encontrados recibos runtime nesse clone. Não assumir que não existem noutro runtime.

### 11.3 Website PR #26 e issue #36 — estado reconciliado

- A PR Website #26 continua aberta/draft. O head documentado é `185523816ee1c242431024689221f434790444c0`; CI #156, Prisma Generate, typecheck, unit tests, build e Vercel Preview/Visibility foram reportados como sucesso.
- A branch da PR #26 já implementa transação Prisma Serializable, substituição determinística do conjunto de assets, rollback quando a escrita falha, validação comercial/preço, versão congelada, conflito retryable P2034 (HTTP 409 + Retry-After) e correção do contrato de capa vazia. O emissor Studio repete o mesmo body para conflitos transitórios.
- A inspeção do schema confirma `PublicationVariant.variantId` e `Product.slug` UNIQUE; `Product.publicationVariantId` não é UNIQUE. A proteção concorrente atual depende de Serializable + retry, não de constraint declarativa.
- O checksum SHA-256 é calculado no Studio sobre `json.dumps(envelope, ensure_ascii=False, sort_keys=True)` antes de incluir `checksum`. Em 12 Nov foi acrescentada ao branch Website #26 a verificação do digest sobre o body bruto, antes do Zod, com serialização compatível com Python e preservação de tokens numéricos (`1.0`). Foi criada fixture comum Python/Node com Unicode/emoji/decimais e testes de tampering. CI/typecheck/testes ainda pendentes de confirmação.
- Faltam testes reais de integração PostgreSQL: repetição, concorrência, rollback após falha de asset, replays e ausência de duplicados/inconsistências. Não declarar concluído apenas com CI.
- A issue Website #36 foi criada como checklist explícita de atomicidade e falha de assets, mas sobrepõe-se em grande parte à PR #26. A PR #26 é a via de implementação existente; a issue #36 deve acompanhar os critérios que ainda faltam, evitando uma segunda implementação paralela.
- Website issue #30 continua aberta: guardar URLs não prova que os bytes dos assets são materializados em storage durável próprio. Website deve funcionar com Studio/PC doméstico desligado.

### 11.4 Memória, repositórios locais e próximos passos

- O PC doméstico está online via Desktop Commander. Os clones locais Studio e Website estão limpos, em `main`, mas desatualizados face às branches/PRs remotas; não os usar para sobrescrever estado remoto.
- O diretório local do clone Studio não tem `storage/`; a memória/runtime operacional não foi localizada. A pesquisa de recibos `website_sync` permanece pendente até localizar a instalação/runtime correto.
- A memória técnica privada/AndreOS deve ser atualizada em paralelo com esta documentação; não guardar segredos nem conteúdo familiar privado em repositórios públicos.

### 11.5 Próxima sequência obrigatória

1. Localizar o runtime/instalação efetiva do Studio e obter, apenas em leitura, contagens/estados de projetos elegíveis, pacotes congelados e recibos `website_sync`; nunca expor conteúdo privado no relatório.
2. Comparar recibos com IDs de publicações/variantes/produtos/assets do Website; só então decidir republicações pontuais.
3. Continuar PR #26: integração PostgreSQL, checksum efetivo com fixtures Python/Node e política de unicidade por variante, sem migração destrutiva.
4. Resolver issue #30: materialização durável dos bytes, hash/MIME/tamanho, retries e teste com Studio desligado.
5. Rever RLS de `system_metadata` e o alerta `readable-secret`; nenhuma alteração sem desenho de policies/rotação coordenada.
6. Validar `DIRECT_URL` e Supavisor sem expor valores secretos.
7. Executar sandbox Stripe/PayPal, login, biblioteca e checkout só em ambiente de teste; não usar pagamentos reais.
8. Prosseguir com P0 de autenticação/RBAC/storage do Studio e validar todas as rotas; manter as fases editoriais e multilingues como pendentes até testes reais.


### 11.6 Investigação adicional do runtime e verificação SHA-256 — 12 Nov 2026, 21:06 UTC

**Pesquisa local (apenas leitura):**
- PC doméstico acessível. Foram verificados os clones `baribudos-studio`, `baribudos-studio-primary`, `baribudos-studio-home-edition` e `baribudos-studio-website` em `C:\\ProgramasGodMode`.
- Studio clone `main` está em `3cd6888`; Website clone `main` em `ecf001a`; histórico primary `main` em `0be88a4`; home-edition `main` em `076a509`. Não foram observadas alterações locais nestes clones.
- O home-edition implementa armazenamento local por defeito em `<process.cwd()>\\storage` (ou `BARIBUDOS_STORAGE_ROOT`), e o instalador cria `storage/data/projects.json`, `users.json`, etc. Essa pasta não existe no clone verificado.
- Pesquisa de ficheiros operacionais `projects.json`, `users.json`, `publications.json`, `settings.json` e `storage/data` nos quatro clones não encontrou resultados.
- Não foi encontrado processo Baribudos/uvicorn/node, listener nas portas 8787/8000/8001/5173/3000/8080, tarefa agendada com nome Studio/Baribudos, nem variáveis de ambiente `BARIBUDOS_STORAGE_ROOT`, `BARIBUDOS_HOME`, `BARIBUDOS_STUDIO_HOME`, `PORT` ou `HOST` ao nível User/Machine.
- Limite: o acesso do Desktop Commander não permitiu inspecionar diretamente alguns diretórios de perfil AppData; a ausência de runtime/recibos só está confirmada nas localizações acessíveis verificadas. Não concluir que os dados foram perdidos ou inexistentes noutro disco/perfil.

**Alterações de código Website PR #26 (branch `fix/v6-atomic-publication-sync`):**
- Adicionado `src/lib/publication-checksum.ts`: parser JSON que retém os tokens numéricos do body bruto, ordenação de chaves por code point Unicode, serialização equivalente ao `json.dumps(..., ensure_ascii=False, sort_keys=True)` do Studio e SHA-256 com comparação constante.
- Rota `POST /api/studio/publish` passa a ler o body uma vez, validar checksum antes de `JSON.parse`/Zod e rejeitar digest ausente/inválido com `publication_checksum_mismatch`, antes de qualquer write.
- Adicionados testes Node para fixture válida Python, Unicode/emoji, float token `1.0`, alteração de conteúdo, digest alterado, digest em falta e independência da ordem das chaves.
- Fixture `tests/fixtures/website-ingest-v1-checksum.json` partilhada byte a byte com o repo Studio; teste Python recalcula com o algoritmo de produção.
- Contrato documentado em Website `docs/STUDIO_INGEST_CHECKSUM_CONTRACT.md`.
- Commits no branch Website: `44324e1`, `60ed1bc`, `01e9f24`, `a4114ab`, `5e1e98b`, `87bcbd6`, `cd239ab` (sequência inclui helper, route, teste, correção de tipagem, fixture partilhada e documentação).
- A implementação ainda não é considerada validada até CI, typecheck e suite de testes confirmarem sucesso. Nenhuma alteração foi aplicada à produção.

**Próximos passos atualizados:**
1. Aguardar/verificar CI e corrigir erros do checksum antes de avançar para testes PostgreSQL.
2. Executar a fixture Python no repo Studio e fixture Node no Website; manter os bytes idênticos.
3. Continuar a localizar a instalação/runtime real do Studio noutros perfis/discos autorizados; pedir indicação de caminho apenas se a pesquisa local continuar bloqueada.
4. Reconciliar recibos reais com Website antes de qualquer republicação.
5. Completar testes PostgreSQL concorrentes/rollback, unicidade por variante e materialização durável de assets.

### 11.7 Resultado de validação do checksum — 12 Nov 2026, 21:12 UTC

- Website CI #161 terminou com `success` no head `cd239ab0249283937a1e0cafd90b1e0daa9373ff`.
- Confirmados como sucesso: instalação de dependências, Secret hygiene, Prisma Generate, Typecheck, Unit tests e Build.
- Repository Visibility Only #155 também terminou com sucesso.
- A validação Node do Website passou incluindo fixture partilhada, Unicode/emoji, float token `1.0`, tampering de conteúdo/digest e reordenação de chaves.
- O teste Python foi adicionado ao Studio, mas ainda não há execução CI/local registada para esse ficheiro. A fixture foi gerada com o algoritmo Python de produção e o digest conferido durante a criação.
- O gate de checksum no Website pode ser considerado validado pelo CI #161. PR #26 permanece draft porque faltam testes PostgreSQL reais, unicidade comercial por variante e assets duráveis (issue #30).

**Próxima etapa técnica:** analisar a infraestrutura de testes e as opções de storage durável do Website; não usar a base de produção para testes de escrita. A pesquisa do runtime Studio continua limitada aos caminhos acessíveis e não encontrou os recibos.

### 11.8 PostgreSQL CI de integração e inventário de storage — 12 Nov 2026, 21:15 UTC

**Website PR #26 — integração PostgreSQL:**
- Workflow `.github/workflows/website-ci.yml` agora provisiona PostgreSQL 17 efémero, aplica `prisma db push` somente nesse container e executa `tests/publication-sync.integration.test.ts` com `tsx@4.19.2`.
- Testes reais do serviço `syncPublicationToCommerce`: replay idempotente, substituição de assets, atualização de preço, rollback integral forçado por trigger PostgreSQL e duas entregas concorrentes com retry do envelope mais recente.
- Website CI #162 concluiu com sucesso os passos Prisma Generate, schema efémero, Typecheck, Unit tests, integração PostgreSQL e Build; job estava a finalizar na última consulta.
- Website CI #164 foi iniciado para validar a versão final do teste concorrente e a versão atualizada do workflow; ainda em execução.
- Nenhum teste usa a base Supabase de produção.

**Storage:**
- Consulta read-only de `storage.buckets` + `storage.objects` no Supabase original devolveu zero buckets.
- Listagem Vercel integration configurations para project e account/team devolveu zero integrações.
- Não foi criado bucket/store, segredo, env var, subscrição ou alteração de infraestrutura. Provider e eventual custo carecem de decisão explícita. Website issue #30 continua aberta.

**Próximos gates:**
1. Confirmar CI #164 completo.
2. Executar teste Python da fixture partilhada no Studio.
3. Resolver unicidade declarativa de `Product.publicationVariantId` com análise de dados históricos e migração segura.
4. Obter decisão explícita sobre provider/storage e limite de custo; só depois implementar upload, hash/MIME/tamanho e serving durável.
5. Continuar procura do runtime Studio nos caminhos/perfis/discos autorizados e reconciliar recibos.

### 11.9 Resultado final da validação PostgreSQL — 12 Nov 2026, 21:17 UTC

- Website CI #164 terminou `success` no head `ce9f9da7fd21c505524b1fea300c13218d95d90a`.
- Sucesso confirmado em todos os passos: container PostgreSQL, Prisma Generate, `prisma db push` isolado, Typecheck, Unit tests, testes de integração PostgreSQL e Build.
- Repository Visibility Only #158 terminou `success`.
- A suite de integração final inclui replay, substituição de assets, atualização de preço, rollback forçado por trigger PostgreSQL e duas entregas concorrentes com retry da versão mais recente.
- O Website CI #161 também passou o checksum real e fixture Node/Python.
- Fixture foi recalculada com Python `hashlib/json.dumps`; digest confere. O teste Python correspondente existe no repositório Studio, embora ainda sem execução CI própria.
- PR Website #26 permanece draft: falta resolver a unicidade/índice comercial por variante e materialização dos bytes em storage durável (provider não configurado). A issue #30 recebeu confirmação de zero buckets Supabase e zero integrações Vercel visíveis.
- Nenhum teste escreveu na base de produção; nenhuma infraestrutura de storage foi criada.
