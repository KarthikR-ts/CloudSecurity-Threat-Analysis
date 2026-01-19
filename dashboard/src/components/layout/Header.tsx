"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Bell, Wifi, WifiOff, Shield } from "lucide-react";
import { RoleSwitcher } from "./RoleSwitcher";
import { useSSE } from "@/hooks/useSSE";

export function Header() {
    const pathname = usePathname();
    const { isConnected, stats } = useSSE();

    // Simple breadcrumb logic
    const segments = pathname?.split("/").filter(Boolean) || [];
    const title = segments[segments.length - 1] || "Dashboard";

    return (
        <header className="h-16 border-b border-white/10 bg-gray-900/80 backdrop-blur-xl sticky top-0 z-40 flex items-center justify-between px-8">
            <div className="flex items-center gap-6">
                <Link href="/" className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-900/30">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                </Link>
                <h2 className="text-xl font-bold tracking-tight text-white">
                    {title.replace("-", " ")}
                </h2>

                <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold border ${isConnected
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    : "bg-red-500/10 text-red-400 border-red-500/20"
                    }`}>
                    {isConnected ? (
                        <>
                            <Wifi className="w-3 h-3" />
                            <span>LIVE</span>
                            {stats && <span className="text-emerald-300">• {stats.total_alerts} alerts</span>}
                        </>
                    ) : (
                        <>
                            <WifiOff className="w-3 h-3" />
                            <span>OFFLINE</span>
                        </>
                    )}
                </div>
            </div>

            <div className="flex items-center gap-4">
                <RoleSwitcher />

                <div className="flex items-center gap-3 pl-4 border-l border-white/10">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-white">Aurora CSPM</p>
                        <p className="text-xs text-gray-400">Demo Mode</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                        <span className="text-white font-medium text-sm">AC</span>
                    </div>
                </div>
            </div>
        </header>
    );
}

