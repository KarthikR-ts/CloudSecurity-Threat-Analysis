"use client";

import { usePathname } from "next/navigation";
import Link from "next/link";
import { cn } from "@/lib/utils";
import {
    LayoutDashboard,
    AlertTriangle,
    FileText,
    Settings,
    Shield,
    LogOut
} from "lucide-react";

const navItems = [
    { href: "/dashboard/enterprise", label: "Overview", icon: LayoutDashboard },
    { href: "/dashboard/incidents", label: "Incidents", icon: AlertTriangle },
    { href: "/dashboard/policies", label: "Policies", icon: FileText },
    { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 h-screen fixed left-0 top-0 bg-slate-900 border-r border-slate-800 flex flex-col z-50 transition-all duration-300 ease-in-out">
            <div className="p-6 border-b border-slate-800">
                <Link href="/" className="flex items-center gap-3 group">
                    <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-900/20">
                        <Shield className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-lg tracking-tight text-white">Sentinel</span>
                </Link>
            </div>

            <nav className="flex-1 p-4 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href || pathname?.startsWith(item.href + "/");
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-4 py-3 rounded-md transition-all duration-200 font-medium text-sm",
                                isActive
                                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-900/10"
                                    : "text-slate-400 hover:text-white hover:bg-slate-800"
                            )}
                        >
                            <item.icon className={cn("w-5 h-5", isActive ? "text-white" : "text-slate-400 group-hover:text-white")} />
                            <span>{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-slate-800">
                <Link
                    href="/"
                    className="flex items-center gap-3 px-4 py-3 rounded-md text-slate-400 hover:bg-slate-800 hover:text-white transition-colors"
                >
                    <LogOut className="w-5 h-5" />
                    <span className="font-medium text-sm">Switch Role</span>
                </Link>
            </div>
        </aside>
    );
}
