"use client";

import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const data = [
    { time: "00:00", alerts: 12 },
    { time: "04:00", alerts: 8 },
    { time: "08:00", alerts: 24 },
    { time: "12:00", alerts: 45 },
    { time: "16:00", alerts: 32 },
    { time: "20:00", alerts: 18 },
    { time: "24:00", alerts: 10 },
];

export function AlertVolumeChart() {
    return (
        <div className="h-[300px] bg-white border border-gray-200 rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="font-semibold text-lg text-gray-900">Alert Volume</h3>
                    <p className="text-sm text-gray-500">Inbound signals over last 24h</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-blue-500"></span>
                    <span className="text-xs text-gray-500">Signals</span>
                </div>
            </div>

            <div className="h-[200px] w-full mt-4">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="colorAlerts" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis
                            dataKey="time"
                            stroke="#94a3b8"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis
                            stroke="#94a3b8"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                            tickFormatter={(value) => `${value}`}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                            itemStyle={{ color: '#1e293b' }}
                        />
                        <Area
                            type="monotone"
                            dataKey="alerts"
                            stroke="#3b82f6"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#colorAlerts)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </div>
    );
}
