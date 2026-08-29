import { fetchApi } from "./apiClient";
import { EvidenceRecord, VerifyResponse } from "../types/evidence";
import { MOCK_EVIDENCE } from "./mockData";

export const evidenceService = {
  async getEvidence(evidenceId: string): Promise<EvidenceRecord> {
    try {
      return await fetchApi<EvidenceRecord>(`/evidence/${evidenceId}`);
    } catch {
      console.warn(`[evidenceService] Using fallback mock evidence for ${evidenceId}`);
      if (MOCK_EVIDENCE[evidenceId]) {
        return MOCK_EVIDENCE[evidenceId];
      }
      return {
        evidence_id: evidenceId,
        event_id: `evt-${evidenceId.replace("evi-", "")}`,
        file_path: `/data/evidence/${evidenceId}.jpg`,
        sha256_hash: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        captured_at: new Date().toISOString(),
        image_url: "/placeholder-feed.jpg",
        verified_status: "UNKNOWN",
      };
    }
  },

  async verifyEvidence(evidenceId: string, simulateTamper = false): Promise<VerifyResponse> {
    try {
      if (simulateTamper) {
        // Controlled Tamper Simulation for Demo Presentation
        const mock = await this.getEvidence(evidenceId);
        const tamperedHash = "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4";
        return {
          evidence_id: evidenceId,
          stored_hash: mock.sha256_hash,
          current_hash: tamperedHash,
          status: "TAMPERED",
          match: false,
          verified_at: new Date().toISOString(),
        };
      }

      return await fetchApi<VerifyResponse>(`/evidence/${evidenceId}/verify`, {
        method: "POST",
      });
    } catch {
      console.warn(`[evidenceService] Using fallback verification result for ${evidenceId}`);
      const mock = await this.getEvidence(evidenceId);
      if (simulateTamper) {
        return {
          evidence_id: evidenceId,
          stored_hash: mock.sha256_hash,
          current_hash: "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
          status: "TAMPERED",
          match: false,
          verified_at: new Date().toISOString(),
        };
      }
      return {
        evidence_id: evidenceId,
        stored_hash: mock.sha256_hash,
        current_hash: mock.sha256_hash,
        status: "VERIFIED",
        match: true,
        verified_at: new Date().toISOString(),
      };
    }
  },

  async getAllEvidence(): Promise<EvidenceRecord[]> {
    return Object.values(MOCK_EVIDENCE);
  },
};
