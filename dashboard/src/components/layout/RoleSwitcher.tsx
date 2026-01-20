"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useRoleStore, ROLES, UserRole } from "@/stores/roleStore";
import { Terminal, Briefcase, Brain, ChevronDown, Check } from "lucide-react";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";

const ROLE_ICONS = {
    CLOUD_ENGINEER: Terminal,
    NON_TECHNICAL: Briefcase,
    ML_ENGINEER: Brain
};

const ROLE_ROUTES = {
    CLOUD_ENGINEER: "/dashboard/cloud-engineer",
    NON_TECHNICAL: "/dashboard/executive",
    ML_ENGINEER: "/dashboard/ml-engineer"
};

export function RoleSwitcher() {
    const [isOpen, setIsOpen] = useState(false);
    const router = useRouter();
    const { currentRole, setRole } = useRoleStore();
    const currentInfo = ROLES[currentRole];
    const CurrentIcon = ROLE_ICONS[currentRole];

    const handleRoleChange = (roleId: UserRole) => {
        setRole(roleId);
        setIsOpen(false);
        router.push(ROLE_ROUTES[roleId]);
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    "flex items-center gap-2.5 px-3 py-2 rounded-lg transition-all duration-200",
                    "bg-zinc-900 border border-zinc-800 hover:border-zinc-700 hover:bg-zinc-800/80",
                    "text-sm text-zinc-300"
                )}
            >
                <CurrentIcon className="w-4 h-4 text-zinc-400" />
                <span className="hidden md:block font-medium">{currentInfo.label}</span>
                <ChevronDown className={cn("w-3 h-3 text-zinc-500 transition-transform duration-200", isOpen && "rotate-180")} />
            </button>

            <AnimatePresence>
                {isOpen && (
                    <>
                        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
                        <motion.div
                            initial={{ opacity: 0, y: 8, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            exit={{ opacity: 0, y: 8, scale: 0.95 }}
                            transition={{ duration: 0.15, ease: "easeOut" }}
                            className="absolute right-0 top-full mt-2 w-64 z-50 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl overflow-hidden"
                        >
                            <div className="p-1">
                                {(Object.keys(ROLES) as UserRole[]).map((roleId) => {
                                    const role = ROLES[roleId];
                                    const Icon = ROLE_ICONS[roleId];
                                    const isActive = currentRole === roleId;

                                    return (
                                        <button
                                            key={roleId}
                                            onClick={() => handleRoleChange(roleId)}
                                            className={cn(
                                                "w-full flex items-center gap-3 p-2 rounded-md transition-colors text-left",
                                                isActive ? "bg-zinc-800 text-zinc-100" : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
                                            )}
                                        >
                                            <Icon className={cn("w-4 h-4", isActive ? "text-zinc-100" : "text-zinc-500")} />
                                            <div className="flex-1">
                                                <div className="text-sm font-medium">{role.label}</div>
                                            </div>
                                            {isActive && <Check className="w-3.5 h-3.5" />}
                                        </button>
                                    );
                                })}
                            </div>
                        </motion.div>
                    </>
                )}
            </AnimatePresence>
        </div>
    );
}
