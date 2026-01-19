"use client";

/**
 * SHAP Waterfall Chart Component
 * Visualizes feature contributions to model predictions
 */

import { useMemo } from "react";

interface ShapValue {
    feature: string;
    value: number;
    featureValue?: any;
}

interface ShapWaterfallProps {
    baseValue: number;
    shapValues: ShapValue[];
    prediction: string;
    maxFeatures?: number;
}

export function ShapWaterfall({
    baseValue,
    shapValues,
    prediction,
    maxFeatures = 10
}: ShapWaterfallProps) {
    const processedData = useMemo(() => {
        // Sort by absolute value and take top N
        const sorted = [...shapValues]
            .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
            .slice(0, maxFeatures);

        // Calculate cumulative values
        let cumulative = baseValue;
        const bars = sorted.map((item) => {
            const start = cumulative;
            cumulative += item.value;
            return {
                ...item,
                start,
                end: cumulative,
                isPositive: item.value >= 0
            };
        });

        return { bars, finalValue: cumulative };
    }, [baseValue, shapValues, maxFeatures]);

    const { bars, finalValue } = processedData;

    // Calculate scale
    const allValues = [baseValue, finalValue, ...bars.flatMap(b => [b.start, b.end])];
    const minVal = Math.min(...allValues);
    const maxVal = Math.max(...allValues);
    const range = maxVal - minVal || 1;

    const chartWidth = 400;
    const chartHeight = bars.length * 40 + 80;
    const barHeight = 28;
    const leftMargin = 160;
    const rightMargin = 60;
    const barAreaWidth = chartWidth - leftMargin - rightMargin;

    const scale = (val: number) => ((val - minVal) / range) * barAreaWidth + leftMargin;
    const baseX = scale(baseValue);

    return (
        <div className="w-full">
            <div className="mb-4 flex items-center justify-between">
                <h4 className="text-sm font-medium text-gray-400">SHAP Feature Contributions</h4>
                <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-red-500" />
                        <span className="text-gray-400">Increases prediction</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded bg-blue-500" />
                        <span className="text-gray-400">Decreases prediction</span>
                    </div>
                </div>
            </div>

            <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`}>
                {/* Base value line */}
                <line
                    x1={baseX}
                    y1={20}
                    x2={baseX}
                    y2={chartHeight - 40}
                    stroke="rgba(255,255,255,0.2)"
                    strokeWidth="1"
                    strokeDasharray="4,4"
                />

                {/* Base value label */}
                <text
                    x={baseX}
                    y={15}
                    fill="#9ca3af"
                    fontSize="10"
                    textAnchor="middle"
                >
                    Base: {baseValue.toFixed(2)}
                </text>

                {/* Feature bars */}
                {bars.map((bar, idx) => {
                    const y = 30 + idx * 40;
                    const x1 = scale(bar.start);
                    const x2 = scale(bar.end);
                    const barWidth = Math.abs(x2 - x1);
                    const barX = Math.min(x1, x2);

                    return (
                        <g key={bar.feature}>
                            {/* Connector line */}
                            {idx > 0 && (
                                <line
                                    x1={scale(bars[idx - 1].end)}
                                    y1={y - 12}
                                    x2={scale(bars[idx - 1].end)}
                                    y2={y + barHeight / 2}
                                    stroke="rgba(255,255,255,0.1)"
                                    strokeWidth="1"
                                />
                            )}

                            {/* Feature label */}
                            <text
                                x={leftMargin - 10}
                                y={y + barHeight / 2 + 4}
                                fill="#e5e7eb"
                                fontSize="11"
                                textAnchor="end"
                                className="font-mono"
                            >
                                {bar.feature.length > 18 ? bar.feature.slice(0, 18) + '...' : bar.feature}
                            </text>

                            {/* Bar */}
                            <rect
                                x={barX}
                                y={y}
                                width={Math.max(barWidth, 2)}
                                height={barHeight}
                                rx={4}
                                fill={bar.isPositive ? "#ef4444" : "#3b82f6"}
                                opacity={0.8}
                            />

                            {/* Value label */}
                            <text
                                x={scale(bar.end) + (bar.isPositive ? 5 : -5)}
                                y={y + barHeight / 2 + 4}
                                fill={bar.isPositive ? "#fca5a5" : "#93c5fd"}
                                fontSize="10"
                                textAnchor={bar.isPositive ? "start" : "end"}
                                fontWeight="bold"
                            >
                                {bar.value > 0 ? "+" : ""}{bar.value.toFixed(3)}
                            </text>
                        </g>
                    );
                })}

                {/* Final prediction */}
                <g transform={`translate(0, ${chartHeight - 35})`}>
                    <rect
                        x={leftMargin}
                        y={0}
                        width={barAreaWidth}
                        height={30}
                        rx={6}
                        fill="rgba(255,255,255,0.05)"
                    />
                    <text
                        x={leftMargin + 10}
                        y={20}
                        fill="#e5e7eb"
                        fontSize="12"
                        fontWeight="bold"
                    >
                        Prediction: {prediction}
                    </text>
                    <text
                        x={chartWidth - rightMargin - 10}
                        y={20}
                        fill="#22c55e"
                        fontSize="12"
                        fontWeight="bold"
                        textAnchor="end"
                    >
                        f(x) = {finalValue.toFixed(3)}
                    </text>
                </g>
            </svg>
        </div>
    );
}
