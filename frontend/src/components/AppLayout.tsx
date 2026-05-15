import { Search, Bell, CircleUser } from "lucide-react";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Input } from "@/components/ui/input";

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-background">
        <AppSidebar />

        <div className="flex flex-1 flex-col">
          <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-xl">
            <SidebarTrigger />
            <div className="hidden h-5 w-px bg-border md:block" />

            <div className="relative flex-1 max-w-xl">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Rechercher une entité, un client, un topic…"
                className="h-9 pl-9 bg-muted/50 border-border/60 font-mono text-xs placeholder:text-muted-foreground/70"
              />
            </div>

            <div className="ml-auto flex items-center gap-3">
              <div className="hidden items-center gap-2 rounded-md border border-border/60 bg-muted/40 px-2.5 py-1 font-mono text-[10px] uppercase tracking-widest text-muted-foreground md:flex">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-risk-low" />
                Live
              </div>
              <button className="relative rounded-md p-2 text-muted-foreground transition hover:bg-muted hover:text-foreground">
                <Bell className="h-4 w-4" />
                <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-primary" />
              </button>
              <button className="flex items-center gap-2 rounded-md border border-border/60 bg-muted/40 px-2 py-1.5 text-xs hover:bg-muted">
                <CircleUser className="h-4 w-4 text-primary" />
                <span className="hidden sm:inline">Analyste</span>
              </button>
            </div>
          </header>

          <main className="flex-1">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}
