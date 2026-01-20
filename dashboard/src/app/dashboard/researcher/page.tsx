import { GlassCard } from "@/components/ui/GlassCard";
import { NeonButton } from "@/components/ui/NeonButton";
import { Brain, Terminal } from "lucide-react";
import { DashboardToolbar } from "@/components/dashboard/DashboardToolbar";

export default function ResearcherDashboard() {
    return (
        <div className="space-y-6">
            <DashboardToolbar />
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-primary to-purple-400">Model Diagnostics</h1>
                    <p className="text-muted-foreground mt-1">Deep learning triage model inference viewer</p>
                </div>
                <NeonButton icon={<Brain className="w-4 h-4" />}>Retrain Model V2</NeonButton>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <GlassCard className="h-full">
                    <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <Terminal className="w-4 h-4 text-brand-primary" />
                        Live Inference Log
                    </h3>
                    <div className="bg-black/50 rounded-lg p-4 font-mono text-xs text-green-400 h-[400px] overflow-y-auto space-y-2 border border-white/5">
                        <p><span className="text-gray-500">[14:20:01]</span> &lt;INF&gt; Ingested event ID: evt_99882</p>
                        <p><span className="text-gray-500">[14:20:01]</span> &lt;DBG&gt; Vectorizing features: [ip_reputation, login_time, user_agent]</p>
                        <p><span className="text-gray-500">[14:20:02]</span> &lt;INF&gt; Prediction: <span className="text-red-400">True Positive (0.982)</span></p>
                        <p><span className="text-gray-500">[14:20:05]</span> &lt;INF&gt; Mapping to MITRE T1078 (Valid Accounts)</p>
                        <p><span className="text-gray-500">[14:20:05]</span> &lt;WRN&gt; Anomalous geographic velocity detected (NY -&gt; London &lt; 1hr)</p>
                        <p className="opacity-50">...</p>
                    </div>
                </GlassCard>

                <div className="space-y-6">
                    <GlassCard>
                        <h3 className="text-lg font-semibold mb-2">Feature Importance (SHAP)</h3>
                        <div className="space-y-3">
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span>IP Reputation Score</span>
                                    <span className="text-brand-primary font-bold">0.45</span>
                                </div>
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-brand-primary w-[45%]" />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span>Time of Day (Off-hours)</span>
                                    <span className="text-brand-primary font-bold">0.32</span>
                                </div>
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-brand-primary w-[32%]" />
                                </div>
                            </div>
                            <div>
                                <div className="flex justify-between text-sm mb-1">
                                    <span>Resource Sensitivity</span>
                                    <span className="text-brand-primary font-bold">0.15</span>
                                </div>
                                <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                    <div className="h-full bg-brand-primary w-[15%]" />
                                </div>
                            </div>
                        </div>
                    </GlassCard>

                    <GlassCard className="bg-gradient-to-br from-brand-primary/10 to-transparent border-brand-primary/20">
                        <h3 className="text-lg font-semibold mb-2">Model Confidence Distribution</h3>
                        <div className="h-32 flex items-end justify-between px-2 gap-1">
                            {[10, 25, 40, 60, 80, 45, 20, 10, 5, 2].map((h, i) => (
                                <div key={i} className="bg-brand-primary/40 hover:bg-brand-primary transition-colors w-full rounded-t-sm" style={{ height: `${h}%` }} />
                            ))}
                        </div>
                        <div className="flex justify-between text-xs text-muted-foreground mt-2">
                            <span>0.0</span>
                            <span>Confidence Score</span>
                            <span>1.0</span>
                        </div>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
