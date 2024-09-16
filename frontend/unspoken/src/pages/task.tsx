import React, { useState, useEffect } from 'react'
import { useLoaderData, LoaderFunctionArgs } from 'react-router-dom';
import { API } from '@/api';
import { TaskResponse, TaskStatus } from '@/types/api';
import { Skeleton } from "@/components/ui/skeleton"
import { Header } from '@/components/header';


interface AudioInfo {
    title: string
    duration: string
    date: string
}

interface DisplayMessage {
    timestamp: string;
    speaker: string;
    text: string;
}

const formatTime = (seconds: number): string => {
    if (isNaN(seconds)) {
        return "00:00:00";
    }
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

const convertToDisplayMessages = (messages: TaskResponse['messages']): DisplayMessage[] => {
    return messages?.map(m => ({
        timestamp: formatTime(m.start || 0),
        speaker: m.speaker || '',
        text: m.text || ''
    })) || [];
}

const MessageRow = ({ message }: { message: DisplayMessage }) => {
    return (
        <div className="mb-4 text-left">
            <div className="flex items-center mb-1">
                <span className="text-sm font-medium text-muted-foreground mr-2">{message.timestamp}</span>
                <span className="text-sm font-semibold">{message.speaker}</span>
            </div>
            <p className="text-sm">{message.text}</p>
        </div>
    )
}


export async function loader({ params }: LoaderFunctionArgs): Promise<TaskResponse> {
    const taskId = params.taskId;
    if (!taskId || isNaN(parseInt(taskId))) {
        throw new Error('Invalid taskId');
    }
    const response = await fetch(API.getTask(parseInt(taskId)));
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

export default function Task() {
    const data = useLoaderData() as TaskResponse;
    const [taskData, setTaskData] = useState<TaskResponse>(data);
    const [isLoading, setIsLoading] = useState(taskData.status === TaskStatus.queued || taskData.status === TaskStatus.transcribing);
    const [messages, setMessages] = useState<DisplayMessage[]>(convertToDisplayMessages(taskData.messages));


    const [audioInfo] = useState<AudioInfo>({
        title: data.file_name || "Team Meeting - Q2 Planning",
        duration: "45:32",
        date: "2023-06-15"
    })


    useEffect(() => {
        let intervalId: NodeJS.Timeout;

        const checkTaskStatus = async () => {
            try {
                const response = await fetch(API.getTask(taskData.id));
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const updatedData: TaskResponse = await response.json();
                setTaskData(updatedData);

                if (updatedData.status === TaskStatus.completed) {
                    setIsLoading(false);
                    setMessages(convertToDisplayMessages(updatedData.messages));
                    clearInterval(intervalId);
                }
            } catch (error) {
                console.error("Error checking task status:", error);
            }
        };

        if (isLoading) {
            intervalId = setInterval(checkTaskStatus, 5000); // Check every 5 seconds
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [isLoading, taskData.id]);



    const [copied, setCopied] = useState(false)

    const exportTranscript = () => {
        const transcript = messages.map(m => `[${m.timestamp}] ${m.speaker}: ${m.text}`).join('\n')
        navigator.clipboard.writeText(transcript).then(() => {
            setCopied(true)
            setTimeout(() => setCopied(false), 2000)
        })
    }

    return (
        <div className="flex flex-col min-h-screen bg-background">
            <Header
                showCopyTranscript={!isLoading}
                onCopyTranscript={exportTranscript}
                copied={copied}
                isLoading={isLoading}
            />
            <main className="flex-1 py-6 px-4 sm:px-6 lg:px-8 min-w-[640px]">
                {isLoading ? (
                    <div className="max-w-4xl mx-auto space-y-4">
                        <p className="text-center text-lg font-medium">Transcribing audio...</p>
                        <div className="flex justify-center">
                            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
                        </div>
                        <div className="space-y-2">
                            {[1, 2, 3].map((_, index) => (
                                <div key={index} className="space-y-2">
                                    <Skeleton className="h-4 w-1/4" />
                                    <Skeleton className="h-4 w-full" />
                                    <Skeleton className="h-4 w-5/6" />
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="max-w-4xl mx-auto">
                        <div className="bg-card rounded-lg shadow-sm mb-6 p-4">
                            <h1 className="text-2xl font-bold mb-2">{audioInfo.title}</h1>
                            {/* <div className="text-sm text-muted-foreground">
                                <span>Duration: {audioInfo.duration}</span>
                                <span className="mx-2">•</span>
                                <span>Date: {audioInfo.date}</span>
                            </div> */}
                        </div>
                        <div className="border rounded-md p-4">
                            {messages.map((message, index) => (
                                <React.Fragment key={index}>
                                    <MessageRow message={message} />
                                    {index < messages.length - 1 && <hr className="my-4" />}
                                </React.Fragment>
                            ))}
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}