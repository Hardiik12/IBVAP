import { fetchApi } from "./apiClient";
import { EvidenceRecord, VerifyResponse } from "../types/evidence";

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
      evidence_id: res.id || res.evidence_id,
      event_id: res.event_id,
      camera_id: res.camera_id,
      file_path: res.file_path,
      sha256_hash: res.sha256_hash,
      captured_at: res.captured_at,
      image_url: res.image_url || `/api/v1/evidence/${res.id || res.evidence_id}/image`,
      verified_status: "VERIFIED",
    };
  },

  async getEvidence(evidenceId: string): Promise<EvidenceRecord> {
    const data = await fetchApi<any>(`/evidence/${evidenceId}`);
    return {
      evidence_id: data.id || data.evidence_identifier || evidenceId,
      event_id: data.event_id,
      camera_id: data.metadata?.camera_id || "cam-01",
      file_path: data.file_path,
      sha256_hash: data.sha256_hash || "NOT_HASHED",
      captured_at: data.captured_at || new Date().toISOString(),
      image_url: data.image_url || `/api/v1/evidence/${data.id || evidenceId}/image`,
      verified_status: data.sha256_hash ? "UNKNOWN" : "NOT_HASHED",
    };
  },

  async generateHash(evidenceId: string): Promise<any> {
    return await fetchApi<any>(`/evidence/${evidenceId}/hash`, {
      method: "POST",
    });
  },

  async verifyEvidence(evidenceId: string, simulateTamper = false): Promise<VerifyResponse> {
    const query = simulateTamper ? "?simulate_tamper=true" : "";
    const res = await fetchApi<any>(`/evidence/${evidenceId}/verify${query}`, {
      method: "GET",
    });

    const isMatch = res.verified === true || res.status === "VERIFIED";

    return {
      evidence_id: res.evidence_id || evidenceId,
      stored_hash: res.stored_hash || null,
      current_hash: res.current_hash || null,
      status: res.status || (isMatch ? "VERIFIED" : "MISMATCH"),
      verified: isMatch,
      match: isMatch,
      verified_at: res.verified_at || new Date().toISOString(),
    };
  },

  async getAllEvidence(): Promise<EvidenceRecord[]> {
    try {
      const data = await fetchApi<any[]>("/evidence");
      if (data && Array.isArray(data)) {
        return data.map((e) => ({
          evidence_id: e.id || e.evidence_identifier,
          event_id: e.event_id,
          camera_id: e.metadata?.camera_id || "cam-01",
          file_path: e.file_path,
          sha256_hash: e.sha256_hash || "NOT_HASHED",
          captured_at: e.captured_at || e.created_at || new Date().toISOString(),
          image_url: e.image_url || `/api/v1/evidence/${e.id}/image`,
          verified_status: e.sha256_hash ? "UNKNOWN" : "NOT_HASHED",
        }));
      }
    } catch (err) {
      console.warn("[evidenceService] Failed to load backend evidence:", err);
      return [];
    }
    return [];
  },

  async clearEvidenceVault(): Promise<{ message: string; cleared_count: number }> {
    return await fetchApi<{ message: string; cleared_count: number }>("/evidence", {
      method: "DELETE",
    });
  },
};
