const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const API = {
  upload: `${API_BASE_URL}/upload/media`,
  getTask: (id: number) => `${API_BASE_URL}/task/${id}/`,
  updateSpeakerName: (speakerId: number) => `${API_BASE_URL}/speakers/${speakerId}/name`,
  updateMessageSpeaker: (messageId: number) => `${API_BASE_URL}/messages/${messageId}/speaker`,
};


