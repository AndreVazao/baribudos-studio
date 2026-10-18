# Avaliação de plugins, skills, MCP e ferramentas externas — 2026-10-14

## Estado
- Tipo: documentação de avaliação; não constitui aprovação de instalação.
- Branch: `docs/tooling-capability-audit-2026-10-14`
- Estado global: **proposto / por validar tecnicamente**.
- Nenhuma ferramenta foi instalada, nenhuma credencial foi criada e nenhuma operação de produção foi executada nesta tarefa.

## Objetivo
Avaliar capacidades reutilizáveis para o ecossistema AndreOS/DGM-MAT, privilegiando soluções gratuitas ou locais, baixo consumo, manutenção sustentável, segurança e evidência verificável. A meta é integrar capacidades úteis, não acumular plugins.

## Regras obrigatórias
1. Investigar o repositório oficial, licença, atividade, dependências, requisitos de hardware, modelo de custos e permissões antes de aprovar.
2. Comparar com capacidades já existentes para evitar duplicação de orquestradores, agentes e servidores.
3. Testar primeiro numa cópia/branch isolada; registar comandos, resultados e limitações.
4. Preservar estado local, histórico Git e trabalho não auditado. Não executar `reset`, `clean`, merges ou pushes em massa sem revisão explícita.
5. Não modificar clones de terceiros, upstreams, repositórios espelho ou labs excluídos do âmbito.
6. Nunca habilitar permissões globais indiscriminadas ou desativar todas as confirmações. Separar leitura, escrita, execução, rede e publicação.
7. Segredos fora do repositório, com permissões restritas; nunca os escrever em logs nem em commits.
8. CAPTCHA, autenticação, pagamentos, envio de mensagens e operações irreversíveis exigem controlo humano adequado.
9. Medir RAM, CPU, tempo, tokens/custos, fiabilidade, qualidade e custo de manutenção antes de adotar.
10. A instalação e a integração só avançam depois de revisão e autorização do responsável pelo projeto.

## Candidatos prioritários para avaliação
| Candidato | Utilidade pretendida | Decisão inicial |
|---|---|---|
| Superpowers | Planeamento, implementação, testes e revisão disciplinados | Avaliar em ambiente isolado |
| Understand Anything | Mapa de arquitetura, relações e explicação de código | Avaliar em repositórios não críticos |
| Playwright | Testes de UI e automação web autorizada | Avaliar com testes reproduzíveis |
| Skill Creator | Converter procedimentos aprovados em skills reutilizáveis | Avaliar e versionar skills |
| MCP Builder | Criar interfaces MCP limitadas e auditáveis | Avaliar após definir contratos |
| Claude plugins/skills oficiais | Descoberta de competências mantidas | Verificar origem e permissões |
| wshobson/agents e agency-agents | Catálogos de agentes especializados | Seleção individual; não instalar coleções completas |
| frontend-design, Canva e Figma | Design e prototipagem de interfaces | Usar por necessidade de UI |
| CLI-Anything | Interfaces CLI estruturadas para ferramentas existentes | Confirmar repositório, maturidade e adequação |
| Scrapling | Extração de páginas acessíveis e autorizadas | Teste seletivo; verificar dependências e regras do site |
| MoneyPrinterTurbo, Remotion e Hyperframes | Pipeline de produção de vídeo | Avaliar no projeto de conteúdo, não no núcleo |
| Langflow, OpenHands, Open Dots, Habblaud, Maestro/Overclock | Alternativas de agentes/orquestração | Adiar até provar vantagem e compatibilidade |
| APIs LLM gratuitas e free-for-dev | Descobrir quotas e serviços gratuitos | Validar termos, privacidade, limites e disponibilidade |
| Z-Image / LTX-2.5 | Geração de imagem/vídeo | Avaliar requisitos de hardware/licença; não presumir viabilidade local |
| Supabase, Notion, Canva, Stripe, Zapier e outros MCP | Integrações específicas | Só ativar se o projeto realmente as usar e com escopo mínimo |

Os nomes acima provêm de uma lista inicial de candidatos e não constituem verificação de que cada projeto, pacote ou marketplace é oficial, ativo, seguro ou compatível. Resolver ambiguidades de nomes e URLs antes de qualquer instalação.

## Compatibilidade e hardware
O PC de desenvolvimento reportado tem 2 núcleos e cerca de 3 GB de RAM. Dar preferência a ferramentas leves, execução sob demanda e serviços já disponíveis. Não assumir que modelos de imagem/vídeo, containers pesados ou agentes autónomos funcionam localmente. Não introduzir APIs pagas por defeito.

## Processo de adoção
1. Descoberta: URL oficial, licença, release/commit, mantenedor e sinais de manutenção.
2. Segurança: permissões, scripts de instalação, dependências, telemetria, segredos e superfície de ataque.
3. Adequação: problema concreto, sobreposição com stack atual, compatibilidade e custo.
4. Piloto isolado: testes reproduzíveis, sem credenciais de produção e sem alterações destrutivas.
5. Medição: recursos, qualidade, erros, tempo de configuração e manutenção.
6. Decisão documentada: adotar, adiar, rejeitar ou voltar a avaliar, com evidência.
7. Atualizar memória central e documentação do projeto antes de ampliar o uso.

## Próximas ações
- Inventariar ferramentas já instaladas antes de adicionar dependências.
- Recolher URLs oficiais e versões exatas dos candidatos.
- Criar matriz de avaliação com evidência, requisitos, risco, custo, projeto-alvo e decisão.
- Manter este trabalho numa branch documental; não fazer merge para `main` automaticamente.

## Aplicação ao Baribudos Studio / ViralVazao
Avaliar Remotion e Hyperframes para montagem programática, MoneyPrinterTurbo como pipeline experimental e Canva para peças gráficas. LTX-2.5 e Z-Image exigem avaliação separada de hardware, licença, disponibilidade e custo; não assumir que são viáveis no PC atual.

O piloto deve validar consistência visual dos personagens, qualidade de narração/legendas, tempo de produção, licenças de imagens/música e exportação vertical. Gerar primeiro numa área experimental; só publicar após revisão humana.

## Referência cruzada
Registo central: `AndreVazao/andreos-memory`, branch `docs/tooling-capability-audit-2026-10-14`.
