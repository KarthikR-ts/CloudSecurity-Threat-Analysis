import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
    noHover?: boolean;
    liquid?: boolean;
}

export function GlassCard({ children, className, noHover = false, liquid = true, ...props }: GlassCardProps) {
    return (
        <div
            className={cn(
                "glass-card group relative p-6 transition-all duration-500",
                liquid && "liquid-glass",
                !noHover && "hover:scale-[1.01] hover:border-white/30 hover:shadow-[0_0_40px_rgba(139,92,246,0.15)]",
                className
            )}
            {...props}
        >
            <div className="relative z-10">{children}</div>
        </div>
    );
}

