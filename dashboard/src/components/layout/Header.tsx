"use client";

import { usePathname } from "next/navigation";
import { Bell, Search } from "lucide-react";

export function Header() {
    const pathname = usePathname();
    // Simple breadcrumb logic
    const segments = pathname?.split("/").filter(Boolean) || [];
    const title = segments[segments.length - 1] || "Dashboard";

    return (
        <header className="h-16 border-b border-gray-200 bg-white sticky top-0 z-40 flex items-center justify-between px-8 ml-64">
            <div className="flex items-center gap-4">
                <h2 className="text-xl font-semibold capitalize tracking-tight text-gray-800">
                    {title.replace("-", " ")}
                </h2>
            </div>

            <div className="flex items-center gap-6">
                <button className="p-2 rounded-full hover:bg-gray-100 transition-colors">
                    <Bell className="w-5 h-5 text-gray-500" />
                </button>

                <div className="flex items-center gap-3 pl-6 border-l border-gray-200">
                    <div className="text-right hidden sm:block">
                        <p className="text-sm font-medium text-gray-900">Admin User</p>
                        <p className="text-xs text-gray-500">Administrator</p>
                    </div>
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-gray-600 font-medium">AD</span>
                    </div>
                </div>
            </div>
        </header>
    );
}
