function normalizeText(value) {
  return String(value || "").trim()
}

function inferVoiceType(profile = {}) {
  if (profile.is_variant || profile.variant_of_profile_id || profile.original_profile_id || profile.variant_policy) {
    return "variant"
  }
  return "original"
}

export function buildVoiceUsageUiState(profile = {}) {
  const realOwner = normalizeText(profile.real_owner_name || profile.voice_owner_name || profile.owner_name || profile.real_owner || profile.owner)
  const creditedName = normalizeText(profile.credit_name || profile.credited_name || profile.display_credit_name || profile.name)
  const voiceType = inferVoiceType(profile)
  const linkedOriginal = normalizeText(profile.original_profile_name || profile.original_profile_id || profile.variant_of_profile_id)

  let usage = {
    label: "Uso recomendado",
    meaning: "Seguro para uso editorial normal.",
    tone: "positive",
  }

  if (voiceType === "variant") {
    usage = {
      label: "Uso recomendado",
      meaning: linkedOriginal
        ? `Variante editorial ligada a ${linkedOriginal}. Rever apenas se o contexto pedir máxima fidelidade ao original.`
        : "Variante editorial segura para uso normal, com revisão recomendada quando necessário.",
      tone: "neutral",
    }
  }

  if (!realOwner || !creditedName) {
    usage = {
      label: "Uso com atenção",
      meaning: "Faltam dados de dono real ou nome para créditos. Rever antes de usar em publicação final.",
      tone: "warning",
    }
  }

  return {
    realOwner: realOwner || "Não definido",
    creditedName: creditedName || "Não definido",
    voiceType,
    voiceTypeLabel: voiceType === "variant" ? "Variante editorial" : "Original",
    linkedOriginal,
    usage,
    nextAction: !realOwner || !creditedName
      ? "Completar dono real e nome para créditos."
      : voiceType === "variant"
        ? "Confirmar atribuição ao papel certo e manter vínculo ao perfil original."
        : "Aplicar esta voz ao papel certo no elenco.",
  }
}
