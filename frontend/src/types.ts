export interface Attack {
   id: string;
   name: string;
   description: string;
   longDescription?: string;
   references?: string[];
}

export interface Defense {
   id: string;
   name: string;
   description: string;
   longDescription?: string;
   references?: string[];
}

export interface Model {
   id: string;
   name: string;
   description: string;
}

export interface Prompt {
   text: string;
   timestamp: string;
   attack: Attack;
   defense: Defense;
   model: Model;
   scriptOutput: string;
   isBlocked: boolean;
   attackSuccess: boolean;
   progress: number;
   gpuInfo?: string;
}

export interface ASRData {
   overall_asr?: number;
   by_attack?: Record<string, number>;
}

export interface DefenseBypassData {
   bypass_rate?: number;
   baseline_asr?: number;
   delta?: number;
}

export interface QueryBudgetData {
   median_queries?: number;
   median_tokens?: number;
   median_time?: number;
}

export interface RefusalData {
   refusal_rate?: number;
   safe_completion_rate?: number;
   over_refusal_rate?: number;
}

export interface ToolLeakageData {
   tool_misuse_rate?: number;
   data_leakage_rate?: number;
}

export interface AdditionalData {
   block_rate?: number;
}
