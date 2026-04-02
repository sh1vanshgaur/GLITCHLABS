export function NavLink({ children }) {
  return (
    <a
      className="text-[0.72rem] uppercase tracking-[0.24em] text-white/80 transition hover:text-white"
      href="#"
    >
      {children}
    </a>
  );
}

export function AccentTag({ children, tone = "blue" }) {
  const tones = {
    blue: "border-[#1b4699] bg-[#2b6fdd] text-white",
    lime: "border-[#468e1c] bg-[#5dd92a] text-[#113400]",
    red: "border-[#a83d3d] bg-[#ff6b6b] text-white",
    yellow: "border-[#997c1c] bg-[#ffd84d] text-[#503b00]",
    violet: "border-[#5a46a8] bg-[#8e63ff] text-white"
  };

  return (
    <span
      className={`inline-flex items-center rounded-[999px] border-2 px-3 py-1 text-[0.65rem] font-semibold uppercase tracking-[0.18em] shadow-[0_3px_0_rgba(0,0,0,0.12)] ${tones[tone]}`}
    >
      {children}
    </span>
  );
}

export function Panel({ children, className = "" }) {
  return <section className={`panel-shell ${className}`}>{children}</section>;
}

export function SectionTitle({ eyebrow, title, aside }) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
      <div className="max-w-xl">
        <p className="font-mono text-[0.68rem] uppercase tracking-[0.28em] text-white/70">
          {eyebrow}
        </p>
        <h2 className="mt-3 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
          {title}
        </h2>
      </div>
      {aside}
    </div>
  );
}

export function ActionButton({ children, kind = "primary", ...props }) {
  const styles = {
    primary:
      "border-[#46bb1e] bg-[#52e52a] text-[#123100] shadow-[0_5px_0_rgba(43,128,16,0.65)] hover:-translate-y-0.5",
    ghost:
      "border-[#1b4699] bg-[#3b8fe8] text-white shadow-[0_5px_0_rgba(20,67,150,0.6)] hover:-translate-y-0.5"
  };

  return (
    <button
      className={`rounded-[0.8rem] border-2 px-5 py-3 text-sm font-semibold transition duration-200 ${styles[kind]}`}
      {...props}
    >
      {children}
    </button>
  );
}

export function DataChip({ label, value, tone = "blue" }) {
  const tones = {
    blue: "from-[#3d7fe8] to-[#2c63bf] text-white",
    lime: "from-[#69dd34] to-[#4ebe21] text-[#123100]",
    red: "from-[#ff7c74] to-[#ef5454] text-white",
    yellow: "from-[#ffdf6a] to-[#efc43d] text-[#573f00]"
  };

  return (
    <div className={`rounded-[1rem] border-2 border-[#1a4596] bg-gradient-to-br p-4 shadow-[0_5px_0_rgba(24,67,147,0.35)] ${tones[tone]}`}>
      <p className="font-mono text-[0.62rem] uppercase tracking-[0.2em] text-white/80">{label}</p>
      <p className="mt-2 text-lg font-semibold">{value}</p>
    </div>
  );
}

export function VoteButton({ active, children, tone = "blue", ...props }) {
  const tones = {
    blue: active
      ? "border-[#1b4699] bg-[#56a8ff] text-white"
      : "border-[#1b4699] bg-[#2b63bf] text-white/85 hover:bg-[#3b78df]",
    lime: active
      ? "border-[#468e1c] bg-[#78ef3a] text-[#103100]"
      : "border-[#2d6b14] bg-[#469820] text-white hover:bg-[#58b92a]",
    yellow: active
      ? "border-[#9c7c1f] bg-[#ffd84d] text-[#573f00]"
      : "border-[#8a6d19] bg-[#d9b93b] text-white hover:bg-[#ecc84a]"
  };

  return (
    <button
      className={`rounded-[0.8rem] border-2 px-4 py-2 text-sm font-semibold transition shadow-[0_4px_0_rgba(0,0,0,0.12)] ${tones[tone]}`}
      {...props}
    >
      {children}
    </button>
  );
}
