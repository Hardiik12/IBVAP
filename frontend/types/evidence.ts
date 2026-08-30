export type VerifyStatus = "VERIFIED" | "MISMATCH" | "TAMPERED" | "UNKNOWN" | "PENDING" | "NOT_HASHED";

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
  stored_hash?: string | null;
  current_hash?: string | null;
  status: string;
  verified?: boolean;
  match?: boolean;
  verified_at?: string;
}
