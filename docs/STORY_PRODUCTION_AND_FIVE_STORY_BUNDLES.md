# Baribudos — produção editorial e volumes de cinco histórias

**Estado:** builders técnicos existentes; volume, guia e compilação bloqueados até existir aprovação humana autenticada e persistente. A CI não concede aprovação nem autorização de publicação.

## Unidade editorial

Cada história é uma unidade autónoma e mantém o canon da sua própria IP. Para cada revisão editorial aprovada, o Studio deverá preparar, de forma independente:

1. Texto canónico e versões localizadas, cada uma com revisão própria.
2. Revisão humana, editorial e pedagógica.
3. Continuidade visual, créditos, direitos e consentimentos.
4. E-book EPUB.
5. Audiobook no idioma aprovado, sem reutilizar automaticamente a sua faixa como narração da minissérie.
6. Episódio/minissérie individual, com guião, narração e assets próprios.
7. Validação técnica e editorial de cada artefacto.

A geração de um ficheiro não o torna aprovado. Um EPUB, WAV, slideshow ou animatic só pode ser declarado concluído no âmbito correspondente depois de validado; a aprovação editorial não substitui a validação de cada artefacto.

## Regra do volume de cinco

Um volume só pode ser formado quando existirem **cinco revisões de histórias distintas**, da mesma IP, saga e locale, cada uma com:

- identidade e revisão imutáveis;
- checksum do conteúdo e do canon aplicável;
- decisão humana explícita, autenticada no servidor e persistida, ligada à revisão/checksum exatos;
- episódio individual validado;
- créditos, direitos e consentimentos aplicáveis.

O volume conserva os cinco livros e os cinco episódios individuais, pela ordem editorial, e acrescenta um guia para pais e uma compilação dos cinco episódios. A compilação não cria uma sexta história, não substitui os episódios e não é uma temporada de oito episódios. A sexta história elegível inicia o volume seguinte; nunca é anexada silenciosamente a um volume fechado.

O guia para pais exige revisão humana própria. A compilação exige validação audiovisual própria. Nenhum dos dois fica aprovado por ter sido gerado.

## Duração e canon

A issue [#55 — duração adaptativa por IP/faixa etária](https://github.com/AndreVazao/baribudos-studio/issues/55) e os canons atuais prevalecem sobre referências fixas antigas:

- Para Baribudos (4–10 anos), cerca de **5 minutos por minissérie individual** é uma referência editorial inicial, não um limite rígido nem uma janela de rejeição.
- Não existe mínimo/máximo universal para episódios ou compilações.
- A compilação preserva a soma das durações reais dos cinco episódios e das transições necessárias, sem padding, loops ou cortes forçados.
- O audiobook tem duração independente e preserva a história integral.
- Outras IPs definem os seus próprios públicos, canon, ritmo e recomendações; não herdam automaticamente a política Baribudos.

## Aprovação: fronteira de segurança atual

Os campos `approved`, `editorial_status` e `approval_state` dentro de project JSON, payloads ou dados enviados pelo cliente **não são decisões humanas autenticadas** e nunca podem autorizar produção, guia, compilação ou publicação.

No código atual desta branch, `story_bundle_service._approved()` falha em segurança e devolve sempre `false` até existir um resolver de decisões server-side. Por isso:

- `select_complete_story_groups()` não aceita grupos baseados em flags do projeto;
- `build_five_story_bundle()` permanece em `waiting_for_five_approved_stories`;
- os builders de guia e compilação recusam membros sem decisão autorizada;
- não existe endpoint novo, migração, alteração de dados ou mudança de clientes nesta frente.

Este bloqueio é intencional. A próxima implementação depende de autenticação/RBAC central, ledger de revisões ligado à geração e um registo append-only de decisões humanas com ator autenticado, revisão/checksum/canon ligados, idempotência, revogação e supersessão. A aprovação editorial não equivale a autorização de publicação.

## Validação cloud e limites

O workflow cloud usa uma VM efémera e ferramentas multimédia para validar tecnicamente artefactos de teste. O teste de integração atual gera apenas uma história sintética e verifica EPUB, WAV e animatic/slideshow. Cinco linhas de fixture com flags de aprovação falsificadas são usadas apenas para provar que o gate as rejeita.

O relatório esperado declara explicitamente:

- `validation_scope=synthetic fixture validation only`;
- `human_editorial_approvals=0`;
- `client_approval_flags_accepted=false`;
- nenhum guia de volume nem filme compilatório gerado;
- nenhuma publicação ou temporada criada.

Isto não é produção editorial real, não são cinco histórias canónicas distintas, não comprova vozes/consentimentos/assets finais e não aprova BB-001.

## Bloqueios antes da primeira produção real

1. Concluir autenticação server-side, RBAC, sessão e migração coordenada React/Tauri/Capacitor.
2. Ligar o ledger append-only à geração, preservando revisões anteriores, lineage, prompt/modelo, locale e checksums.
3. Implementar decisões humanas server-side, imutáveis, autenticadas e ligadas à revisão exata.
4. Implementar seleção idempotente de cinco revisões elegíveis e persistir a identidade/ordem do volume.
5. Completar localização real com revisão humana por idioma.
6. Validar continuidade visual, créditos, direitos e consentimentos.
7. Produzir e validar EPUB, audiobook e episódio individual com assets reais autorizados.
8. Só depois gerar guia e compilação de cinco episódios e submetê-los à revisão humana própria.
9. Publicar/sincronizar para Website apenas após gates editoriais, comerciais e de direitos, com pacote congelado e recibo.

Não alterar produção, dados, schema, migrations aplicadas, credenciais, secrets, permissões, buckets, storage ou infraestrutura nesta fase. O Studio doméstico permanece privado e não é exposto à Internet.
