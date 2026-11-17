import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_BODY, FONT_DISPLAY, KineticCaptions, SceneProps, SceneSfxCue, TechBackdrop, popIn } from "../theme";

export const HookScene: React.FC<SceneProps> = ({ mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const badgeP = popIn(frame, fps, 1);
  const titleP = popIn(frame, fps, 7);
  const p1 = popIn(frame, fps, 36);
  const p2 = popIn(frame, fps, 68);
  const p3 = popIn(frame, fps, 100);
  const bgScale = interpolate(frame, [0, 220], [1.02, 1.12], { extrapolateRight: "clamp" });

  const pains = [
    { prog: p1, text: "❌  Horas copiando telefone no Google" },
    { prog: p2, text: "❌  Oferta para quem já tem tudo" },
    { prog: p3, text: "❌  Vácuo ou bloqueio no WhatsApp" },
  ];

  return (
    <AbsoluteFill>
      <TechBackdrop accent="red" />
      <SceneSfxCue file="audio/sfx_boom.wav" atFrame={2} volume={0.45} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={36} volume={0.28} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={68} volume={0.28} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={100} volume={0.28} />

      <AbsoluteFill style={{ opacity: 0.16 }}>
        <Img
          src={staticFile("img/saas-hero.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover", scale: `${bgScale}` }}
        />
      </AbsoluteFill>

      <AbsoluteFill
        style={{
          padding: mobile ? "180px 72px 340px" : "95px 120px 140px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
        }}
      >
        <div
          style={{
            background: "rgba(239, 68, 68, 0.18)",
            border: "1px solid rgba(239, 68, 68, 0.5)",
            color: "#fca5a5",
            fontFamily: FONT_BODY,
            fontSize: mobile ? 26 : 24,
            fontWeight: 800,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            padding: mobile ? "12px 28px" : "10px 26px",
            borderRadius: 999,
            marginBottom: mobile ? 34 : 26,
            opacity: badgeP,
            scale: `${interpolate(badgeP, [0, 1], [0.85, 1])}`,
          }}
        >
          Chega de perder tempo
        </div>

        <h1
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: mobile ? 86 : 82,
            fontWeight: 900,
            lineHeight: 1.06,
            color: COLORS.white,
            maxWidth: mobile ? 940 : 1440,
            margin: mobile ? "0 0 54px" : "0 0 40px",
            letterSpacing: "-0.025em",
            opacity: titleP,
            translate: `0px ${interpolate(titleP, [0, 1], [36, 0])}px`,
          }}
        >
          Pare de caçar cliente{" "}
          <span style={{ color: "#f87171" }}>no braço!</span>
        </h1>

        <div
          style={{
            display: "flex",
            flexDirection: mobile ? "column" : "row",
            gap: mobile ? 22 : 22,
            flexWrap: "wrap",
            justifyContent: "center",
            width: mobile ? "100%" : "auto",
            maxWidth: mobile ? 880 : "none",
          }}
        >
          {pains.map((item, idx) => (
            <div
              key={idx}
              style={{
                background: "rgba(15, 23, 42, 0.88)",
                border: "1px solid rgba(239, 68, 68, 0.4)",
                borderRadius: 18,
                padding: mobile ? "22px 28px" : "18px 28px",
                color: "#e2e8f0",
                fontFamily: FONT_BODY,
                fontSize: mobile ? 32 : 27,
                fontWeight: 700,
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

      <KineticCaptions sceneKey="01_hook" mobile={mobile} />
    </AbsoluteFill>
  );
};
