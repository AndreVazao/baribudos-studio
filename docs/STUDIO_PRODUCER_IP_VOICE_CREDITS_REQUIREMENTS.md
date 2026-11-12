# Baribudo Estúdio — identidade de produtora, IPs, vozes e créditos

**Estado:** adenda de requisitos funcionais, 2026-11-12.  
**Âmbito:** identidade do estúdio, propriedade intelectual, colaboradores, vozes, créditos finais, patrocínios e primeiro acesso familiar.  
**Relação com documentação existente:** complementa, não substitui, `MULTI_IP_SAGA_PRINCIPLE.md`, `FAMILY_PRIVATE_STUDIO_EDITORIAL_OWNERSHIP.md`, `VOICE_CREDITS_AND_SPONSORSHIP_RULES.md`, `VOICE_PROFILE_IMPLEMENTATION_SPEC.md` e `BARIBUDOS_PRODUCT_VISION_AND_ACCEPTANCE.md`.

## 1. Separação de identidade: produtora e propriedades intelectuais

### 1.1 Baribudo Estúdio é a produtora

**Baribudo Estúdio** é a marca/estrutura de produção audiovisual e de conteúdos. É uma produtora e uma plataforma de criação de propriedade intelectual (IP), não uma marca limitada ao universo Baribudos.

O estúdio deve poder desenvolver, gerir e produzir, entre outros:
- histórias, livros e publicações;
- audiobooks, narração e interpretação vocal;
- personagens e universos ficcionais;
- ilustração, imagem, fotografia e arte;
- vídeo, minisséries, séries e outros formatos audiovisuais;
- música, som, efeitos, dobragem e pós-produção;
- materiais promocionais, campanhas e conteúdos patrocinados.

A arquitetura e a identidade do produto devem permitir criar várias marcas e IPs sem assumir que todas pertencem ao mesmo universo narrativo.

### 1.2 Baribudos é uma IP criada/produzida pelo estúdio

**Baribudos** é uma IP/universo de histórias, com as suas próprias sagas, personagens canónicas, regras narrativas, visuais e pedagógicas. É a primeira IP atualmente desenvolvida no estúdio, não o nome da produtora nem o limite do sistema.

Cada IP deve possuir, no seu próprio âmbito:
- identidade, nome, marca e metadados;
- personagens e respetivos canons;
- regras narrativas, visuais, linguísticas e editoriais;
- sagas, séries, temporadas, episódios e coleções;
- perfis vocais permitidos, casting e regras de consentimento;
- colaboradores, créditos, direitos e patrocínios aplicáveis.

Uma personagem, voz, asset ou outro elemento só pode ser partilhado entre IPs através de uma relação explícita, autorizada e rastreável. Não deve haver contaminação automática entre universos.

### 1.3 Separação de propriedade e responsabilidades

Não confundir:
1. marca/produtora que opera o estúdio;
2. titular ou responsável editorial de cada IP;
3. autor/criador de um elemento específico;
4. pessoa que contribuiu para uma produção;
5. titular de uma voz ou imagem usada;
6. patrocinador de uma produção.

O uso da infraestrutura Baribudo Estúdio não transfere automaticamente a propriedade editorial de uma IP para o estúdio, para o administrador técnico ou para todos os membros da família. A propriedade e as permissões devem ser definidas por IP, saga e produto, conforme a documentação multi-IP já existente.

## 2. Registo de pessoas e nomes para créditos

O Studio deve manter um registo central de pessoas, separado das contas de autenticação. Uma pessoa pode ter:
- identificador interno estável;
- nome registado para créditos;
- conta de acesso (quando aplicável);
- relação familiar ou papel interno, se necessário;
- estado de consentimento e autorizações relevantes;
- preferências de visibilidade dos créditos.

Os nomes de acesso atuais fornecidos para a família são:

**Filhos — ordem do mais velho para o mais novo**
1. Rita
2. Marco António
3. João Cleber
4. Ana Clara
5. Luís Augusto
6. Eduardo
7. Ruth

**Pais**
- André Vazão
- Daura Tejanos

