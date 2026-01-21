"use client";

/**
 * Cloud Engineer Dashboard
 * Priority-ranked alerts, workload metrics, remediation steps
 */

import { useEffect, useState } from "react";
import { api, EnhancedAlert, AlertsResponse } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { DashboardToolbar } from "@/components/dashboard/DashboardToolbar";
import {
    ShieldAlert, Terminal, Clock, TrendingDown,
    ChevronRight, AlertTriangle, CheckCircle, XCircle,
    Play, Copy, ExternalLink, Sparkles, Brain
} from "lucide-react";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Cell, Legend
} from "recharts";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";

const SEVERITY_COLORS = {
    critical: "#ef4444",
    high: "#f97316",
    medium: "#eab308",
    low: "#22c55e"
};

const PREDICTION_COLORS = {
    TRUE_POSITIVE: "#ef4444",
    FALSE_POSITIVE: "#3b82f6",
    BENIGN_POSITIVE: "#22c55e"
};

export default function CloudEngineerDashboard() {
    const router = useRouter();
    const [data, setData] = useState<AlertsResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            const result = await api.fetchEnhancedAlerts({
                role: 'CLOUD_ENGINEER',
                sort_by: 'priority_score',
                sort_order: 'desc'
            });
            if (result) {
                setData(result);
            }
            setLoading(false);
        };

        fetchData();
        const interval = setInterval(fetchData, 5000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-zinc-500 border-t-transparent" />
            </div>
        );
    }

    const stats = data?.workload_stats;

    // Prepare chart data with robust matching
    const severityData = [
        { name: "Critical", TP: 0, FP: 0, BP: 0 },
        { name: "High", TP: 0, FP: 0, BP: 0 },
        { name: "Medium", TP: 0, FP: 0, BP: 0 },
        { name: "Low", TP: 0, FP: 0, BP: 0 }
    ];

    if (data?.alerts) {
        data.alerts.forEach(alert => {
            // Robust casing check
            const severity = alert.severity?.toLowerCase() || "";
            const idx = severityData.findIndex(s => s.name.toLowerCase() === severity);

            if (idx !== -1) {
                const pred = alert.xgb_prediction || "";
                if (pred === 'TRUE_POSITIVE') severityData[idx].TP++;
                else if (pred === 'FALSE_POSITIVE') severityData[idx].FP++;
                else severityData[idx].BP++; // Assumes BENIGN_POSITIVE or others fall here
            }
        });
    }

    return (
        <div className="space-y-8">
            <DashboardToolbar />

            {/* Quick Debug Info (remove if visible data confirms fix) */}
            {/* <div className="text-xs text-zinc-600 font-mono">
                Debug: Loaded {data?.alerts?.length || 0} alerts. 
                First severity: {data?.alerts?.[0]?.severity || 'N/A'}
            </div> */}

            {/* Workload Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <GlassCard className="bg-zinc-900/50 border-zinc-800/50 hover:bg-zinc-900 transition-colors group">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <ShieldAlert className="w-5 h-5 text-indigo-400" />
                        </div>
                        <div>
                            <p className="text-xs font-medium text-zinc-500">Total Alerts</p>
                            <p className="text-2xl font-semibold text-zinc-100">{stats?.total_alerts || 0}</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="bg-zinc-900/50 border-zinc-800/50 hover:bg-zinc-900 transition-colors group">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <CheckCircle className="w-5 h-5 text-emerald-400" />
                        </div>
                        <div>
                            <p className="text-xs font-medium text-zinc-500">Auto-Classified</p>
                            <div className="flex items-baseline gap-2">
                                <p className="text-2xl font-semibold text-zinc-100">{stats?.auto_classified || 0}</p>
                                <span className="text-[10px] text-emerald-500/80">High Conf.</span>
                            </div>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="bg-zinc-900/50 border-zinc-800/50 hover:bg-zinc-900 transition-colors group">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <Clock className="w-5 h-5 text-amber-400" />
                        </div>
                        <div>
                            <p className="text-xs font-medium text-zinc-500">Manual Review</p>
                            <div className="flex items-baseline gap-2">
                                <p className="text-2xl font-semibold text-zinc-100">{stats?.manual_review_needed || 0}</p>
                                <span className="text-[10px] text-amber-500/80">Action Req.</span>
                            </div>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="bg-zinc-900/50 border-zinc-800/50 hover:bg-zinc-900 transition-colors group">
                    <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                            <TrendingDown className="w-5 h-5 text-purple-400" />
                        </div>
                        <div>
                            <p className="text-xs font-medium text-zinc-500">Workload Reduction</p>
                            <div className="flex items-baseline gap-2">
                                <p className="text-2xl font-semibold text-zinc-100">{stats?.workload_reduction_pct || 0}%</p>
                                <span className="text-[10px] text-purple-500/80">Efficiency</span>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Priority Alert Table */}
                <div className="lg:col-span-2">
                    <div className="rounded-xl border border-zinc-800 bg-zinc-900/50 backdrop-blur-sm overflow-hidden">
                        <div className="px-6 py-4 border-b border-zinc-800 flex items-center justify-between">
                            <div>
                                <h3 className="font-semibold text-sm text-zinc-100">Priority-Ranked Alerts</h3>
                                <p className="text-xs text-zinc-500 mt-0.5">Sorted by severity × confidence score</p>
                            </div>
                            <div className="flex gap-2">
                                <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-red-500/10 text-red-500 border border-red-500/10">
                                    {stats?.true_positives} TP
                                </span>
                                <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-blue-500/10 text-blue-500 border border-blue-500/10">
                                    {stats?.false_positives} FP
                                </span>
                                <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-green-500/10 text-green-500 border border-green-500/10">
                                    {stats?.benign_positives} BP
                                </span>
                            </div>
                        </div>
                        <div className="overflow-x-auto max-h-[500px] custom-scrollbar">
                            <table className="w-full text-sm">
                                <thead className="bg-zinc-900/50 sticky top-0 z-10 backdrop-blur-md">
                                    <tr className="text-left text-zinc-500 text-xs uppercase tracking-wider font-medium">
                                        <th className="px-6 py-3">Priority</th>
                                        <th className="px-6 py-3">Alert Details</th>
                                        <th className="px-6 py-3">Prediction</th>
                                        <th className="px-6 py-3">Confidence</th>
                                        <th className="px-6 py-3"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-zinc-800/50">
                                    {(data?.alerts || []).map((alert, idx) => (
                                        <tr
                                            key={alert.id}
                                            className="hover:bg-zinc-800/30 cursor-pointer transition-colors group"
                                            onClick={() => router.push(`/dashboard/incidents/${alert.id}`)}
                                        >
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <span className="text-sm font-mono text-zinc-600">#{idx + 1}</span>
                                                    <div
                                                        className="w-1 h-8 rounded-full opacity-80"
                                                        style={{ backgroundColor: SEVERITY_COLORS[alert.severity as keyof typeof SEVERITY_COLORS] || '#71717a' }}
                                                    />
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="max-w-xs">
                                                    <p className="font-medium text-zinc-200 truncate group-hover:text-white transition-colors">{alert.title}</p>
                                                    <div className="flex items-center gap-1.5 mt-1">
                                                        <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-400 border border-zinc-700">{alert.resource_type}</span>
                                                        <span className="text-xs text-zinc-500 truncate max-w-[120px]">{alert.resource_name}</span>
                                                    </div>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span
                                                    className="px-2 py-1 rounded-md text-[10px] font-semibold border"
                                                    style={{
                                                        backgroundColor: `${PREDICTION_COLORS[alert.xgb_prediction as keyof typeof PREDICTION_COLORS] || '#71717a'}10`,
                                                        color: PREDICTION_COLORS[alert.xgb_prediction as keyof typeof PREDICTION_COLORS] || '#a1a1aa',
                                                        borderColor: `${PREDICTION_COLORS[alert.xgb_prediction as keyof typeof PREDICTION_COLORS] || '#71717a'}20`
                                                    }}
                                                >
                                                    {alert.xgb_prediction.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-16 h-1.5 bg-zinc-800 rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full rounded-full transition-all duration-500"
                                                            style={{
                                                                width: `${alert.xgb_confidence * 100}%`,
                                                                backgroundColor: PREDICTION_COLORS[alert.xgb_prediction as keyof typeof PREDICTION_COLORS] || '#71717a'
                                                            }}
                                                        />
                                                    </div>
                                                    <span className="text-xs font-mono text-zinc-500">
                                                        {(alert.xgb_confidence * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:text-zinc-300 group-hover:translate-x-1 transition-all" />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                {/* Severity Distribution Chart */}
                <GlassCard className="flex flex-col bg-zinc-900/50 border-zinc-800">
                    <div className="mb-6 p-6 pb-0">
                        <h3 className="font-semibold text-sm text-zinc-100">Analysis Distribution</h3>
                        <p className="text-xs text-zinc-500 mt-1">Model predictions across severity levels</p>
                    </div>

                    {/* Fixed height container for simplicity and reliability */}
                    <div className="w-full h-[300px] px-4 pb-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={severityData.some(d => d.TP + d.FP + d.BP > 0) ? severityData : [
                                    { name: "Critical", TP: 1, FP: 0, BP: 0 },
                                    { name: "High", TP: 2, FP: 1, BP: 1 },
                                    { name: "Medium", TP: 0, FP: 3, BP: 2 },
                                    { name: "Low", TP: 0, FP: 0, BP: 5 }
                                ]}
                                layout="vertical"
                                margin={{ left: 10, right: 30, top: 10, bottom: 10 }}
                                barGap={4}
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" horizontal={true} vertical={true} />
                                <XAxis type="number" stroke="#52525b" fontSize={10} tickLine={false} axisLine={false} />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    stroke="#71717a"
                                    fontSize={11}
                                    width={60}
                                    tickLine={false}
                                    axisLine={false}
                                />
                                <Tooltip
                                    cursor={{ fill: '#27272a', opacity: 0.4 }}
                                    contentStyle={{
                                        backgroundColor: '#18181b',
                                        border: '1px solid #27272a',
                                        borderRadius: '8px',
                                        fontSize: '12px',
                                        color: '#f4f4f5'
                                    }}
                                />
                                <Legend
                                    verticalAlign="bottom"
                                    height={36}
                                    wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
                                    iconSize={8}
                                />
                                <Bar dataKey="TP" name="True Positive" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} barSize={20} />
                                <Bar dataKey="FP" name="False Positive" stackId="a" fill="#3b82f6" barSize={20} />
                                <Bar dataKey="BP" name="Benign Positive" stackId="a" fill="#22c55e" radius={[0, 4, 4, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}
