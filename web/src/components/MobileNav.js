"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home, LayoutDashboard, Map, Settings } from "lucide-react";

export default function MobileNav() {
  const pathname = usePathname();

  return (
    <div className="mobile-nav">
      <Link href="/" className={`nav-item ${pathname === "/" ? "active" : ""}`}>
        <Home size={20} />
        <span>Home</span>
      </Link>
      <Link href="/dashboard" className={`nav-item ${pathname === "/dashboard" ? "active" : ""}`}>
        <LayoutDashboard size={20} />
        <span>Grid</span>
      </Link>
      <Link href="/map" className={`nav-item ${pathname === "/map" ? "active" : ""}`}>
        <Map size={20} />
        <span>Map</span>
      </Link>
      <Link href="/settings" className={`nav-item ${pathname === "/settings" ? "active" : ""}`}>
        <Settings size={20} />
        <span>Settings</span>
      </Link>
    </div>
  );
}
