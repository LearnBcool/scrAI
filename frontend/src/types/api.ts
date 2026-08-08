export type JobStatusValue = "queued" | "running" | "completed" | "partial" | "failed";

export type JobStage =
  | "parsing"
  | "searching"
  | "crawling"
  | "extracting"
  | "validating"
  | "synthesizing"
  | "done"
  | null;

export interface SearchRequest {
  query: string;
  segment?: string;
  city?: string;
  state?: string;
  max_leads?: number;
  max_pages?: number;
}

export interface SearchResponse {
  job_id: string;
  status_url: string;
}

export interface JobStatus {
  id: string;
  status: JobStatusValue;
  stage: JobStage;
  progress: number;
  message: string | null;
  lead_count: number;
  error: string | null;
  query: string;
  created_at: string;
  updated_at: string;
}

export interface LeadSocial {
  instagram?: string;
  linkedin?: string;
  facebook?: string;
}

export type LeadStatus = "new" | "contacted" | "skipped";

export interface Lead {
  id: string;
  job_id: string;
  name: string;
  segment: string | null;
  city: string | null;
  state: string | null;
  website: string | null;
  emails: string[];
  phones: string[];
  whatsapp: string[];
  social: LeadSocial;
  confidence: number;
  source_url: string;
  notes: string | null;
  created_at: string;
  status: LeadStatus;
}

export interface LeadList {
  job_id: string;
  query: string;
  leads: Lead[];
  summary: string | null;
  generated_at: string;
  total: number;
  rejected: number;
}

export type OutreachChannel = "email" | "whatsapp";

export interface OutreachChoice {
  job_id: string;
  channel: OutreachChannel;
  lead_ids: string[];
  template?: string;
}

export interface OutreachRecipient {
  lead_id: string;
  name: string;
  contact: string;
  message: string;
}

export type OutreachPlanStatus = "draft" | "scheduled" | "sent";

export interface OutreachPlan {
  id: string;
  job_id: string;
  channel: OutreachChannel;
  recipients: OutreachRecipient[];
  message_template: string;
  status: OutreachPlanStatus;
  created_at: string;
}

export interface OutreachPlanResponse {
  plan: OutreachPlan;
}

export interface OutreachSendResult {
  plan_id: string;
  delivered: number;
  stub: boolean;
  message: string;
}