Estes são os nomes de referência para créditos, não uma instrução para criar contas sem os respetivos e-mails pré-registados. Os identificadores técnicos devem ser estáveis e não depender apenas do texto do nome. O proprietário poderá corrigir ou atualizar nomes de apresentação sem perder o histórico de contribuições.

## 3. Créditos finais obrigatórios e rastreáveis

### 3.1 Princípio

Toda a produção que seja publicada ou distribuída deve ter créditos finais derivados de contribuições reais e registadas. Os créditos não são opcionais nem podem depender apenas de preenchimento manual no fim do processo.

A propriedade editorial da IP/produto e a lista de contribuidores são conceitos separados. Creditar alguém não transfere, por si só, propriedade editorial ou direitos de publicação.

### 3.2 Tipos de contribuição a registar

O sistema deve suportar, pelo menos:
- ideia/conceito;
- texto, argumento, escrita, adaptação e tradução;
- revisão editorial e pedagógica;
- criação de personagens e direção criativa;
- ilustração, desenho, pintura, imagem e fotografia;
- voz original gravada;
- voz clonada ou sintetizada a partir de uma pessoa;
- narração;
- interpretação/voz de personagem;
- direção vocal e casting;
- transformação/variação de voz;
- música, composição, interpretação musical e som;
- efeitos sonoros e sound design;
- animação, vídeo, realização, montagem e pós-produção;
- produção executiva/técnica;
- agradecimentos especiais e patrocínios.

Cada contribuição deve guardar pessoa responsável, função, elemento/asset associado, produto/projeto, IP/saga, origem, data e estado de aprovação. Quando uma contribuição é feita por uma ferramenta ou provider, isso pode ser registado como metadado técnico, mas não substitui o crédito da pessoa que criou ou forneceu o material de origem.

### 3.3 Créditos por utilização efetiva

Os créditos devem refletir o que foi efetivamente usado na versão publicada, não todas as pessoas ou assets que alguma vez participaram no projeto.

Exemplos:
- Se a voz da Ruth for usada para interpretar uma personagem, os créditos identificam **Ruth**, a personagem e a função vocal.
- Se a voz de André Vazão for usada na narração, os créditos identificam **André Vazão — narração**.
- Se uma gravação original de uma pessoa for transformada para ficar mais grave, aguda, rápida ou com outro timbre, a variante continua ligada ao perfil e à pessoa que forneceu a voz original. Os créditos identificam essa pessoa e, quando útil, a função/personagem interpretada.
- Se uma ilustração de uma pessoa for usada na edição final, essa pessoa deve constar dos créditos de ilustração, mesmo que a imagem tenha sido posteriormente tratada por ferramentas.
- Se texto, imagem, áudio ou vídeo forem gerados/transformados com assistência de IA, o registo deve preservar a contribuição humana de origem e a ferramenta/provider usado, segundo a política editorial e de divulgação aplicável.

Uma variante vocal nunca deve criar uma nova identidade de titularidade nem apagar a ligação à voz de origem. O perfil original deve permanecer imutável como origem; cada variante deve apontar para o perfil original e preservar o seu `owner_person_id` e nome de crédito.

### 3.4 Dados mínimos de uma atribuição vocal

Cada atribuição de voz a uma produção deve preservar:
- `voice_profile_id` e, se aplicável, `source_voice_profile_id`;
- pessoa titular da gravação/voz original;
- nome de crédito aprovado;
- variante vocal aplicada e parâmetros editoriais relevantes;
- personagem ou papel interpretado;
- tipo de utilização (narração, personagem, promo, ambiente, etc.);
- consentimento e âmbito de utilização válidos;
- projeto, IP, saga e versão final em que foi usada.

Os créditos automáticos devem ser calculados a partir do casting e dos assets realmente incorporados no pacote final. A reconstrução de créditos deve ser repetível e não deve perder edições aprovadas nem criar duplicados.

### 3.5 Obrigatoriedade como gate de publicação

Antes de congelar/publicar uma produção:
- verificar se todos os assets/contribuições usados têm autoria/origem identificada ou uma exceção explicitamente aprovada;
- validar consentimentos e âmbitos de utilização;
- gerar a lista de créditos;
- permitir revisão e aprovação pelo responsável editorial;
- bloquear publicação se existirem contribuições obrigatórias sem atribuição, consentimento ou decisão editorial.

