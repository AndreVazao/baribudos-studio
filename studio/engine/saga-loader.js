import fs from "fs";
import path from "path";

const SAGAS_BASE_PATH = path.join(process.cwd(), "studio", "sagas");

class SagaLoader {
  constructor() {
    this.loadedSagas = {};
  }

  loadAllSagas() {
    const sagaFolders = fs.readdirSync(SAGAS_BASE_PATH);

    sagaFolders.forEach(sagaId => {
      this.loadedSagas[sagaId] = this.loadSaga(sagaId);
    });

    return this.loadedSagas;
  }

  loadSaga(sagaId) {
    const sagaPath = path.join(SAGAS_BASE_PATH, sagaId);

    const visualCanon = this.safeLoadJSON(sagaPath, "visual-canon.json");
    const narrativeCanon = this.safeLoadJSON(sagaPath, "narrative-canon.json");
    const characters = this.safeLoadJSON(sagaPath, "characters-master.json");
    const seriesArc = this.safeLoadJSON(sagaPath, "series-arc-canon.json");
    const episodeCanon = this.safeLoadJSON(sagaPath, "episode-canon.json");

    return {
      id: sagaId,
      visualCanon,
      narrativeCanon,
      characters,
      seriesArc,
      episodeCanon
    };
  }

  safeLoadJSON(base, file) {
    const filePath = path.join(base, file);

    if (!fs.existsSync(filePath)) {
      console.warn(`Missing ${file} in ${base}`);
      return null;
    }

    return JSON.parse(fs.readFileSync(filePath, "utf-8"));
  }

  getSaga(sagaId) {
    return this.loadedSagas[sagaId];
  }

  validateStoryAgainstCanon(sagaId, story) {
    const saga = this.getSaga(sagaId);

    if (!saga) throw new Error("Saga not found");

    if (!story.structure) {
      throw new Error("Story missing narrative structure");
    }

    if (!saga.narrativeCanon) return true;

    const requiredSteps = saga.narrativeCanon.narrative_structure_standard;

    requiredSteps.forEach(step => {
      if (!story.structure.includes(step)) {
        console.warn("Missing narrative step:", step);
      }
    });

    return true;
  }

  validateVisualConsistency(sagaId, illustrationMeta) {
    const saga = this.getSaga(sagaId);

    if (!saga.visualCanon) return true;

    if (illustrationMeta.realistic === true) {
      throw new Error("Visual violation: realism not allowed");
    }

    if (illustrationMeta.scary === true) {
      throw new Error("Visual violation: scary content");
    }

    return true;
  }

  isProtectedIP(sagaId) {
    return sagaId === "baribudos";
  }

  canUserEditSaga(userRole, sagaId) {
    if (this.isProtectedIP(sagaId)) {
      return userRole === "creator";
    }
    return true;
  }
}

export default new SagaLoader();
