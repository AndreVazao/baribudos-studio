# Baribudos — produção de histórias e bundles de cinco

**Estado:** primeira implementação de agrupamento e validação cloud; não é ainda autorização para publicação comercial.

## Unidade editorial

Cada história é uma unidade autónoma de produção. A partir de uma versão editorial aprovada, o Studio deve produzir:

1. E-book EPUB.
2. Audiobook no idioma aprovado.
3. Minissérie/episódio audiovisual correspondente.

Os três outputs devem apontar para a mesma história, versão, IP/saga e locale. Um output não deve ser considerado concluído apenas porque uma função terminou: o ficheiro tem de existir, ser legível e passar validação técnica.

## Bundle de cinco histórias

Depois de existirem cinco histórias explicitamente aprovadas, o Studio pode preparar um bundle complementar com:

- Guia para pais cobrindo as cinco histórias, temas, perguntas de conversa e ações sugeridas aos adultos.
- Filme compilatório que concatena as cinco minisséries/episódios existentes.

O agrupamento é isolado por IP/saga e idioma. Histórias em rascunho, sem ID estável ou de outra IP/idioma não contam para completar o grupo. Grupos incompletos ficam em espera. O tamanho de cinco é a regra aprovada para este bundle, não uma regra universal para volumes, temporadas ou coleções comerciais.

## Implementação atual

- `studio_core/services/story_bundle_service.py` seleciona grupos completos e determinísticos de cinco histórias aprovadas.
- `build_parent_guide` gera um guia Markdown com perguntas adequadas à conversa familiar e salvaguardas pedagógicas.
- `build_five_story_compilation` exige cinco vídeos existentes, concatena-os com FFmpeg, re-encoda H.264/AAC e verifica os streams com FFprobe.
- `build_five_story_bundle` não cria bundle enquanto não existir um grupo completo e exige seleção explícita quando há mais do que um grupo pronto.
- O serviço é ainda uma capacidade invocável e testável; não está ligado automaticamente à API ou ao dashboard. A integração no fluxo de aprovação requer persistência/versionamento e autorização server-side, atualmente bloqueada pela auditoria de segurança P0.

## Validação cloud

Workflow `.github/workflows/story-production-cloud-validation.yml` usa uma VM efémera Ubuntu e instala FFmpeg, FFprobe e eSpeak NG. O teste de integração executa builders reais do Studio para gerar:

- EPUB e valida a estrutura ZIP/OPF/TOC.
- WAV de audiobook com TTS real, não silêncio fabricado.
- MP4 de minissérie a partir de frames sintéticos aprovados e do WAV produzido.
- Guia de pais e filme compilatório de cinco histórias, com verificação H.264/AAC.

Os ficheiros e o relatório são publicados como artifact temporário do GitHub Actions. São fixtures sintéticas, nunca dados familiares ou conteúdo de produção.

## Limites conhecidos antes da primeira publicação real

- `story_generation_engine.py` usa atualmente templates determinísticos; não é geração narrativa generativa por provider de IA. O resultado tem de ser revisto e aprovado por um adulto.
- A localização/tradução para idiomas diferentes da origem não pode ser marcada como concluída: o serviço de tradução existente é simulado.
- O TTS eSpeak NG prova que a geração de áudio funciona tecnicamente, mas não certifica voz artística, pronúncia, emoção ou adequação editorial final.
- A minissérie e o filme compilatório atuais são slideshow/animatic de imagens estáticas com áudio. Não são animação fluida nem incluem lip-sync.
- Os assets usados na CI são sintéticos. A produção real exige ilustrações aprovadas, character lock, direitos/consentimentos e créditos completos.
- Não publicar nem sincronizar para Website sem gate editorial, pacote congelado, direitos, créditos, assets persistidos e autorização explícita.

## Próximas fases

1. Ligar seleção de cinco histórias ao modelo persistente de coleções/bundles, com idempotência e versionamento.
2. Integrar a geração do guia e compilação no dashboard com estados `waiting_for_five`, `ready_for_review`, `approved`, `generated` e `failed`.
3. Construir validação automática de EPUB, WAV e MP4 e gates editoriais/pedagógicos.
4. Substituir a geração por templates por provider generativo configurável, com canon e revisão humana.
5. Implementar localização real, com revisão humana por idioma.
6. Evoluir o animatic para animação real, sem confundir os dois níveis de capacidade.
7. Só então executar o primeiro lote editorial real e a publicação comercial.
