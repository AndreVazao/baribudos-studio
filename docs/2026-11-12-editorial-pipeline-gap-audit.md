# Baribudos Studio — auditoria de lacunas da pipeline editorial

**Data:** 2026-11-12  
**Tipo:** revisão estática de código e documentação; não é teste de execução.  
**Objetivo:** comparar a pipeline real com a visão de produto aprovada em BARIBUDOS_PRODUCT_VISION_AND_ACCEPTANCE.md.

## Resultado executivo

O Studio já tem componentes reais para carregar canons, estruturar histórias, produzir EPUB, sintetizar áudio, gerar vídeo e registar execuções. Porém, a pipeline automática atual ainda não deve ser apresentada como uma linha editorial completa e fiável. Há diferenças importantes entre os nomes dos outputs e o conteúdo efetivamente produzido.

Não reescrever a pipeline toda de uma vez. Corrigir em etapas, com fixtures, testes unitários, testes de integração e aprovação de outputs.

## Achados confirmados no código

### P1 — geração automática de histórias é atualmente baseada em templates

Evidência:
- studio_core/services/project_factory_engine.py chama diretamente generate_canon_story() para criar as variantes.
- studio_core/services/story_generation_engine.py constrói as cenas a partir de templates fixos: introdução, problema, questionamento emocional, orientação, transformação e moral.
- A função seleciona protagonistas/personagens, tema de valor, estrutura narrativa e frase final a partir do runtime/canons, mas não chama um modelo generativo nem um serviço de IA nesta via principal.

Impacto:
- O modo auto pode criar um esqueleto narrativo coerente com alguns elementos do canon, mas não corresponde ainda à criação autónoma de histórias originais e ricas descrita pelo proprietário.
- A história pode parecer diferente pelo título/personagens/tema, embora a sequência e grande parte do texto sejam padrões fixos.

Correção pretendida:
- Separar o orquestrador editorial do provider de geração.
- Criar um contrato de geração com contexto obrigatório: canon narrativo, personagens permitidos, arco da série, canon pedagógico, faixa etária, idioma e objetivo da história.
- Usar provider configurável (local/remoto) com timeout, validação de schema, rastreio de modelo/prompt e tratamento de falhas.
- Manter o template atual como fallback explícito de protótipo, nunca apresentá-lo como geração IA concluída.
- Exigir revisão/edição/rejeição humana antes de aprovar a história.

### P1 — variantes de idioma não constituem ainda tradução fiável

Evidência:
- project_factory_engine.py cria uma variante por idioma chamando generate_canon_story().
- story_generation_engine.py define language nos metadados, mas as frases dos templates estão escritas em português.
- O raw_text do projeto só é reutilizado diretamente quando o idioma da variante coincide com o idioma principal; não foi identificada uma etapa de tradução nesta chamada principal.

Impacto:
- Uma variante pode declarar en-US, fr-FR ou outro idioma sem o conteúdo estar realmente traduzido.
- O Website pode receber conteúdo com metadados linguísticos incorretos.

Correção pretendida:
- Introduzir uma etapa explícita de tradução, com idioma de origem/destino, glossário de personagens/nomes próprios e revisão.
- Validar idioma real do texto e não marcar uma variante como pronta apenas porque existe um objeto com o código de idioma.
- Manter a versão original imutável e ligar cada tradução à sua versão de origem.

### P1 — integridade técnica dos segmentos WAV (correção em curso)

Evidência revista no código atual:
- _synthesize_system_tts() já falha explicitamente quando espeak/espeak-ng não está disponível ou quando a síntese falha; não cria um WAV silencioso como fallback.
- build_audiobook() rejeita resultados com ok=false e regista fallback_used/fallback_segments; os testes existentes cobrem a falha do motor local e a identificação do provider de fallback.
- Esta branch valida cada WAV devolvido pelo provider: formato PCM suportado, canais, sample width, sample rate, número de frames, comprimento integral e sinal não silencioso.
- A combinação rejeita segmentos com parâmetros WAV incompatíveis e não cria um ficheiro final para uma lista vazia ou inválida. O novo ficheiro é escrito temporariamente e só substitui o destino após a escrita completa.

Impacto antes da correção:
- Um provider podia devolver ok=true com um WAV vazio, truncado ou silencioso e o ficheiro podia ser aceite.
- Segmentos com parâmetros PCM diferentes podiam ser concatenados sob os parâmetros do primeiro segmento, produzindo áudio corrompido ou com velocidade/tom incorretos.
- Uma falha durante a escrita podia deixar um ficheiro final parcial.

