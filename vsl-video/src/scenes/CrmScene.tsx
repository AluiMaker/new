import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BrowserWindow, COLORS, FONT_BODY, FONT_DISPLAY, SubtitleBar, TechBackdrop, popIn } from "../theme";

export const CrmScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const winP = popIn(frame, fps, 14);
  const pill1 = popIn(frame, fps, 60);
  const pill2 = popIn(frame, fps, 110);

  const imgPan = interpolate(frame, [0, 245], [1, 1.05], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <TechBackdrop accent="blue" />

      <AbsoluteFill
        style={{
          padding: "64px 100px 135px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-end",
            marginBottom: 24,
            opacity: headP,
            translate: `0px ${interpolate(headP, [0, 1], [24, 0])}px`,
          }}
        >
          <div>
            <div
              style={{
                display: "inline-block",
                background: "rgba(37, 99, 235, 0.22)",
                border: "1px solid rgba(96, 165, 250, 0.45)",
                color: "#93c5fd",
                fontFamily: FONT_BODY,
                fontSize: 20,
                fontWeight: 800,
                padding: "6px 18px",
                borderRadius: 999,
                marginBottom: 10,
              }}
            >
              ORGANIZAÇÃO AUTOMÁTICA
            </div>
            <h2 style={{ fontFamily: FONT_DISPLAY, fontSize: 56, fontWeight: 900, color: COLORS.white, margin: 0 }}>
              CRM Kanban + <span style={{ color: COLORS.primaryLight }}>Quebra-Gelo Anti-Bloqueio</span>
            </h2>
          </div>

          <div style={{ display: "flex", gap: 14 }}>
            <div
              style={{
                background: "rgba(22, 34, 56, 0.92)",
                border: "1px solid rgba(96, 165, 250, 0.4)",
                borderRadius: 14,
                padding: "12px 20px",
                color: "#fff",
                fontFamily: FONT_BODY,
                fontSize: 21,
                fontWeight: 700,
                opacity: pill1,
                scale: `${interpolate(pill1, [0, 1], [0.85, 1])}`,
              }}
            >
              🏷️ Etiquetas Automáticas
            </div>
            <div
              style={{
                background: "rgba(16, 185, 129, 0.2)",
                border: "1px solid rgba(52, 211, 153, 0.45)",
                borderRadius: 14,
                padding: "12px 20px",
                color: "#34d399",
                fontFamily: FONT_BODY,
                fontSize: 21,
                fontWeight: 700,
                opacity: pill2,
                scale: `${interpolate(pill2, [0, 1], [0.85, 1])}`,
              }}
            >
              🧊 Copys Anti-Bloqueio
            </div>
          </div>
        </div>

        <BrowserWindow
          url="https://mapaleadspro.online/app · CRM & Pipeline"
          style={{
            opacity: winP,
            scale: `${interpolate(winP, [0, 1], [0.94, 1])}`,
            translate: `0px ${interpolate(winP, [0, 1], [30, 0])}px`,
          }}
        >
          <div style={{ height: 610, overflow: "hidden" }}>
            <Img
              src={staticFile("img/ui-crm.png")}
              style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top left", scale: `${imgPan}` }}
            />
          </div>
        </BrowserWindow>
      </AbsoluteFill>

      <SubtitleBar text="Cada empresa entra organizada no CRM Kanban com etiquetas automáticas e modelos curtos de quebra-gelo." />
    </AbsoluteFill>
  );
};

