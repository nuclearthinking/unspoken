import React, { useState, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { ClipboardCopyIcon, CheckIcon } from "lucide-react"
import { useLoaderData, Link, LoaderFunctionArgs } from 'react-router-dom';
import { API } from '@/api';
import { TaskResponse, TaskStatus } from '@/types/api';
import { Skeleton } from "@/components/ui/skeleton"

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
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
}

const convertToDisplayMessages = (messages: TaskResponse['messages']): DisplayMessage[] => {
    return messages?.map(m => ({
        timestamp: m.start ? formatTime(m.start) : '',
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

const Logo = () => {
    return (
        <div className="flex items-center space-x-2">
            <Link to="/" className="flex items-center space-x-2">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="h-6 w-6"
                >
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                    <line x1="12" x2="12" y1="19" y2="22" />
                </svg>
                <span className="font-bold text-xl">UNSPOKEN</span>
            </Link>
            <a href="https://github.com/nuclearthinking/unspoken" target="_blank" rel="noopener noreferrer">
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="black"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="lucide lucide-github"
                >
                    <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
                    <path d="M9 18c-4.51 2-5-2-7-2" />
                </svg>
            </a>
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
            <header className="sticky top-0 z-10 w-full border-b bg-white">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8 min-w-[640px]">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex-1 flex justify-center sm:justify-start">
                            <Logo />
                        </div>
                        <div className="flex-1 flex justify-center sm:justify-end">
                            <Button onClick={exportTranscript} variant="outline" size="sm" disabled={isLoading}>
                                {copied ? (
                                    <>
                                        <CheckIcon className="h-4 w-4 mr-2" />
                                        Copied!
                                    </>
                                ) : (
                                    <>
                                        <ClipboardCopyIcon className="h-4 w-4 mr-2" />
                                        Copy Transcript
                                    </>
                                )}
                            </Button>
                        </div>
                    </div>
                </div>
            </header>
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
                            <div className="text-sm text-muted-foreground">
                                <span>Duration: {audioInfo.duration}</span>
                                <span className="mx-2">•</span>
                                <span>Date: {audioInfo.date}</span>
                            </div>
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