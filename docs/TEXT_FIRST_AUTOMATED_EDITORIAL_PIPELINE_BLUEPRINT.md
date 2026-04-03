# Blueprint — pipeline editorial automatizada text-first

## Objetivo
Transformar o Studio numa pipeline onde a produção começa por **texto** e, a partir daí, gera automaticamente:
- livro infantil
- traduções
- paginação
- capa
- ilustrações
- audiobook
- minissérie
- volumes
- guia para pais
- mini-filmes por conjunto de volumes

O objetivo é manter o fluxo o mais automatizado possível, com:
- IA local sempre que possível
- revisão/edição final humana curta
- aprovação final antes de entrar em produção/publicação

---

## 1. Fluxo-base pretendido
## Etapa 1 — entrada do texto
O texto original é criado fora ou dentro do ecossistema de escrita, e depois é colado/importado para um campo próprio no dashboard do Studio.

### Regra
O texto é o ponto de partida oficial do pipeline.

### Campos recomendados
- `story_source_text`
- `story_source_language`
- `story_source_type`
- `story_source_notes`
- `text_locked`
- `text_approved`

---

## Etapa 2 — tradução automática multi-língua
Depois do texto entrar, o Studio deve criar automaticamente versões traduzidas para as línguas configuradas para a IP/saga/projeto.

### Línguas iniciais prioritárias
- pt-PT
- pt-BR
- en
- fr
- es
- de
- it
- nl
- zh
- ja

### Regra
- o texto-base gera uma tradução por língua
- cada tradução pode ter revisão final humana antes de ficar congelada
- cada língua passa a ter o seu próprio fluxo de produção derivado

### Entidades recomendadas
- `story_translation`
- `language`
- `translation_status`
- `translation_locked`
- `translation_reviewed_by`

---

## Etapa 3 — paginação automática
Depois da tradução, o Studio deve partir a história em páginas.

### Regra inicial Baribudos
Para Baribudos, o default inicial deve ser:
- aproximadamente **3 a 5 linhas por página**

### Regra multi-IP
Isto **não pode ficar hardcoded globalmente**.
Cada IP/saga deve poder definir:
- linhas por página
- densidade de texto
- faixa etária
- tipo de layout
- tamanho do livro

### Configuração recomendada
- `page_split_mode`
- `target_lines_per_page_min`
- `target_lines_per_page_max`
- `page_density_profile`
- `audience_age_band`

### Output esperado
- storyboard textual por página
- resumo de cada página
- intenção visual por página

---

## Etapa 4 — capa, ilustrações e assets visuais
Com a história já paginada, o Studio entra na produção visual.

### Ordem pretendida
1. análise do conteúdo da história
2. criação da capa
3. criação das ilustrações por página
4. validação do character lock / visual rules
5. aprovação final humana curta

### Regra
- para Baribudos e outras IPs com personagens recorrentes, a pipeline deve respeitar `character_lock`
- a produção visual deve herdar:
  - canon visual
  - visual sets
  - voice casting quando influenciar o tom
  - regras da IP/saga

---

## Etapa 5 — audiobook multi-língua
Depois das páginas/ilustrações, o Studio deve criar o audiobook em cada língua.

### Regra
- usar perfis vocais pré-definidos
- usar casting vocal por papel narrativo/personagem
- permitir vozes da família e clones de voz com consentimento
- gerar créditos automáticos de vozes e narração

### Fluxo recomendado
1. escolher voice casting da língua
2. gerar narração
3. gerar vozes de personagens, quando aplicável
4. adicionar sons/ambientes leves
5. exportar audiobook final

---

## Etapa 6 — minissérie multi-língua
Depois do livro e/ou audiobook, o Studio deve conseguir criar uma minissérie por livro.

### Regra
Cada livro pode dar origem a:
- uma **minissérie curta**
- em várias línguas
- orientada a YouTube Kids ou equivalente

### Inputs
- páginas aprovadas
- ilustrações aprovadas
- áudio/narração aprovados
- storyboard temporal

### Outputs
- episódios curtos
- assets promocionais
- versões por língua

---

