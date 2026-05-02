"use client";
import { useRouter } from "next/navigation";

export default function GatewayPage() {
  const router = useRouter();

  return (
    <>
      {/* Google Fonts */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@700;800&family=DM+Sans:wght@400;500;600&display=swap');

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
          font-family: 'DM Sans', sans-serif;
          background: #F7F6F2;
        }

        .gateway-root {
          min-height: 100vh;
          background-color: #F7F6F2;
          background-image:
            radial-gradient(circle at 85% 10%, rgba(220,38,38,0.07) 0%, transparent 45%),
            radial-gradient(circle at 10% 90%, rgba(15,28,77,0.07) 0%, transparent 45%),
            radial-gradient(rgba(20,35,80,0.04) 1px, transparent 1px);
          background-size: auto, auto, 40px 40px;
          position: relative;
          display: flex;
          flex-direction: column;
        }

        /* ─── HEADER ─── */
        .gw-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 20px 48px;
          background: rgba(247,246,242,0.85);
          backdrop-filter: blur(12px);
          border-bottom: 1px solid rgba(20,35,80,0.06);
          position: sticky;
          top: 0;
          z-index: 100;
        }

        .gw-logo {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        .gw-logo-icon {
          width: 44px;
          height: 44px;
          border-radius: 12px;
          background: linear-gradient(135deg, #DC2626, #B91C1C);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          box-shadow: 0 4px 14px rgba(220,38,38,0.3);
        }
        .gw-logo-text {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 800;
          font-size: 22px;
          color: #0F1C4D;
          letter-spacing: -0.5px;
        }
        .gw-logo-text span { color: #DC2626; }
        .gw-logo-sub {
          font-size: 10px;
          color: #9CA3AF;
          font-weight: 600;
          letter-spacing: 1.5px;
          text-transform: uppercase;
          margin-top: 1px;
        }

        .gw-nav {
          display: flex;
          gap: 32px;
          align-items: center;
        }
        .gw-nav a {
          font-size: 14px;
          font-weight: 600;
          color: #4B5563;
          text-decoration: none;
          transition: color 0.2s;
        }
        .gw-nav a:hover { color: #0F1C4D; }

        .status-pill {
          display: inline-flex;
          align-items: center;
          gap: 7px;
          padding: 6px 14px;
          background: #DCFCE7;
          border: 1px solid #86EFAC;
          border-radius: 40px;
          font-size: 11px;
          font-weight: 700;
          color: #15803D;
          letter-spacing: 0.5px;
        }
        .status-dot {
          width: 7px;
          height: 7px;
          border-radius: 50%;
          background: #16A34A;
          box-shadow: 0 0 0 3px rgba(22,163,74,0.2);
          animation: blink 2s infinite;
        }
        @keyframes blink {
          0%,100%{opacity:1} 50%{opacity:0.3}
        }

        /* ─── HERO ─── */
        .gw-hero {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 72px 24px 40px;
          text-align: center;
        }

        .gw-eyebrow {
          font-size: 11px;
          font-weight: 600;
          letter-spacing: 3px;
          color: #9CA3AF;
          text-transform: uppercase;
          margin-bottom: 18px;
        }

        .gw-title {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 800;
          font-size: clamp(52px, 7vw, 80px);
          line-height: 1;
          letter-spacing: -1px;
          color: #0F1C4D;
          margin-bottom: 16px;
        }
        .gw-title span { color: #DC2626; }

        .gw-subtitle {
          font-size: 16px;
          color: #6B7280;
          font-weight: 400;
          max-width: 480px;
          line-height: 1.7;
          margin-bottom: 52px;
        }

        /* ─── CARDS ─── */
        .gw-cards {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
          gap: 28px;
          width: 100%;
          max-width: 860px;
          margin-bottom: 48px;
        }

        .gw-card {
          background: #ffffff;
          border-radius: 20px;
          border: 1px solid #E5E7EB;
          overflow: hidden;
          cursor: pointer;
          transition: transform 0.25s cubic-bezier(0.4,0,0.2,1), box-shadow 0.25s cubic-bezier(0.4,0,0.2,1);
          box-shadow: 0 2px 8px rgba(15,28,77,0.04);
        }
        .gw-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 20px 40px rgba(15,28,77,0.1);
        }

        .gw-card-accent {
          height: 5px;
          width: 100%;
        }
        .gw-card-accent.red {
          background: linear-gradient(90deg, #DC2626, #EF4444);
        }
        .gw-card-accent.navy {
          background: linear-gradient(90deg, #1E3A8A, #2563EB);
        }

        .gw-card-body {
          padding: 36px 36px 32px;
        }

        .gw-card-icon {
          width: 56px;
          height: 56px;
          border-radius: 14px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 26px;
          margin-bottom: 24px;
        }
        .gw-card-icon.red { background: #FEF2F2; }
        .gw-card-icon.blue { background: #EFF6FF; }

        .gw-card-title {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 800;
          font-size: 28px;
          letter-spacing: -0.5px;
          margin-bottom: 10px;
        }
        .gw-card-title.red { color: #7F1D1D; }
        .gw-card-title.blue { color: #1E3A8A; }

        .gw-card-desc {
          font-size: 14px;
          color: #6B7280;
          line-height: 1.7;
          margin-bottom: 28px;
        }

        .gw-card-cta {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          padding: 12px 22px;
          border-radius: 10px;
          border: none;
          cursor: pointer;
          font-weight: 700;
          font-size: 13px;
          color: #ffffff;
          letter-spacing: 0.5px;
          transition: filter 0.2s, transform 0.2s;
          margin-bottom: 24px;
        }
        .gw-card-cta:hover { filter: brightness(1.1); transform: scale(1.02); }
        .gw-card-cta.red { background: #DC2626; box-shadow: 0 4px 14px rgba(220,38,38,0.3); }
        .gw-card-cta.navy { background: #1E3A8A; box-shadow: 0 4px 14px rgba(30,58,138,0.3); }

        .gw-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
        .gw-tag {
          padding: 4px 12px;
          border-radius: 20px;
          font-size: 11px;
          font-weight: 700;
        }
        .gw-tag.red {
          background: #FEF2F2;
          border: 1px solid #FECACA;
          color: #991B1B;
        }
        .gw-tag.blue {
          background: #EFF6FF;
          border: 1px solid #BFDBFE;
          color: #1D4ED8;
        }

        /* ─── STATS BAR ─── */
        .gw-stats {
          width: 100%;
          max-width: 860px;
          background: #0F1C4D;
          border-radius: 16px;
          padding: 20px 32px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .gw-stat {
          text-align: center;
          flex: 1;
        }
        .gw-stat-label {
          font-size: 9px;
          font-weight: 600;
          letter-spacing: 1.5px;
          text-transform: uppercase;
          color: rgba(255,255,255,0.35);
          margin-bottom: 4px;
        }
        .gw-stat-value {
          font-family: 'Barlow Condensed', sans-serif;
          font-weight: 800;
          font-size: 24px;
          color: #ffffff;
          letter-spacing: -0.5px;
        }
        .gw-stat-value.green { color: #4ADE80; }
        .gw-stat-value.amber { color: #FCD34D; }

        .gw-stat-divider {
          width: 1px;
          height: 36px;
          background: rgba(255,255,255,0.1);
        }

        /* ─── FOOTER ─── */
        .gw-footer {
          text-align: center;
          padding: 24px;
          font-size: 11px;
          color: #D1D5DB;
          letter-spacing: 1px;
          text-transform: uppercase;
          font-weight: 600;
        }
      `}</style>

      <div className="gateway-root">
        {/* Header */}
        <header className="gw-header">
          <div className="gw-logo">
            <div className="gw-logo-icon">🚑</div>
            <div>
              <div className="gw-logo-text">Navi<span>Raksha</span></div>
              <div className="gw-logo-sub">Emergency AI</div>
            </div>
          </div>

          <nav className="gw-nav">
            <a href="/citizen">Citizen Portal</a>
            <a href="/dispatcher">Command Center</a>
            <a href="/simulation">Simulation</a>
          </nav>

          <div className="status-pill">
            <span className="status-dot" />
            Navi Mumbai Grid Active
          </div>
        </header>

        {/* Hero */}
        <main className="gw-hero">
          <p className="gw-eyebrow">▸ AI-Powered Emergency Intelligence — Navi Mumbai</p>

          <h1 className="gw-title">
            Navi<span>Raksha</span>
          </h1>

          <p className="gw-subtitle">
            Next-generation ambulance dispatch powered by a Random Forest AI model — coordinating Navi Mumbai&apos;s emergency response grid in real time.
          </p>

          {/* Cards */}
          <div className="gw-cards">
            {/* Citizen Portal */}
            <div className="gw-card" onClick={() => router.push("/citizen")}>
              <div className="gw-card-accent red" />
              <div className="gw-card-body">
                <div className="gw-card-icon red">🆘</div>
                <h2 className="gw-card-title red">Citizen Portal</h2>
                <p className="gw-card-desc">
                  Report emergencies instantly. Share your location and injury type — our AI dispatches the right ambulance in seconds.
                </p>
                <button className="gw-card-cta red" onClick={() => router.push("/citizen")}>
                  ENTER SYSTEM →
                </button>
                <div className="gw-tags">
                  {["SOS Alert", "Live Location", "AI ETA"].map(t => (
                    <span key={t} className="gw-tag red">{t}</span>
                  ))}
                </div>
              </div>
            </div>

            {/* Command Center */}
            <div className="gw-card" onClick={() => router.push("/dispatcher")}>
              <div className="gw-card-accent navy" />
              <div className="gw-card-body">
                <div className="gw-card-icon blue">🛡️</div>
                <h2 className="gw-card-title blue">Command Center</h2>
                <p className="gw-card-desc">
                  Authorized personnel only. Monitor fleet, validate ML model output, and coordinate Navi Mumbai&apos;s response grid.
                </p>
                <button className="gw-card-cta navy" onClick={() => router.push("/dispatcher")}>
                  ADMIN ACCESS →
                </button>
                <div className="gw-tags">
                  {["RF Model", "Fleet Control", "ML Dispatch"].map(t => (
                    <span key={t} className="gw-tag blue">{t}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

        </main>

        <footer className="gw-footer">
          © 2026 NaviRaksha · Navi Mumbai Emergency AI Grid
        </footer>
      </div>
    </>
  );
}
