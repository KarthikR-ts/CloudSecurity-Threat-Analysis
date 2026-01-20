"use client";

/**
 * Executive Dashboard (Non-Technical User)
 * Risk gauge, plain-language actions, business impact
 */

import { useEffect, useState } from "react";
import { api, EnhancedAlert, MetricsSummary } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { RiskGauge } from "@/components/charts/RiskGauge";
import { DashboardToolbar } from "@/components/dashboard/DashboardToolbar";
import {
    AlertTriangle, Shield, Users, DollarSign,
    CheckCircle, ArrowRight, Lightbulb, TrendingUp,
    Brain, Sparkles
} from "lucide-react";
import {
    PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend
} from "recharts";

const CATEGORY_COLORS = {
    Data: "#ef4444",
    Identity: "#8b5cf6",
    Network: "#3b82f6",
    Compute: "#22c55e"
};

interface Action {
    priority: number;
    title: string;
    impact: string;
    effort: "Easy" | "Medium" | "Hard";
    owner: string;
}

export default function ExecutiveDashboard() {
    const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
    const [alerts, setAlerts] = useState<EnhancedAlert[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                // Check if API methods exist to prevent runtime errors during HMR
                if (typeof api.fetchMetricsSummary !== 'function' || typeof api.fetchEnhancedAlerts !== 'function') {
                    console.warn("API methods not available yet, waiting for reload...");
                    return;
                }

                const [metricsData, alertsData] = await Promise.all([
                    api.fetchMetricsSummary(),
                    api.fetchEnhancedAlerts({ role: 'NON_TECHNICAL' })
                ]);

                if (metricsData) setMetrics(metricsData);
                if (alertsData) setAlerts(alertsData.alerts);
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500" />
            </div>
        );
    }

    // Generate plain-language actions from top alerts
    const actions: Action[] = alerts.slice(0, 5).map((alert, idx) => ({
        priority: idx + 1,
        title: getPlainLanguageTitle(alert),
        impact: alert.business_impact || getDefaultImpact(alert),
        effort: getEffortLevel(alert),
        owner: getOwner(alert)
    }));

    // Prepare donut chart data
    const categoryData = Object.entries(metrics?.risk_categories || {}).map(([name, value]) => ({
        name,
        value,
        color: CATEGORY_COLORS[name as keyof typeof CATEGORY_COLORS] || "#6b7280"
    }));

    const riskScore = metrics?.overall_risk_score || 0;

    return (
        <div className="space-y-6">
            <DashboardToolbar />

            {/* Risk Overview Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Risk Gauge */}
                <GlassCard className="flex items-center justify-center py-8">
                    <RiskGauge value={riskScore} size={220} label="Cloud Security Risk Score" />
                </GlassCard>

                {/* Status Cards */}
                <div className="lg:col-span-2 grid grid-cols-2 gap-4">
                    <GlassCard className={`${riskScore <= 33
                        ? 'bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20'
                        : riskScore <= 66
                            ? 'bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20'
                            : 'bg-gradient-to-br from-red-500/10 to-pink-500/10 border-red-500/20'
                        }`}>
                        <div className="flex items-center gap-4">
                            <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${riskScore <= 33 ? 'bg-green-500/20' : riskScore <= 66 ? 'bg-amber-500/20' : 'bg-red-500/20'
                                }`}>
                                <Shield className={`w-7 h-7 ${riskScore <= 33 ? 'text-green-400' : riskScore <= 66 ? 'text-amber-400' : 'text-red-400'
                                    }`} />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">Security Status</p>
                                <p className={`text-xl font-bold ${riskScore <= 33 ? 'text-green-400' : riskScore <= 66 ? 'text-amber-400' : 'text-red-400'
                                    }`}>
                                    {riskScore <= 33 ? 'Protected' : riskScore <= 66 ? 'Needs Attention' : 'Critical Issues'}
                                </p>
                            </div>
                        </div>
                    </GlassCard>

                    <GlassCard className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 rounded-2xl bg-purple-500/20 flex items-center justify-center">
                                <AlertTriangle className="w-7 h-7 text-purple-400" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">Active Issues</p>
                                <p className="text-xl font-bold text-white">{metrics?.total_alerts || 0}</p>
                                <p className="text-xs text-purple-400">
                                    {metrics?.prediction_distribution?.true_positive || 0} require action
                                </p>
                            </div>
                        </div>
                    </GlassCard>

                    <GlassCard className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/20">
                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center">
                                <TrendingUp className="w-7 h-7 text-blue-400" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">AI Confidence</p>
                                <p className="text-xl font-bold text-white">
                                    {((metrics?.model_metrics?.f1_score || 0) * 100).toFixed(0)}%
                                </p>
                                <p className="text-xs text-blue-400">Model accuracy</p>
                            </div>
                        </div>
                    </GlassCard>

                    <GlassCard className="bg-gradient-to-br from-emerald-500/10 to-teal-500/10 border-emerald-500/20">
                        <div className="flex items-center gap-4">
                            <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 flex items-center justify-center">
                                <CheckCircle className="w-7 h-7 text-emerald-400" />
                            </div>
                            <div>
                                <p className="text-sm text-gray-400">Auto-Resolved</p>
                                <p className="text-xl font-bold text-white">
                                    {(metrics?.prediction_distribution?.false_positive || 0) +
                                        (metrics?.prediction_distribution?.benign_positive || 0)}
                                </p>
                                <p className="text-xs text-emerald-400">Non-threats filtered</p>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Plain Language Actions */}
                <div className="lg:col-span-2">
                    <GlassCard>
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-xl font-semibold text-white flex items-center gap-2">
                                    <Lightbulb className="w-5 h-5 text-amber-400" />
                                    Recommended Actions
                                </h3>
                                <p className="text-sm text-gray-400">Plain-language steps your team can take now</p>
                            </div>
                        </div>

                        <div className="space-y-4">
                            {actions.map((action, idx) => (
                                <div
                                    key={idx}
                                    className="p-4 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex items-start gap-4">
                                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${action.priority === 1
                                                ? 'bg-red-500/20 text-red-400'
                                                : action.priority === 2
                                                    ? 'bg-amber-500/20 text-amber-400'
                                                    : 'bg-blue-500/20 text-blue-400'
                                                }`}>
                                                {action.priority}
                                            </div>
                                            <div className="flex-1">
                                                <h4 className="font-medium text-white">{action.title}</h4>
                                                <p className="text-sm text-gray-400 mt-1">{action.impact}</p>
                                                <div className="flex items-center gap-3 mt-2">
                                                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${action.effort === 'Easy'
                                                        ? 'bg-green-500/20 text-green-400'
                                                        : action.effort === 'Medium'
                                                            ? 'bg-amber-500/20 text-amber-400'
                                                            : 'bg-red-500/20 text-red-400'
                                                        }`}>
                                                        {action.effort} fix
                                                    </span>
                                                    <span className="text-xs text-gray-500 flex items-center gap-1">
                                                        <Users className="w-3 h-3" />
                                                        {action.owner}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </GlassCard>
                </div>

                {/* Risk by Category */}
                <GlassCard>
                    <h3 className="font-semibold text-white mb-4">Risk by Business Area</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <PieChart>
                            <Pie
                                data={categoryData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={90}
                                dataKey="value"
                                paddingAngle={4}
                            >
                                {categoryData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={entry.color}
                                        stroke="transparent"
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Legend
                                formatter={(value) => <span className="text-gray-300">{value}</span>}
                            />
                        </PieChart>
                    </ResponsiveContainer>

                    <div className="mt-4 space-y-2">
                        {categoryData.map(cat => (
                            <div key={cat.name} className="flex items-center justify-between text-sm">
                                <div className="flex items-center gap-2">
                                    <div
                                        className="w-3 h-3 rounded-full"
                                        style={{ backgroundColor: cat.color }}
                                    />
                                    <span className="text-gray-300">{cat.name}</span>
                                </div>
                                <span className="text-gray-500">{cat.value} issues</span>
                            </div>
                        ))}
                    </div>
                </GlassCard>
            </div>

            {/* AI Trust Indicator */}
            <GlassCard className="bg-gradient-to-r from-indigo-600/20 to-purple-600/20 border-white/20 shadow-[0_0_50px_rgba(99,102,241,0.15)] overflow-hidden relative">
                <div className="absolute top-0 right-0 p-4 opacity-10">
                    <Sparkles className="w-24 h-24 text-white" />
                </div>
                <div className="flex items-center justify-between relative z-10">
                    <div className="flex items-center gap-6">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-xl">
                            <Brain className="w-8 h-8 text-white" />
                        </div>
                        <div>
                            <h4 className="text-xl font-bold text-white flex items-center gap-2">
                                Hybrid AI Analysis Engine
                                <span className="text-[10px] bg-white/20 px-2 py-0.5 rounded-full uppercase tracking-tighter">XGBoost + RAG</span>
                            </h4>
                            <p className="text-gray-300 mt-1 max-w-xl leading-relaxed">
                                Our system cross-references <strong>{metrics?.total_alerts || 0} alerts</strong> against the <strong>Azure Security Knowledge Base</strong>
                                using RAG, identifying <strong>{metrics?.prediction_distribution?.true_positive || 0} verified threats</strong> with
                                {((metrics?.model_metrics?.f1_score || 0) * 100).toFixed(0)}% precision.
                            </p>
                        </div>
                    </div>
                    <div className="text-right">
                        <div className="text-4xl font-black text-white tracking-tight">
                            {((metrics?.model_metrics?.f1_score || 0) * 100).toFixed(0)}%
                        </div>
                        <div className="text-xs font-bold text-indigo-400 uppercase tracking-widest mt-1">Trust Score</div>
                    </div>
                </div>
            </GlassCard>

        </div>
    );
}

// Helper functions
function getPlainLanguageTitle(alert: EnhancedAlert): string {
    const titles: Record<string, string> = {
        'StorageAccount': 'Secure your cloud file storage',
        'VM': 'Review suspicious activity on server',
        'SQLDB': 'Protect your customer database',
        'AKSCluster': 'Review container security settings',
        'KeyVault': 'Verify secret access permissions'
    };
    return titles[alert.resource_type] || `Review security issue: ${alert.title}`;
}

function getDefaultImpact(alert: EnhancedAlert): string {
    if (alert.severity === 'critical') {
        return 'Immediate action required. Potential data exposure or compliance violation.';
    }
    if (alert.severity === 'high') {
        return 'High priority. Could lead to security breach if not addressed.';
    }
    return 'Review recommended. Lower risk but should be addressed.';
}

function getEffortLevel(alert: EnhancedAlert): "Easy" | "Medium" | "Hard" {
    if (alert.resource_type === 'StorageAccount') return 'Easy';
    if (alert.resource_type === 'KeyVault') return 'Medium';
    return 'Medium';
}

function getOwner(alert: EnhancedAlert): string {
    const owners: Record<string, string> = {
        'StorageAccount': 'Cloud Team',
        'VM': 'DevOps',
        'SQLDB': 'DBA Team',
        'AKSCluster': 'Platform Team',
        'KeyVault': 'Security Team'
    };
    return owners[alert.resource_type] || 'IT Team';
}
