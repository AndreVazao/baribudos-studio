function normalizeText(value) {
  return String(value || "").trim()
}

function hasText(value) {
  return normalizeText(value).length > 0
}

export function buildStoryFlowUiState({
  storyText = "",
  layoutInfo = null,
  lastAction = "",
  stageMode = "",
} = {}) {
  const rawTextPresent = hasText(storyText)
  const shapedStoryPresent = Boolean(layoutInfo && (layoutInfo.pages?.length || layoutInfo.sections?.length || layoutInfo.structure))

  let state = {
    label: "História por introduzir",
    meaning: "Este é o ponto de entrada do texto bruto da história.",
    nextAction: "Introduzir texto da história.",
    tone: "warning",
  }

  if (rawTextPresent) {
    state = {
      label: "Texto guardado",
      meaning: "A história já está guardada no Studio e pronta para edição e paginação.",
      nextAction: shapedStoryPresent ? "Rever layout e completude da história." : "Abrir layout para organizar páginas e estrutura.",
      tone: "positive",
    }
  }

  if (lastAction === "updated") {
    state = {
      ...state,
      label: "Alterações guardadas",
      meaning: "A versão atual da história já está guardada no Studio.",
    }
  }

  const illustrationReadiness = rawTextPresent && shapedStoryPresent
    ? {
        label: "Pronto para avançar para ilustração",
        meaning: "O texto e a estrutura já estão estáveis o suficiente para avançar para visuais.",
        tone: "positive",
      }
    : {
        label: "Ainda não estável para ilustração",
        meaning: "Convém fechar texto e estrutura antes de avançar para visuais, para evitar retrabalho.",
        tone: "warning",
      }

  const modeLabel = stageMode === "story_input_mode"
    ? "Introdução de texto"
    : stageMode === "illustration_mode"
      ? "Ilustração"
      : stageMode === "audio_mode"
        ? "Áudio"
        : stageMode === "video_mode"
          ? "Vídeo"
          : "Fluxo editorial"

  return {
    state,
    rawTextPresent,
    shapedStoryPresent,
    illustrationReadiness,
    modeLabel,
  }
}
