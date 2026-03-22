import { useEffect, useState } from "react"
import {
  ensureLocalProvider,
  getLocalAiRuntimeStatus,
  getLocalEngineManagerStatus,
  setLocalAiDefaultProvider,
  setupLocalAi,
  stopLocalProvider
} from "../api.js"

export default function LocalAiInstallerPanel() {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    load()
  }, [])

  async function load() {
    try {
      const runtime = await getLocalAiRuntimeStatus()
      const manager = await getLocalEngineManagerStatus()

      setStatus({
        runtime,
        manager
      })
    } catch {
      setStatus(null)
    }
  }

  async function setup() {
    await setupLocalAi({})
    await load()
  }

  async function ensure(provider) {
    await ensureLocalProvider(provider)
    await load()
  }

  async function stop(provider) {
    await stopLocalProvider(provider)
    await load()
  }

  async function setDefault(provider) {
    await setLocalAiDefaultProvider(provider)
    await load()
  }

  return (
    <div>
      <h2>Local AI</h2>

      <button onClick={setup}>Setup</button>

      <button onClick={() => ensure("stable_diffusion")}>
        Ensure SD
      </button>

      <button onClick={() => ensure("automatic1111")}>
        Ensure A1111
      </button>

      <button onClick={() => stop("stable_diffusion")}>
        Stop SD
      </button>

      <button onClick={() => stop("automatic1111")}>
        Stop A1111
      </button>

      <button onClick={() => setDefault("stable_diffusion")}>
        Default SD
      </button>

      <button onClick={() => setDefault("automatic1111")}>
        Default A1111
      </button>

      <pre>{JSON.stringify(status, null, 2)}</pre>
    </div>
  )
  }