Validação ainda necessária:
- Executar Studio CI e confirmar os testes de silêncio, ficheiro truncado, lista vazia, formatos incompatíveis e fallback válido.
- Ensaiar providers reais e avaliar pronúncia, idioma, clipping, pausas, duração e completude. A integridade técnica do WAV não certifica a qualidade editorial do audiobook.

### P1 — sequência de storyboard não chegava a todos os caminhos de vídeo

Evidência revista no código:
- build_video_frame_sequence() usa build_storyboard_manifest(), que por sua vez usa list_approved_frames(); só entram frames marcados approved=true e com image_path.
- O caminho automático de project_factory_engine já passa sequence_frames para build_series_episode(); tests/test_project_factory_video_sequence.py já protege esse comportamento.
- Dois caminhos alternativos ainda enviavam apenas capa e áudio: _run_manual_outputs() em production_pipeline_service.py e POST /videos/export/{project_id} em api/routes/videos.py.
- video_service.py cria slideshow quando recebe imagens existentes; sem sequência válida, usa uma única capa.

Impacto antes da correção:
- O mesmo projeto podia produzir uma sequência de cenas no caminho automático e um vídeo estático nos caminhos manual/export.
- A experiência dependia do endpoint/modo usado, apesar de existirem frames aprovados.

Correção aplicada nesta branch:
- Os dois caminhos alternativos passam agora a usar o mesmo construtor de sequência aprovada.
- Foram acrescentados testes que confirmam a passagem integral de sequence_frames na pipeline manual e na rota direta.
- Se não houver frames aprovados existentes, video_service mantém o fallback de capa e reporta frames_used=0; não inventa cenas.

Validação ainda necessária:
- Executar Studio CI para confirmar os novos testes e a compilação.
- Fazer um ensaio de integração com imagens reais aprovadas, áudio e FFmpeg para verificar duração, ordem, sincronização e reprodução do MP4. Os testes unitários de encaminhamento não certificam qualidade audiovisual.

### P1 — execução da pipeline pode marcar completed sem verificar os outputs

Evidência:
- studio_core/services/production_pipeline_service.py define state="completed" assim que run_project_factory_engine() ou _run_manual_outputs() regressa sem exceção.
- Não existe nesta função uma validação final dos artefactos: presença, tamanho, formato, duração, integridade, idioma ou qualidade de áudio/vídeo.
- project_factory_engine.py pode devolver cover=None quando não existe illustration_path, mas a execução global pode continuar e terminar como completed.
- A summary contém indicadores como cover_created e listas de idiomas, mas estes indicadores não bloqueiam o estado final.

Impacto:
- completed significa atualmente que a função terminou sem lançar exceção, não que todos os outputs pedidos estejam válidos e prontos.
- A interface pode transmitir uma conclusão mais forte do que a evidência técnica permite.

Correção pretendida:
- Introduzir estado por etapa: pending, running, succeeded, needs_review, blocked, failed.
- Validar cada artefacto após produção e antes de o marcar como succeeded.
- Calcular estado global a partir das etapas obrigatórias; permitir partial/needs_review sem falsos positivos.
- Guardar evidência de validação, versão, ficheiro, hash, duração, provider e mensagens de erro.
- Não congelar/publicar pacote enquanto os gates obrigatórios não estiverem aprovados.

### P1 — a minissérie não está ligada a uma entidade editorial persistente

Evidência:
- A factory produz outputs de vídeo indexados por idioma e o serviço de pipeline guarda esses outputs no projeto.
- Nesta via não foi demonstrado um modelo persistente de episódios, temporadas/séries, relações entre livro/audiobook e minissérie, ordem de episódios, versões ou estado de aprovação por episódio.

Impacto:
- A relação conceptual “um livro → audiobook → minissérie → série/temporada” ainda não está comprovada como modelo editorial rastreável.
- É difícil gerir temporadas, continuidade, versões, episódios e republicação multicanal com segurança se tudo ficar agregado a um único output de vídeo do projeto.

Correção pretendida:
- Definir entidades e relações explícitas para Book/Publication, Audiobook, MiniSeries, Episode, Season/Series e Collection/Volume.
- Ligar cada artefacto à mesma versão editorial aprovada e ao canon usado.
- Tornar as regras de agrupamento configuráveis por IP/saga, sem fixar globalmente a quantidade de livros/episódios.
- Preservar histórico quando um livro ou episódio é revisto.

