/**
 * Role Store - Zustand state management for user roles
 * Aurora CSPM Platform
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type UserRole = 'CLOUD_ENGINEER' | 'NON_TECHNICAL' | 'ML_ENGINEER';

export interface RoleInfo {
    id: UserRole;
    label: string;
    description: string;
    icon: string;
    color: string;
}

export const ROLES: Record<UserRole, RoleInfo> = {
    CLOUD_ENGINEER: {
        id: 'CLOUD_ENGINEER',
        label: 'Cloud Engineer',
        description: 'Technical remediation & threat prioritization',
        icon: 'Terminal',
        color: 'blue'
    },
    NON_TECHNICAL: {
        id: 'NON_TECHNICAL',
        label: 'Executive',
        description: 'Business risk & plain-language actions',
        icon: 'Briefcase',
        color: 'purple'
    },
    ML_ENGINEER: {
        id: 'ML_ENGINEER',
        label: 'ML Engineer',
        description: 'Model performance & explainability',
        icon: 'Brain',
        color: 'green'
    }
};

interface RoleState {
    currentRole: UserRole;
    setRole: (role: UserRole) => void;
    getRoleInfo: () => RoleInfo;
}

export const useRoleStore = create<RoleState>()(
    persist(
        (set, get) => ({
            currentRole: 'CLOUD_ENGINEER',

            setRole: (role: UserRole) => set({ currentRole: role }),

            getRoleInfo: () => ROLES[get().currentRole]
        }),
        {
            name: 'aurora-cspm-role'
        }
    )
);
