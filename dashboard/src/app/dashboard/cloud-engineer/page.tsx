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
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
            </div>
        );
    }

    const stats = data?.workload_stats;

    // Prepare chart data
    const severityData = [
        { name: "Critical", TP: 0, FP: 0, BP: 0 },
        { name: "High", TP: 0, FP: 0, BP: 0 },
        { name: "Medium", TP: 0, FP: 0, BP: 0 },
        { name: "Low", TP: 0, FP: 0, BP: 0 }
    ];

    data?.alerts.forEach(alert => {
        const idx = severityData.findIndex(s => s.name.toLowerCase() === alert.severity);
        if (idx !== -1) {
            if (alert.xgb_prediction === 'TRUE_POSITIVE') severityData[idx].TP++;
            else if (alert.xgb_prediction === 'FALSE_POSITIVE') severityData[idx].FP++;
            else severityData[idx].BP++;
        }
    });

    return (
        <div className="space-y-6">
            <DashboardToolbar />

            {/* Workload Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <GlassCard className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/20">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                            <ShieldAlert className="w-6 h-6 text-blue-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Total Alerts</p>
                            <p className="text-2xl font-bold text-white">{stats?.total_alerts || 0}</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                            <CheckCircle className="w-6 h-6 text-green-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Auto-Classified</p>
                            <p className="text-2xl font-bold text-white">{stats?.auto_classified || 0}</p>
                            <p className="text-xs text-green-400">High confidence</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                            <Clock className="w-6 h-6 text-amber-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Manual Review</p>
                            <p className="text-2xl font-bold text-white">{stats?.manual_review_needed || 0}</p>
                            <p className="text-xs text-amber-400">Needs attention</p>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                            <TrendingDown className="w-6 h-6 text-purple-400" />
                        </div>
                        <div>
                            <p className="text-sm text-gray-400">Workload Reduction</p>
                            <p className="text-2xl font-bold text-white">{stats?.workload_reduction_pct || 0}%</p>
                            <p className="text-xs text-purple-400">vs manual triage</p>
                        </div>
                    </div>
                </GlassCard>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Priority Alert Table */}
                <div className="lg:col-span-2">
                    <GlassCard className="p-0 overflow-hidden">
                        <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
                            <div>
                                <h3 className="font-semibold text-lg text-white">Priority-Ranked Alerts</h3>
                                <p className="text-xs text-gray-400">Sorted by severity × confidence</p>
                            </div>
                            <div className="flex gap-2">
                                <span className="px-2 py-1 rounded text-xs bg-red-500/20 text-red-400">
                                    {stats?.true_positives} TP
                                </span>
                                <span className="px-2 py-1 rounded text-xs bg-blue-500/20 text-blue-400">
                                    {stats?.false_positives} FP
                                </span>
                                <span className="px-2 py-1 rounded text-xs bg-green-500/20 text-green-400">
                                    {stats?.benign_positives} BP
                                </span>
                            </div>
                        </div>
                        <div className="overflow-x-auto max-h-96">
                            <table className="w-full text-sm">
                                <thead className="bg-white/5 sticky top-0">
                                    <tr className="text-left text-gray-400">
                                        <th className="px-4 py-3">Priority</th>
                                        <th className="px-4 py-3">Alert</th>
                                        <th className="px-4 py-3">Prediction</th>
                                        <th className="px-4 py-3">Confidence</th>
                                        <th className="px-4 py-3"></th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-white/5">
                                    {data?.alerts.map((alert, idx) => (
                                        <tr
                                            key={alert.id}
                                            className="hover:bg-white/5 cursor-pointer transition-colors group"
                                            onClick={() => router.push(`/dashboard/incidents/${alert.id}`)}
                                        >
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <span className="text-lg font-bold text-gray-300">#{idx + 1}</span>
                                                    <div
                                                        className="w-2 h-8 rounded-full"
                                                        style={{ backgroundColor: SEVERITY_COLORS[alert.severity] }}
                                                    />
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="max-w-xs">
                                                    <p className="font-medium text-white truncate group-hover:text-blue-400 transition-colors">{alert.title}</p>
                                                    <p className="text-xs text-gray-500">{alert.resource_type} • {alert.resource_name}</p>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span
                                                    className="px-2 py-1 rounded text-xs font-medium"
                                                    style={{
                                                        backgroundColor: `${PREDICTION_COLORS[alert.xgb_prediction]}20`,
                                                        color: PREDICTION_COLORS[alert.xgb_prediction]
                                                    }}
                                                >
                                                    {alert.xgb_prediction.replace('_', ' ')}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                                                        <div
                                                            className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full"
                                                            style={{ width: `${alert.xgb_confidence * 100}%` }}
                                                        />
                                                    </div>
                                                    <span className="text-xs text-gray-400">
                                                        {(alert.xgb_confidence * 100).toFixed(0)}%
                                                    </span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <ChevronRight className="w-4 h-4 text-gray-500 group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </GlassCard>
                </div>

                {/* Severity Distribution Chart */}
                <GlassCard>
                    <h3 className="font-semibold text-white mb-4">Alerts by Severity & Prediction</h3>
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={severityData} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis type="number" stroke="#9ca3af" fontSize={12} />
                            <YAxis dataKey="name" type="category" stroke="#9ca3af" fontSize={12} width={60} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Legend />
                            <Bar dataKey="TP" name="True Positive" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
                            <Bar dataKey="FP" name="False Positive" stackId="a" fill="#3b82f6" />
                            <Bar dataKey="BP" name="Benign Positive" stackId="a" fill="#22c55e" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </GlassCard>
            </div>
        </div>
    );
}
