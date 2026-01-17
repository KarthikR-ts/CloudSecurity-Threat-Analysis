import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface NeonButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "danger" | "ghost";
    isLoading?: boolean;
    icon?: React.ReactNode;
}

export function NeonButton({
    children,
    className,
    variant = "primary",
    isLoading,
    icon,
    ...props
}: NeonButtonProps) {
    const variants = {
        primary: "bg-brand-primary/20 text-brand-primary border-brand-primary/50 hover:bg-brand-primary/30 hover:shadow-[0_0_15px_rgba(139,92,246,0.4)]",
        secondary: "bg-brand-secondary/20 text-brand-secondary border-brand-secondary/50 hover:bg-brand-secondary/30 hover:shadow-[0_0_15px_rgba(16,185,129,0.4)]",
        danger: "bg-brand-accent/20 text-brand-accent border-brand-accent/50 hover:bg-brand-accent/30 hover:shadow-[0_0_15px_rgba(239,68,68,0.4)]",
        ghost: "bg-transparent text-muted hover:text-white hover:bg-white/5 border-transparent",
    };

    return (
        <button
            className={cn(
                "relative flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium border transition-all duration-300 active:scale-95 disabled:opacity-50 disabled:pointer-events-none",
                variants[variant],
                className
            )}
            disabled={isLoading}
            {...props}
        >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : icon}
            {children}
        </button>
    );
}
