# Studio — arquitetura de sessão e migração RBAC

**Data:** 13-11-2026  
**Estado:** proposta técnica para implementação faseada; não altera runtime.  
**Dependências:** issue #43 e PR #44.

## 1. Objetivo e fronteiras

O Studio é uma aplicação privada/doméstica. O backend não deve confiar em identidade, papel, nome, owner ou permissões enviados pelo cliente. O Website continua a ser um sistema separado e só recebe publicações aprovadas através da integração autenticada Studio → Website.

Princípios obrigatórios:

1. Identidade vem exclusivamente de uma credencial validada pelo backend.
2. Autorização é aplicada no servidor em cada operação, com negação por omissão.
3. Roles são permissões de capacidade, não prova de identidade.
4. Âmbito por projeto/IP é verificado no servidor e usa IDs estáveis, nunca nomes.
5. Conta familiar não equivale a conta infantil com poderes editoriais: crianças têm capacidades guiadas e supervisionadas.
6. Credenciais, sessões e dados privados nunca são servidos por StaticFiles nem incluídos em respostas públicas.

## 2. Modelo de identidade e sessão

### Utilizador

Campos recomendados:

- `id`: identificador estável e imutável.
- `name`: nome de apresentação, não usado como chave de autorização.
- `role`: papel controlado pelo owner no servidor.
- `is_active`: estado da conta.
- `password_hash`: hash Argon2id (ou algoritmo moderno equivalente com parâmetros versionados).
- `must_change_password`: bloqueia operações normais até alteração da credencial inicial.
- `credential_version`: incrementado em reset/alteração para invalidar sessões anteriores.
- `created_at`, `updated_at`.

Nunca devolver `password_hash`, PIN, token, segredo de recuperação ou metadados internos em respostas API. Usar DTOs explícitos de saída; não serializar diretamente o registo persistido.

### Sessões

Preferir tokens opacos aleatórios, de alta entropia, emitidos após login:

- Token completo só é devolvido uma vez ao cliente.
- Backend persiste apenas hash do token, user_id, created_at, expires_at, last_seen_at, revoked_at e credential_version.
- Expiração absoluta e por inatividade; revogação individual e revogação de todas as sessões.
- Em cada pedido, validar token, sessão não revogada, utilizador ativo e versão de credencial.
- Não aceitar identidade/role enviados em query, path ou payload como substituto do principal autenticado.
- Respostas 401 para ausência/invalidade/expiração; 403 para utilizador autenticado sem permissão.

A persistência atual em JSON precisa de escrita atómica, lock entre processos e testes de concorrência antes de alojar sessões. Se isso não puder ser garantido, selecionar uma store transacional local já suportada pelo produto; não introduzir serviço pago ou dependência remota nesta fase.

### Clientes

- Desktop Tauri: token no armazenamento seguro do sistema operativo, nunca em ficheiro de preferências ou localStorage.
- Mobile Capacitor: token em armazenamento seguro apoiado por Keychain/Keystore, não localStorage.
- Memória de processo para o token durante a sessão; logout limpa memória e armazenamento seguro e revoga a sessão no backend.
- A resposta de login devolve perfil público mínimo, token e metadados de expiração; não devolve o registo persistido.
- Não guardar PIN/password depois do login.

A implementação tem de confirmar primeiro quais os plugins de secure storage já presentes nas aplicações. Não instalar dependências sem verificar compatibilidade e licenças.

## 3. Autorização RBAC e âmbito

Criar um principal imutável por pedido, por exemplo `AuthenticatedPrincipal(user_id, role, permissions, session_id)`, produzido apenas pela dependência de autenticação.

Separar:

- `get_current_principal`: autenticação.
- `require_permission("...")`: capacidade global.
- `authorize_project(project_id, permission)`: permissão e pertença ao projeto.
- `authorize_ip(slug, permission)`: permissão e ACL da IP.
- `require_owner`: operações de administração de contas, credenciais e configuração sensível.

A matriz de permissões deve definir explicitamente:

