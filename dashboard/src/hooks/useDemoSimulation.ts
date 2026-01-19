/**
 * Demo Simulation Hook
 * Triggers a single alert simulation and tracks its lifecycle
 */

import { useState } from "react";
import { api } from "@/lib/api";

export interface DemoState {
    isRunning: boolean;
    currentStep: 'idle' | 'generating' | 'classifying' | 'analyzing' | 'complete';
    newAlertId: string | null;
    error: string | null;
}

export function useDemoSimulation() {
    const [demoState, setDemoState] = useState<DemoState>({
        isRunning: false,
        currentStep: 'idle',
        newAlertId: null,
        error: null
    });

    const startDemo = async () => {
        setDemoState({
            isRunning: true,
            currentStep: 'generating',
            newAlertId: null,
            error: null
        });

        try {
            // Step 1: Generate alert (simulate detection)
            await new Promise(resolve => setTimeout(resolve, 1500));
            setDemoState(prev => ({ ...prev, currentStep: 'classifying' }));

            // Step 2: Classify with ML (simulate XGBoost prediction)
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Step 3: Trigger alert creation via API
            const response = await fetch('http://localhost:8000/api/alerts/simulate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: "DEMO: Suspicious PowerShell Execution Detected",
                    description: "Encoded PowerShell command detected on VM 'prod-web-01' executing during non-business hours.",
                    resource_type: "VM",
                    resource_name: "prod-web-01",
                    severity: "critical",
                    xgb_prediction: "TRUE_POSITIVE",
                    xgb_confidence: 0.94,
                    priority_score: 94.0,
                    mitre_techniques: ["T1059.001 - PowerShell", "T1027 - Obfuscated Files"],
                    cis_controls: ["CIS Azure 7.1 - Enable Azure Defender"],
                    azure_policies: ["Adaptive application controls should be enabled"],
                    business_impact: "Potential ransomware deployment. Could result in 72-hour business disruption.",
                    risk_category: "Compute",
                    features: {
                        encoded_command: 1,
                        execution_hour: 2,
                        is_production: 1,
                        user_is_admin: 1,
                        command_length: 2048
                    },
                    shap_values: {
                        encoded_command: 0.38,
                        execution_hour: 0.24,
                        is_production: 0.19,
                        user_is_admin: 0.13,
                        command_length: 0.06
                    }
                })
            });

            if (!response.ok) throw new Error('Failed to create demo alert');

            const result = await response.json();
            setDemoState(prev => ({
                ...prev,
                currentStep: 'analyzing',
                newAlertId: result.alert_id
            }));

            // Step 4: RAG analysis (simulate retrieval and generation)
            await new Promise(resolve => setTimeout(resolve, 2500));

            setDemoState(prev => ({
                ...prev,
                currentStep: 'complete',
                isRunning: false
            }));

            // Auto-reset after 5 seconds
            setTimeout(() => {
                setDemoState({
                    isRunning: false,
                    currentStep: 'idle',
                    newAlertId: null,
                    error: null
                });
            }, 5000);

        } catch (error) {
            setDemoState({
                isRunning: false,
                currentStep: 'idle',
                newAlertId: null,
                error: error instanceof Error ? error.message : 'Demo failed'
            });
        }
    };

    return { demoState, startDemo };
}
