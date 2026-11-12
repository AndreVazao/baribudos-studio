# Baribudos — visão de produto, modelo familiar e critérios de aceitação

**Estado:** especificação funcional de referência, aprovada pelo proprietário em 2026-11-12.  
**Âmbito:** Baribudos Studio, Baribudos Website, pipeline editorial e distribuição externa.

> Esta especificação esclarece a intenção do produto. Não substitui nem apaga canons, contratos de API ou documentação técnica existente. Preservar dados e comportamentos atuais até qualquer divergência ser analisada.

## 1. Origem e identidade da marca

Baribudos é uma marca familiar em desenvolvimento, inspirada nas histórias dos “Baribudos na floresta” que o fundador recorda de ouvir do avô paterno durante a infância. O projeto procura recuperar esse património afetivo, reinterpretá-lo para a realidade atual e transformá-lo num universo original de histórias, personagens e conteúdos infantis.

A marca ainda não está formalmente registada. Não declarar que existe registo legal ou exclusividade jurídica até isso ser efetivamente tratado. Preservar documentação, autoria, versões e datas de criação para apoiar futura proteção da marca e propriedade intelectual.

A referência a séries familiares de qualidade como Bluey é apenas uma referência de ambição editorial: personagens recorrentes, relações familiares, humor, emoção, continuidade e histórias com significado. Não copiar personagens, nomes, design, universo, episódios, diálogos ou identidade visual de obras existentes.

## 2. Dois softwares, um centro de comando

### 2.1 Baribudos Studio — autoridade interna e familiar

O Studio é privado, doméstico e de acesso restrito ao fundador e à família autorizada. Corre num computador privado em casa, que funciona como servidor local do ecossistema.

É a autoridade interna para:
- criar, importar, rever e aprovar histórias;
- gerir marca, IPs, sagas, personagens e canons;
- manter continuidade narrativa e visual;
- orquestrar e-books, audiobooks, ilustrações, minisséries, séries, coleções e materiais pedagógicos;
- gerir utilizadores familiares e permissões;
- aprovar versões finais, catálogo, metadados, preços, territórios, direitos e canais;
- comandar o Website através de um dashboard único;
- consultar vendas, encomendas, clientes, desempenho por canal e alertas operacionais.

O utilizador não deve precisar de abrir um segundo dashboard de administração para gerir o Website. O Website pode ter serviços e APIs próprios, mas o painel operacional principal é o Studio.

### 2.2 Baribudos Website — presença pública e distribuição

O Website é a camada pública, alojada externamente e disponível mesmo quando o computador doméstico/Studio está desligado.

Responsabilidades:
- apresentar marca, histórias, livros, audiobooks, vídeos, séries e catálogo aprovado;
- servir páginas públicas, campanhas, previews e conteúdos promocionais;
- vender produtos, processar checkout e pagamentos, gerir contas de clientes e bibliotecas;
- manter catálogo, assets e encomendas no ambiente público;
- gerir conectores/adapters de distribuição para plataformas externas, quando houver integração oficial e autorizada;
- acompanhar estado de publicação, vendas, unidades, receitas, royalties e relatórios disponibilizados por cada plataforma;
- reconciliar dados comerciais e devolver métricas/eventos ao Studio.

O Website é a autoridade operacional externa sobre o estado observado nos marketplaces e plataformas (IDs de listagem, processamento e relatórios recebidos). Não é a autoridade editorial nem pode alterar autonomamente conteúdo aprovado, canon ou preço-base definido no Studio. Preços específicos por canal só podem resultar de uma política de conversão/território explicitamente aprovada no Studio.

### 2.3 Ligação Studio → Website

