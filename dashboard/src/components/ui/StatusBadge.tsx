import { cn } from "@/lib/utils";

interface StatusBadgeProps {
    status: "success" | "warning" | "danger" | "neutral";
    text: string;
    className?: string;
    pulse?: boolean;
}

export function StatusBadge({ status, text, className, pulse = false }: StatusBadgeProps) {
    const styles = {
        success: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
        warning: "bg-amber-500/10 text-amber-400 border-amber-500/20",
        danger: "bg-red-500/10 text-red-400 border-red-500/20",
        neutral: "bg-gray-500/10 text-gray-400 border-gray-500/20",
    };

    const dotColors = {
        success: "bg-emerald-400",
        warning: "bg-amber-400",
        danger: "bg-red-400",
        neutral: "bg-gray-400",
    };

    return (
        <span
            className={cn(
                "inline-flex items-center gap-2 px-2.5 py-1 rounded-full text-xs font-medium border backdrop-blur-sm",
                styles[status],
                className
            )}
        >
            {pulse && (
                <span className="relative flex h-2 w-2">
                    <span className={cn("animate-ping absolute inline-flex h-full w-full rounded-full opacity-75", dotColors[status])}></span>
                    <span className={cn("relative inline-flex rounded-full h-2 w-2", dotColors[status])}></span>
                </span>
            )}
            {text}
        </span>
    );
}
