export type VerifyStatus = "VERIFIED" | "TAMPERED" | "UNKNOWN" | "PENDING";

export interface EvidenceRecord {
  evidence_id: string;
  event_id: string;
  camera_id?: string;
  file_path: string;
  sha256_hash: string;
  captured_at: string;
  image_url: string;
  verified_status?: VerifyStatus;
  last_verified_at?: string;
}

export interface VerifyResponse {
  evidence_id: string;
  stored_hash: string;
  current_hash: string;
  status: "VERIFIED" | "TAMPERED";
  match: boolean;
  verified_at: string;
}
