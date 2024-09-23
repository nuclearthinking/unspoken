

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


export interface UploadResponse {
    task_id: number;
    task_status: TaskStatus;
}


export enum LabelingTaskStatus {
    queued = 'queued',
    labeling = 'labeling',
    done = 'done'
}


export enum LabelingSegmentStatus {
    in_progress = 'in_progress',
    done = 'done'
}

export interface LabelingSpeakerResponse {
    id: number;
    name: string;
}

export interface LabelingSegmentResponse {
    id: number;
    start: number;
    end: number;
    text: string;
    speaker: LabelingSpeakerResponse;
    status: LabelingSegmentStatus;
}

export interface LabelingTaskResponse {
    id: number;
    transcript_id: number;
    file_name: string;
    status: LabelingTaskStatus;
    segments: LabelingSegmentResponse[];
    speakers: LabelingSpeakerResponse[];
}