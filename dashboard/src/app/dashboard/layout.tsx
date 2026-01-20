import { Header } from "@/components/layout/Header";
import { SimulationOverlay } from "@/components/dashboard/SimulationOverlay";
import { PageTransition } from "@/components/layout/PageTransition";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-black transition-colors duration-300">
            <Header />
            <SimulationOverlay />
            <main className="mx-auto max-w-7xl p-6 lg:p-12">
                <PageTransition>
                    {children}
                </PageTransition>
            </main>
        </div>
    );
}

