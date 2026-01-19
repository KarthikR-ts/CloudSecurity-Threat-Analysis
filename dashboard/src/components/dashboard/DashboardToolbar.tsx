"use client";

import { useState } from "react";
import { Play, Download, Settings, Loader2 } from "lucide-react";

export function DashboardToolbar() {
    const [isScanning, setIsScanning] = useState(false);

    const handleScan = () => {
        setIsScanning(true);
        // Simulate scan duration
        setTimeout(() => {
            setIsScanning(false);
        }, 3000);
    };

    return (
        <div className="flex items-center justify-between mb-8 p-4 bg-white border border-slate-200 rounded-xl shadow-sm">
            <div className="flex items-center gap-4">
                <h2 className="text-xl font-bold text-slate-900 tracking-tight">Security Overview</h2>
                <span className="h-6 w-px bg-slate-200" />
                <div className="flex flex-col">
                    <div className="flex items-center gap-2 text-sm text-slate-800 font-bold">
                        <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)] animate-pulse" />
                        System Active
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono uppercase tracking-widest mt-0.5">Last Sync: {new Date().toLocaleTimeString()}</span>
                </div>
            </div>

            <div className="flex items-center gap-3">
                <button
                    className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-all shadow-sm"
                >
                    <Settings className="w-4 h-4 text-slate-500" />
                    Configure
                </button>
                <button
                    className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 hover:text-slate-900 transition-all shadow-sm"
                >
                    <Download className="w-4 h-4 text-slate-500" />
                    Export Report
                </button>
                <button
                    onClick={handleScan}
                    disabled={isScanning}
                    className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition-all shadow-md shadow-indigo-600/20 disabled:opacity-70 disabled:shadow-none"
                >
                    {isScanning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
                    {isScanning ? "Scanning..." : "Run System Scan"}
                </button>
            </div>
        </div>
    );
}
