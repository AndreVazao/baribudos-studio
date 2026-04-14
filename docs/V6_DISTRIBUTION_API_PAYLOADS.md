# V6 Distribution API Payloads

## PATCH channel state
Request body example:
```json
{
  "status": "ready",
  "notes": "Payload preparado para submissão externa",
  "payload_snapshot_json": {
    "title": "Baribudos - Episódio 1",
    "cover": "/assets/covers/baribudos-ep1.jpg",
    "description": "Primeira aventura no universo Baribudos"
  }
}
```

## POST attempt
Request body example:
```json
{
  "attempted_at": "2026-04-13T12:00:00Z",
  "notes": "Tentativa manual a partir do Studio"
}
```

## POST publish success
Request body example:
```json
{
  "published_at": "2026-04-13T12:05:00Z",
  "notes": "Publicado com sucesso no canal externo"
}
```

## POST publish failed
Request body example:
```json
{
  "failed_at": "2026-04-13T12:06:00Z",
  "error": "Missing thumbnail asset",
  "notes": "Falha na preparação final do payload"
}
```

## Regra
Cada canal deve poder guardar o seu próprio snapshot, o seu próprio histórico de tentativas e o seu próprio último erro.