- O Studio inicia a sincronização outbound; não expor diretamente o computador doméstico à Internet.
- Comunicação autenticada, versionada, auditável e repetível, com validação de payload e integridade dos assets.
- O Website persiste a publicação aprovada e todos os bytes necessários em armazenamento durável controlado pelo Website.
- Depois da publicação confirmada, páginas, previews, downloads, checkout e biblioteca não podem depender de URLs, ficheiros ou serviços no computador doméstico.
- O Studio pode desligar-se sem interromper o Website, as vendas ou o acesso a compras já realizadas.
- Eventos e relatórios comerciais ficam no Website e são reconciliados pelo Studio quando este voltar a ligar-se.
- Falhas devem ser visíveis no dashboard do Studio; nunca marcar uma publicação como concluída antes da confirmação real.

## 3. Utilizadores do Studio: família fechada

### 3.1 Sem registo público

O Studio não é uma plataforma pública de contas. Não deve permitir auto-registo aberto. O proprietário pré-regista cada pessoa, com endereço de e-mail individual. O login identifica a pessoa pelo e-mail previamente autorizado.

As contas de clientes do Website são independentes das contas familiares do Studio. Não partilhar sessões, permissões ou credenciais entre os dois sistemas.

### 3.2 Primeiro acesso e credenciais individuais

Intenção funcional:
1. O proprietário cria/pre-regista a conta familiar com e-mail, nome, estado e permissões.
2. A pessoa usa a credencial temporária inicial atribuída para o primeiro acesso (a referência funcional atual é o PIN 1234).
3. O primeiro acesso força a definição imediata de uma credencial pessoal nova.
4. Até a alteração estar concluída, a conta só pode aceder ao fluxo de configuração inicial; não pode usar APIs, dashboard ou operações normais.
5. Depois da alteração, a credencial temporária deixa de funcionar. Cada pessoa passa a ter a sua própria credencial.
6. O proprietário pode desativar contas, redefinir o acesso e alterar permissões.

Requisitos de segurança:
- 1234 nunca pode ser credencial permanente, permitir acesso normal ou ser exposto em respostas API, logs ou cliente.
- A credencial temporária só pode ser aceite para uma conta previamente autorizada e apenas no fluxo de primeiro acesso; aplicar limitação de tentativas, bloqueio e auditoria.
- Preferir códigos temporários únicos por pessoa, com expiração e rotação, se isso puder ser introduzido sem contrariar o fluxo familiar. Se se mantiver o PIN inicial comum, restringir rigorosamente o primeiro acesso à rede privada e exigir a troca antes de qualquer outra operação.
- Guardar apenas hashes fortes de credenciais (Argon2id ou alternativa suportada e testada); nunca PIN/password em texto simples.
- Emitir sessões autenticadas pelo servidor, expiradas e revogáveis. Identidade e função vêm da sessão validada, nunca de user_name, user_role ou user_id enviados pelo cliente.
- Não manter o Studio exposto diretamente à Internet. Acesso remoto futuro deve usar solução privada autenticada, por exemplo VPN, depois de análise própria.
- O bootstrap do proprietário deve ser explícito e seguro, não a criação silenciosa de uma conta administrativa previsível em todas as instalações.

### 3.3 Modelo de permissões familiar

As permissões devem ser aplicadas no servidor e na interface. Ocultar botões não é autorização.

| Perfil funcional | Capacidades permitidas | Restrições |
|---|---|---|
| Proprietário | Controlo total, gestão de contas, permissões, canons, produção, aprovações, Website, preços, distribuição e operações | Ações críticas auditadas |
| Adulto administrador/editor | Criar e rever histórias, participar na produção e executar áreas atribuídas | Não pode alterar o proprietário nem elevar a própria função |
| Colaborador familiar | Participar em tarefas editoriais/voz autorizadas | Sem gestão de utilizadores, credenciais, preços ou publicação externa |
| Criança / pequeno colaborador | Gravar voz, responder a perguntas simples, ditar ideias e contribuir em experiências guiadas | Sem administração, compras, publicação, eliminação, dados de clientes, credenciais, integrações ou alteração de canons |
| Consulta | Ver apenas áreas expressamente autorizadas | Sem escrita |