A exceção de anonimato ou omissão de um crédito público exige decisão explícita e auditável. Mesmo quando o nome não é mostrado publicamente, a origem e a pessoa responsável devem continuar registadas internamente, respeitando privacidade e permissões.

## 4. Vozes, clones e variantes

O Studio deve ser também uma biblioteca de vozes e um sistema de produção vocal:
- gravar e catalogar vozes humanas;
- criar clones de voz através de providers compatíveis;
- produzir narração e vozes de personagens;
- pesquisar/selecionar vozes sintéticas ou licenciadas para papéis que necessitem de outra voz;
- transformar vozes próprias em variantes editoriais;
- manter casting por personagem, papel, IP e produção.

O perfil de voz deve separar claramente:
- pessoa titular da voz original;
- perfil/gravação de origem;
- clone ou modelo derivado;
- variante editorial;
- nome apresentado ao operador;
- nome que aparece nos créditos;
- consentimento, restrições e usos permitidos.

Nenhuma voz humana ou clone deve ser utilizado sem consentimento válido e âmbito autorizado. O consentimento deve poder ser limitado, suspenso ou revogado. Para menores, qualquer gravação, clonagem ou utilização deve depender de autorização parental/tutelar adequada e de regras reforçadas de proteção; a participação infantil não pode ser presumida a partir da existência de uma conta familiar.

Uma voz sintética externa/licenciada deve ter origem, provider/licença e condições de utilização registadas. Não atribuir a uma pessoa da família uma voz que não lhe pertence.

## 5. Patrocínios e espaços comerciais na produção

O processo de criação deve disponibilizar espaços configuráveis para patrocínios e apoios comerciais, sem os misturar com créditos de autoria.

Manter os escopos já definidos:
- `studio_global`;
- `ip`;
- `saga`;
- `product`;
- `campaign`.

Cada patrocínio deve guardar, pelo menos, patrocinador, âmbito e alvo, período de validade, texto de crédito, logótipo/asset, CTA/URL, regras de colocação, exclusividade, prioridade e notas internas.

O editor deve permitir definir, por produção:
- se existe patrocínio;
- em que locais pode aparecer (abertura, encerramento, página de créditos, descrição, capa promocional, vídeo promocional, website, etc.);
- texto e asset aprovados;
- duração/validade;
- restrições de categoria e exclusividade;
- aprovação editorial/comercial.

Um patrocinador de uma IP, saga ou produto não aparece automaticamente noutras IPs. A precedência de escopos existente deve ser mantida e testada. Os créditos de autoria e os avisos de patrocínio devem aparecer como blocos distintos e não podem sugerir que o patrocinador criou ou aprovou editorialmente a obra.

## 6. Primeiro acesso e reposição de password familiar

O acesso ao Studio continua privado, fechado por pré-registo e sem auto-registo público.

Decisão funcional:
1. O proprietário pré-regista a pessoa e define o nome, e-mail e permissões.
2. A credencial inicial comum atualmente definida é `1234`, apenas para o primeiro acesso.
3. Depois de autenticar com essa credencial temporária, a pessoa é obrigada a escolher uma password pessoal antes de aceder a qualquer área ou API normal.
4. O sistema marca a conta como `must_change_password` até a alteração estar concluída e não emite uma sessão normal enquanto essa condição existir.
5. A password temporária deixa de ser aceite após a primeira alteração.
6. O proprietário/gestor pode iniciar uma reposição de password para qualquer membro autorizado.
7. Uma reposição pelo gestor volta a colocar a conta em estado de alteração obrigatória no próximo acesso. O gestor não precisa de conhecer nem consultar a password pessoal do utilizador.
8. A reposição, alteração, falhas de autenticação e ações administrativas ficam auditadas.

