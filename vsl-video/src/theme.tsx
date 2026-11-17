import React from "react";
import { loadFont as loadJakarta } from "@remotion/google-fonts/PlusJakartaSans";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { AbsoluteFill, Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const { fontFamily: FONT_DISPLAY } = loadJakarta("normal", {
  weights: ["700", "800"],
  subsets: ["latin"],
  ignoreTooManyRequestsWarning: true,
});
export const { fontFamily: FONT_BODY } = loadInter("normal", {
  weights: ["500", "600", "700"],
  subsets: ["latin"],
  ignoreTooManyRequestsWarning: true,
});

export const COLORS = {
  bgDark: "#070d19",
  bgNavy: "#0f172a",
  surfaceDark: "#162238",
  primary: "#2563eb",
  primaryLight: "#60a5fa",
  emerald: "#10b981",
  emeraldLight: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  white: "#ffffff",
  muted: "#94a3b8",
  border: "rgba(148, 163, 184, 0.22)",
};

export const TechBackdrop: React.FC<{ accent?: "blue" | "emerald" | "red" }> = ({ accent = "blue" }) => {
  const frame = useCurrentFrame();
  const driftX = interpolate(frame, [0, 400], [0, 60], { extrapolateRight: "extend" });
  const glowColor =
    accent === "emerald"
      ? "rgba(16, 185, 129, 0.24)"
      : accent === "red"
      ? "rgba(239, 68, 68, 0.20)"
      : "rgba(37, 99, 235, 0.26)";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: COLORS.bgDark,
        backgroundImage: `
          radial-gradient(900px 540px at ${20 + (driftX % 30)}% 20%, ${glowColor}, transparent 70%),
          radial-gradient(800px 500px at 85% 85%, rgba(16, 185, 129, 0.16), transparent 70%),
          linear-gradient(rgba(148, 163, 184, 0.045) 1px, transparent 1px),
          linear-gradient(90deg, rgba(148, 163, 184, 0.045) 1px, transparent 1px)
        `,
        backgroundSize: "100% 100%, 100% 100%, 64px 64px, 64px 64px",
      }}
    />
  );
};

export const SubtitleBar: React.FC<{ text: string; delay?: number }> = ({ text, delay = 6 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame: Math.max(0, frame - delay), fps, config: { damping: 200 } });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 44,
        left: 110,
        right: 110,
        display: "flex",
        justifyContent: "center",
        opacity: progress,
        translate: `0px ${interpolate(progress, [0, 1], [18, 0])}px`,
      }}
    >
      <div
        style={{
          background: "rgba(7, 13, 25, 0.86)",
          border: "1px solid rgba(255,255,255,0.16)",
          backdropFilter: "blur(12px)",
          color: "#f8fafc",
          fontFamily: FONT_BODY,
          fontSize: 30,
          fontWeight: 600,
          padding: "14px 32px",
          borderRadius: 16,
          textAlign: "center",
          boxShadow: "0 18px 40px -10px rgba(0,0,0,0.65)",
          maxWidth: 1460,
          lineHeight: 1.35,
        }}
      >
        {text}
      </div>
    </div>
  );
};

export const BrowserWindow: React.FC<{
  url?: string;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ url = "https://mapaleadspro.online/app", children, style }) => (
  <div
    style={{
      background: "#0f172a",
      borderRadius: 22,
      border: "1px solid rgba(148,163,184,0.28)",
      overflow: "hidden",
      boxShadow: "0 36px 80px -20px rgba(0,0,0,0.8)",
      ...style,
    }}
  >
    <div
      style={{
        height: 44,
        background: "#1e293b",
        borderBottom: "1px solid rgba(148,163,184,0.18)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 20px",
      }}
    >
      <div style={{ display: "flex", gap: 9 }}>
        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#ef4444" }} />
        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#f59e0b" }} />
        <div style={{ width: 12, height: 12, borderRadius: "50%", background: "#10b981" }} />
      </div>
      <div
        style={{
          background: "#0f172a",
          color: "#94a3b8",
          fontFamily: "monospace",
          fontSize: 16,
          padding: "4px 20px",
          borderRadius: 999,
        }}
      >
        {url}
      </div>
      <div style={{ color: "#34d399", fontFamily: FONT_BODY, fontSize: 15, fontWeight: 700 }}>
        ● AO VIVO
      </div>
    </div>
    {children}
  </div>
);

export const popIn = (frame: number, fps: number, delay = 0) =>
  spring({
    frame: Math.max(0, frame - delay),
    fps,
    config: { damping: 14, stiffness: 140, mass: 0.9 },
  });

export const easeOut = (frame: number, start: number, end: number, from: number, to: number) =>
  interpolate(frame, [start, end], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
