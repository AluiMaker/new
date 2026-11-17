import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_BODY, FONT_DISPLAY, SubtitleBar, TechBackdrop, popIn } from "../theme";

export const HookScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const badgeP = popIn(frame, fps, 2);
  const titleP = popIn(frame, fps, 10);
  const p1 = popIn(frame, fps, 42);
  const p2 = popIn(frame, fps, 72);
  const p3 = popIn(frame, fps, 102);

  const bgScale = interpolate(frame, [0, 210], [1.02, 1.12], { extrapolateRight: "clamp" });

  const pains = [
    { prog: p1, text: "❌  Horas copiando telefone manual no Google" },
    { prog: p2, text: "❌  Mandando oferta para quem já tem tudo" },
    { prog: p3, text: "❌  Levando vácuo ou bloqueio no WhatsApp" },
  ];

  return (
    <AbsoluteFill>
      <TechBackdrop accent="red" />
      <AbsoluteFill style={{ opacity: 0.16 }}>
        <Img
          src={staticFile("img/saas-hero.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover", scale: `${bgScale}` }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          padding: "95px 120px 140px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <div
          style={{
            background: "rgba(239, 68, 68, 0.16)",
            border: "1px solid rgba(239, 68, 68, 0.45)",
            color: "#fca5a5",
            fontFamily: FONT_BODY,
            fontSize: 24,
            fontWeight: 800,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            padding: "10px 26px",
            borderRadius: 999,
            marginBottom: 28,
            opacity: badgeP,
            scale: `${interpolate(badgeP, [0, 1], [0.85, 1])}`,
          }}
        >
          Chega de prospecção no escuro
        </div>

        <h1
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 82,
            fontWeight: 900,
            lineHeight: 1.08,
            color: COLORS.white,
            maxWidth: 1440,
            margin: "0 0 42px",
            letterSpacing: "-0.025em",
            opacity: titleP,
            translate: `0px ${interpolate(titleP, [0, 1], [36, 0])}px`,
          }}
        >
          Você ainda perde horas{" "}
          <span style={{ color: "#f87171" }}>caçando clientes na mão?</span>
        </h1>

        <div style={{ display: "flex", gap: 22, flexWrap: "wrap", justifyContent: "center" }}>
          {pains.map((item, idx) => (
            <div
              key={idx}
              style={{
                background: "rgba(15, 23, 42, 0.85)",
                border: "1px solid rgba(239, 68, 68, 0.35)",
                borderRadius: 18,
                padding: "18px 28px",
                color: "#e2e8f0",
                fontFamily: FONT_BODY,
                fontSize: 27,
                fontWeight: 600,
                opacity: item.prog,
                translate: `0px ${interpolate(item.prog, [0, 1], [28, 0])}px`,
                scale: `${interpolate(item.prog, [0, 1], [0.92, 1])}`,
                boxShadow: "0 20px 40px -12px rgba(0,0,0,0.55)",
              }}
            >
              {item.text}
            </div>
          ))}
        </div>
      </AbsoluteFill>

      <SubtitleBar text="Você ainda perde horas procurando cliente na mão, sem saber quem realmente precisa do seu serviço?" />
    </AbsoluteFill>
  );
};