### P2 — validação de prontidão pode ser demasiado superficial

Evidência:
- production_readiness_service.py inclui um check de produção que considera outputs prontos quando o objeto outputs é truthy.
- Os checks específicos de audiobook visíveis nesta camada verificam existência de texto, copy comercial e capa; não validam o ficheiro de áudio, duração, codec, silêncio ou créditos.
- A prontidão do pacote pode acrescentar outras validações através de build_publication_package(); estas têm de ser revistas separadamente antes de concluir que todo o gate é insuficiente.

Impacto:
- A pontuação pode refletir presença de metadados, não a validade dos artefactos.
- O dashboard pode mostrar “quase pronto” sem prova de que os ficheiros são utilizáveis.

Correção pretendida:
- Rever build_publication_package() e os seus checks antes de alterar o readiness.
- Criar validators por formato: EPUB, áudio, vídeo, imagens, legendas e metadados.
- Separar readiness editorial, técnica, comercial, direitos e distribuição.
- Mostrar a razão exata de cada bloqueio no dashboard.

## Outras áreas já identificadas

### Segurança e dados familiares — prioridade P0

Consultar docs/security/2026-11-09-authentication-and-storage-exposure-audit.md. Permanecem por resolver e testar:
- exposição potencial de data/*.json através da montagem estática de toda a raiz de storage;
- PINs em texto simples, PIN inicial previsível e respostas que podem devolver PIN;
- login atual por nome/PIN em vez de e-mail pré-registado;
- ausência de troca obrigatória de credencial no primeiro acesso;
- ausência de sessão server-side e autorização central em todos os routers;
- confiança em identidade/função enviada pelo cliente;
- CORS wildcard com credenciais.

O modelo familiar fechado, a experiência infantil e as permissões por idade estão definidos em BARIBUDOS_PRODUCT_VISION_AND_ACCEPTANCE.md. Não implementar apenas restrições de interface: a autorização tem de ser validada na API.

### Website independente — prioridade P0/P1

A issue AndreVazao/baribudos-studio-website#30 continua a bloquear a prova de autonomia: o Website guarda URLs de assets, mas ainda não está demonstrado que materializa os bytes num storage durável próprio. Nenhuma publicação deve ser considerada totalmente autónoma até os testes com Studio desligado passarem.

### Distribuição externa

A roadmap multicanal foi documentada e integrada no Website em 2026-11-12 (PR #33). É uma base de descoberta e planeamento, não prova de conectores ativos nem de contas/plataformas autorizadas.

## Ordem de correção recomendada

1. P0: conter e testar exposição de ficheiros internos e iniciar migração de autenticação familiar sem quebrar desktop/móvel.
2. P0: provar e corrigir a autonomia de assets do Website.
3. P1: corrigir falsos sucessos da pipeline, especialmente áudio silencioso e validação final de artefactos.
4. P1: passar efetivamente os frames aprovados para a montagem de vídeo e distinguir slideshow/animatic de minissérie.
5. P1: separar geração narrativa real de templates, integrar provider e revisão humana.
6. P1: implementar tradução real e validação linguística.
7. P1: formalizar entidades e relações livro/audiobook/minissérie/episódio/série/coleção.
8. P2: reforçar readiness com validators específicos e evidência por etapa.

## Estratégia de implementação

- Um PR por problema coeso, sem reescrever simultaneamente autenticação, pipeline e armazenamento.
- Antes de alterações a dados, criar backup e ensaiar migração/rollback num ambiente isolado.
- Criar testes unitários e integração com providers simulados; executar testes reais em hardware/ambiente controlado quando necessário.
- Nunca gerar outputs de silêncio/fallback e apresentá-los como concluídos.
- Nunca afirmar que um e-book, audiobook, minissérie, tradução ou publicação está pronto sem validação do artefacto.
- Preservar os canons e fixtures existentes; qualquer mudança de canon requer revisão humana.
- Não ativar publicação externa sem aprovação explícita do Studio e verificação de direitos.

## Limites desta auditoria

A revisão foi feita por leitura estática dos ficheiros referidos e documentação disponível. Não foram executados o Studio, os providers TTS, FFmpeg, o pipeline real, testes HTTP, testes de áudio/vídeo ou ensaios de publicação. Os achados de código são fortes indícios verificáveis, mas a validação dinâmica é uma etapa obrigatória antes de cada correção ser considerada concluída.
