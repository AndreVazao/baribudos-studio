function normalizeText(value) {
  return String(value || "").trim()
}

export function getPublishFailureInfo(message = "") {
  const normalized = normalizeText(message).toLowerCase()
  if (!normalized) return null

  if (
    normalized.includes("website_publish_connection_error") ||
    normalized.includes("website_control_connection_error") ||
    normalized.includes("connection refused") ||
    normalized.includes("timed out")
  ) {
    return {
      label: "Website indisponível",
      meaning: "O Studio não conseguiu comunicar com o Website.",
      nextAction: "Verificar ligação ao Website e tentar novamente.",
      kind: "website_unavailable",
    }
  }

  if (
    normalized.includes("website_publish_api_key_missing") ||
    normalized.includes("401") ||
    normalized.includes("403") ||
    normalized.includes("unauthorized") ||
    normalized.includes("credenciais")
  ) {
    return {
      label: "Autenticação do Website falhou",
      meaning: "O Website rejeitou as credenciais usadas pelo Studio.",
      nextAction: "Verificar credenciais do Website antes de repetir.",
      kind: "website_auth_failed",
    }
  }

  if (
    normalized.includes("project_not_publishable") ||
    normalized.includes("publication_package_not_frozen") ||
    normalized.includes("contract") ||
    normalized.includes("schema") ||
    normalized.includes("invalid")
  ) {
    return {
      label: "Publicação rejeitada pelo Website",
      meaning: "O Website recebeu o pedido, mas rejeitou o contrato/payload público.",
      nextAction: "Rever package e contrato antes de voltar a publicar.",
      kind: "contract_rejected",
    }
  }

  if (normalized.includes("checksum") || normalized.includes("project_version") || normalized.includes("diverg")) {
    return {
      label: "Divergência entre Studio e Website",
      meaning: "O estado do Website já não coincide plenamente com a intenção atual do Studio.",
      nextAction: "Abrir reconcile e corrigir divergência.",
      kind: "divergence_detected",
    }
  }

  if (normalized.includes("materializa") || normalized.includes("materialized")) {
    return {
      label: "Materialização no Website não confirmada",
      meaning: "Há sinais de receção, mas ainda não há confirmação clara da materialização.",
      nextAction: "Abrir status ou reconcile e confirmar materialização.",
      kind: "materialization_not_confirmed",
    }
  }

  return {
    label: "Falha ao comunicar com o Website",
    meaning: "O Studio não conseguiu concluir a operação no Website com confiança.",
    nextAction: "Confirmar estado do Website e repetir após validação.",
    kind: "generic_failure",
  }
}

export function buildWebsitePublishUiState({
  selectedProject = null,
  publishStatus = null,
  publicationDetail = null,
  divergence = null,
  lastError = "",
} = {}) {
  const currentSync = selectedProject?.website_sync || publishStatus?.website_sync || null
  const publicationPolicy = publishStatus?.publication_policy || null
  const failure = getPublishFailureInfo(lastError)

  const packageReady = Boolean(
    selectedProject?.ready_for_publish &&
    publishStatus?.has_frozen_package &&
    publicationPolicy?.eligible_for_website_publish
  )
  const publishSent = Boolean(currentSync?.published_at)
  const websiteReceived = Boolean(currentSync?.ok && (currentSync?.response?.ok ?? true) && currentSync?.synced_at)
  const websiteMaterialized = Boolean(
    publicationDetail?.publication_id &&
    ((publicationDetail?.variants || []).length > 0 || publicationDetail?.status === "published")
  )
  const divergenceDetected = Boolean(divergence && divergence.divergence_ok === false)

  let primary = {
    key: "preparacao_em_curso",
    label: "Preparação em curso",
    meaning: "O projeto ainda não está pronto para publicar com confiança.",
    ok: false,
    nextAction: "Fechar bloqueios de package e readiness antes de publicar.",
  }

  if (packageReady) {
    primary = {
      key: "pacote_pronto",
      label: "Pacote pronto para publicar",
      meaning: "O Studio já tem package congelado e pronto para envio público.",
      ok: true,
      nextAction: "Publicar no Website.",
    }
  }

  if (publishSent) {
    primary = {
      key: "publish_enviado",
      label: "Publicação enviada",
      meaning: "O Studio já enviou a publicação, mas ainda falta confirmação do Website.",
      ok: true,
      nextAction: "Aguardar confirmação do Website.",
    }
  }

  if (websiteReceived) {
    primary = {
      key: "website_recebido",
      label: "Website confirmou receção",
      meaning: "O Website aceitou a publicação enviada pelo Studio.",
      ok: true,
      nextAction: "Confirmar materialização no Website.",
    }
  }

  if (websiteMaterialized) {
    primary = {
      key: "website_materializado",
      label: "Website materializado",
      meaning: "A publicação já está refletida no lado público/comercial do Website.",
      ok: true,
      nextAction: "Rever status final ou continuar operação.",
    }
  }

  if (divergenceDetected) {
    primary = {
      key: "divergencia_detectada",
      label: "Divergência detetada",
      meaning: "O Website já não coincide plenamente com a intenção atual do Studio.",
      ok: false,
      nextAction: "Abrir reconcile e corrigir divergência.",
    }
  }

  if (failure) {
    primary = {
      key: "falha_operacional",
      label: failure.label,
      meaning: failure.meaning,
      ok: false,
      nextAction: failure.nextAction,
    }
  }

  const receipt = websiteReceived
    ? {
        label: websiteMaterialized
          ? "Recebido e materialização confirmada"
          : divergenceDetected
            ? "Recebido, mas requer atenção"
            : "Recebido e aguardando confirmação de materialização",
        publicationId: currentSync?.publication_id || currentSync?.response?.publication_id || "-",
        variantId: currentSync?.variant_id || currentSync?.response?.variant_id || "-",
        receivedAt: currentSync?.synced_at || currentSync?.response?.received_at || "-",
      }
    : null

  return {
    currentSync,
    publicationPolicy,
    failure,
    primary,
    receipt,
    steps: [
      { label: "Pacote pronto para publicar", done: packageReady },
      { label: "Publicação enviada", done: publishSent },
      { label: "Website confirmou receção", done: websiteReceived },
      { label: "Website materializado", done: websiteMaterialized },
      { label: "Divergência detetada", done: divergenceDetected, attention: true },
    ],
  }
}
