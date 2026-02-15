import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { ClipboardCopyIcon, CheckIcon, Trash2 } from "lucide-react";
import clipboardCopy from 'clipboard-copy';
import GithubIcon from '@/assets/github.svg';
import LogoSvg from './logo_svg';
import {
    AlertDialog,
    AlertDialogTitle,
    AlertDialogDescription,
    AlertDialogFooter,
} from '@/components/ui/alert-dialog';

const Logo = () => {
    return (
        <div className="flex items-center space-x-2">
            <Link to="/" className="flex items-center space-x-2">
                <LogoSvg className="h-6 w-6" />
                <span className="font-bold text-xl">UNSPOKEN</span>
            </Link>
            <a href="https://github.com/nuclearthinking/unspoken" target="_blank" rel="noopener noreferrer">
                <img src={GithubIcon} alt="GitHub" className="h-6 w-6" />
            </a>
        </div>
    )
}


const CopyTranscriptButton = ({ onCopyTranscript, disabled }: {
    onCopyTranscript: () => string,
    disabled: boolean,
}) => {
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState(false);

    const handleCopy = async () => {
        try {
            const transcript = onCopyTranscript();
            await clipboardCopy(transcript);
            setCopied(true);
        } catch (err) {
            console.error('Unable to copy to clipboard', err);
            setError(true);
        } finally {
            setTimeout(() => {
                setCopied(false);
                setError(false);
            }, 2000);
        }
    };

    return (
        <Button onClick={handleCopy} variant="outline" size="sm" disabled={disabled}>
            {copied ? (
                <>
                    <CheckIcon className="h-4 w-4 mr-2" />
                    Copied!
                </>
            ) : error ? (
                <>
                    <ClipboardCopyIcon className="h-4 w-4 mr-2" />
                    <span className="text-red-500">Copy failed!</span>
                </>
            ) : (
                <>
                    <ClipboardCopyIcon className="h-4 w-4 mr-2" />
                    Copy Transcript
                </>
            )}
        </Button>
    );
};

const DeleteTaskButton = ({ onDeleteTask, disabled }: {
    onDeleteTask: () => Promise<void>,
    disabled: boolean,
}) => {
    const [dialogOpen, setDialogOpen] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const [deleteError, setDeleteError] = useState(false);

    const handleConfirmDelete = async () => {
        setDeleting(true);
        setDeleteError(false);
        try {
            await onDeleteTask();
            setDialogOpen(false);
        } catch (err) {
            console.error('Failed to delete task', err);
            setDeleteError(true);
        } finally {
            setDeleting(false);
        }
    };

    return (
        <>
            <Button
                onClick={() => setDialogOpen(true)}
                variant="outline"
                size="sm"
                disabled={disabled}
                className="text-red-600 border-red-200 hover:bg-red-50 hover:text-red-700"
            >
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
            </Button>
            <AlertDialog open={dialogOpen} onOpenChange={setDialogOpen}>
                <AlertDialogTitle>Delete Task</AlertDialogTitle>
                <AlertDialogDescription>
                    This action is irreversible. The task and all associated data (transcript,
                    speakers, messages) will be permanently deleted.
                </AlertDialogDescription>
                {deleteError && (
                    <p className="text-sm text-red-500 mt-2">Failed to delete task. Please try again.</p>
                )}
                <AlertDialogFooter>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setDialogOpen(false)}
                        disabled={deleting}
                    >
                        Cancel
                    </Button>
                    <Button
                        variant="destructive"
                        size="sm"
                        onClick={handleConfirmDelete}
                        disabled={deleting}
                    >
                        {deleting ? 'Deleting...' : 'Delete'}
                    </Button>
                </AlertDialogFooter>
            </AlertDialog>
        </>
    );
};

interface HeaderProps {
    showCopyTranscript: boolean;
    onCopyTranscript: () => string;
    showDelete?: boolean;
    onDeleteTask?: () => Promise<void>;
    isLoading: boolean;
    error: boolean;
}

export const Header: React.FC<HeaderProps> = ({
    showCopyTranscript,
    onCopyTranscript,
    showDelete = false,
    onDeleteTask,
    isLoading,
    error,
}) => {
    return (
        <header className="sticky top-0 z-10 w-full border-b bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 min-w-[640px]">
                <div className="flex justify-between items-center h-16">
                    <div className="flex-1 flex justify-center sm:justify-start">
                        <Logo />
                    </div>
                    <div className="flex-1 flex justify-center sm:justify-end gap-2">
                        {showCopyTranscript && (
                            <CopyTranscriptButton
                                onCopyTranscript={onCopyTranscript}
                                disabled={isLoading || error}
                            />
                        )}
                        {showDelete && onDeleteTask && (
                            <DeleteTaskButton
                                onDeleteTask={onDeleteTask}
                                disabled={isLoading}
                            />
                        )}
                    </div>
                </div>
            </div>
        </header>
    )
}