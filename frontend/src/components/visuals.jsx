export function CinematicDebugArt() {
  return (
    <div className="relative min-h-[420px] overflow-hidden rounded-[2rem] border-2 border-[#173f90] bg-[linear-gradient(180deg,#2d63bf_0%,#2554af_100%)] shadow-[0_26px_0_rgba(22,61,136,0.55),0_36px_80px_rgba(18,45,98,0.24)]">
      <div className="absolute inset-0 opacity-20" style={{ backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='180' height='180' viewBox='0 0 180 180'%3E%3Cg fill='none' stroke='%23163f93' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='34' cy='34' r='10'/%3E%3Cpath d='M18 72c12-8 24-8 36 0'/%3E%3Cpath d='M118 28h20v20h-20z'/%3E%3Cpath d='M126 78l10-14 10 14'/%3E%3Cpath d='M28 132l14-14 14 14-14 14z'/%3E%3Cpath d='M108 126c0-10 8-18 18-18s18 8 18 18'/%3E%3C/g%3E%3C/svg%3E\")", backgroundSize: "180px 180px" }} />
      <div className="absolute inset-x-0 bottom-0 h-24 bg-[#214b9f]/70" />

      <div className="absolute left-[10%] top-[14%] w-[34%] min-w-[180px] rounded-[1.2rem] border-2 border-[#153b84] bg-[#2b5bb6]/95 p-4 shadow-[0_10px_0_rgba(20,61,136,0.45)]">
        <div className="mb-3 flex items-center gap-2">
          <span className="h-2.5 w-2.5 rounded-full bg-signal-red" />
          <span className="h-2.5 w-2.5 rounded-full bg-warning-yellow" />
          <span className="h-2.5 w-2.5 rounded-full bg-neon-lime" />
        </div>
        <div className="space-y-2 font-mono text-sm text-white/90">
          <div><span className="text-white/45">01</span> for (i = 0; i &lt;= lobby.size(); i++)</div>
          <div className="text-warning-yellow"><span className="text-white/45">02</span> winner = lobby[i];</div>
          <div><span className="text-white/45">03</span> // fix it fast</div>
        </div>
      </div>

      <div className="absolute right-[10%] top-[13%] flex gap-3">
        <Badge color="bg-signal-red" />
        <Badge color="bg-warning-yellow" />
        <Badge color="bg-neon-lime" />
        <Badge color="bg-electric-blue" />
      </div>

      <div className="absolute left-1/2 top-[53%] h-[210px] w-[210px] -translate-x-1/2 -translate-y-1/2 rounded-full border-[10px] border-[#0f2357] bg-[#4866ff] shadow-[0_0_0_10px_rgba(28,57,134,0.25)]">
        <div className="absolute left-[27%] top-[28%] h-5 w-5 rounded-full bg-[#0f2357]" />
        <div className="absolute right-[27%] top-[28%] h-5 w-5 rounded-full bg-[#0f2357]" />
        <div className="absolute left-[28%] top-[50%] h-3 w-[44%] rounded-full bg-[#0f2357]" />
        <div className="absolute left-[20%] top-[18%] h-10 w-10 -rotate-12 border-b-[8px] border-l-[8px] border-[#0f2357]" />
        <div className="absolute right-[20%] top-[18%] h-10 w-10 rotate-12 border-b-[8px] border-r-[8px] border-[#0f2357]" />
      </div>

      <div className="absolute left-[20%] top-[42%] flex flex-col gap-4">
        <ArrowToken>{"<"}</ArrowToken>
        <ArrowToken>{"<"}</ArrowToken>
        <ArrowToken>{"<"}</ArrowToken>
      </div>
      <div className="absolute right-[20%] top-[42%] flex flex-col gap-4">
        <ArrowToken>{">"}</ArrowToken>
        <ArrowToken>{">"}</ArrowToken>
        <ArrowToken>{">"}</ArrowToken>
      </div>

      <div className="absolute bottom-[14%] left-1/2 flex -translate-x-1/2 gap-3">
        <MiniBlock tone="blue" />
        <MiniBlock tone="lime" />
        <MiniBlock tone="yellow" />
        <MiniBlock tone="red" />
      </div>
    </div>
  );
}

function Badge({ color }) {
  return <div className={`h-5 w-5 rounded-[4px] border-2 border-[#183f8a] ${color}`} />;
}

function ArrowToken({ children }) {
  return (
    <div className="font-mono text-4xl font-bold text-[#0f2357] drop-shadow-[2px_2px_0_rgba(255,255,255,0.15)]">
      {children}
    </div>
  );
}

function MiniBlock({ tone }) {
  const tones = {
    blue: "bg-electric-blue",
    lime: "bg-neon-lime",
    yellow: "bg-warning-yellow",
    red: "bg-signal-red"
  };

  return <div className={`h-5 w-5 rounded-[4px] border-2 border-[#173f90] ${tones[tone]}`} />;
}

export function OrbitDecor() {
  return (
    <>
      <div className="pointer-events-none absolute right-[9%] top-24 hidden font-display text-6xl text-white/8 lg:block">
        *
      </div>
      <div className="pointer-events-none absolute bottom-20 left-[6%] hidden h-16 w-16 rotate-12 border border-plasma-violet/40 bg-plasma-violet/10 lg:block" />
    </>
  );
}
