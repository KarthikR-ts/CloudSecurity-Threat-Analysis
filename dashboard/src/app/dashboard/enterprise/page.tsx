"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AlertVolumeChart } from "@/components/dashboard/AlertVolumeChart";
import { IncidentTable } from "@/components/dashboard/IncidentTable";
import { MetricCard } from "@/components/dashboard/MetricCard";
import { DashboardToolbar } from "@/components/dashboard/DashboardToolbar";
import { GlassCard } from "@/components/ui/GlassCard";
import { MOCK_ALERTS, MOCK_METRICS } from "@/lib/mock-data";
import { ShieldAlert, Activity, CheckCircle2, AlertOctagon, XCircle } from "lucide-react";

export default function EnterpriseDashboard() {
    const [alerts, setAlerts] = useState(MOCK_ALERTS);
    const [status, setStatus] = useState<any>(null);
    const [showAlert, setShowAlert] = useState(false);
    const [lastAlertCount, setLastAlertCount] = useState(MOCK_ALERTS.length);

    useEffect(() => {
        const loadIncidents = async () => {
            const data = await api.fetchIncidents();
            if (data && data.length > 0) {
                if (data.length > lastAlertCount) {
                    setShowAlert(true);
                    setTimeout(() => setShowAlert(false), 5000);
                    setLastAlertCount(data.length);
                }
                setAlerts(data);
            }
        };

        const loadStatus = async () => {
            const data = await api.fetchSystemStatus();
            if (data) setStatus(data);
        };

        loadIncidents();
        loadStatus();

        const interval = setInterval(() => {
            loadIncidents();
            loadStatus();
        }, 3000);

        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6 relative">
            {showAlert && (
                <div className="fixed top-20 right-8 z-50 animate-in fade-in slide-in-from-right-10 duration-500">
                    <div className="bg-brand-accent text-white px-6 py-4 rounded-xl shadow-2xl flex items-center gap-4 border border-white/20 backdrop-blur-md">
                        <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center animate-pulse">
                            <ShieldAlert className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <p className="font-bold text-sm">SECURITY ALERT</p>
                            <p className="text-xs text-white/80">New incident detected by AI Engine</p>
                        </div>
                    </div>
                </div>
            )}
            <DashboardToolbar />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                <MetricCard
                    title="Total Alerts"
                    value={alerts.length.toString()}
                    icon={<AlertOctagon className="w-5 h-5 text-brand-primary" />}
                    trend={{ value: "Live", direction: "neutral" }}
                    glowColor="primary"
                    className="lg:col-span-1"
                />
                <MetricCard
                    title="True Positives"
                    value={alerts.filter(a => a.classification === 'TP').length.toString()}
                    icon={<ShieldAlert className="w-5 h-5 text-red-500" />}
                    trend={{ value: "+12%", direction: "up" }}
                    glowColor="accent"
                />
                <MetricCard
                    title="False Positives"
                    value={alerts.filter(a => a.classification === 'FP').length.toString()}
                    icon={<XCircle className="w-5 h-5 text-amber-500" />}
                    trend={{ value: "-5%", direction: "down" }}
                />
                <MetricCard
                    title="Benign Positives"
                    value={alerts.filter(a => a.classification === 'BP').length.toString()}
                    icon={<CheckCircle2 className="w-5 h-5 text-emerald-500" />}
                    trend={{ value: "+8%", direction: "up" }}
                />
                <MetricCard
                    title="Avg MTTR"
                    value={MOCK_METRICS.mttr}
                    icon={<Activity className="w-5 h-5 text-blue-400" />}
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    <AlertVolumeChart />
                </div>
                <div className="lg:col-span-1">
                    <GlassCard className="h-full">
                        <h3 className="font-semibold text-lg mb-4">System Health</h3>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${status?.status === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                                    <span className="text-sm font-medium">Core API Pipeline</span>
                                </div>
                                <span className="text-xs text-muted-foreground">{status?.status || 'connecting...'}</span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className={`w-2 h-2 rounded-full ${status?.knowledge_base === 'connected' ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`} />
                                    <span className="text-sm font-medium">RAG Vector Engine</span>
                                </div>
                                <span className="text-xs text-muted-foreground">{status?.knowledge_base || 'checking...'}</span>
                            </div>
                            <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                                <div className="flex items-center gap-3">
                                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                    <span className="text-sm font-medium">ML Inference Modality</span>
                                </div>
                                <span className="text-xs text-muted-foreground">XGBoost-V2.1</span>
                            </div>
                        </div>

                        <div className="mt-6 pt-6 border-t border-white/10">
                            <h4 className="text-sm font-medium text-muted-foreground mb-3">Coverage Map</h4>
                            <div className="flex gap-2 flex-wrap">
                                <span className="px-2 py-1 bg-white/5 rounded text-xs text-white border border-white/10">AWS: prod-east-1</span>
                                <span className="px-2 py-1 bg-white/5 rounded text-xs text-white border border-white/10">Azure: core-vnet</span>
                                <span className="px-2 py-1 bg-white/5 rounded text-xs text-white border border-white/10">GCP: k8s-cluster</span>
                            </div>
                        </div>
                    </GlassCard>
                </div>
            </div>

            <IncidentTable alerts={alerts} />
        </div>
    );
}
