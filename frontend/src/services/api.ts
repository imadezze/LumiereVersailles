import axios from 'axios';
import { ChatRequest, ChatResponse, ApiError } from '../types/chat';

// Use environment variable for API URL, fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const chatApi = {
  sendMessage: async (request: ChatRequest): Promise<ChatResponse> => {
    try {
      const response = await api.post<ChatResponse>('/api/chat', request);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = error.response?.data || { detail: 'Une erreur est survenue' };
      throw new Error(apiError.detail);
    }
  },

  checkHealth: async (): Promise<any> => {
    try {
      const response = await api.get('/health');
      return response.data;
    } catch (error) {
      throw new Error('Impossible de se connecter au serveur');
    }
  },

  clearConversation: async (conversationId: string): Promise<any> => {
    try {
      const response = await api.delete(`/conversation/${conversationId}`);
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = error.response?.data || { detail: 'Erreur lors du nettoyage de la conversation' };
      throw new Error(apiError.detail);
    }
  },

  transcribeAudio: async (audioBlob: Blob): Promise<{ transcript: string; status: string }> => {
    try {
      const formData = new FormData();

      // Determine file extension from blob mime type
      let extension = 'webm'; // default
      const mimeType = audioBlob.type;
      if (mimeType.includes('webm')) extension = 'webm';
      else if (mimeType.includes('mp4') || mimeType.includes('m4a')) extension = 'm4a';
      else if (mimeType.includes('ogg')) extension = 'ogg';
      else if (mimeType.includes('wav')) extension = 'wav';
      else if (mimeType.includes('mpeg') || mimeType.includes('mp3')) extension = 'mp3';

      formData.append('audio', audioBlob, `recording.${extension}`);

      const response = await axios.post<{ transcript: string; status: string }>(
        `${API_BASE_URL}/api/transcribe`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    } catch (error: any) {
      const apiError: ApiError = error.response?.data || { detail: 'Erreur lors de la transcription audio' };
      throw new Error(apiError.detail);
    }
  }
};

export default api;