Requisitos de segurança:
- guardar apenas hashes fortes de passwords;
- nunca devolver passwords/PINs em respostas API, logs ou dados do cliente;
- limitar tentativas e aplicar bloqueio/atraso contra força bruta;
- revogar sessões anteriores quando uma password é alterada ou reposta;
- obter identidade e permissões da sessão validada no servidor;
- não permitir que o cliente contorne o estado `must_change_password`;
- manter o Studio fora da Internet pública.

A credencial comum `1234` é uma exceção de bootstrap deliberada e de curta duração, não uma password de uso normal. Deve ser aceite apenas para contas pré-registadas no primeiro acesso e apenas no fluxo de troca de credencial. A implementação deve avaliar o risco de partilha dessa credencial e, se possível sem prejudicar a experiência familiar, migrar para códigos temporários individuais.

## 7. Critérios de aceitação

### Identidade e multi-IP
- [ ] A interface distingue claramente Baribudo Estúdio (produtora) de Baribudos (IP).
- [ ] É possível criar uma nova IP sem copiar ou herdar por acidente os canons de Baribudos.
- [ ] Cada IP tem canons, personagens, regras, vozes, permissões e patrocínios próprios.
- [ ] Partilha entre IPs exige uma relação explícita e autorizada.

### Pessoas e créditos
- [ ] Existe um registo central de pessoas e nomes de crédito, independente do login.
- [ ] Cada texto, imagem, áudio, vídeo e asset usado pode ser associado a contribuições e pessoas.
- [ ] O casting identifica a pessoa de origem, personagem/papel e perfil vocal utilizado.
- [ ] Variantes preservam a ligação ao titular da voz original.
- [ ] Os créditos finais são derivados dos elementos efetivamente usados na versão publicada.
- [ ] O pacote editorial inclui créditos e a publicação é bloqueada quando faltam atribuições/consentimentos obrigatórios.
- [ ] Créditos internos, créditos no produto, créditos no Website e créditos promocionais têm visibilidade configurável.

### Vozes
- [ ] Perfis originais, clones e variantes são distinguíveis.
- [ ] Consentimento e escopo são validados antes de cada utilização.
- [ ] É possível atribuir vozes a narradores, personagens e outros papéis.
- [ ] A origem e o titular permanecem rastreáveis após transformação.

### Patrocínios
- [ ] Existem escopos global, IP, saga, produto e campanha.
- [ ] A colocação e o texto são configuráveis e aprovados.
- [ ] Patrocínios não atravessam IPs sem autorização.
- [ ] Patrocínio é apresentado separadamente dos créditos de autoria.

### Autenticação familiar
- [ ] A primeira autenticação temporária obriga a definir password pessoal.
- [ ] O utilizador não consegue aceder a endpoints normais antes da troca.
- [ ] O gestor pode repor a credencial de outra pessoa sem conhecer a password nova.
- [ ] A reposição volta a exigir alteração no próximo acesso.
- [ ] Sessões antigas são revogadas e as ações ficam auditadas.

## 8. Estado técnico conhecido em 2026-11-12 — não confundir com conclusão

A inspeção estática do branch `main` encontrou componentes e serviços que já suportam parte destes conceitos:
- perfis vocais com titular, nome de crédito, consentimento, escopos e política de variações;
- orientação de interface para distinguir titular real e nome de crédito;
- atribuição de vozes no AudioCast;
- reconstrução de créditos de produto com campos para narração e vozes de personagens;
- serviço e rotas para créditos de produto;
- serviço de patrocínios com escopos global/IP/saga/produto/campanha;
- criação de IPs e canons por IP/saga.

Isto é uma base parcial, não prova que os créditos de texto, imagem, áudio e vídeo estejam completos, que os créditos sejam obrigatórios no pacote final ou que o fluxo esteja protegido por consentimento em todos os pontos de utilização.

A inspeção também encontrou autenticação legada baseada em nome/PIN em texto simples no serviço de login, e a aplicação ainda contém CORS aberto e montagem estática da raiz de storage. Por isso, os requisitos de primeiro acesso/reposição descritos nesta adenda **não estão considerados implementados** e devem ser tratados no trabalho de segurança/autenticação, com testes server-side antes de qualquer declaração de conclusão.

Esta adenda é uma especificação e um mapa de aceitação; não declara que as funcionalidades estejam concluídas.
