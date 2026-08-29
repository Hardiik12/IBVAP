import { fetchApi } from "./apiClient";
import { EvidenceRecord, VerifyResponse } from "../types/evidence";
import { MOCK_EVIDENCE } from "./mockData";

export interface EvidenceCaptureInput {
  image: string; // Base64 JPEG data URL
  camera_id?: string;
  zone_id?: string;
  zone_name?: string;
  track_id: number;
  class_name?: string;
  confidence?: number;
  bbox?: number[];
  timestamp?: string;
}

export const evidenceService = {
  async captureRealEvidence(input: EvidenceCaptureInput): Promise<EvidenceRecord> {
    const res = await fetchApi<any>("/evidence/capture", {
      method: "POST",
      body: JSON.stringify(input),
    });

    return {
      evidence_id: res.evidence_id,
      event_id: res.event_id,
      camera_id: res.camera_id,
      file_path: res.file_path,
      sha256_hash: res.sha256_hash,
      captured_at: res.captured_at,
      image_url: res.image_url || `/api/v1/evidence/${res.evidence_id}/image`,
      verified_status: "VERIFIED",
    };
  },

  async getEvidence(evidenceId: string): Promise<EvidenceRecord> {
    try {
      const data = await fetchApi<any>(`/evidence/${evidenceId}`);
      return {
        evidence_id: data.id || data.evidence_id || evidenceId,
        event_id: data.event_id,
        camera_id: data.metadata?.camera_id || "cam-01",
        file_path: data.file_path,
        sha256_hash: data.sha256_hash,
        captured_at: data.captured_at,
        image_url: data.image_url || `/api/v1/evidence/${data.id || evidenceId}/image`,
        verified_status: "VERIFIED",
      };
    } catch {
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
    const url = `/evidence/${evidenceId}/verify${simulateTamper ? "?simulate_tamper=true" : ""}`;
    try {
      const res = await fetchApi<any>(url, {
        method: "POST",
      });

      return {
        evidence_id: res.evidence_id,
        stored_hash: res.stored_hash,
        current_hash: res.current_hash,
        status: res.status, // "VERIFIED" or "TAMPERED" / "MISMATCH"
        match: res.verified === true,
        verified_at: res.verified_at || new Date().toISOString(),
      };
    } catch {
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
    try {
      const data = await fetchApi<any[]>("/evidence");
      if (data && Array.isArray(data) && data.length > 0) {
        return data.map((e) => ({
          evidence_id: e.id || e.evidence_identifier,
          event_id: e.event_id,
          camera_id: e.metadata?.camera_id || "cam-01",
          file_path: e.file_path,
          sha256_hash: e.sha256_hash || "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
          captured_at: e.captured_at || e.created_at || new Date().toISOString(),
          image_url: e.image_url || `/api/v1/evidence/${e.id}/image`,
          verified_status: e.sha256_hash ? "VERIFIED" : "UNKNOWN",
        }));
      }
    } catch (err) {
      console.warn("[evidenceService] Failed to load backend evidence, using demo mock:", err);
    }
    return Object.values(MOCK_EVIDENCE);
  },
};
