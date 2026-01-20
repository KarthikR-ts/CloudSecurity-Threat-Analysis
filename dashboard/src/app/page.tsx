"use client";

import { ShieldCheck, BrainCircuit, Building2, ChevronRight, Activity } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";
import { PageTransition } from "@/components/layout/PageTransition";
import { motion } from "framer-motion";
import PixelSnow from "@/components/PixelSnow";

export default function Home() {
  const roles = [
    {
      id: "cloud-engineer",
      title: "Cloud Engineer",
      description: "Real-time thread remediations & raw logs.",
      icon: <ShieldCheck className="w-5 h-5 text-indigo-400" />,
      href: "/dashboard/cloud-engineer",
      color: "hover:border-indigo-500/50 hover:bg-indigo-500/5",
    },
    {
      id: "ml-engineer",
      title: "ML Engineer",
      description: "Model inference metrics & drift analysis.",
      icon: <BrainCircuit className="w-5 h-5 text-emerald-400" />,
      href: "/dashboard/ml-engineer",
      color: "hover:border-emerald-500/50 hover:bg-emerald-500/5",
    },
    {
      id: "executive",
      title: "Executive",
      description: "High-level risk posture & business impact.",
      icon: <Building2 className="w-5 h-5 text-amber-400" />,
      href: "/dashboard/executive",
      color: "hover:border-amber-500/50 hover:bg-amber-500/5",
    },
  ];

  return (
    <PageTransition>
      <main className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center p-6 bg-background relative overflow-hidden">
        {/* Abstract Background */}
        <div className="absolute inset-0 w-full h-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))] pointer-events-none" />

        {/* Snow Effect */}
        <div className="absolute inset-0 w-full h-full pointer-events-none z-0 opacity-40">
          <PixelSnow
            color="#ffffff"
            flakeSize={0.01}
            minFlakeSize={1.25}
            pixelResolution={200}
            speed={1.25}
            depthFade={8}
            farPlane={20}
            brightness={1}
            gamma={0.4545}
            density={0.3}
            variant="square"
            direction={125}
          />
        </div>

        <div className="z-10 text-center max-w-2xl mx-auto mb-24">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-[11px] font-medium text-zinc-400 mb-8"
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            System Operational
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-5xl md:text-7xl font-bold tracking-tight mb-8 text-white bg-clip-text text-transparent bg-gradient-to-b from-white via-white/90 to-white/70"
          >
            Cloud Sentinel
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-zinc-400 text-lg md:text-xl leading-relaxed max-w-lg mx-auto font-light"
          >
            Next-generation automated incident response & triage system.
            Select your role to access the workspace.
          </motion.p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl z-10 px-4">
          {roles.map((role, i) => (
            <motion.div
              key={role.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 + (i * 0.1) }}
            >
              <Link href={role.href} className="block h-full cursor-pointer">
                <div className={cn(
                  "h-full group flex flex-col items-start gap-4 p-6 rounded-2xl border border-zinc-800 bg-zinc-900/40 backdrop-blur-sm transition-all duration-300 hover:shadow-2xl hover:shadow-black/50 select-none",
                  role.color
                )}>
                  <div className="p-3 rounded-xl bg-zinc-900 border border-zinc-800 shadow-sm group-hover:scale-110 transition-transform duration-300">
                    {role.icon}
                  </div>

                  <div className="mt-2">
                    <h3 className="text-lg font-semibold text-zinc-100 mb-2 group-hover:text-white transition-colors">
                      {role.title}
                    </h3>
                    <p className="text-sm text-zinc-500 leading-relaxed font-normal">
                      {role.description}
                    </p>
                  </div>

                  <div className="mt-auto pt-6 w-full flex items-center justify-between text-xs font-medium text-zinc-500 group-hover:text-zinc-300 transition-colors">
                    <span>Enter Workspace</span>
                    <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        <footer className="absolute bottom-8 text-center text-xs text-zinc-600 font-mono">
          ID: CX-8492 // ENCRYPTED
        </footer>
      </main>
    </PageTransition>
  );
}
