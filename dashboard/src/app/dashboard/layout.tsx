import { Header } from "@/components/layout/Header";
import { SimulationOverlay } from "@/components/dashboard/SimulationOverlay";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-background text-foreground bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-brand-primary/5 via-background to-background">
            <Header />
            <SimulationOverlay />
            <main className="p-8 animate-fade-in-up">
                {children}
            </main>
        </div>
    );
}

