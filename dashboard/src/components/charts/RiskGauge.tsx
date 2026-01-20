"use client";

/**
 * Risk Gauge Component
 * Animated SVG gauge showing 0-100 risk score with color zones
 */

import { useEffect, useState } from "react";

interface RiskGaugeProps {
    value: number; // 0-100
    size?: number;
    label?: string;
}

export function RiskGauge({ value, size = 200, label = "Risk Score" }: RiskGaugeProps) {
    const [animatedValue, setAnimatedValue] = useState(0);

    useEffect(() => {
        // Animate from current to target
        const duration = 1000;
        const startTime = Date.now();
        const startValue = animatedValue;

        const animate = () => {
            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Easing function
            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = startValue + (value - startValue) * easeOut;
            setAnimatedValue(current);

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }, [value]);

    const radius = (size - 20) / 2;
    const center = size / 2;
    const circumference = Math.PI * radius; // Half circle
    const strokeWidth = 16;

    // Calculate stroke offset based on value
    const offset = circumference - (animatedValue / 100) * circumference;

    // Determine color based on value
    const getColor = (v: number) => {
        if (v <= 33) return { color: "#22c55e", label: "Safe", bg: "rgba(34, 197, 94, 0.1)" };
        if (v <= 66) return { color: "#f59e0b", label: "Attention", bg: "rgba(245, 158, 11, 0.1)" };
        return { color: "#ef4444", label: "Critical", bg: "rgba(239, 68, 68, 0.1)" };
    };

    const status = getColor(animatedValue);

    // Needle angle (0 degrees = left, 180 degrees = right)
    const needleAngle = (animatedValue / 100) * 180 - 90; // -90 to 90

    return (
        <div className="flex flex-col items-center">
            <svg width={size} height={size / 2 + 40} viewBox={`0 0 ${size} ${size / 2 + 40}`}>
                {/* Background track */}
                <path
                    d={`M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`}
                    fill="none"
                    stroke="rgba(255, 255, 255, 0.1)"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                />

                {/* Active progress */}
                <path
                    d={`M ${center - radius} ${center} A ${radius} ${radius} 0 0 1 ${center + radius} ${center}`}
                    fill="none"
                    stroke={status.color}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    style={{
                        transition: "stroke 0.3s ease",
                        filter: `drop-shadow(0 0 8px ${status.color})`
                    }}
                />

                {/* Needle */}
                <g transform={`translate(${center}, ${center})`}>
                    <line
                        x1="0"
                        y1="0"
                        x2="0"
                        y2={-radius + 30}
                        stroke="white"
                        strokeWidth="3"
                        strokeLinecap="round"
                        transform={`rotate(${needleAngle})`}
                        style={{ filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.5))" }}
                    />
                    <circle r="8" fill="white" />
                    <circle r="4" fill={status.color} />
                </g>

                {/* Labels */}
                <text x={center - radius - 5} y={center + 20} fill="#9ca3af" fontSize="12" textAnchor="end">0</text>
                <text x={center} y={center - radius - 10} fill="#9ca3af" fontSize="12" textAnchor="middle">50</text>
                <text x={center + radius + 5} y={center + 20} fill="#9ca3af" fontSize="12" textAnchor="start">100</text>
            </svg>

            {/* Value display */}
            <div className="text-center -mt-6">
                <div
                    className="text-5xl font-bold transition-colors duration-300"
                    style={{ color: status.color }}
                >
                    {Math.round(animatedValue)}
                </div>
                <div
                    className="text-sm font-medium mt-1 px-3 py-1 rounded-full inline-block"
                    style={{
                        color: status.color,
                        backgroundColor: status.bg
                    }}
                >
                    {status.label}
                </div>
                <div className="text-xs text-gray-500 mt-2">{label}</div>
            </div>
        </div>
    );
}
