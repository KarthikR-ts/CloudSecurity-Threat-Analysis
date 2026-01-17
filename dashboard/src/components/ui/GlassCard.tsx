import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
    children: React.ReactNode;
    className?: string;
    noHover?: boolean;
}

export function GlassCard({ children, className, noHover = false, ...props }: GlassCardProps) {
    return (
        <div
            className={cn(
                "bg-white/5 border border-white/10 backdrop-blur-md rounded-2xl p-6 transition-all duration-300",
                !noHover && "hover:bg-white/10 hover:shadow-[0_0_20px_rgba(139,92,246,0.1)] hover:border-white/20",
                className
            )}
            {...props}
        >
            {children}
        </div>
    );
}
