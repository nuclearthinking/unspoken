const API_PORT = import.meta.env.VITE_API_PORT || '8080'
const protocol = window.location.protocol
const hostname = window.location.hostname



const API_BASE_URL = `${protocol}//${hostname}:${API_PORT}`
export const API = {
  upload: `${API_BASE_URL}/api/upload/media`,
  getTask: (id: number) => `${API_BASE_URL}/api/task/${id}/`,
  updateSpeakerName: (speakerId: number) => `${API_BASE_URL}/api/speakers/${speakerId}/name`,
  updateMessageSpeaker: (messageId: number) => `${API_BASE_URL}/api/messages/${messageId}/speaker`,
};


