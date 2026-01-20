"use client";

import { useState } from "react";
import { Play, Download, Settings, Loader2, Sparkles, Terminal } from "lucide-react";
import { useSimulationStore } from "@/lib/store";
import { api } from "@/lib/api";

export function DashboardToolbar() {
    const { startSimulation, isSimulating } = useSimulationStore();
    const [isScanning, setIsScanning] = useState(false);

    const handleRunSimulation = () => {
        startSimulation(() => api.runSimulation());
    };

    const handleScan = () => {
        setIsScanning(true);
        // Simulate scan duration
        setTimeout(() => {
            setIsScanning(false);
        }, 3000);
    };

    return (
        <div className="flex items-center justify-center mb-8 p-4 bg-white/5 border border-white/10 rounded-xl shadow-xl backdrop-blur-md">
            <button
                onClick={handleRunSimulation}
                disabled={isSimulating}
                className="flex items-center gap-3 px-8 py-3 text-base font-bold text-white bg-gradient-to-r from-brand-primary via-brand-secondary to-brand-primary bg-[length:200%_auto] animate-gradient-x rounded-xl hover:scale-105 transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)] disabled:opacity-50"
            >
                {isSimulating ? <Loader2 className="w-5 h-5 animate-spin" /> : <Sparkles className="w-5 h-5" />}
                {isSimulating ? "AI Simulation in Progress..." : "Run Threat Simulation"}
            </button>
        </div>
    );
}