Os filhos mais novos (atualmente com 4 e 6 anos) precisam de uma experiência infantil muito limitada e adequada à idade:
- botões grandes, linguagem simples e tarefas curtas;
- gravação de voz e ditado de ideias/histórias através de fluxos guiados;
- acesso apenas a projetos/atividades escolhidos pelo adulto;
- revisão e aprovação adulta antes de qualquer conteúdo se tornar oficial;
- nenhuma capacidade para publicar, comprar, alterar preços, gerir contas, apagar trabalho ou aceder a informação privada/comercial;
- supervisão adulta e proteção contra pedidos inadequados, exposição de dados pessoais e interações abertas não supervisionadas.

As funções existentes no modelo atual (owner, creator, admin, editor, voice-recorder, child, viewer) podem ser aproveitadas se forem mapeadas para uma matriz de permissões explícita. Os nomes das funções não provam que as permissões já estejam implementadas ou protegidas.

## 4. Produto editorial e pipeline

### 4.1 Fluxo de produção desejado

O Studio deve suportar modo manual assistido e modo automático orquestrado. Em ambos, a família mantém checkpoints claros e aprovação humana antes de congelar/publicar.

Fluxo conceptual:
1. Criar projeto/história a partir de ideia, texto, voz ou pedido de geração automática.
2. Gerar/rever a história e permitir rejeitar, editar ou pedir nova versão.
3. Carregar os canons da IP/saga aplicável e identificar personagens canónicas relevantes.
4. Validar continuidade narrativa, tom pedagógico e coerência dos personagens.
5. Aprovar e congelar o texto-base.
6. Gerar paginação, storyboard, capa e ilustrações.
7. Aplicar character lock e visual canon a todas as imagens.
8. Gerar o e-book e validar o artefacto final.
9. A partir do livro/texto aprovado, gerar o audiobook com casting vocal, narração e créditos.
10. A partir do livro e do audiobook aprovados, gerar a minissérie audiovisual correspondente.
11. Agrupar minisséries/livros relacionados numa série/temporada ou coleção maior, mantendo continuidade entre episódios e volumes.
12. Preparar metadados, materiais de promoção, guias para pais e pacote comercial.
13. Apresentar readiness e pedir aprovação humana final antes de publicar.
14. Enviar snapshot aprovado para o Website; distribuição externa é uma ação posterior e explicitamente aprovada.

Relações de conteúdo pretendidas:
- uma história aprovada origina um e-book;
- o e-book origina um audiobook;
- cada livro/audiobook tem uma minissérie associada;
- minisséries relacionadas são organizadas numa série/temporada;
- conjuntos de livros/minisséries formam coleções/volumes e podem alimentar séries mais abrangentes.

A quantidade de episódios, livros por coleção/volume e regras de agregação devem ser configuráveis por IP/saga. Um blueprint antigo propõe 5 livros por volume; manter isso como configuração/documentação existente, mas não fixar esse número globalmente sem validação funcional.

### 4.2 Personagens canónicos e consistência visual

Os personagens canónicos já têm documentação no Studio. Esses ficheiros são ativos centrais da propriedade intelectual e não devem ser substituídos por aproximações geradas livremente.

Requisitos:
- carregar personagens canónicos quando a história pertence à respetiva IP/saga;
- manter nome, anatomia, proporções, cores, marcas, roupa/figurino, acessórios, personalidade e relações consistentes;
- usar referências visuais aprovadas e visual sets como condicionantes de geração;
- preservar identidade entre capa, páginas, audiobook (casting) e minissérie;
- validar cada imagem contra regras canónicas e permitir rejeitar/regenerar imagens divergentes;
- versionar alterações aprovadas ao canon, com histórico e impacto nos projetos;
- não alterar o canon automaticamente porque uma geração produziu uma variação visual.

Canons identificados no código/documentação:
- characters-master.json
- visual-canon.json
- narrative-canon.json
- episode-canon.json
- series-arc-canon.json
- pedagogical-canon.json
- age-badge-canon.json

### 4.3 Objetivo pedagógico e proteção infantil

As histórias devem ajudar crianças a compreender situações difíceis e riscos reais de forma adequada à idade, sem as assustar nem culpabilizar.

