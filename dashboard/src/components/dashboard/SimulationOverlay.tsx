
"use client";

import { useSimulationStore } from "@/lib/store";
import { GlassCard } from "@/components/ui/GlassCard";
import { BrainCircuit, Cpu, Loader2, Sparkles, X, CheckCircle2, ShieldAlert, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";

export function SimulationOverlay() {
    const { isSimulating, currentStep, steps, result, remediation, resetSimulation } = useSimulationStore();

    if (!isSimulating) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
            <GlassCard className="max-w-4xl w-full border-white/20 shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
                <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-brand-primary/20 border border-brand-primary/30">
                            <Sparkles className="w-5 h-5 text-brand-primary animate-pulse" />
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-white tracking-tight">Threat Simulation Engine</h2>
                            <p className="text-sm text-neutral-400">Aurora AI Pipeline Trace</p>
                        </div>
                    </div>
                    <button
                        onClick={resetSimulation}
                        className="p-2 rounded-full hover:bg-white/10 text-neutral-400 hover:text-white transition-colors"
                    >
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    {steps.map((step, idx) => (
                        <div
                            key={step.id}
                            className={cn(
                                "relative p-4 rounded-xl border transition-all duration-500",
                                step.status === 'completed' ? "bg-emerald-500/10 border-emerald-500/30" :
                                    step.status === 'loading' ? "bg-brand-primary/10 border-brand-primary/40 scale-105 shadow-lg" :
                                        "bg-white/5 border-white/10 opacity-50"
                            )}
                        >
                            <div className="flex items-center justify-between mb-3">
                                {step.status === 'completed' ? (
                                    <CheckCircle2 className="w-5 h-5 text-emerald-500" />
                                ) : step.status === 'loading' ? (
                                    <Loader2 className="w-5 h-5 text-brand-primary animate-spin" />
                                ) : (
                                    <div className="w-5 h-5 rounded-full border-2 border-white/20" />
                                )}
                                <span className="text-[10px] font-mono text-neutral-500 uppercase tracking-widest">Step 0{idx + 1}</span>
                            </div>
                            <h3 className="font-bold text-white mb-1">{step.name}</h3>
                            <p className="text-xs text-neutral-400 leading-relaxed">{step.description}</p>

                            {step.status === 'completed' && step.data && (
                                <div className="mt-4 p-2 rounded bg-black/40 border border-white/5 font-mono text-[10px] text-emerald-400/80 overflow-hidden text-ellipsis whitespace-nowrap">
                                    {JSON.stringify(step.data).substring(0, 50)}...
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="flex-1 overflow-hidden flex flex-col min-h-0">
                    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar space-y-8 pb-6">
                        {result && (
                            <div className="animate-in slide-in-from-bottom-5 duration-500">
                                <h4 className="text-xs font-black text-brand-primary uppercase tracking-[0.2em] mb-4 flex items-center gap-2">
                                    <ShieldAlert className="w-4 h-4" /> ML Classification Result
                                </h4>
                                <div className="p-6 rounded-2xl bg-white/5 border border-emerald-500/20 shadow-inner">
                                    <div className="flex flex-col md:flex-row gap-6 items-start md:items-center mb-6">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-3">
                                                <span className={cn(
                                                    "px-2 py-1 rounded text-[10px] font-black uppercase tracking-wider",
                                                    result.xgb_prediction === 'TRUE_POSITIVE' ? "bg-red-500/20 text-red-500 border border-red-500/30" : "bg-emerald-500/20 text-emerald-500 border border-emerald-500/30"
                                                )}>
                                                    {result.xgb_prediction.replace('_', ' ')}
                                                </span>
                                                <span className="text-white font-bold text-lg">{result.title}</span>
                                            </div>
                                            <p className="text-sm text-neutral-400 leading-relaxed font-medium">
                                                {result.description}
                                            </p>
                                        </div>
                                        <div className="text-center md:border-l border-white/10 md:pl-10">
                                            <div className="text-4xl font-black text-white tracking-tighter">{Math.round(result.xgb_confidence * 100)}%</div>
                                            <div className="text-[10px] text-neutral-500 font-bold uppercase tracking-[0.2em] mt-1">Confidence</div>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                        {Object.entries(result.features).map(([key, value]: [string, any]) => (
                                            <div key={key} className="p-3 rounded-xl bg-black/30 border border-white/5 hover:border-white/10 transition-colors">
                                                <div className="text-[9px] text-neutral-500 font-bold uppercase tracking-wider mb-1">{key.replace(/_/g, ' ')}</div>
                                                <div className="text-xs font-mono text-brand-secondary font-bold">{String(value)}</div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {currentStep === 2 && !remediation && (
                            <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-white/10 rounded-3xl bg-white/5 animate-pulse">
                                <div className="relative mb-4">
                                    <div className="absolute inset-0 bg-brand-secondary/20 blur-xl rounded-full" />
                                    <BrainCircuit className="w-12 h-12 text-brand-secondary relative z-10" />
                                </div>
                                <p className="text-sm font-bold text-neutral-400 uppercase tracking-widest">Querying Knowledge Artifacts...</p>
                                <p className="text-xs text-neutral-500 mt-2">Synthesizing remediation strategy via Gemini 1.5 Pro</p>
                            </div>
                        )}

                        {remediation && (
                            <div className="animate-in slide-in-from-bottom-5 duration-500 delay-200">
                                <div className="flex items-center justify-between mb-4">
                                    <h4 className="text-xs font-black text-brand-secondary uppercase tracking-[0.2em] flex items-center gap-2">
                                        <BookOpen className="w-4 h-4" /> RAG Remediation Strategy
                                    </h4>
                                    <span className="px-2 py-0.5 rounded bg-brand-secondary/20 text-brand-secondary text-[8px] font-black uppercase tracking-widest border border-brand-secondary/30">
                                        Verified Action
                                    </span>
                                </div>
                                <div className="p-6 rounded-2xl bg-white/5 border border-brand-secondary/30 shadow-lg shadow-brand-secondary/5">
                                    <div className="p-5 rounded-xl bg-brand-secondary/10 border-l-4 border-brand-secondary mb-6">
                                        <p className="text-sm text-white leading-relaxed font-semibold italic">
                                            "{remediation.advice}"
                                        </p>
                                    </div>
                                    <div className="space-y-4">
                                        <h5 className="text-[10px] font-black text-neutral-500 uppercase tracking-[0.2em]">Retrieved Knowledge Artifacts</h5>
                                        <div className="flex flex-wrap gap-2">
                                            {remediation.sources.map((source: any, i: number) => (
                                                <div key={i} className="px-3 py-1.5 bg-white/5 border border-white/10 rounded-lg text-xs text-neutral-300 font-medium flex items-center gap-2">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-brand-secondary/60" />
                                                    {source.source || 'Knowledge Base'}
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

                <div className="mt-8 pt-6 border-t border-white/10 flex justify-end gap-4">
                    <button
                        onClick={resetSimulation}
                        className="px-8 py-3 rounded-xl bg-white/10 text-white font-bold hover:bg-white/20 transition-all border border-white/10"
                    >
                        Dismiss
                    </button>
                    <button
                        onClick={resetSimulation}
                        className="px-8 py-3 rounded-xl bg-brand-primary text-white font-bold hover:bg-brand-primary/80 transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)]"
                    >
                        Apply Remediation & Return
                    </button>
                </div>
            </GlassCard>
        </div>
    );
}
