"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import {
    Terminal,
    Briefcase,
    Brain,
    AlertTriangle,
    Settings,
    Shield,
    Sparkles,
    LayoutGrid
} from "lucide-react";

const roleItems = [
    { href: "/dashboard/cloud-engineer", label: "Cloud Engineer", icon: Terminal, color: "text-indigo-400" },
    { href: "/dashboard/executive", label: "Executive", icon: Briefcase, color: "text-amber-400" },
    { href: "/dashboard/ml-engineer", label: "ML Engineer", icon: Brain, color: "text-emerald-400" },
];

const navItems = [
    // { href: "/dashboard/enterprise", label: "Overview", icon: LayoutDashboard }, // Removed as per request
    { href: "/dashboard/incidents", label: "Incidents", icon: AlertTriangle },
    { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 h-screen fixed left-0 top-0 bg-black/95 border-r border-zinc-800 flex flex-col z-50">
            {/* Logo */}
            <div className="p-6 border-b border-zinc-800">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="h-8 w-8 rounded-lg bg-zinc-100 flex items-center justify-center shadow-lg shadow-zinc-500/10 transition-transform group-hover:scale-105">
                        <Shield className="w-4 h-4 text-black fill-current" />
                    </div>
                    <div>
                        <span className="font-bold text-sm tracking-tight text-zinc-100">Aurora</span>
                        <span className="text-[10px] block text-zinc-500 font-mono">CSPM Platform</span>
                    </div>
                </Link>
            </div>

            {/* Role Dashboards */}
            <div className="p-4">
                <div className="flex items-center gap-2 px-3 mb-2">
                    <Sparkles className="w-3 h-3 text-zinc-600" />
                    <span className="text-[10px] font-semibold text-zinc-600 uppercase tracking-widest">Dashboards</span>
                </div>
                <nav className="space-y-0.5">
                    {roleItems.map((item) => {
                        const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200 font-medium text-sm border border-transparent",
                                    isActive
                                        ? "bg-zinc-900 text-zinc-100 border-zinc-800"
                                        : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50"
                                )}
                            >
                                <item.icon className={cn("w-4 h-4", isActive ? item.color : "text-zinc-500")} />
                                <span>{item.label}</span>
                                {isActive && (
                                    <div className="ml-auto w-1 h-1 rounded-full bg-current animate-pulse opacity-50" />
                                )}
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* General Navigation */}
            <div className="p-4 mt-2">
                <span className="text-[10px] font-semibold text-zinc-600 uppercase tracking-widest px-3">General</span>
                <nav className="mt-2 space-y-0.5">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200 font-medium text-sm border border-transparent",
                                    isActive
                                        ? "bg-zinc-900 text-zinc-100 border-zinc-800"
                                        : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/50"
                                )}
                            >
                                <item.icon className="w-4 h-4 text-zinc-500" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* Status Footer */}
            <div className="mt-auto p-4 border-t border-zinc-800">
                <div className="px-3 py-2 rounded-md bg-zinc-900/50 border border-zinc-800">
                    <div className="flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[10px] font-medium text-zinc-400">System Online</span>
                    </div>
                    <div className="mt-1 text-[10px] text-zinc-600 font-mono">
                        v2.4.0-stable
                    </div>
                </div>
            </div>
        </aside>
    );
}

