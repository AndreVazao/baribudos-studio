import test, { after, before } from "node:test"
import assert from "node:assert/strict"

const storage = new Map()
globalThis.localStorage = {
  getItem: (key) => storage.has(key) ? storage.get(key) : null,
  setItem: (key, value) => storage.set(key, String(value)),
  removeItem: (key) => storage.delete(key)
}
const dispatched = []
globalThis.CustomEvent = class CustomEvent {
  constructor(type) { this.type = type }
}
globalThis.window = {
  dispatchEvent: (event) => dispatched.push(event.type)
}

const api = await import("../src/api/core.js")
const originalFetch = globalThis.fetch

before(() => {
  api.clearAuthSession()
})

after(() => {
  globalThis.fetch = originalFetch
  api.clearAuthSession()
})

test("authenticated GET and POST attach the bearer token", async () => {
  const requests = []
  globalThis.fetch = async (url, options = {}) => {
    requests.push({ url, options })
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  }

  api.setAuthToken("opaque-session-token")
  await api.get("https://studio.example/api/projects")
  await api.post("https://studio.example/api/projects", { title: "Story" })

  assert.equal(requests.length, 2)
  for (const request of requests) {
    assert.equal(request.options.headers.get("Authorization"), "Bearer opaque-session-token")
  }
})

test("multipart requests receive Bearer without forcing a JSON content type", async () => {
  let captured
  globalThis.fetch = async (url, options = {}) => {
    captured = { url, options }
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  }

  api.setAuthToken("multipart-session-token")
  const form = new FormData()
  form.append("file", new Blob(["asset"]), "asset.png")
  await api.handle(api.apiFetch("https://studio.example/api/assets/upload", {
    method: "POST",
    body: form
  }))

  assert.equal(captured.options.headers.get("Authorization"), "Bearer multipart-session-token")
  assert.equal(captured.options.headers.has("Content-Type"), false)
})

test("profile cache is memory-only and never writes the legacy localStorage key", () => {
  api.setSavedUser({ id: "user-1", name: "Editor", role: "editor" })
  assert.equal(api.getSavedUser().id, "user-1")
  assert.equal(storage.has("baribudos_python_user"), false)
})

test("401 clears the in-memory session and notifies the application", async () => {
  api.setAuthToken("expired-token")
  globalThis.fetch = async () => new Response(JSON.stringify({ detail: "Sessão expirada" }), {
    status: 401,
    headers: { "Content-Type": "application/json" }
  })

  await assert.rejects(api.get("https://studio.example/api/users/me"), /Sessão expirada/)
  assert.equal(api.hasAuthToken(), false)
  assert.equal(api.getSavedUser(), null)
  assert.ok(dispatched.includes("baribudos:auth-expired"))
})
