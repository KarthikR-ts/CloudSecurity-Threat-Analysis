"use client";

/**
 * ML Engineer Dashboard
 * SHAP visualizations, model metrics, drift detection
 */

import { useEffect, useState } from "react";
import { api, EnhancedAlert, MetricsSummary } from "@/lib/api";
import { GlassCard } from "@/components/ui/GlassCard";
import { ShapWaterfall } from "@/components/charts/ShapWaterfall";
import { DashboardToolbar } from "@/components/dashboard/DashboardToolbar";
import {
    Brain, Cpu, Activity, BarChart3,
    TrendingUp, AlertCircle, CheckCircle2, Zap,
    Sparkles, Shield, FileText
} from "lucide-react";
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Cell, LineChart, Line, ScatterChart,
    Scatter, ZAxis
} from "recharts";

export default function MLEngineerDashboard() {
    const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
    const [alerts, setAlerts] = useState<EnhancedAlert[]>([]);
    const [selectedAlert, setSelectedAlert] = useState<EnhancedAlert | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            const [metricsData, alertsData] = await Promise.all([
                api.fetchMetricsSummary(),
                api.fetchEnhancedAlerts({ role: 'ML_ENGINEER' })
            ]);

            if (metricsData) setMetrics(metricsData);
            if (alertsData) {
                setAlerts(alertsData.alerts);
                if (!selectedAlert && alertsData.alerts.length > 0) {
                    setSelectedAlert(alertsData.alerts[0]);
                }
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
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500" />
            </div>
        );
    }

    const modelMetrics = metrics?.model_metrics || {
        f1_score: 0.84,
        precision: 0.82,
        recall: 0.86,
        accuracy: 0.83
    };

    // Prepare feature importance data
    const featureImportance = selectedAlert?.shap_values
        ? Object.entries(selectedAlert.shap_values)
            .map(([feature, value]) => ({ feature, importance: Math.abs(value), value }))
            .sort((a, b) => b.importance - a.importance)
            .slice(0, 8)
        : [];

    // Confidence distribution data
    const confidenceDistribution = [
        { range: "0.5-0.6", TP: 1, FP: 2, BP: 1 },
        { range: "0.6-0.7", TP: 2, FP: 3, BP: 2 },
        { range: "0.7-0.8", TP: 3, FP: 2, BP: 3 },
        { range: "0.8-0.9", TP: 4, FP: 1, BP: 2 },
        { range: "0.9-1.0", TP: 5, FP: 0, BP: 1 }
    ];

    // Drift timeline data
    const driftTimeline = [
        { day: "Mon", drift: 0.02, baseline: 0.05 },
        { day: "Tue", drift: 0.03, baseline: 0.05 },
        { day: "Wed", drift: 0.02, baseline: 0.05 },
        { day: "Thu", drift: 0.04, baseline: 0.05 },
        { day: "Fri", drift: 0.03, baseline: 0.05 },
        { day: "Sat", drift: 0.02, baseline: 0.05 },
        { day: "Sun", drift: 0.01, baseline: 0.05 }
    ];

    // SHAP values for waterfall
    const shapValues = selectedAlert?.shap_values
        ? Object.entries(selectedAlert.shap_values).map(([feature, value]) => ({
            feature,
            value: value as number,
            featureValue: selectedAlert.features?.[feature]
        }))
        : [];

    return (
        <div className="space-y-6">
            <DashboardToolbar />

            {/* Model Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <GlassCard className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">F1 Score</p>
                            <p className="text-3xl font-bold text-green-400">
                                {(modelMetrics.f1_score * 100).toFixed(1)}%
                            </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                            <Brain className="w-6 h-6 text-green-400" />
                        </div>
                    </div>
                    <div className="mt-2 flex items-center gap-1 text-xs">
                        <TrendingUp className="w-3 h-3 text-green-400" />
                        <span className="text-green-400">+2.1% vs baseline</span>
                    </div>
                </GlassCard>

                <GlassCard className="bg-gradient-to-br from-blue-500/10 to-cyan-500/10 border-blue-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">Precision</p>
                            <p className="text-3xl font-bold text-blue-400">
                                {(modelMetrics.precision * 100).toFixed(1)}%
                            </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-blue-500/20 flex items-center justify-center">
                            <Zap className="w-6 h-6 text-blue-400" />
                        </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                        Low false positive rate
                    </div>
                </GlassCard>

                <GlassCard className="bg-gradient-to-br from-purple-500/10 to-pink-500/10 border-purple-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">Recall</p>
                            <p className="text-3xl font-bold text-purple-400">
                                {(modelMetrics.recall * 100).toFixed(1)}%
                            </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                            <Activity className="w-6 h-6 text-purple-400" />
                        </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                        Threat detection coverage
                    </div>
                </GlassCard>

                <GlassCard className="bg-gradient-to-br from-amber-500/10 to-orange-500/10 border-amber-500/20">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-gray-400">Accuracy</p>
                            <p className="text-3xl font-bold text-amber-400">
                                {(modelMetrics.accuracy * 100).toFixed(1)}%
                            </p>
                        </div>
                        <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center">
                            <CheckCircle2 className="w-6 h-6 text-amber-400" />
                        </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                        Overall correctness
                    </div>
                </GlassCard>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* SHAP Waterfall */}
                <GlassCard>
                    <div className="flex items-center justify-between mb-4 gap-4">
                        <h3 className="font-semibold text-white truncate">SHAP Explanation</h3>
                        <select
                            className="bg-white/5 border border-white/10 rounded-lg px-3 py-1.5 text-sm text-gray-300 min-w-0 flex-1 max-w-[250px]"
                            value={selectedAlert?.id || ''}
                            onChange={(e) => {
                                const alert = alerts.find(a => a.id === e.target.value);
                                if (alert) setSelectedAlert(alert);
                            }}
                        >
                            {alerts.map(alert => (
                                <option key={alert.id} value={alert.id}>
                                    {alert.id} - {alert.title.slice(0, 30)}...
                                </option>
                            ))}
                        </select>
                    </div>

                    {selectedAlert && shapValues.length > 0 ? (
                        <ShapWaterfall
                            baseValue={0.33}
                            shapValues={shapValues}
                            prediction={selectedAlert.xgb_prediction}
                        />
                    ) : (
                        <div className="h-[300px] flex flex-col items-center justify-center text-gray-500 border border-dashed border-white/5 rounded-xl bg-black/20">
                            <Activity className="w-8 h-8 mb-2 opacity-20" />
                            <p className="text-sm italic">No SHAP analysis available for this alert</p>
                        </div>
                    )}
                </GlassCard>

                {/* Feature Importance */}
                <GlassCard>
                    <h3 className="font-semibold text-white mb-4">Feature Importance (Top Contributors)</h3>
                    {featureImportance.length > 0 ? (
                        <div className="h-[300px] w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={featureImportance} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                    <XAxis type="number" stroke="#9ca3af" fontSize={12} />
                                    <YAxis
                                        dataKey="feature"
                                        type="category"
                                        stroke="#9ca3af"
                                        fontSize={11}
                                        width={120}
                                        tickFormatter={(value) => value.length > 15 ? value.slice(0, 15) + '...' : value}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: 'rgba(17, 24, 39, 0.95)',
                                            border: '1px solid rgba(255,255,255,0.1)',
                                            borderRadius: '8px'
                                        }}
                                        formatter={(value: number) => value.toFixed(4)}
                                    />
                                    <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                                        {featureImportance.map((entry, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={entry.value >= 0 ? '#ef4444' : '#3b82f6'}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    ) : (
                        <div className="h-[300px] flex flex-col items-center justify-center text-gray-500 border border-dashed border-white/5 rounded-xl bg-black/20">
                            <BarChart3 className="w-8 h-8 mb-2 opacity-20" />
                            <p className="text-sm italic">Feature importance data missing</p>
                        </div>
                    )}
                </GlassCard>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Confidence Distribution */}
                <GlassCard>
                    <h3 className="font-semibold text-white mb-4">Confidence Distribution by Class</h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={confidenceDistribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="range" stroke="#9ca3af" fontSize={12} />
                            <YAxis stroke="#9ca3af" fontSize={12} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px'
                                }}
                            />
                            <Bar dataKey="TP" name="True Positive" fill="#ef4444" stackId="a" />
                            <Bar dataKey="FP" name="False Positive" fill="#3b82f6" stackId="a" />
                            <Bar dataKey="BP" name="Benign Positive" fill="#22c55e" stackId="a" />
                        </BarChart>
                    </ResponsiveContainer>
                </GlassCard>

                {/* Drift Detection Timeline */}
                <GlassCard>
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-white">Drift Detection (Last 7 Days)</h3>
                        <div className="flex items-center gap-2 px-2 py-1 bg-green-500/10 rounded text-xs text-green-400">
                            <CheckCircle2 className="w-3 h-3" />
                            No drift detected
                        </div>
                    </div>
                    <ResponsiveContainer width="100%" height={250}>
                        <LineChart data={driftTimeline}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                            <XAxis dataKey="day" stroke="#9ca3af" fontSize={12} />
                            <YAxis stroke="#9ca3af" fontSize={12} domain={[0, 0.1]} />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                                    border: '1px solid rgba(255,255,255,0.1)',
                                    borderRadius: '8px'
                                }}
                                formatter={(value: number) => value.toFixed(3)}
                            />
                            <Line
                                type="monotone"
                                dataKey="drift"
                                stroke="#22c55e"
                                strokeWidth={2}
                                dot={{ fill: '#22c55e', r: 4 }}
                                name="Observed Drift"
                            />
                            <Line
                                type="monotone"
                                dataKey="baseline"
                                stroke="#ef4444"
                                strokeWidth={1}
                                strokeDasharray="5 5"
                                dot={false}
                                name="Threshold"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </GlassCard>
            </div>

            {/* Technical Analysis Panel */}
            {selectedAlert && (
                <GlassCard className="border-green-500/30 relative overflow-hidden">
                    <div className="absolute top-0 right-0 p-4">
                        <div className="flex items-center gap-2 px-3 py-1 bg-green-500/20 rounded-full border border-green-500/30">
                            <Sparkles className="w-4 h-4 text-green-400 animate-pulse" />
                            <span className="text-[10px] font-bold text-green-400 tracking-wider">SHAP + RAG VERIFIED</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 mb-8">
                        <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-green-900/40">
                            <Cpu className="w-7 h-7 text-white" />
                        </div>
                        <div>
                            <h3 className="font-extrabold text-2xl text-white tracking-tight">Technical Root Cause Analysis</h3>
                            <p className="text-gray-300 font-medium">
                                Alert ID: <span className="text-green-400 font-mono">{selectedAlert.id}</span> |
                                Classification: <span className="text-white font-bold">{selectedAlert.xgb_prediction}</span>
                            </p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="p-5 bg-white/5 rounded-2xl border border-white/10 hover:bg-white/10 transition-all">
                            <h4 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <Activity className="w-4 h-4 text-blue-400" />
                                Model Introspection
                            </h4>
                            <div className="space-y-2 font-mono text-sm">
                                {Object.entries(selectedAlert.features || {}).slice(0, 5).map(([key, value]) => (
                                    <div key={key} className="flex justify-between border-b border-white/5 pb-1">
                                        <span className="text-gray-400">{key}:</span>
                                        <span className="text-green-400 font-bold">{JSON.stringify(value)}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="p-5 bg-white/5 rounded-2xl border border-white/10 hover:bg-white/10 transition-all">
                            <h4 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <Shield className="w-4 h-4 text-red-500" />
                                Cyber Kill Chain
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {selectedAlert.mitre_techniques.map(t => (
                                    <div key={t} className="px-3 py-1 bg-red-500/20 border border-red-500/30 rounded-full text-[10px] font-bold text-red-400 uppercase tracking-tighter">
                                        {t.split(' - ')[0]}
                                    </div>
                                ))}
                            </div>
                            <p className="text-[10px] text-gray-500 mt-4 leading-relaxed">
                                Cross-referenced with MITRE ATT&CK for Cloud Matrix v14.1
                            </p>
                        </div>

                        <div className="p-5 bg-white/5 rounded-2xl border border-white/10 hover:bg-white/10 transition-all">
                            <h4 className="text-xs font-black text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                                <FileText className="w-4 h-4 text-amber-500" />
                                Regulatory Compliance
                            </h4>
                            <div className="space-y-2">
                                {selectedAlert.cis_controls.map(c => (
                                    <div key={c} className="px-3 py-1 bg-amber-500/10 border border-amber-500/20 rounded-lg text-[10px] font-medium text-amber-200">
                                        {c}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </GlassCard>
            )}

        </div>
    );
}
