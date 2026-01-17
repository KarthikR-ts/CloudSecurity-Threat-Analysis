import { GlassCard } from "@/components/ui/GlassCard";
import { ShieldCheck, BrainCircuit, Building2, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const roles = [
    {
      id: "enterprise",
      title: "Enterprise Security",
      description: "SOC Analyst view for real-time triage and remediation.",
      icon: <ShieldCheck className="w-10 h-10 text-brand-primary" />,
      href: "/dashboard/enterprise",
      gradient: "from-brand-primary/20 to-transparent",
    },
    {
      id: "researcher",
      title: "ML Researcher",
      description: "Deep dive into model inference, feature importance, and drift.",
      icon: <BrainCircuit className="w-10 h-10 text-brand-secondary" />,
      href: "/dashboard/researcher",
      gradient: "from-brand-secondary/20 to-transparent",
    },
    {
      id: "vendor",
      title: "Platform Vendor",
      description: "Manage compliance policies and drift detection rules.",
      icon: <Building2 className="w-10 h-10 text-brand-accent" />,
      href: "/dashboard/vendor",
      gradient: "from-brand-accent/20 to-transparent",
    },
  ];

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-brand-primary/10 via-background to-background">
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[20%] w-[500px] h-[500px] bg-brand-primary/5 rounded-full blur-[100px]" />
        <div className="absolute bottom-[-10%] right-[20%] w-[500px] h-[500px] bg-brand-secondary/5 rounded-full blur-[100px]" />
      </div>

      <div className="z-10 text-center max-w-2xl mx-auto mb-16 animate-fade-in-up">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-brand-primary mb-6">
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-brand-primary"></span>
          </span>
          System Operational
        </div>
        <h1 className="text-5xl font-bold tracking-tight mb-4 text-glow">
          Cloud Sentinel
        </h1>
        <p className="text-muted-foreground text-lg">
          AI-Driven Cloud Incident Response & Triage System. <br />
          Select your operational role to begin.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 z-10 w-full max-w-5xl animate-fade-in-up" style={{ animationDelay: "0.2s" }}>
        {roles.map((role) => (
          <Link key={role.id} href={role.href} className="group">
            <GlassCard className="h-full flex flex-col items-start gap-4 hover:-translate-y-1 transition-transform duration-300">
              <div className={`p-3 rounded-xl bg-gradient-to-br ${role.gradient} border border-white/5`}>
                {role.icon}
              </div>
              <div>
                <h3 className="text-xl font-semibold mb-2 group-hover:text-white transition-colors">
                  {role.title}
                </h3>
                <p className="text-sm text-neutral-400 leading-relaxed">
                  {role.description}
                </p>
              </div>
              <div className="mt-auto pt-4 flex items-center text-sm font-medium text-muted-foreground group-hover:text-white transition-colors">
                Launch Dashboard <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
              </div>
            </GlassCard>
          </Link>
        ))}
      </div>
    </main>
  );
}