Princípios editoriais:
- ensinar a reconhecer comportamentos inadequados, manipulação, pressão, segredo imposto, ameaças e situações inseguras;
- reforçar que a criança pode e deve pedir ajuda a adultos de confiança;
- ensinar a falar sobre o que aconteceu, mesmo quando sente medo, vergonha ou confusão;
- explicar que não tem de resolver situações perigosas sozinha;
- distinguir surpresas saudáveis de segredos que causam medo ou pedem ocultação;
- mostrar respostas seguras: afastar-se quando possível, procurar um adulto seguro e continuar a pedir ajuda se o primeiro adulto não ouvir;
- não culpabilizar a criança pelo comportamento de terceiros;
- adaptar linguagem, intensidade, exemplos e conclusão à faixa etária;
- incluir orientações e perguntas para pais/cuidadores quando apropriado.

As histórias podem abordar males da vida e ações prejudiciais de pessoas, mas não devem recorrer a descrições gráficas, exploração do medo, instruções perigosas ou encenações que incentivem a criança a confrontar sozinha uma pessoa potencialmente perigosa. A mensagem final deve ser clara, protetora e adequada ao desenvolvimento infantil.

## 5. Distribuição e canais externos

O Website é o gestor operacional dos conectores externos, mas o Studio decide o que pode sair e em que condições.

Canais a investigar/avaliar por tipo:
- e-books: Amazon KDP, Apple Books, Google Play Books, Kobo e outros distribuidores legítimos;
- audiobooks: Spotify for Authors, ACX/Audible, Google Play Books e outros canais adequados;
- vídeo/minisséries: YouTube e, quando elegível, descoberta no YouTube Kids;
- Website próprio: canal público primário e sempre sob controlo editorial do Studio.

Regras:
- não assumir que todas as plataformas têm API de publicação;
- usar APIs oficiais quando existirem e forem autorizadas; caso contrário, suportar preparação de pacote e submissão assistida/manual;
- YouTube Kids não deve ser tratado como destino com API de publicação direta nem como inclusão garantida;
- verificar direitos, territórios, exclusividade, royalties, formatos, identificadores e termos antes de cada canal;
- aprovação por canal, idioma, território, formato e janela de lançamento deve ficar registada no Studio;
- o Website recolhe estados e resultados reais das plataformas; não inventar vendas ou royalties quando o provider não os fornece.

## 6. Estado técnico observado no levantamento inicial (2026-11-12)

### Já existe, pelo menos parcialmente/documentalmente
- Backend do Studio em FastAPI e cliente React/Vite.
- Modelo de utilizador com nomes de função owner, creator, admin, editor, voice-recorder, child, viewer.
- Login por nome e PIN no código atual.
- Estruturas de canon narrativo, pedagógico, visual, episódios e personagens.
- Serviços para geração de histórias, produção editorial, e-book, audiobook, vídeo e pipeline de ilustração.
- Blueprint text-first que descreve tradução, paginação, ilustração, audiobook, minissérie, volumes e guias para pais.
- Website com catálogo, produtos, contas de clientes, biblioteca, checkout e providers Stripe/PayPal.
- Roadmap documental de distribuição externa e adapters para canais.

### Não está ainda demonstrado como concluído
- Login familiar por e-mail pré-registado e primeiro acesso com troca obrigatória de credencial.
- Sessão server-side e RBAC aplicado de forma consistente a todos os routers/serviços.
- Experiência infantil com permissões efetivamente aplicadas no servidor.
- Pipeline ponta-a-ponta automática com gates reais entre história, e-book, audiobook e minissérie.
- Consistência visual validada para todos os personagens em todas as gerações.
- Independência do Website relativamente aos ficheiros do Studio depois da publicação.
- Conectores externos operacionais, contas autorizadas e reconciliação real de vendas em cada plataforma.

