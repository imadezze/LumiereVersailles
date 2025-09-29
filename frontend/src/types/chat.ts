export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  isError?: boolean;
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  reponse: string;
  conversation_id?: string;
  status: string;
}

export interface ApiError {
  detail: string;
}