"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { Wifi, WifiOff, Shield, Bell } from "lucide-react";
import { RoleSwitcher } from "./RoleSwitcher";
import { useSSE } from "@/hooks/useSSE";
import { cn } from "@/lib/utils";

export function Header() {
    const pathname = usePathname();
    const { isConnected, stats } = useSSE();

    // Simple breadcrumb logic
    const segments = pathname?.split("/").filter(Boolean) || [];
    const title = segments[segments.length - 1] || "Dashboard";

    return (
        <header className="h-16 border-b border-zinc-800 bg-black/50 backdrop-blur-xl sticky top-0 z-50 flex items-center justify-between px-6 transition-all duration-200">
            <div className="flex items-center gap-6">
                <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                    <div className="h-8 w-8 rounded-lg bg-zinc-100 flex items-center justify-center shadow-lg shadow-zinc-500/10">
                        <Shield className="w-4 h-4 text-zinc-900" strokeWidth={2.5} />
                    </div>
                    <span className="font-bold tracking-tight text-zinc-100 hidden md:block">
                        Cloud Sentinel
                    </span>
                </Link>

                <div className="h-4 w-[1px] bg-zinc-800 hidden md:block" />

                <h2 className="text-sm font-medium text-zinc-400 capitalize hidden md:block">
                    {title.replace(/-/g, " ")}
                </h2>

                <div className={cn(
                    "flex items-center gap-2 px-2.5 py-0.5 rounded-full text-[10px] font-semibold border uppercase tracking-wider shadow-sm",
                    isConnected
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : "bg-red-500/10 text-red-500 border-red-500/20"
                )}>
                    {isConnected ? (
                        <>
                            <div className="relative flex h-1.5 w-1.5">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-1.5 w-1.5 bg-emerald-500"></span>
                            </div>
                            <span>LIVE</span>
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

                <button className="relative p-2 text-zinc-400 hover:text-zinc-100 transition-colors hover:bg-zinc-800/50 rounded-lg">
                    <Bell className="w-4 h-4" />
                    <span className="absolute top-2.5 right-2.5 w-1.5 h-1.5 bg-red-500 rounded-full border border-zinc-950" />
                </button>

                <div className="flex items-center gap-3 pl-4 border-l border-zinc-800">
                    <div className="text-right hidden sm:block">
                        <p className="text-xs font-semibold text-zinc-200">Aurora CSPM</p>
                        <p className="text-[10px] text-zinc-500 font-medium">Pro Plan</p>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center hover:border-zinc-500 transition-colors cursor-pointer group">
                        <span className="text-xs font-semibold text-zinc-300 group-hover:text-white">AC</span>
                    </div>
                </div>
            </div>
        </header>
    );
}

