import axios, { AxiosInstance, AxiosError } from 'axios';
import { UploadResponse, TaskResponse , LabelingTaskResponse} from '@/types/api';

const API_PORT = import.meta.env.VITE_API_PORT || '8080'
const protocol = window.location.protocol
const hostname = window.location.hostname
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || `${protocol}//${hostname}:${API_PORT}`

export class APIError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}


const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      throw new APIError(`HTTP error! status: ${error.response.status}`, error.response.status);
    } else if (error.request) {
      // The request was made but no response was received
      throw new APIError('No response received from the server');
    } else {
      // Something happened in setting up the request that triggered an Error
      throw new APIError('Error setting up the request');
    }
  }
);

export const API = {
  upload: async (file: File): Promise<UploadResponse> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiClient.post<UploadResponse>('/api/upload/media', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('An unexpected error occurred');
    }
  },

  getTask: async (id: number): Promise<TaskResponse> => {
    try {
      const response = await apiClient.get<TaskResponse>(`/api/task/${id}/`);
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('An unexpected error occurred');
    }
  },


  // LABELING 
  getLabelingTask: async (id: number): Promise<LabelingTaskResponse> => {
    try {
      const response = await apiClient.get<LabelingTaskResponse>(`/api/labeling/task/${id}`);
      return response.data;
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('An unexpected error occurred');
    }
  },

  getSegmentAudio: (task_id: number, segment_id: number) => `${API_BASE_URL}/api/labeling/task/${task_id}/segments/${segment_id}/audio`

};


