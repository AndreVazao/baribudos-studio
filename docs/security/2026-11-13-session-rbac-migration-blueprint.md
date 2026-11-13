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
