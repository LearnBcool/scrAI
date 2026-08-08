import { apiRequest } from "./client";
import type {
  JobStatus,
  Lead,
  LeadList,
  OutreachChoice,
  OutreachPlan,
  OutreachPlanResponse,
  OutreachSendResult,
  SearchRequest,
  SearchResponse,
} from "../types/api";

export interface LeadQueryParams {
  job_id?: string;
  segment?: string;
  city?: string;
  q?: string;
}

export function startSearch(request: SearchRequest): Promise<SearchResponse> {
  return apiRequest<SearchResponse>("/search", { method: "POST", body: request });
}

export function getJob(jobId: string): Promise<JobStatus> {
  return apiRequest<JobStatus>(`/jobs/${encodeURIComponent(jobId)}`);
}

export function listJobs(limit = 20): Promise<JobStatus[]> {
  return apiRequest<JobStatus[]>("/jobs", { params: { limit } });
}

export function listLeads(params: LeadQueryParams = {}): Promise<LeadList> {
  const query: Record<string, string | number | undefined> = {
    job_id: params.job_id,
    segment: params.segment,
    city: params.city,
    q: params.q,
  };
  return apiRequest<LeadList>("/leads", { params: query });
}

export function getLead(leadId: string): Promise<Lead> {
  return apiRequest<Lead>(`/leads/${encodeURIComponent(leadId)}`);
}

export function chooseOutreach(body: OutreachChoice): Promise<OutreachPlanResponse> {
  return apiRequest<OutreachPlanResponse>("/outreach/choose", { method: "POST", body });
}

export function sendOutreach(body: { plan_id: string }): Promise<OutreachSendResult> {
  return apiRequest<OutreachSendResult>("/outreach/send", { method: "POST", body });
}

export function getPlan(planId: string): Promise<OutreachPlan> {
  return apiRequest<OutreachPlan>(`/outreach/plans/${encodeURIComponent(planId)}`);
}
