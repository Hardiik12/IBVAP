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
  },

  async verifyEvidence(evidenceId: string, simulateTamper = false): Promise<VerifyResponse> {
    const url = `/evidence/${evidenceId}/verify${simulateTamper ? "?simulate_tamper=true" : ""}`;
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
  },

  async getAllEvidence(): Promise<EvidenceRecord[]> {
    try {
      const list = await fetchApi<any[]>("/evidence");
      return list.map((item) => ({
        evidence_id: item.id,
        event_id: item.event_id,
        camera_id: item.metadata?.camera_id || "cam-01",
        file_path: item.file_path,
        sha256_hash: item.sha256_hash,
        captured_at: item.captured_at,
        image_url: item.image_url || `/api/v1/evidence/${item.id}/image`,
        verified_status: "VERIFIED",
      }));
    } catch {
      return [];
    }
  },
};
