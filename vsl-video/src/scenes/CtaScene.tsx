import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_BODY, FONT_DISPLAY, KineticCaptions, SceneProps, SceneSfxCue, TechBackdrop, popIn } from "../theme";

export const CtaScene: React.FC<SceneProps> = ({ mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoP = popIn(frame, fps, 2);
  const card1 = popIn(frame, fps, 36);
  const card2 = popIn(frame, fps, 68);
  const card3 = popIn(frame, fps, 100);
  const ctaP = popIn(frame, fps, 140);
  const pulse = 1 + 0.025 * Math.sin(Math.max(0, frame - 155) * 0.16);

  return (
    <AbsoluteFill>
      <TechBackdrop accent="emerald" />
      <SceneSfxCue file="audio/sfx_whoosh.wav" atFrame={0} volume={0.32} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={36} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={68} volume={0.28} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={100} volume={0.25} />
      <SceneSfxCue file="audio/sfx_boom.wav" atFrame={140} volume={0.45} />

      <AbsoluteFill
        style={{
          padding: mobile ? "150px 64px 320px" : "56px 110px 135px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: mobile ? "center" : "space-between",
          gap: mobile ? 26 : 0,
          textAlign: "center",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 20,
            opacity: logoP,
            scale: `${interpolate(logoP, [0, 1], [0.85, 1])}`,
          }}
        >
          <Img
            src={staticFile("img/app-icon-1024.png")}
            style={{
              width: mobile ? 86 : 78,
              height: mobile ? 86 : 78,
              borderRadius: 22,
              boxShadow: "0 16px 38px -8px rgba(16, 185, 129, 0.55)",
            }}
          />
          <div style={{ textAlign: "left" }}>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 48 : 42, fontWeight: 900, color: "#fff", lineHeight: 1 }}>
              MapaLeads <span style={{ color: COLORS.primaryLight }}>PRO</span>
            </div>
            <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 22 : 20, color: COLORS.emeraldLight, fontWeight: 700, marginTop: 4 }}>
              Oferta de Lançamento Ativa
            </div>
          </div>
        </div>

        <h2
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: mobile ? 64 : 64,
            fontWeight: 900,
            color: "#fff",
            lineHeight: 1.08,
            margin: 0,
            opacity: logoP,
          }}
        >
          Comece grátis ou <span style={{ color: COLORS.emeraldLight }}>garanta sua vaga</span>
        </h2>

        <div
          style={{
            display: mobile ? "flex" : "grid",
            flexDirection: mobile ? "column" : undefined,
            gridTemplateColumns: mobile ? undefined : "repeat(3, 1fr)",
            gap: mobile ? 18 : 26,
            width: "100%",
            maxWidth: mobile ? 900 : 1460,
          }}
        >
          {/* Teste */}
          <div
            style={{
              background: "rgba(22, 34, 56, 0.88)",
              border: "1px solid rgba(148, 163, 184, 0.3)",
              borderRadius: 22,
              padding: mobile ? "22px 26px" : "30px 26px",
              display: mobile ? "flex" : "block",
              justifyContent: "space-between",
              alignItems: "center",
              opacity: card1,
              translate: `0px ${interpolate(card1, [0, 1], [32, 0])}px`,
            }}
          >
            <div style={{ textAlign: mobile ? "left" : "center" }}>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 30 : 28, fontWeight: 800, color: "#fff" }}>Teste Grátis 24h</div>
              <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 22 : 21, color: "#cbd5e1", marginTop: 4 }}>
                25 leads · Sem cartão
              </div>
            </div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 54 : 56, fontWeight: 900, color: "#93c5fd", margin: mobile ? 0 : "12px 0" }}>
              R$ 0
            </div>
          </div>

          {/* Starter Featured */}
          <div
            style={{
              background: "linear-gradient(180deg, rgba(37,99,235,0.32) 0%, rgba(16,185,129,0.26) 100%)",
              border: "2px solid #34d399",
              borderRadius: 24,
              padding: mobile ? "26px 26px" : "30px 26px",
              position: "relative",
              boxShadow: "0 24px 60px -15px rgba(16, 185, 129, 0.45)",
              display: mobile ? "flex" : "block",
              justifyContent: "space-between",
              alignItems: "center",
              opacity: card2,
              translate: `0px ${interpolate(card2, [0, 1], [32, 0])}px`,
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -15,
                left: mobile ? 26 : "50%",
                translate: mobile ? "0 0" : "-50% 0",
                background: "#dc2626",
                color: "#fff",
                fontFamily: FONT_BODY,
                fontSize: 16,
                fontWeight: 800,
                padding: "4px 16px",
                borderRadius: 999,
                whiteSpace: "nowrap",
              }}
            >
              OFERTA DE LANÇAMENTO
            </div>
            <div style={{ textAlign: mobile ? "left" : "center" }}>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 32 : 28, fontWeight: 800, color: "#fff" }}>Plano Starter</div>
              <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 22 : 21, color: "#fff", marginTop: 4 }}>
                500 leads · Todas funções
              </div>
            </div>
            <div style={{ textAlign: mobile ? "right" : "center" }}>
              <div style={{ fontFamily: FONT_BODY, fontSize: 18, color: "#cbd5e1", textDecoration: "line-through" }}>
                De R$ 97
              </div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 56 : 60, fontWeight: 900, color: "#34d399", lineHeight: 1 }}>
                R$ 37<span style={{ fontSize: 22, color: "#cbd5e1" }}>/mês</span>
              </div>
            </div>
          </div>

          {/* PRO */}
          <div
            style={{
              background: "rgba(22, 34, 56, 0.88)",
              border: "1px solid rgba(96, 165, 250, 0.45)",
              borderRadius: 22,
              padding: mobile ? "22px 26px" : "30px 26px",
              display: mobile ? "flex" : "block",
              justifyContent: "space-between",
              alignItems: "center",
              opacity: card3,
              translate: `0px ${interpolate(card3, [0, 1], [32, 0])}px`,
            }}
          >
            <div style={{ textAlign: mobile ? "left" : "center" }}>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 30 : 28, fontWeight: 800, color: "#fff" }}>Plano PRO</div>
              <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 22 : 21, color: "#cbd5e1", marginTop: 4 }}>
                2.000 leads + Prioridade
              </div>
            </div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 52 : 56, fontWeight: 900, color: "#60a5fa", margin: mobile ? 0 : "12px 0" }}>
              R$ 79<span style={{ fontSize: 22, color: "#cbd5e1" }}>/mês</span>
            </div>
          </div>
        </div>

        <div
          style={{
            background: "linear-gradient(90deg, #10b981, #2563eb)",
            color: "#fff",
            fontFamily: FONT_DISPLAY,
            fontSize: mobile ? 32 : 34,
            fontWeight: 900,
            padding: mobile ? "22px 34px" : "22px 54px",
            borderRadius: 18,
            boxShadow: "0 20px 50px -10px rgba(16, 185, 129, 0.65)",
            opacity: ctaP,
            scale: `${interpolate(ctaP, [0, 1], [0.85, 1]) * pulse}`,
            width: mobile ? "100%" : "auto",
            maxWidth: mobile ? 900 : "none",
          }}
        >
          🚀 CLIQUE ABAIXO E COMECE HOJE!
        </div>
      </AbsoluteFill>

      <KineticCaptions sceneKey="06_cta" mobile={mobile} />
    </AbsoluteFill>
  );
};
