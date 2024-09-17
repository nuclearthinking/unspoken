

export enum TaskStatus {
    queued = 'queued',
    processing = 'processing',
    completed = 'completed',
    failed = 'failed',
}


export interface Message {
    start: number;
    end: number;
    text: string;
    speaker: string;
}

export interface TaskResponse {
    id: number;
    file_name: string;
    status: TaskStatus;
    speakers: string[];
    messages: Message[];
}