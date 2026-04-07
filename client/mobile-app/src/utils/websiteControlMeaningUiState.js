function normalizeText(value) {
  return String(value || "").trim()
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function inferHealthState(health = {}, lastError = "") {
  if (normalizeText(lastError)) {
    return {
      label: "Website com atenção necessária",
      meaning: "O Studio encontrou falhas recentes ao consultar ou controlar o Website.",
      tone: "warning",
      nextAction: "Atualizar cockpit ou rever falha antes de continuar.",
    }
  }

  if (health?.ok || normalizeText(health?.status).toLowerCase() === "healthy") {
    return {
      label: "Website operacional",
      meaning: "O Website está acessível e a responder corretamente ao Studio.",
      tone: "positive",
      nextAction: "Continuar operação normal ou rever publicações ativas.",
    }
  }

  return {
    label: "Website indisponível",
    meaning: "O Website não está a responder como esperado ao Studio.",
    tone: "warning",
    nextAction: "Rever conectividade, deploy ou estado do Website antes de publicar.",
  }
}

function inferPublicationState(publicationDetail = null) {
  if (!publicationDetail) {
    return {
      label: "Materialização por confirmar",
      meaning: "Ainda não há detalhe suficiente para confirmar se a publicação já está refletida no Website.",
      tone: "warning",
      nextAction: "Consultar a publication antes de concluir a operação.",
    }
  }

  const variants = asArray(publicationDetail?.variants)
  const activeProducts = variants.flatMap((variant) => asArray(variant?.products)).filter((product) => product?.active)
  const publishedVariants = variants.filter((variant) => variant?.published)

  if (publishedVariants.length > 0 && activeProducts.length > 0) {
    return {
      label: "Materialização confirmada",
      meaning: "A publicação já está refletida no lado público/comercial com variantes e produtos utilizáveis.",
      tone: "positive",
      nextAction: "Rever status final ou continuar operação.",
    }
  }

  return {
    label: "Materialização incompleta",
    meaning: "A publicação existe, mas ainda não está refletida de forma confortável no lado público/comercial.",
    tone: "warning",
    nextAction: "Rever variantes, produtos ativos ou revalidar a publicação.",
  }
}

function inferDivergenceState(divergence = null) {
  if (!divergence) {
    return {
      label: "Divergência por confirmar",
      meaning: "Ainda não existe leitura suficiente para confirmar se há ou não divergência real.",
      tone: "neutral",
      nextAction: "Consultar divergence/reconcile se necessário.",
      reasons: [],
    }
  }

  if (divergence?.divergence_ok) {
    return {
      label: "Sem divergência crítica",
      meaning: "O Studio e o Website parecem alinhados no estado principal desta publicação.",
      tone: "positive",
      nextAction: "Continuar operação normal ou rever apenas detalhes finais.",
      reasons: asArray(divergence?.reasons),
    }
  }

  const practicalReasons = asArray(divergence?.reasons).map((reason) => {
    const text = normalizeText(reason)
    const lower = text.toLowerCase()
    if (lower.includes("checksum") || lower.includes("version")) return "Versão ou checksum diferente da esperada"
    if (lower.includes("product") || lower.includes("active")) return "Publicação ativa sem material comercial suficientemente refletido"
    return text || "Materialização incompleta ou diferente do esperado"
  })

  return {
    label: "Divergência detetada",
    meaning: "O Website recebeu algo diferente ou ainda não refletiu totalmente o que o Studio esperava.",
    tone: "warning",
    nextAction: "Revalidar, rever publication detail ou corrigir antes de republicar.",
    reasons: [...new Set(practicalReasons)],
  }
}

export function buildWebsiteControlMeaningUiState({ health = null, publicationDetail = null, divergence = null, lastError = "" } = {}) {
  const healthState = inferHealthState(health || {}, lastError)
  const publicationState = inferPublicationState(publicationDetail)
  const divergenceState = inferDivergenceState(divergence)

  return {
    healthState,
    publicationState,
    divergenceState,
  }
}
