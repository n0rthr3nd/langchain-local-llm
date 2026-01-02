export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: number;
}

export interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  model: string;
  createdAt: number;
  updatedAt: number;
}

export interface ChatRequest {
  messages: Message[];
  model: string;
  temperature?: number;
  max_tokens?: number;
  system_prompt?: string;
}

export interface ChatResponse {
  response: string;
  model: string;
}

export interface ModelInfo {
  name: string;
  size?: string;
  modified_at?: string;
}

export interface ChatSettings {
  model: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
}
