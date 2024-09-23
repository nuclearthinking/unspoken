import { useState, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { AlertCircle, CheckCircle, Edit2, Play, User } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Label } from "@/components/ui/label"
import { useLoaderData, LoaderFunctionArgs } from 'react-router-dom';
import { API } from '@/api'
import { LabelingTaskResponse, LabelingSegmentResponse, LabelingSegmentStatus } from '@/types/api'


const speakerOptions = ["John", "Sarah", "Michael", "Emma", "Unknown"]

export async function loader({ params }: LoaderFunctionArgs): Promise<LabelingTaskResponse> {
    const taskId = params.taskId;
    if (!taskId || isNaN(parseInt(taskId))) {
        throw new Error('Invalid taskId');
    }
    return await API.getLabelingTask(parseInt(taskId))
}

const LabelingItem = ({ segment, editingSegment, taskId, handlePlayPause, handleTextChange, handleSpeakerChange, handleConfirm }: {
    segment: LabelingSegmentResponse,
    editingSegment: number | null,
    taskId : number, 
    handlePlayPause: (segmentId: number) => void,
    handleTextChange: (segmentId: number, newText: string) => void,
    handleSpeakerChange: (segmentId: number, newSpeaker: string) => void,
    handleConfirm: (segmentId: number) => void
}) => {
    const audioRef = useRef<HTMLAudioElement | null>(null)

    return (
        <div
            key={segment.id}
            className={`p-4 border-b last:border-b-0 ${segment.status === 'in_progress' ? 'bg-muted' : ''
                }`}
        >
            <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">
                    Segment {segment.id} ({segment.start.toFixed(2)}s - {segment.end.toFixed(2)}s)
                </span>
                <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                    segment.status === LabelingSegmentStatus.done ? 'bg-green-100 text-green-800' :
                    'bg-blue-100 text-blue-800'
                    }`}>
                    {segment.status.replace('_', ' ')}
                </span>
            </div>
            <div className="flex items-center space-x-2 mb-2">
                <Button
                    onClick={() => handlePlayPause(segment.id)}
                    variant="outline"
                    size="sm"
                >
                    <Play className="h-4 w-4" />
                </Button>
                <audio
                    ref={audioRef}
                    src={API.getSegmentAudio(taskId, segment.id)}
                />
                <div className="flex-grow h-8 bg-muted rounded-md"></div>
            </div>
            <div className="space-y-2">
                <div className="flex items-center justify-between group">
                    <Label htmlFor={`text-${segment.id}`} className="flex items-center text-sm font-medium text-muted-foreground">
                        <User className="h-4 w-4 mr-2" />
                        {editingSegment === segment.id ? (
                            <Select
                                value={segment.speaker.name}
                                onValueChange={(value) => handleSpeakerChange(segment.id, value)}
                            >
                                <SelectTrigger className="w-[180px]">
                                    <SelectValue placeholder="Select speaker" />
                                </SelectTrigger>
                                <SelectContent>
                                    {speakerOptions.map((speaker) => (
                                        <SelectItem key={speaker} value={speaker}>
                                            {speaker}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        ) : (
                            <span>{segment.speaker.name}</span>
                        )}
                    </Label>
                    <Button
                        onClick={() => handleConfirm(segment.id)}
                        variant="ghost"
                        size="sm"
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                    >
                        <Edit2 className="h-4 w-4" />
                    </Button>
                </div>
                <div className="space-y-2">
                    {editingSegment === segment.id ? (
                        <Input
                            id={`text-${segment.id}`}
                            value={segment.text}
                            onChange={(e) => handleTextChange(segment.id, e.target.value)}
                            className="w-full"
                        />
                    ) : (
                        <p id={`text-${segment.id}`} className="text-sm">{segment.text}</p>
                    )}
                </div>
            </div>
            {editingSegment === segment.id && (
                <div className="mt-2 flex justify-end">
                    <Button
                        onClick={() => handleConfirm(segment.id)}
                        size="sm"
                        className="w-24"
                    >
                        Confirm
                        <CheckCircle className="h-4 w-4 ml-2" />
                    </Button>
                </div>
            )}
        </div>
    )
}

export default function LabelingList() {
    const labelingTask = useLoaderData() as LabelingTaskResponse;
    const [segments, setSegments] = useState<LabelingSegmentResponse[]>(labelingTask.segments);
    const [error, setError] = useState<string | null>(null);
    const [editingSegment, setEditingSegment] = useState<number | null>(null);


    const handlePlayPause = (segmentId: number) => {
        return segmentId
        // const audio = audioRefs.current[segmentId]
        // if (audio) {
        //     if (audio.paused) {
        //         audio.play()
        //     } else {
        //         audio.pause()
        //     }
        // }
    }

    const handleTextChange = (segmentId: number, newText: string) => {
        setSegments(segments.map(seg =>
            seg.id === segmentId ? { ...seg, text: newText } : seg
        ))
    }

    const handleSpeakerChange = (segmentId: number, newSpeaker: string) => {
        console.log('Mock handleSpeakerChange called with segmentId:', segmentId, 'and newSpeaker:', newSpeaker);
    }

    const handleConfirm = async (segmentId: number) => {
        try {
            // Mock function for now
            await new Promise(resolve => setTimeout(resolve, 1000));
            setSegments(segments.map(seg =>
                seg.id === segmentId ? { ...seg, status: LabelingSegmentStatus.done } : seg
            ));
            setEditingSegment(null);
        } catch (err) {
            setError("Failed to update segment. Please try again.");
        }
    }

    if (error) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-background">
                <Alert variant="destructive" className="max-w-md">
                    <AlertCircle className="h-4 w-4" />
                    <AlertTitle>Error</AlertTitle>
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            </div>
        )
    }

    return (
        <div className="flex flex-col min-h-screen bg-background">
            <header className="sticky top-0 z-10 w-full border-b bg-background">
                <div className="container mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex-1 flex justify-center sm:justify-start">
                            <div className="flex items-center space-x-2">
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
                            </div>
                        </div>
                        <div className="flex-1 flex justify-center sm:justify-end">
                            <span className="text-sm text-muted-foreground">
                                Audio Labeling
                            </span>
                        </div>
                    </div>
                </div>
            </header>
            <main className="flex-1 py-6 px-4 sm:px-6 lg:px-8 min-w-[640px]">
                <div className="max-w-4xl mx-auto">
                    <ScrollArea className="h-[calc(100vh-8rem)] rounded-md border">
                        {segments.map((segment) => (
                            <LabelingItem
                                key={segment.id}
                                segment={segment}
                                taskId={labelingTask.id}
                                editingSegment={editingSegment}
                                handlePlayPause={handlePlayPause}
                                handleTextChange={handleTextChange}
                                handleSpeakerChange={handleSpeakerChange}
                                handleConfirm={handleConfirm}
                            />
                        ))}
                    </ScrollArea>
                </div>
            </main>
        </div>
    )
}