## Etapa 7 — volumes
A lógica editorial pretendida é por agrupamento.

### Regra inicial
Cada **5 livros** formam um **volume**.

Cada volume inclui:
- 5 livros
- 1 guia para pais

### Regras recomendadas
- `books_per_volume`
- `include_parent_guide`
- `volume_sequence_number`
- `volume_theme`

---

## Etapa 8 — guia para pais
Cada volume deve gerar automaticamente um **guia para pais**.

### Objetivo
Permitir aos pais:
- perceber a lição didática do volume
- avaliar se os filhos entenderam a mensagem
- fazer exercícios e acompanhamento
- perceber se os livros estão a ajudar

### Conteúdo esperado do guia
- resumo pedagógico dos 5 livros
- lições principais
- perguntas para conversar com a criança
- exercícios simples
- sinais de compreensão emocional/comportamental

### Entidade recomendada
- `parent_guide`
- `volume_id`
- `pedagogical_objectives`
- `family_exercises`
- `comprehension_questions`

---

## Etapa 9 — mini-filmes por conjunto de volumes
Além da minissérie por livro, existe o objetivo de gerar um formato maior.

### Regra desejada
- cada 5 livros → volume
- cada livro → minissérie
- mais tarde, a união de volumes pode originar **mini-filmes** ou filmes mais completos

### Exemplo editorial
- Volume 1 = 5 livros + guia para pais
- Volume 2 = 5 livros + guia para pais
- a junção das minisséries/linhas narrativas dos volumes pode originar um mini-filme mais completo

### Configuração recomendada
- `volumes_per_film`
- `film_cut_strategy`
- `series_to_film_merge_rules`

---

## 2. Filosofia de automação
## Objetivo operacional
O ideal é que o fluxo seja:

1. texto entra
2. Studio traduz
3. Studio pagina
4. Studio cria capa/ilustrações
5. Studio cria audiobook
6. Studio cria minissérie
7. Studio agrupa em volumes
8. Studio gera guia para pais
9. Studio prepara assets comerciais
10. humano faz uma revisão curta e dá **OK final**

### Regra
Automatizar o máximo possível, mas manter:
- checkpoints
- gates de qualidade
- aprovação final humana curta

---

## 3. Gates obrigatórios recomendados
Antes da produção final/publicação, o sistema deve validar:

- `text_ready`
- `translations_ready`
- `page_split_ready`
- `cover_ready`
- `illustrations_ready`
- `character_lock_ready`
- `audio_ready`
- `credits_ready`
- `sponsorship_context_resolved`
- `final_approval_ready`

---

## 4. Regra Baribudos vs outras IPs
Baribudos começa com regras iniciais mais específicas, por exemplo:
- 3 a 5 linhas por página
- tom infantil-didático
- forte controlo de character lock
- outputs multi-língua
- mini-série por livro
- volume por cada 5 livros
- guia para pais por volume

Mas isto não pode limitar o sistema.

### Regra estrutural
Cada IP/saga deve poder configurar:
- paginação
- densidade
- outputs
- número de livros por volume
- necessidade de guia para pais
- série vs filme
- regras visuais e de voz

---

## 5. Melhor forma de implementar
### Camadas recomendadas
### A. text-first orchestration
Responsável por:
- texto base
- traduções
- paginação
- storyboard textual

### B. media generation orchestration
Responsável por:
- capa
- ilustração
- audiobook
- minissérie
- trailers/promos

### C. editorial packaging orchestration
Responsável por:
- volumes
- guias para pais
- créditos
- patrocínios
- bundles/produtos

### D. final approval orchestration
Responsável por:
- reunir checks
- mostrar o que falta
- aceitar revisão final humana
- disparar produção/publicação

---

## 6. Regra final
O Studio deve tender para este resultado:

- colar/importar texto
- deixar a pipeline trabalhar quase toda sozinha
- fazer apenas pequenas revisões finais
- dar `OK final`
- entrar em produção/publicação

Isto deve funcionar primeiro muito bem em Baribudos,
mas ficar estruturalmente preparado para outras IPs, outras sagas e outros estilos editoriais.