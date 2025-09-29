export interface ToolUsage {
  name: string;
  args: Record<string, any>;
  execution_time_ms?: number;
}

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isError?: boolean;
  toolsUsed?: ToolUsage[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  reponse: string;
  conversation_id?: string;
  status: string;
  tools_used?: ToolUsage[];
}

export interface ApiError {
  detail: string;
}