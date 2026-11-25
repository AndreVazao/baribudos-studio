# Baribudos Studio — checkpoint de continuidade
**Atualizado:** 2026-11-25 UTC  
**Base de referência:** main `ee9acd90ff62bf8f751f60d3652918a8741b13b9`  
**PRs em desenvolvimento:** #76

## Como retomar
Este documento é o checkpoint para novas conversas quando o contexto anterior ficar cheio. Ler primeiro este ficheiro, depois o roadmap `STUDIO_CURRENT_STATE_AND_COMPLETION_ROADMAP.md`, o contrato de aprovação editorial e os PRs ativos. Nunca assumir que Draft significa integrado, nem que CI verde significa produção.

## Regras de execução
- Trabalhar em branches novas baseadas na main atual; não rebasear branches divergentes sem aprovação.
- Criar PRs incrementais e Draft quando incompletas.
- Não fazer merge, deployment, ações financeiras, ler/decriptar secrets ou alterar produção sem autorização específica.
- Relatar commits, URLs, CI verificada, riscos e próximos passos; não fabricar validações.
- Priorizar correções funcionais e código, não documentação isolada.

## Segurança P0 — ainda bloqueada
- Auth atual identificada como nome/PIN com PIN em texto simples e default conhecido 1234.
- API users expõe dados brutos; login devolve user record sem sessão revogável.
- Clientes restauram identidade a partir de localStorage sem validação server-side.
- Autorização histórica aceita role/user fornecidos pelo cliente; rotas sensíveis sem cobertura central comprovada.
- CORS wildcard com credentials e mounts estáticos/storage potencialmente expostos; requer remediação e testes HTTP.
- PR #63 auth/RBAC/storage central continua divergente; não rebasear sem autorização.
- PR #75 route audit Draft: alerta sobre endpoint export sem auth dependency visível.
- PR #68 contract Draft/roadmap de aprovação; PR #73 contrato de aprovação editorial já integrado.
- PR #69 ledger de revisão e #71 bloqueio de falsa aprovação integrados; #74 roadmap integrado.

## Avanço 2026-11-25 — PR #76
URL: https://github.com/AndreVazao/baribudos-studio/pull/76
Branch: `security/server-auth-sessions-foundation-2026-11-25`
Head: `faa189dba30ff8e64f9544a98a0661898a43dd2d`
Base: `ee9acd90ff62bf8f751f60d3652918a8741b13b9`
Draft, 2 commits, 0 behind, 2 files/238 additions.
- `studio_core/services/auth_sessions.py`: tokens opacos via secrets, apenas hash SHA-256 persistido, TTL 8h configurável, resolver/revogar individual/revogar utilizador, purga expirados, escrita atómica e permissões 0600 quando suportadas; armazenamento corrupto falha fechado.
- `tests/test_auth_sessions.py`: emissão, token não persistido, expiração, revogação, token inválido e armazenamento corrompido.
- Workflow runs consultados no head; resultado vazio. **CI ainda não verificada**.
- Limitações: não ligado ao login, endpoints, FastAPI principal, RBAC, rate limit, cliente, PIN nem configuração de storage privado. JSON store exige revisão de concorrência multi-processo e localização privada. Não é remediação P0 completa.

## Próxima execução (ordem)
1. Confirmar CI e rever PR #76, corrigir problemas encontrados.
2. Ligar criação de sessão no login, DTO seguro sem credenciais, endpoint `/auth/me`, logout com revogação.
3. Implementar principal/dependency de autenticação server-side e gates owner/admin.
4. Rate limit login, migração segura/recuperação de credenciais e remoção do PIN default.
5. Route-policy inventory/coverage, negativos (401/403), CORS restrito, storage privado, static mounts revistos.
6. Migrar clientes desktop/mobile para token e armazenamento seguro, validação startup e logout remoto.
7. Revalidar pipeline editorial com artefactos reais, geração narrativa provider-backed, segurança de aprovação e produção end-to-end.

## Canon editorial
- Livro/story canónico individual = minissérie individual.
- Cinco livros aprovados distintos da mesma IP/saga/idioma = volume, cinco episódios individuais, compilação real e guia parental; sexta história inicia volume seguinte.
- Episódio target 5 min, mínimo 4:30, sem máximo rígido. Compilação calcula duração real + transições, sem padding.
- Audiobook independente da minissérie; slideshow/animatic não é animação final.
- Idades 4–10 agrupadas 4–5, 6–7, 8–10; segurança emocional, autonomia, pensamento crítico; um valor principal, secundário opcional, 3 perguntas familiares; sem medo, vergonha, humilhação ou punição como resolução.
- BB-001 “O Eco que Pedia Silêncio” e BB-002 “A Semente que Não Tinha Pressa” continuam drafts não aprovados.
- Consentimento de voz obrigatório; sem clonagem sem consentimento explícito.

## Provider story generation PR #65
Draft, branch divergente (57 ahead/8 behind na última auditoria), não rebasear sem aprovação. Head anterior `e99ae8616e2bfef508c3acdb0f57d20ea07d3b10` com workflows reportados verdes. Sem chamada live a provider, custos ou produção; canon vazio bloqueia e neutraliza aprovação provider. Revalidar head/CI antes de usar.

## Política de estados
Separar: código presente; testes locais/CI; Preview READY; integração; validação de produção. Não declarar uma etapa superior sem evidência.
