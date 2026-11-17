import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_BODY, FONT_DISPLAY, SubtitleBar, TechBackdrop, popIn } from "../theme";

export const CtaScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const logoP = popIn(frame, fps, 2);
  const card1 = popIn(frame, fps, 45);
  const card2 = popIn(frame, fps, 75);
  const card3 = popIn(frame, fps, 105);
  const ctaP = popIn(frame, fps, 150);

  // Subtle button pulse once visible
  const pulse = 1 + 0.025 * Math.sin(Math.max(0, frame - 165) * 0.16);

  return (
    <AbsoluteFill>
      <TechBackdrop accent="emerald" />

      <AbsoluteFill
        style={{
          padding: "56px 110px 135px",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "space-between",
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
              width: 78,
              height: 78,
              borderRadius: 20,
              boxShadow: "0 16px 38px -8px rgba(16, 185, 129, 0.55)",
            }}
          />
          <div style={{ textAlign: "left" }}>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 42, fontWeight: 900, color: "#fff", lineHeight: 1 }}>
              MapaLeads <span style={{ color: COLORS.primaryLight }}>PRO</span>
            </div>
            <div style={{ fontFamily: FONT_BODY, fontSize: 20, color: COLORS.emeraldLight, fontWeight: 700, marginTop: 4 }}>
              Condição Especial de Lançamento
            </div>
          </div>
        </div>

        <h2
          style={{
            fontFamily: FONT_DISPLAY,
            fontSize: 64,
            fontWeight: 900,
            color: "#fff",
            lineHeight: 1.08,
            margin: 0,
            opacity: logoP,
          }}
        >
          Comece grátis hoje ou garanta <span style={{ color: COLORS.emeraldLight }}>sua vaga</span>
        </h2>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 26, width: "100%", maxWidth: 1460 }}>
          {/* Teste */}
          <div
            style={{
              background: "rgba(22, 34, 56, 0.88)",
              border: "1px solid rgba(148, 163, 184, 0.3)",
              borderRadius: 24,
              padding: "30px 26px",
              opacity: card1,
              translate: `0px ${interpolate(card1, [0, 1], [32, 0])}px`,
            }}
          >
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 28, fontWeight: 800, color: "#fff" }}>Teste Grátis 24h</div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 56, fontWeight: 900, color: "#93c5fd", margin: "12px 0" }}>
              R$ 0
            </div>
            <div style={{ fontFamily: FONT_BODY, fontSize: 21, color: "#cbd5e1" }}>
              25 empresas · Sem cartão · Acesso na hora
            </div>
          </div>

          {/* Starter Featured */}
          <div
            style={{
              background: "linear-gradient(180deg, rgba(37,99,235,0.28) 0%, rgba(16,185,129,0.22) 100%)",
              border: "2px solid #34d399",
              borderRadius: 24,
              padding: "30px 26px",
              position: "relative",
              boxShadow: "0 24px 60px -15px rgba(16, 185, 129, 0.45)",
              opacity: card2,
              translate: `0px ${interpolate(card2, [0, 1], [32, 0])}px`,
            }}
          >
            <div
              style={{
                position: "absolute",
                top: -16,
                left: "50%",
                translate: "-50% 0",
                background: "#dc2626",
                color: "#fff",
                fontFamily: FONT_BODY,
                fontSize: 16,
                fontWeight: 800,
                padding: "5px 18px",
                borderRadius: 999,
                whiteSpace: "nowrap",
              }}
            >
              OFERTA DE LANÇAMENTO
            </div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 28, fontWeight: 800, color: "#fff" }}>Plano Starter</div>
            <div style={{ fontFamily: FONT_BODY, fontSize: 19, color: "#cbd5e1", textDecoration: "line-through", marginTop: 6 }}>
              De R$ 97/mês
            </div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 60, fontWeight: 900, color: "#34d399", lineHeight: 1.05 }}>
              R$ 37<span style={{ fontSize: 24, color: "#cbd5e1" }}>/mês</span>
            </div>
            <div style={{ fontFamily: FONT_BODY, fontSize: 21, color: "#fff", marginTop: 10 }}>
              500 leads salvos · Todas funções liberadas
            </div>
          </div>

          {/* PRO */}
          <div
            style={{
              background: "rgba(22, 34, 56, 0.88)",
              border: "1px solid rgba(96, 165, 250, 0.45)",
              borderRadius: 24,
              padding: "30px 26px",
              opacity: card3,
              translate: `0px ${interpolate(card3, [0, 1], [32, 0])}px`,
            }}
          >
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 28, fontWeight: 800, color: "#fff" }}>Plano PRO</div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 56, fontWeight: 900, color: "#60a5fa", margin: "12px 0" }}>
              R$ 79<span style={{ fontSize: 24, color: "#cbd5e1" }}>/mês</span>
            </div>
            <div style={{ fontFamily: FONT_BODY, fontSize: 21, color: "#cbd5e1" }}>
              2.000 leads salvos + Prioridade na fila
            </div>
          </div>
        </div>

        <div
          style={{
            background: "linear-gradient(90deg, #10b981, #2563eb)",
            color: "#fff",
            fontFamily: FONT_DISPLAY,
            fontSize: 34,
            fontWeight: 900,
            padding: "22px 54px",
            borderRadius: 18,
            boxShadow: "0 20px 50px -10px rgba(16, 185, 129, 0.65)",
            opacity: ctaP,
            scale: `${interpolate(ctaP, [0, 1], [0.85, 1]) * pulse}`,
          }}
        >
          🚀 CLIQUE ABAIXO E FAÇA SUA 1ª BUSCA HOJE · mapaleadspro.online
        </div>
      </AbsoluteFill>

      <SubtitleBar text="Teste grátis por 24h sem cartão ou assine o Starter por R$ 37/mês. Clique no botão abaixo!" />
    </AbsoluteFill>
  );
};