| Domínio | Capacidades mínimas |
|---|---|
| Contas | listar perfil limitado, criar, alterar papel, desativar, resetar credencial, revogar sessões |
| Projetos | listar por âmbito, criar, ler, editar, arquivar |
| Editorial | rever, aprovar, rejeitar, regenerar, congelar pacote |
| Comercial | alterar preço, catálogo, promoções e estado comercial |
| Publicação | verificar prontidão, marcar/desmarcar, publicar |
| Distribuição | configurar canal, registar tentativa, registar sucesso/falha |
| IP/canon | ler, editar canon, editar personagens, branding, metadados e paleta |
| Operações | diagnóstico limitado, jobs, deploy, DB, segredos e updater com permissões separadas |

Os nomes de família não concedem privilégios. Acesso infantil deve ser um conjunto de capacidades explícitas e restritas (ex.: gravação/ditado em fluxos supervisionados), nunca role editorial ou administrativo.

## 4. Política de rotas e superfícies públicas

Antes de aplicar dependência global, classificar todas as rotas:

- **Públicas mínimas:** health sem detalhes internos e assets realmente públicos.
- **Família autenticada:** leitura/edição autorizada de conteúdos domésticos.
- **Owner/admin:** contas, credenciais, segredos, deploy, DB e operações críticas.
- **Integração Website:** autenticação máquina-a-máquina independente, com segredo dedicado, escopo de publicação, rotação e logs.
- **Jobs internos:** não expor diretamente sem autenticação e autorização.

CORS deve usar allowlist explícita dos origins reais de desktop/mobile/web em desenvolvimento e produção. Não combinar wildcard de origins com credenciais. Para bearer tokens, manter política CORS restrita mesmo sem cookies.

Remover a montagem de toda a raiz `/storage`. Servir apenas diretórios de assets públicos deliberadamente publicados. Downloads privados passam por endpoint autenticado com autorização por recurso, path canonicalizado e bloqueio de traversal. Nunca expor `data/*.json`, backups, logs, configurações, tokens ou ficheiros de trabalho.

## 5. Migração coordenada

1. Inventariar todos os clientes ativos e todas as chamadas API; identificar versão desktop/mobile e storage seguro disponível.
2. Implementar modelo de credenciais, sessão, revogação e DTO público em paralelo com testes unitários.
3. Implementar dependências RBAC e matriz de permissões; converter primeiro rotas de contas e operações P0.
4. Migrar clientes para login → token → bearer em todas as chamadas; remover envio de `user_id/user_name/user_role` para autorização.
5. Converter rotas restantes por domínio, incluindo leitura privada, uploads, jobs, storage e controlos operacionais.
6. Desativar compatibilidade legacy numa release coordenada; não manter fallback que aceite role/name do cliente.
7. Remover PIN em texto simples e dados de sessão antigos após migração verificada e plano de recuperação.
8. Ativar restrições CORS, rate limit/lockout e monitorização de tentativas inválidas.

Não aplicar um middleware global de bloqueio antes de classificar health, assets, Website inbound, callbacks e jobs. Não deixar uma janela de compatibilidade em que o cliente antigo continue a autenticar-se por identidade declarada.

## 6. Testes de aceitação obrigatórios

### Autenticação

- Sem token → 401.
- Token inválido, expirado, revogado ou de utilizador desativado → 401.
- Alteração/reset de credencial invalida sessões anteriores.
- Login falhado não revela se o nome existe.
- Rate limit/lockout aplicado sem permitir bloqueio trivial de terceiros.
- Hash e token nunca aparecem em qualquer resposta ou log.

### Autorização

- Utilizador autenticado sem permissão → 403.
- Role enviada no payload/query/path não altera permissões.
- Spoof de user_id, owner_id, user_name, created_by ou requested_by não concede acesso.
- Utilizador A não lê/altera projeto ou IP privado de B.
- Criança não consegue alterar preço, publicar, gerir contas, segredos, deploy ou apagar conteúdos.
- Operações de publicação exigem aprovação e readiness válidas no servidor.

### Transporte e storage

- CORS rejeita origins não autorizados.
- `/storage/data/users.json`, projetos, logs, backups e ficheiros privados não são servidos.
- Path traversal e acesso cruzado entre IPs são bloqueados.
- Upload valida tamanho, conteúdo MIME real, extensão e destino; falha não deixa ficheiro órfão.
- Website inbound aceita apenas credencial máquina-a-máquina e payload íntegro.

