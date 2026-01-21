
"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { GlassCard } from "@/components/ui/GlassCard";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { api, PredictionResponse, ExplanationResponse, SearchResponse, AskResponse } from "@/lib/api";
import { MOCK_ALERTS } from "@/lib/mock-data";
import { ArrowLeft, BrainCircuit, ShieldAlert, BookOpen, Activity, CheckCircle, XCircle, Terminal, Copy, Check } from "lucide-react";

export default function IncidentAnalysisPage() {
    const params = useParams();
    const id = params?.id as string;

    const [loading, setLoading] = useState(true);
    const [incident, setIncident] = useState<any>(null);
    const [prediction, setPrediction] = useState<PredictionResponse | null>(null);
    const [explanation, setExplanation] = useState<ExplanationResponse | null>(null);
    const [remediation, setRemediation] = useState<SearchResponse | null>(null);
    const [aiAdvice, setAiAdvice] = useState<AskResponse | null>(null);
    const [fixScript, setFixScript] = useState<{ script: string, platform: string } | null>(null);
    const [generatingFix, setGeneratingFix] = useState(false);
    const [copied, setCopied] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleGenerateFix = async () => {
        if (!incident) return;
        setGeneratingFix(true);
        try {
            const res = await api.generateFix(incident.description, "azure_cli");
            setFixScript(res);
        } catch (err) {
            console.error("Fix generation failed:", err);
        } finally {
            setGeneratingFix(false);
        }
    };

    const copyToClipboard = () => {
        if (fixScript) {
            navigator.clipboard.writeText(fixScript.script);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    useEffect(() => {
        async function loadAnalysis() {
            try {
                // 1. Fetch from Backend API (Enhanced Alerts)
                const alert = await api.fetchEnhancedAlertById(id);

                if (!alert) {
                    // Fallback to Mock if ID matches mock format (just in case)
                    const mockAlert = MOCK_ALERTS.find(a => a.id === id);
                    if (mockAlert) {
                        setIncident(mockAlert);
                    } else {
                        setError("Incident not found.");
                        setLoading(false);
                        return;
                    }
                } else {
                    setIncident(alert);
                }

                // Use the resolved alert object (either from API or Mock)
                const currentIncident: any = alert || MOCK_ALERTS.find(a => a.id === id);
                if (!currentIncident) return;

                // 2. Set Prediction & Explanation from existing data or API
                if (currentIncident.xgb_prediction) {
                    setPrediction({
                        prediction: currentIncident.xgb_prediction.replace('PredictionClass.', ''),
                        confidence: currentIncident.xgb_confidence,
                        probabilities: { [currentIncident.xgb_prediction]: currentIncident.xgb_confidence }
                    });
                } else {
                    const features = currentIncident.features || {};
                    api.predict(features).then(setPrediction).catch(console.error);
                }

                if (currentIncident.shap_values) {
                    const explanationItems = Object.entries(currentIncident.shap_values).map(([feature, value]) => ({
                        feature,
                        shap_value: Number(value)
                    })).sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));

                    setExplanation({
                        prediction: currentIncident.xgb_prediction || 'Unknown',
                        explanation: explanationItems,
                        base_value: 0
                    });
                } else {
                    const features = currentIncident.features || {};
                    api.explain(features).then(setExplanation).catch(console.error);
                }

                // 3. Fetch Rich Guidance/Remediation
                const guidanceRes = await api.fetchGuidance(currentIncident.id, 'CLOUD_ENGINEER');
                if (guidanceRes) {
                    const stepsText = (guidanceRes.remediation_steps || [])
                        .map((s: string, i: number) => `${i + 1}. ${s}`)
                        .join('\n');

                    // Map backend sources to frontend RemediationResult structure
                    const mappedSources = (guidanceRes.sources || []).map((s: any, idx: number) => ({
                        id: `src-${idx}`,
                        score: 0.95, // Default high confidence for manually curated/RAG sources
                        content: s.type ? `Type: ${s.type}` : "Relevant security documentation",
                        source: s.title || "Unknown Source",
                        metadata: {}
                    }));

                    setAiAdvice({
                        query: currentIncident.description,
                        advice: `${guidanceRes.guidance}\n\n**Action Plan:**\n${stepsText}`,
                        sources: mappedSources
                    });

                    if (guidanceRes.code_snippets && guidanceRes.code_snippets.length > 0) {
                        setFixScript({
                            script: guidanceRes.code_snippets[0].code,
                            platform: guidanceRes.code_snippets[0].language || 'bash'
                        });
                    }
                } else {
                    const [remRes, ragRes] = await Promise.all([
                        api.searchRemediation(currentIncident.description),
                        api.askRag(currentIncident.description)
                    ]);
                    setRemediation(remRes);
                    setAiAdvice(ragRes);
                }

            } catch (err: any) {
                console.error("Analysis failed:", err);
                setError(err.message || "Failed to load analysis.");
            } finally {
                setLoading(false);
            }
        }

        if (id) {
            loadAnalysis();
        }
    }, [id]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black text-white">
                <div className="animate-pulse flex flex-col items-center">
                    <Activity className="w-10 h-10 text-brand-primary mb-4 animate-spin" />
                    <p className="text-muted-foreground">Running ML Inference & RAG Retrieval...</p>
                </div>
            </div>
        );
    }

    if (error || !incident) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black text-white">
                <div className="text-center">
                    <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold mb-2">Analysis Failed</h2>
                    <p className="text-muted-foreground mb-4">{error}</p>
                    <Link href="/dashboard/enterprise" className="text-brand-primary hover:underline">
                        Return to Dashboard
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-neutral-950 text-white p-6 space-y-6">

            {/* Header */}
            <div className="flex items-center gap-4 mb-8">
                <Link href="/dashboard/enterprise">
                    <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                </Link>
                <div>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        {incident.title}
                        <span className="text-base font-normal text-muted-foreground">#{incident.id}</span>
                    </h1>
                    <div className="flex items-center gap-3 mt-1 text-sm text-neutral-400">
                        <span>{incident.timestamp}</span>
                        <span>•</span>
                        <span>{incident.source}</span>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Left Column: Classification & Details */}
                <div className="space-y-6">
                    {/* ML Classification Card */}
                    <GlassCard className="border-t-4 border-t-brand-primary">
                        <div className="flex items-center gap-3 mb-4">
                            <BrainCircuit className="w-6 h-6 text-brand-primary" />
                            <h2 className="font-semibold text-lg">ML Classification</h2>
                        </div>

                        {prediction && (
                            <div className="space-y-4">
                                <div className="p-4 rounded-lg bg-white/5 border border-white/10 text-center">
                                    <div className="text-sm text-muted-foreground mb-1">Predicted Grade</div>
                                    <div className={`text-3xl font-bold ${prediction.prediction === 'TP' ? 'text-red-500' :
                                        prediction.prediction === 'FP' ? 'text-amber-500' : 'text-emerald-500'
                                        }`}>
                                        {prediction.prediction === 'TP' ? 'True Positive' :
                                            prediction.prediction === 'FP' ? 'False Positive' : 'Benign Positive'}
                                    </div>
                                    <div className="mt-2 inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 text-sm">
                                        <Activity className="w-4 h-4" />
                                        {(prediction.confidence * 100).toFixed(1)}% Confidence
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <p className="text-xs text-muted-foreground">Class Probabilities</p>
                                    {Object.entries(prediction.probabilities).map(([label, prob]) => (
                                        <div key={label} className="flex items-center justify-between text-sm">
                                            <span>{label}</span>
                                            <div className="flex items-center gap-2 w-1/2">
                                                <div className="h-1.5 flex-1 bg-white/10 rounded-full overflow-hidden">
                                                    <div
                                                        className="h-full bg-brand-primary rounded-full transition-all duration-500"
                                                        style={{ width: `${prob * 100}%` }}
                                                    />
                                                </div>
                                                <span className="text-xs w-8 text-right">{(prob * 100).toFixed(0)}%</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </GlassCard>

                    {/* Incident Details */}
                    <GlassCard>
                        <h3 className="font-medium text-muted-foreground mb-4">Incident Metadata</h3>
                        <div className="space-y-3 text-sm">
                            <div className="flex justify-between py-2 border-b border-white/5">
                                <span className="text-neutral-400">Severity</span>
                                <span className="capitalize text-white">{incident.severity}</span>
                            </div>
                            <div className="flex justify-between py-2 border-b border-white/5">
                                <span className="text-neutral-400">Category</span>
                                <span className="text-white">{incident.category || incident.risk_category}</span>
                            </div>
                            <div className="flex justify-between py-2 border-b border-white/5">
                                <span className="text-neutral-400">Source IP</span>
                                <span className="text-white font-mono">{incident.features.all_features?.IpAddress || 'N/A'}</span>
                            </div>
                        </div>
                    </GlassCard>
                </div>

                {/* Middle Column: Explainability */}
                <div className="lg:col-span-2 space-y-6">
                    <GlassCard>
                        <div className="flex items-center justify-between mb-6">
                            <div className="flex items-center gap-3">
                                <Activity className="w-6 h-6 text-brand-secondary" />
                                <h2 className="font-semibold text-lg">Analysis & Reasoning (XAI)</h2>
                            </div>
                            <StatusBadge status="warning" text="SHAP Analysis" />
                        </div>

                        {explanation ? (
                            <div className="space-y-6">
                                <p className="text-sm text-neutral-400">
                                    Top factors contributing to this classification. Positive values push towards "True Positive", negative away.
                                </p>

                                <div className="space-y-3">
                                    {explanation.explanation.slice(0, 5).map((item, idx) => (
                                        <div key={idx} className="group">
                                            <div className="flex justify-between text-sm mb-1">
                                                <span className="font-medium text-neutral-300">{item.feature}</span>
                                                <span className={`font-mono ${item.shap_value > 0 ? 'text-red-400' : 'text-emerald-400'}`}>
                                                    {item.shap_value > 0 ? '+' : ''}{item.shap_value.toFixed(3)}
                                                </span>
                                            </div>
                                            <div className="relative h-2 bg-white/10 rounded-full overflow-hidden">
                                                <div
                                                    className={`absolute h-full rounded-full ${item.shap_value > 0 ? 'bg-red-500' : 'bg-emerald-500'}`}
                                                    style={{
                                                        width: `${Math.min(Math.abs(item.shap_value) * 20, 100)}%`, // Scaling factor for visual
                                                        left: item.shap_value > 0 ? '50%' : `calc(50% - ${Math.min(Math.abs(item.shap_value) * 20, 100)}%)`
                                                    }}
                                                />
                                                <div className="absolute left-1/2 top-0 h-full w-0.5 bg-white/20" /> {/* Center line */}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="h-40 flex items-center justify-center text-muted-foreground">
                                No explanation available
                            </div>
                        )}
                    </GlassCard>

                    {/* RAG Remediation */}
                    <GlassCard className="border-t-4 border-t-brand-accent">
                        <div className="flex items-center gap-3 mb-6">
                            <BookOpen className="w-6 h-6 text-brand-accent" />
                            <h2 className="font-semibold text-lg">AI Remediation Guide (RAG)</h2>
                        </div>

                        {aiAdvice ? (
                            <div className="space-y-6">
                                {/* AI Generated Advice */}
                                <div className="p-4 rounded-lg bg-brand-accent/5 border border-brand-accent/10">
                                    <div className="flex items-center gap-2 mb-3 text-brand-accent">
                                        <BrainCircuit className="w-5 h-5" />
                                        <h3 className="font-semibold">Gemini Security Analysis</h3>
                                    </div>
                                    <div className="text-neutral-200 text-sm leading-relaxed whitespace-pre-wrap">
                                        {aiAdvice.advice}
                                    </div>
                                </div>

                                {/* Citations */}
                                <div>
                                    <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">References & Policies</h4>
                                    <div className="space-y-3">
                                        {aiAdvice.sources.map((result, idx) => (
                                            <div key={idx} className="p-3 rounded bg-white/5 border-l-2 border-brand-primary transition-colors hover:bg-white/10">
                                                <div className="flex items-center justify-between mb-1">
                                                    <span className="text-xs font-bold text-brand-primary">
                                                        {result.source}
                                                    </span>
                                                    <span className="text-xs text-muted-foreground">Match: {(result.score * 100).toFixed(0)}%</span>
                                                </div>
                                                <p className="text-xs text-neutral-400 line-clamp-2">
                                                    {result.content}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Auto-Fix Actions */}
                                {!fixScript ? (
                                    <button
                                        onClick={handleGenerateFix}
                                        disabled={generatingFix}
                                        className="w-full py-3 rounded-lg border border-brand-accent/20 bg-brand-accent/10 text-brand-accent hover:bg-brand-accent/20 transition-all font-medium flex items-center justify-center gap-2 group"
                                    >
                                        {generatingFix ? (
                                            <>
                                                <Activity className="w-5 h-5 animate-spin" />
                                                Generating Script...
                                            </>
                                        ) : (
                                            <>
                                                <Terminal className="w-5 h-5 group-hover:scale-110 transition-transform" />
                                                Generate Auto-Fix Script (Azure CLI)
                                            </>
                                        )}
                                    </button>
                                ) : (
                                    <div className="rounded-lg border border-white/10 bg-[#0d1117] overflow-hidden">
                                        <div className="flex items-center justify-between px-4 py-2 bg-white/5 border-b border-white/5">
                                            <span className="text-xs font-mono text-muted-foreground flex items-center gap-2">
                                                <Terminal className="w-4 h-4" />
                                                remediation.sh
                                            </span>
                                            <button
                                                onClick={copyToClipboard}
                                                className="p-1.5 hover:bg-white/10 rounded-md transition-colors text-muted-foreground hover:text-white"
                                            >
                                                {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-4 h-4" />}
                                            </button>
                                        </div>
                                        <div className="p-4 overflow-x-auto text-sm font-mono leading-relaxed">
                                            <pre className="text-emerald-400">
                                                {fixScript.script}
                                            </pre>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="text-center py-8 text-muted-foreground">
                                No remediation advice available for this incident.
                            </div>
                        )}
                    </GlassCard>
                </div>
            </div>
        </div>
    );
}
