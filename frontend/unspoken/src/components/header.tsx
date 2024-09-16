import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from "@/components/ui/button";
import { ClipboardCopyIcon, CheckIcon } from "lucide-react";
import GithubIcon from '@/assets/github.svg';
import LogoSvg from './logo_svg';

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

const CopyTranscriptButton = ({ onCopyTranscript, copied, isLoading }: {
    onCopyTranscript: () => void,
    copied: boolean,
    isLoading: boolean
}) => {
    return (
        <Button onClick={onCopyTranscript} variant="outline" size="sm" disabled={isLoading}>
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
    )
}

interface HeaderProps {
    showCopyTranscript: boolean;
    onCopyTranscript: () => void;
    copied: boolean;
    isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({ showCopyTranscript, onCopyTranscript, copied, isLoading }) => {
    return (
        <header className="sticky top-0 z-10 w-full border-b bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8 min-w-[640px]">
                <div className="flex justify-between items-center h-16">
                    <div className="flex-1 flex justify-center sm:justify-start">
                        <Logo />
                    </div>
                    {showCopyTranscript && (
                        <div className="flex-1 flex justify-center sm:justify-end">
                            <CopyTranscriptButton 
                                onCopyTranscript={onCopyTranscript}
                                copied={copied}
                                isLoading={isLoading}
                            />
                        </div>
                    )}
                </div>
            </div>
        </header>
    )
}