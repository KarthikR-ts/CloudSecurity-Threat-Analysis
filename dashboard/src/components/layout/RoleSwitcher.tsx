"use client";

/**
 * Role Switcher Component
 * Allows switching between Cloud Engineer, Executive, and ML Engineer views
 */

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useRoleStore, ROLES, UserRole } from "@/stores/roleStore";
import { Terminal, Briefcase, Brain, ChevronDown, Check } from "lucide-react";

const ROLE_ICONS = {
    CLOUD_ENGINEER: Terminal,
    NON_TECHNICAL: Briefcase,
    ML_ENGINEER: Brain
};

const ROLE_COLORS = {
    CLOUD_ENGINEER: "from-blue-500 to-cyan-500",
    NON_TECHNICAL: "from-purple-500 to-pink-500",
    ML_ENGINEER: "from-green-500 to-emerald-500"
};

const ROLE_ROUTES = {
    CLOUD_ENGINEER: "/dashboard/cloud-engineer",
    NON_TECHNICAL: "/dashboard/executive",
    ML_ENGINEER: "/dashboard/ml-engineer"
};

export function RoleSwitcher() {
    const [isOpen, setIsOpen] = useState(false);
    const router = useRouter();
    const pathname = usePathname();
    const { currentRole, setRole } = useRoleStore();
    const currentInfo = ROLES[currentRole];
    const CurrentIcon = ROLE_ICONS[currentRole];

    const handleRoleChange = (roleId: UserRole) => {
        setRole(roleId);
        setIsOpen(false);
        // Navigate immediately to the role's dashboard
        router.push(ROLE_ROUTES[roleId]);
    };

    return (
        <div className="relative">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`
                    flex items-center gap-3 px-4 py-2.5 rounded-xl
                    bg-gradient-to-r ${ROLE_COLORS[currentRole]}
                    text-white font-medium text-sm
                    shadow-lg shadow-${currentInfo.color}-500/25
                    hover:shadow-xl hover:scale-[1.02]
                    transition-all duration-200
                `}
            >
                <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center">
                    <CurrentIcon className="w-4 h-4" />
                </div>
                <div className="text-left hidden md:block">
                    <div className="font-semibold">{currentInfo.label}</div>
                    <div className="text-xs text-white/70">{currentInfo.description}</div>
                </div>
                <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen && (
                <>
                    <div
                        className="fixed inset-0 z-40"
                        onClick={() => setIsOpen(false)}
                    />
                    <div className="absolute right-0 top-full mt-2 w-72 z-50 
                        bg-gray-900/95 backdrop-blur-xl rounded-xl 
                        border border-white/10 shadow-2xl
                        animate-in fade-in slide-in-from-top-2 duration-200">
                        <div className="p-2">
                            {(Object.keys(ROLES) as UserRole[]).map((roleId) => {
                                const role = ROLES[roleId];
                                const Icon = ROLE_ICONS[roleId];
                                const isActive = currentRole === roleId;

                                return (
                                    <button
                                        key={roleId}
                                        onClick={() => handleRoleChange(roleId)}
                                        className={`
                                            w-full flex items-center gap-3 p-3 rounded-lg
                                            transition-all duration-150
                                            ${isActive
                                                ? `bg-gradient-to-r ${ROLE_COLORS[roleId]} text-white`
                                                : "hover:bg-white/5 text-gray-300"
                                            }
                                        `}
                                    >
                                        <div className={`
                                            w-10 h-10 rounded-lg flex items-center justify-center
                                            ${isActive ? "bg-white/20" : "bg-white/5"}
                                        `}>
                                            <Icon className="w-5 h-5" />
                                        </div>
                                        <div className="flex-1 text-left">
                                            <div className="font-medium">{role.label}</div>
                                            <div className={`text-xs ${isActive ? "text-white/70" : "text-gray-500"}`}>
                                                {role.description}
                                            </div>
                                        </div>
                                        {isActive && (
                                            <Check className="w-5 h-5 text-white" />
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                        <div className="border-t border-white/10 p-3">
                            <p className="text-xs text-gray-500 text-center">
                                Switch roles to see different perspectives of the same alerts
                            </p>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
