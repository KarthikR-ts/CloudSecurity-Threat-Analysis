import { GlassCard } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Alert } from "@/lib/mock-data";
import { Eye } from "lucide-react";
import Link from "next/link";

export function IncidentTable({ alerts }: { alerts: Alert[] }) {
    return (
        <GlassCard className="p-0 overflow-hidden">
            <div className="px-6 py-4 border-b border-white/10 flex items-center justify-between">
                <h3 className="font-semibold text-lg">Active Incidents</h3>
                <button className="text-xs text-brand-primary hover:text-brand-primary/80 transition-colors">View All Analysis</button>
            </div>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-white/5 text-muted-foreground font-medium">
                        <tr>
                            <th className="px-6 py-3">Severity</th>
                            <th className="px-6 py-3">Incident Name</th>
                            <th className="px-6 py-3">Classification</th>
                            <th className="px-6 py-3">Time</th>
                            <th className="px-6 py-3">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                        {alerts.map((alert) => (
                            <tr key={alert.id} className="hover:bg-white/5 transition-colors group">
                                <td className="px-6 py-4">
                                    <div className={`w-1.5 h-8 rounded-full ${alert.severity === 'critical' ? 'bg-brand-accent shadow-[0_0_8px_rgba(239,68,68,0.5)]' :
                                            alert.severity === 'high' ? 'bg-orange-500' : 'bg-brand-secondary'
                                        }`} />
                                </td>
                                <td className="px-6 py-4 font-medium text-white max-w-xs truncate">
                                    {alert.title}
                                    <div className="text-xs text-muted-foreground font-normal mt-0.5">{alert.source} • {alert.id}</div>
                                </td>
                                <td className="px-6 py-4">
                                    <StatusBadge
                                        status={alert.classification === 'TP' ? 'danger' : 'success'}
                                        text={alert.classification === 'TP' ? `${alert.confidence}% Malicious` : 'False Positive'}
                                        pulse={alert.classification === 'TP'}
                                    />
                                </td>
                                <td className="px-6 py-4 text-muted-foreground whitespace-nowrap">
                                    {alert.timestamp}
                                </td>
                                <td className="px-6 py-4">
                                    <Link href={`/dashboard/incidents/${alert.id}`}>
                                        <button className="p-2 rounded-lg hover:bg-white/10 text-muted-foreground hover:text-white transition-colors">
                                            <Eye className="w-4 h-4" />
                                        </button>
                                    </Link>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </GlassCard>
    );
}
