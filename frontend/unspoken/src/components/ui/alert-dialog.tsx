import React, { useEffect } from 'react';
import { cn } from '@/lib/utils';

interface AlertDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    children: React.ReactNode;
}

export function AlertDialog({ open, onOpenChange, children }: AlertDialogProps) {
    useEffect(() => {
        const handleEscape = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onOpenChange(false);
        };
        if (open) {
            document.addEventListener('keydown', handleEscape);
            document.body.style.overflow = 'hidden';
        }
        return () => {
            document.removeEventListener('keydown', handleEscape);
            document.body.style.overflow = '';
        };
    }, [open, onOpenChange]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            <div
                className="fixed inset-0 bg-black/50 animate-in fade-in-0"
                onClick={() => onOpenChange(false)}
            />
            <div className="relative z-50 w-full max-w-md bg-white rounded-lg shadow-lg p-6 animate-in fade-in-0 zoom-in-95">
                {children}
            </div>
        </div>
    );
}

export function AlertDialogTitle({ children, className }: { children: React.ReactNode; className?: string }) {
    return <h2 className={cn('text-lg font-semibold', className)}>{children}</h2>;
}

export function AlertDialogDescription({ children, className }: { children: React.ReactNode; className?: string }) {
    return <p className={cn('text-sm text-muted-foreground mt-2', className)}>{children}</p>;
}

export function AlertDialogFooter({ children, className }: { children: React.ReactNode; className?: string }) {
    return <div className={cn('flex justify-end gap-2 mt-6', className)}>{children}</div>;
}
