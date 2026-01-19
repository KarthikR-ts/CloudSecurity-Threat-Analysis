"use client";

/**
 * Demo Control Button
 * Triggers a step-by-step demonstration of alert detection, classification, and remediation
 */

import { Play, Loader2, CheckCircle2, AlertTriangle } from "lucide-react";
import { useDemoSimulation } from "@/hooks/useDemoSimulation";

const STEP_LABELS = {
    idle: "Start Demo",
    generating: "Detecting Threat...",
    classifying: "ML Classification...",
    analyzing: "RAG Analysis...",
    complete: "Demo Complete!"
};

const STEP_ICONS = {
    idle: Play,
    generating: Loader2,
    classifying: Loader2,
    analyzing: Loader2,
    complete: CheckCircle2
};

export function DemoButton() {
    const { demoState, startDemo } = useDemoSimulation();
    const Icon = STEP_ICONS[demoState.currentStep];

    return (
        <div className="flex flex-col items-center gap-2">
            <button
                onClick={startDemo}
                disabled={demoState.isRunning}
                className={`
                    flex items-center gap-3 px-6 py-3 rounded-xl font-bold text-sm
                    transition-all duration-300 shadow-lg
                    ${demoState.isRunning
                        ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white cursor-wait'
                        : demoState.currentStep === 'complete'
                            ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                            : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-2xl hover:scale-105'
                    }
                    disabled:opacity-75
                `}
            >
                <Icon className={`w-5 h-5 ${demoState.isRunning ? 'animate-spin' : ''}`} />
                <span>{STEP_LABELS[demoState.currentStep]}</span>
            </button>

            {demoState.error && (
                <div className="flex items-center gap-2 text-red-400 text-xs">
                    <AlertTriangle className="w-4 h-4" />
                    <span>{demoState.error}</span>
                </div>
            )}

            {demoState.isRunning && (
                <div className="text-xs text-gray-400 animate-pulse">
                    Watch the dashboard update in real-time...
                </div>
            )}
        </div>
    );
}
