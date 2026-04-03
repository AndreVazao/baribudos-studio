# Baribudos Studio — Merge Ready Checklist

## Core branch gate
- [ ] Frontend build verde
- [ ] Backend import/compile verde
- [ ] Workflow `Studio CI` verde
- [ ] Sem erros críticos no dashboard principal
- [ ] Sem regressões nos painéis principais

## Editorial flow
- [ ] Criação de projeto com `official / standalone / hidden_*`
- [ ] `stage_modes` persistidos por projeto
- [ ] `StorySourcePanel` alinhado com `story_input_mode`
- [ ] `IllustrationPipelinePanel` alinhado com `illustration_mode`
- [ ] `ProductionPipelinePanel` alinhado com `video_mode`
- [ ] `AudioCastPanel` alinhado com casting e ownership

## Voice / clone governance
- [ ] Perfil vocal com `owner_person_id`
- [ ] Perfil vocal com `owner_person_name`
- [ ] Perfil vocal com `credited_name`
- [ ] Política de variações persistida
- [ ] Credits automáticos de áudio no package final

## Publication package
- [ ] `publication_package_service.py` coerente
- [ ] `website_payload` coerente
- [ ] `audio_credit_lines` presentes quando houver casting
- [ ] `typography` presente no package
- [ ] `continuity` presente no package

## Final operational gate
- [ ] Branch pronto para merge em `main`
- [ ] Build desktop confirmada
- [ ] Build APK confirmada
- [ ] Deploy/integrações sem regressão crítica