### Riscos de segurança já documentados no Studio
A auditoria estática existente, em docs/security/2026-11-09-authentication-and-storage-exposure-audit.md, identificou:
- raiz de storage montada como ficheiros estáticos, com possível exposição de JSON operacionais;
- PIN inicial previsível e PINs em texto simples;
- respostas de API que podem devolver campos de PIN;
- identidade/permissões confiadas a parâmetros controlados pelo cliente;
- ausência de sessão server-side central;
- CORS wildcard com credenciais;
- 75 módulos de rotas a inventariar/proteger.

Isto é auditoria estática, não prova de exploração dinâmica. A correção tem de ser faseada e testada sem deixar rotas administrativas abertas nem quebrar desktop/móvel.

### Risco de autonomia do Website já documentado
A issue Website #30 identifica que a ingestão pode guardar URLs de assets sem materializar os bytes em storage durável do Website. Enquanto isso não for resolvido e testado, não se pode afirmar que o Website funciona integralmente com o Studio desligado.

## 7. Ordem de execução e gates

1. Preservar e inventariar: mapear código, dados, canons, APIs, serviços e dependências; fazer backup antes de migrações.
2. Fechar a segurança do Studio: proteger ficheiros, autenticação, sessões, RBAC, gestão familiar, primeiro acesso e testes de regressão.
3. Fechar a autonomia do Website: materializar assets em storage durável, validar hashes e provar operação com o Studio desligado.
4. Consolidar contrato Studio → Website: snapshots versionados, checksum realmente verificado, retry/reconciliação e auditoria.
5. Validar pipeline editorial ponta-a-ponta: história → canon → e-book → audiobook → minissérie → série/coleção, com aprovação e regressão visual.
6. Consolidar o dashboard único: operações do Website, canais, clientes, vendas, encomendas, métricas e erros visíveis no Studio.
7. Ativar distribuição externa por fases: um canal de cada vez, começando por piloto controlado e direitos confirmados.
8. Testar produto real: PC doméstico, rede familiar, dispositivos autorizados, Website público, compras, downloads e recuperação após falhas.

Cada avanço deve ser feito em PRs pequenas e independentes, com testes, revisão do diff e checks verdes antes de merge. Não fazer merge apenas porque o PR é mergeable; não contornar checks ou testes manuais relevantes. Não executar migrações destrutivas nem alterar infraestrutura/contratos externos sem autorização específica.

## 8. Critérios de conclusão do produto

### Studio
- Só pessoas pré-autorizadas da família conseguem entrar.
- Cada pessoa tem identidade e credencial própria; primeiro acesso força a troca da credencial temporária.
- Permissões são aplicadas no servidor e testadas por perfil.
- Crianças conseguem contribuir por voz/ideias em modo guiado, sem acesso administrativo.
- História pode ser criada, rejeitada, revista e aprovada.
- Canons são aplicados e preservados em todos os formatos.
- E-book, audiobook e minissérie são produzidos a partir da mesma versão aprovada.
- O dashboard único controla publicação, preços, catálogo, Website e distribuição.
- Existe histórico auditável de aprovações, alterações e operações.

### Website
- É público, independente e resiliente quando o Studio está desligado.
- Serve todos os assets a partir de armazenamento próprio/durável.
- Apresenta apenas conteúdo aprovado e preços autorizados.
- Vende com pagamentos confirmados e biblioteca consistente.
- Mantém encomendas, clientes, vendas e eventos para reconciliação.
- Executa ou acompanha distribuição externa sem inventar capacidades de plataformas.
- Devolve métricas e estados ao dashboard do Studio.

### Produto integrado
- O Studio é o centro de comando interno.
- O Website é a presença pública, canal de vendas e gestor operacional externo.
- Não existem dois dashboards de administração concorrentes.
- A indisponibilidade de uma plataforma externa não bloqueia o Website próprio.
- A indisponibilidade do Studio não bloqueia o Website nem o acesso dos clientes aos produtos comprados.

---

Esta especificação deve ser consultada em todas as decisões de arquitetura, produto, segurança, UX e novas funcionalidades do Baribudos. Atualizá-la apenas através de alterações deliberadas e rastreáveis, preservando o histórico.
