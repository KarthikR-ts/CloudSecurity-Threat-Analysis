import { cn } from "@/lib/utils";
import { ArrowUpRight, ArrowDownRight, Minus } from "lucide-react";

interface MetricCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: {
        value: string;
        direction: "up" | "down" | "neutral";
    };
    className?: string;
    glowColor?: "primary" | "secondary" | "accent";
}

export function MetricCard({ title, value, icon, trend, className, glowColor }: MetricCardProps) {
    const trendColors = {
        up: "text-brand-accent",
        down: "text-brand-secondary",
        neutral: "text-muted-foreground",
    };

    const TrendIcon = trend?.direction === "up" ? ArrowUpRight : trend?.direction === "down" ? ArrowDownRight : Minus;

    return (
        <div className={cn("relative overflow-hidden bg-white border border-slate-200 rounded-xl shadow-sm hover:shadow-md transition-shadow duration-200 p-5", className)}>
            <div className="flex items-start justify-between mb-4">
                <div className="p-2.5 rounded-lg bg-indigo-50 text-indigo-600">
                    {icon}
                </div>
                {trend && (
                    <div className={cn("flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full border",
                        trend.direction === "up" ? "text-emerald-700 bg-emerald-50 border-emerald-100" :
                            trend.direction === "down" ? "text-rose-700 bg-rose-50 border-rose-100" : "text-slate-600 bg-slate-100 border-slate-200"
                    )}>
                        <TrendIcon className="w-3 h-3" />
                        {trend.value}
                    </div>
                )}
            </div>

            <div className="space-y-1">
                <h3 className="text-2xl font-bold tracking-tight text-gray-900">{value}</h3>
                <p className="text-sm text-gray-500 font-medium">{title}</p>
            </div>
        </div>
    );
}