### Clientes

- Desktop e mobile mantêm sessão após reinício apenas via secure storage.
- Logout revoga no servidor e limpa armazenamento local.
- Token revogado provoca 401 e encaminha para login.
- Falha offline não transforma sessão antiga numa autorização válida indefinida.

## 7. Critérios para rollout

Não considerar a migração concluída até:

- matriz de todas as rotas coberta por classificação e dependência;
- todos os testes negativos acima passarem em CI;
- desktop e mobile atualizados e testados;
- assets públicos e privados separados;
- sessão antiga invalidada e credenciais em texto simples eliminadas;
- integração Website validada sem expor o Studio;
- logs sem segredos e com auditoria de actor/session/resource/action;
- plano de recuperação de owner testado sem PIN universal permanente.

## 8. Riscos e decisões em aberto

- Confirmar armazenamento seguro disponível em Tauri e Capacitor e compatibilidade com as versões atuais.
- Escolher persistência transacional local para sessões caso JSON não suporte concorrência segura.
- Definir TTLs de sessão e política de dispositivos familiares.
- Definir permissões finas para os papéis adultos e fluxos infantis supervisionados.
- Confirmar todos os origins CORS efetivamente usados.
- Definir formato de autenticação máquina-a-máquina Website → Studio, se vier a existir; a direção atualmente suportada é Studio → Website.

**Regra de segurança:** não reduzir controlos para manter clientes antigos funcionais. Se um cliente não suportar bearer/session, deve ser atualizado antes da desativação da autenticação legacy.


## 9. Evidência concreta dos clientes e estado da migração (13-11-2026)

Inspeção do head ff452f71cf627370ad69e495dd789247a6575ba9 confirmou:

### Cliente React/Capacitor/Tauri

- O projeto usa uma única aplicação `client/mobile-app` para Android/Capacitor e desktop/Tauri; não existe um segundo `client/desktop-app` no tree atual.
- `client/mobile-app/package.json` declara Capacitor 7 e Tauri 2, mas não declara plugin de secure storage.
- `client/mobile-app/src-tauri/Cargo.toml` contém apenas `tauri`, `serde` e `serde_json`; não declara plugin de keyring/secure storage.
- `src-tauri/src/lib.rs` inicializa `tauri::Builder::default()` sem plugin de armazenamento seguro.
- `src/api/core.js` persiste o utilizador completo serializado em `localStorage` (`baribudos_python_user`); não guarda token nem envia Authorization bearer.
- `src/App.jsx` restaura esse utilizador no arranque através de `getSavedUser()` sem revalidar sessão no servidor.
- `src/components/LoginPanel.jsx` tem nome e PIN predefinidos no estado inicial (`André`/`1234`).
- As funções `get`, `post`, `put`, `patch` e `del` usam `fetch` sem cabeçalho Authorization.
- `resolveBackendFileUrl()` converte caminhos `/storage/` em URLs HTTP diretas, dependendo da montagem estática do backend.

### Consequência

A migração não pode consistir apenas em adicionar middleware FastAPI. É necessário alterar o contrato de login, o cliente HTTP central, bootstrap da aplicação, logout, gestão de sessões e resolução de media. O mesmo bundle é empacotado em Tauri e Capacitor, pelo que a estratégia de armazenamento seguro deve ser compatível com ambos os ambientes e ter adaptadores nativos separados quando necessário.

### Critérios de implementação para o cliente

1. Remover defaults de nome/PIN da UI.
2. Não persistir perfil como prova de sessão; manter apenas perfil público derivado da resposta validada.
3. Implementar token bearer em memória e armazenamento nativo seguro, sem fallback para localStorage.
4. Validar sessão no arranque e após reconexão; em 401 limpar estado e pedir novo login.
5. Logout deve revogar no backend e limpar o armazenamento nativo, mesmo que a UI esteja offline (com revogação pendente controlada, sem prolongar autorização).
6. Remover envio de `user_id`, `user_name` e `user_role` de todos os pedidos de autorização; manter campos de auditoria apenas se forem preenchidos/confirmados no servidor.
7. Substituir media URLs diretas `/storage/` por URLs de asset público explícito ou endpoint autenticado de download.

