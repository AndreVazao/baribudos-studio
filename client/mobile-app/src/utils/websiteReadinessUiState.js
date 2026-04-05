function normalizeText(value) {
  return String(value || "").trim()
}

function asArray(value) {
  return Array.isArray(value) ? value : []
}

function classifyReasons(reasons = []) {
  const blocking = []
  const optional = []

  for (const reason of asArray(reasons)) {
    const text = normalizeText(reason)
    if (!text) continue

    const normalized = text.toLowerCase()

    if (
      normalized.includes("seo") ||
      normalized.includes("promoc") ||
      normalized.includes("campaign") ||
      normalized.includes("extra") ||
      normalized.includes("opcional")
    ) {
      optional.push(text)
      continue
    }

    blocking.push(text)
  }

  return { blocking, optional }
}

function getContractMeaning(contract = {}, eligibleForPublish = false) {
  const status = normalizeText(contract?.status).toLowerCase()
  const score = Number(contract?.score_percent || 0)

  if (eligibleForPublish || status === "ready" || status === "valid" || score >= 85) {
    return {
      label: "Contrato Website válido para publicar",
      meaning: "O contrato público já tem qualidade suficiente para publicação segura.",
      tone: "positive",
    }
  }

  if (status === "incomplete" || score <= 40) {
    return {
      label: "Contrato Website ainda incompleto",
      meaning: "O pacote público ainda não cumpre o nível necessário para publicação segura.",
      tone: "warning",
    }
  }

  return {
    label: "Contrato Website precisa de revisão antes de publicar",
    meaning: "O contrato existe, mas ainda precisa de revisão antes de uma publicação confortável.",
    tone: "warning",
  }
}

export function buildWebsiteReadinessUiState({ selectedProject = null, publishStatus = null } = {}) {
  const publicationPolicy = publishStatus?.publication_policy || null
  const reasons = asArray(publicationPolicy?.reasons)
  const { blocking: derivedBlocking, optional: derivedOptional } = classifyReasons(reasons)

  const packageFrozen = Boolean(publicationPolicy?.has_frozen_package)
  const readyForPublish = Boolean(publicationPolicy?.ready_for_publish)
  const eligibleForWebsitePublish = Boolean(publicationPolicy?.eligible_for_website_publish)

  const blockingReasons = [...derivedBlocking]
  const optionalReasons = [...derivedOptional]

  if (!selectedProject?.ready_for_publish) {
    blockingReasons.push("Projeto ainda não está pronto para publish")
  }

  if (!packageFrozen) {
    blockingReasons.push("Package ainda não congelado")
  }

  if (!eligibleForWebsitePublish) {
    const contractStatus = normalizeText(publicationPolicy?.contract?.status)
    if (contractStatus) {
      blockingReasons.push(`Contrato Website ainda não aceitável (${contractStatus})`)
    } else {
      blockingReasons.push("Contrato Website ainda não é aceitável o suficiente")
    }
  }

  const uniqueBlocking = [...new Set(blockingReasons)]
  const uniqueOptional = [...new Set(optionalReasons.filter((item) => !uniqueBlocking.includes(item)))]

  let readiness = {
    label: "Ainda bloqueado",
    meaning: "O projeto ainda tem bloqueios que impedem publicação segura.",
    tone: "warning",
    nextAction: "Fechar os bloqueios obrigatórios antes de publicar.",
  }

  if (packageFrozen && uniqueBlocking.length === 0 && eligibleForWebsitePublish && uniqueOptional.length > 0) {
    readiness = {
      label: "Pronto com melhorias opcionais pendentes",
      meaning: "Já não existem bloqueios obrigatórios, mas ainda há melhorias não críticas por fechar.",
      tone: "neutral",
      nextAction: "Publicar agora ou concluir melhorias opcionais primeiro.",
    }
  }

  if (packageFrozen && uniqueBlocking.length === 0 && eligibleForWebsitePublish && uniqueOptional.length === 0) {
    readiness = {
      label: "Pronto para publicar",
      meaning: "O projeto já cumpre os requisitos necessários para publicação segura.",
      tone: "positive",
      nextAction: "Publicar no Website.",
    }
  }

  const contractMeaning = getContractMeaning(publicationPolicy?.contract || {}, eligibleForWebsitePublish)

  if (!packageFrozen) {
    readiness.nextAction = "Congelar o package antes de publicar."
  } else if (!eligibleForWebsitePublish) {
    readiness.nextAction = "Rever o contrato/payload antes de publicar."
  }

  return {
    publicationPolicy,
    packageFrozen,
    readyForPublish,
    eligibleForWebsitePublish,
    readiness,
    blockers: uniqueBlocking,
    optionalImprovements: uniqueOptional,
    contractMeaning,
  }
}
