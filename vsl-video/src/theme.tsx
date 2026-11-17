import React from "react";
import { loadFont as loadJakarta } from "@remotion/google-fonts/PlusJakartaSans";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { AbsoluteFill, Easing, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Audio } from "@remotion/media";
import { VO_DATA } from "./voData";

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

export interface SceneProps {
  mobile?: boolean;
}

export const TechBackdrop: React.FC<{ accent?: "blue" | "emerald" | "red" }> = ({ accent = "blue" }) => {
  const frame = useCurrentFrame();
  const driftX = interpolate(frame, [0, 400], [0, 60], { extrapolateRight: "extend" });
  const glowColor =
    accent === "emerald"
      ? "rgba(16, 185, 129, 0.24)"
      : accent === "red"
      ? "rgba(239, 68, 68, 0.22)"
      : "rgba(37, 99, 235, 0.28)";

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

export const KineticCaptions: React.FC<{ sceneKey: string; mobile?: boolean }> = ({ sceneKey, mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const meta = VO_DATA[sceneKey];
  if (!meta || !meta.captions.length) return null;

  let activeGroup = meta.captions[0];
  for (let i = 0; i < meta.captions.length; i++) {
    const g = meta.captions[i];
    const nextStart = i + 1 < meta.captions.length ? meta.captions[i + 1].start : meta.durationSec + 2;
    if (t >= g.start - 0.06 && t < nextStart - 0.04) {
      activeGroup = g;
      break;
    }
    if (t >= nextStart - 0.04) {
      activeGroup = meta.captions[Math.min(i + 1, meta.captions.length - 1)];
    }
  }

  const groupStartFrame = Math.max(0, Math.floor(activeGroup.start * fps) - 2);
  const groupProg = spring({ frame: Math.max(0, frame - groupStartFrame), fps, config: { damping: 14, stiffness: 180 } });

  return (
    <div
      style={{
        position: "absolute",
        bottom: mobile ? 175 : 42,
        left: mobile ? 64 : 110,
        right: mobile ? 64 : 110,
        display: "flex",
        justifyContent: "center",
        pointerEvents: "none",
      }}
    >
      <div
        style={{
          background: "rgba(7, 13, 25, 0.88)",
          border: "1px solid rgba(255,255,255,0.18)",
          borderRadius: 20,
          padding: mobile ? "16px 26px" : "13px 30px",
          boxShadow: "0 20px 45px -10px rgba(0,0,0,0.75)",
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: mobile ? 12 : 11,
          scale: `${interpolate(groupProg, [0, 1], [0.92, 1])}`,
        }}
      >
        {activeGroup.words.map((w, idx) => {
          const spoken = t >= w.start - 0.04;
          const isCurrent = t >= w.start - 0.04 && t <= w.end + 0.12;
          return (
            <span
              key={`${activeGroup.start}-${idx}`}
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: mobile ? (w.highlight ? 44 : 38) : (w.highlight ? 36 : 31),
                fontWeight: w.highlight ? 900 : 700,
                color: w.highlight
                  ? spoken
                    ? "#34d399"
                    : "#94a3b8"
                  : spoken
                  ? "#ffffff"
                  : "#94a3b8",
                textShadow: w.highlight && spoken ? "0 0 22px rgba(16, 185, 129, 0.65)" : "none",
                scale: isCurrent ? "1.08" : "1",
                display: "inline-block",
              }}
            >
              {w.text}
            </span>
          );
        })}
      </div>
    </div>
  );
};

export const SceneSfxCue: React.FC<{ file: string; atFrame: number; volume?: number }> = ({
  file,
  atFrame,
  volume = 0.35,
}) => (
  <Sequence from={atFrame} durationInFrames={30}>
    <Audio src={staticFile(file)} volume={volume} />
  </Sequence>
);

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
        height: 42,
        background: "#1e293b",
        borderBottom: "1px solid rgba(148,163,184,0.18)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 18px",
      }}
    >
      <div style={{ display: "flex", gap: 8 }}>
        <div style={{ width: 11, height: 11, borderRadius: "50%", background: "#ef4444" }} />
        <div style={{ width: 11, height: 11, borderRadius: "50%", background: "#f59e0b" }} />
        <div style={{ width: 11, height: 11, borderRadius: "50%", background: "#10b981" }} />
      </div>
      <div
        style={{
          background: "#0f172a",
          color: "#94a3b8",
          fontFamily: "monospace",
          fontSize: 15,
          padding: "3px 16px",
          borderRadius: 999,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {url}
      </div>
      <div style={{ color: "#34d399", fontFamily: FONT_BODY, fontSize: 14, fontWeight: 700 }}>
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
    config: { damping: 14, stiffness: 150, mass: 0.85 },
  });

export const easeOut = (frame: number, start: number, end: number, from: number, to: number) =>
  interpolate(frame, [start, end], [from, to], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