**Estado:** diagnóstico estático do cliente concluído. Não foram adicionados plugins, alteradas dependências, credenciais, dados ou runtime. A escolha final do mecanismo secure storage e a implementação continuam pendentes de testes nativos Android/Windows.


## 10. Revisão P0 dos routers registados e superfícies operacionais (13-11-2026)

Inspeção direta de `studio_core/api/main.py` e dos módulos indicados abaixo no commit `2fe853ee459e9756f32efdfc575a77204c9a0677`:

### Evidência transversal em `main.py`

- Não está registado middleware global de autenticação nem dependência global `dependencies=[...]` na criação da app ou nos `include_router` inspecionados.
- CORS permite origins, métodos e headers wildcard com credenciais ativadas.
- A raiz resolvida por `resolve_storage_path()` é montada integralmente em `/storage` com `StaticFiles`, sem filtro de subpastas ou autorização por asset.
- `public/` também é montada em `/public`; esta superfície requer inventário de conteúdo e política explícita, embora não seja equivalente à raiz privada.
- Os routers de users, settings, persistent memory, website admin/control, deploy, DB e secrets são incluídos sem dependência global visível.

### Routers P0 diretamente inspecionados

| Router | Operações encontradas | Evidência observada | Classificação provisória |
|---|---|---|---|
| `secret_control.py` | Listar, revelar, criar, alterar, apagar e exportar vaults | Handlers chamam diretamente serviços; `reveal_values` pode solicitar valores em claro; sem dependência auth visível | P0 crítico |
| `db_control.py` | Estado e readiness DB | Exposição de diagnóstico operacional; sem dependência auth visível | P1 privado |
| `deploy_control.py` | Resumo e lista de deployments Vercel | Exposição de estado operacional; sem dependência auth visível | P1 privado |
| `updater.py` | Versão, check e download | Check/download alteram estado ou obtêm artefactos; sem dependência auth visível | P0/P1 privado |
| `website_admin.py` | Alterar visibilidade e preço de produtos | Mutação comercial chama serviços sem dependência auth visível | P0 crítico |
| `website_control.py` | Health, memory-link, resumo, catálogo, publicação e divergência | Leitura operacional e potencial informação comercial; sem dependência auth visível | P1 privado |
| `settings.py` | Ler e atualizar settings | Leitura/escrita direta sem dependência auth visível | P0 crítico |
| `persistent_memory.py` | Criar projetos, decisões, histórico, backlog, sessão, contexto e URI Obsidian | Escrita/leitura de memória privada sem dependência auth visível | P0 crítico |

### Implicações

1. Não basta proteger os 29 handlers da matriz: as rotas administrativas e de dados sensíveis sem campos `user_*` também exigem classificação e cobertura de autenticação.
2. `secret_control` deve ser bloqueado para anónimos e limitado a owner; os valores de vault não devem ser revelados por omissão nem exportados sem autorização explícita e auditoria.
3. `website_admin` exige owner/admin com permissão comercial explícita e registo de auditoria.
4. `settings` deve separar settings não sensíveis de configuração/segredos; escrita restrita a owner/admin.
5. `persistent_memory` deve ser privado por projeto e não permitir que o `project_name` fornecido no URL/body determine sozinho o âmbito de acesso.
6. `updater` deve validar assinatura, origem, versão e hash dos artefactos; check/download não devem ser tratados como operações públicas.
7. CORS não é mecanismo de autenticação. A política final deve usar origens explícitas por ambiente, mas a correção de CORS isolada não resolve acesso direto à API.
8. A montagem de `/storage` é um bloqueador de privacidade: mover ficheiros privados para fora de qualquer StaticFiles mount e publicar apenas assets explicitamente aprovados através de um registry/allowlist. Downloads privados passam por endpoint autenticado e validado por escopo.

**Limites:** trata-se de inspeção estática dos módulos e do registo da aplicação. Não foram executados testes HTTP nem provada a exploração remota. Dependências indiretas, configuração de deployment e todos os restantes routers ainda precisam de rastreio. Não houve alteração de runtime, storage, dados, CORS, credenciais ou infraestrutura.
