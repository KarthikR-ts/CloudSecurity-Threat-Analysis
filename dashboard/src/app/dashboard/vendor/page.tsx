import { GlassCard } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { CheckCircle, AlertTriangle, XCircle, FileJson } from "lucide-react";

export default function VendorDashboard() {
    const policies = [
        { id: "POL-001", name: "Storage Account Encryption", status: "compliant" },
        { id: "POL-002", name: "MFA Enforcement", status: "compliant" },
        { id: "POL-003", name: "Public Network Access", status: "non_compliant" },
        { id: "POL-004", name: "Kubernetes Role Binding", status: "compliant" },
        { id: "POL-005", name: "SQL Audit Logs", status: "warning" },
    ];

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <GlassCard className="flex items-center gap-4">
                    <div className="p-3 bg-emerald-500/10 rounded-full border border-emerald-500/20">
                        <CheckCircle className="w-8 h-8 text-emerald-500" />
                    </div>
                    <div>
                        <p className="text-3xl font-bold">94%</p>
                        <p className="text-muted-foreground text-sm">Compliance Score</p>
                    </div>
                </GlassCard>
                <GlassCard className="flex items-center gap-4">
                    <div className="p-3 bg-red-500/10 rounded-full border border-red-500/20">
                        <XCircle className="w-8 h-8 text-red-500" />
                    </div>
                    <div>
                        <p className="text-3xl font-bold">2</p>
                        <p className="text-muted-foreground text-sm">Critical Violations</p>
                    </div>
                </GlassCard>
                <GlassCard className="flex items-center gap-4">
                    <div className="p-3 bg-brand-accent/10 rounded-full border border-brand-accent/20">
                        <AlertTriangle className="w-8 h-8 text-brand-accent" />
                    </div>
                    <div>
                        <p className="text-3xl font-bold">14</p>
                        <p className="text-muted-foreground text-sm">Active Drifts</p>
                    </div>
                </GlassCard>
            </div>

            <GlassCard>
                <h3 className="text-lg font-semibold mb-4">Active Policies (Azure & AWS)</h3>
                <div className="space-y-2">
                    {policies.map((p) => (
                        <div key={p.id} className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 group cursor-pointer">
                            <div className="flex items-center gap-4">
                                <FileJson className="w-5 h-5 text-muted-foreground group-hover:text-white" />
                                <div>
                                    <p className="font-medium text-white">{p.name}</p>
                                    <p className="text-xs text-muted-foreground">{p.id}</p>
                                </div>
                            </div>
                            <StatusBadge
                                status={p.status === 'compliant' ? 'success' : p.status === 'warning' ? 'warning' : 'danger'}
                                text={p.status.replace('_', ' ').toUpperCase()}
                            />
                        </div>
                    ))}
                </div>
            </GlassCard>
        </div>
    );
}
