"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    Terminal,
    Briefcase,
    Brain,
    AlertTriangle,
    FileText,
    Settings,
    Shield,
    Sparkles
} from "lucide-react";

const roleItems = [
    { href: "/dashboard/cloud-engineer", label: "Cloud Engineer", icon: Terminal, color: "text-blue-400" },
    { href: "/dashboard/executive", label: "Executive", icon: Briefcase, color: "text-purple-400" },
    { href: "/dashboard/ml-engineer", label: "ML Engineer", icon: Brain, color: "text-green-400" },
];

const navItems = [
    { href: "/dashboard/enterprise", label: "Overview", icon: LayoutDashboard },
    { href: "/dashboard/incidents", label: "Incidents", icon: AlertTriangle },
    { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 h-screen fixed left-0 top-0 bg-gradient-to-b from-slate-900 to-slate-950 border-r border-white/5 flex flex-col z-50">
            {/* Logo */}
            <div className="p-6 border-b border-white/5">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-900/30">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <span className="font-bold text-lg tracking-tight text-white">Aurora</span>
                        <span className="text-xs block text-gray-500">CSPM Platform</span>
                    </div>
                </Link>
            </div>

            {/* Role Dashboards */}
            <div className="p-4">
                <div className="flex items-center gap-2 px-3 mb-2">
                    <Sparkles className="w-3 h-3 text-amber-400" />
                    <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Role Dashboards</span>
                </div>
                <nav className="space-y-1">
                    {roleItems.map((item) => {
                        const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 font-medium text-sm",
                                    isActive
                                        ? "bg-white/10 text-white shadow-lg"
                                        : "text-slate-400 hover:text-white hover:bg-white/5"
                                )}
                            >
                                <item.icon className={cn("w-5 h-5", isActive ? item.color : "text-slate-500")} />
                                <span>{item.label}</span>
                                {isActive && (
                                    <div className="ml-auto w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                                )}
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* General Navigation */}
            <div className="p-4 border-t border-white/5">
                <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-3">General</span>
                <nav className="mt-2 space-y-1">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    "flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 font-medium text-sm",
                                    isActive
                                        ? "bg-white/10 text-white"
                                        : "text-slate-400 hover:text-white hover:bg-white/5"
                                )}
                            >
                                <item.icon className="w-4 h-4" />
                                <span>{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>
            </div>

            {/* Status Footer */}
            <div className="mt-auto p-4 border-t border-white/5">
                <div className="px-4 py-3 rounded-lg bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-xs font-medium text-green-400">System Online</span>
                    </div>
                    <div className="mt-1 text-xs text-gray-500">
                        ML Model: XGBoost v2.1
                    </div>
                </div>
            </div>
        </aside>
    );
}

