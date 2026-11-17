import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_BODY, FONT_DISPLAY, SubtitleBar, TechBackdrop, popIn } from "../theme";

export const OffersScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const photoP = popIn(frame, fps, 14);
  const o1 = popIn(frame, fps, 55);
  const o2 = popIn(frame, fps, 95);
  const o3 = popIn(frame, fps, 135);
  const o4 = popIn(frame, fps, 175);
  const roiP = popIn(frame, fps, 240);

  const imgScale = interpolate(frame, [0, 400], [1, 1.08], { extrapolateRight: "clamp" });

  const offers = [
    { p: o1, icon: "⭐", title: "Plaquinha NFC + QR Code", price: "R$ 150 a R$ 350", desc: "Negócios com poucas avaliações" },
    { p: o2, icon: "🍔", title: "Cardápio Digital", price: "R$ 97 a R$ 297/mês", desc: "Gastronomia sem taxas de app" },
    { p: o3, icon: "🌐", title: "Biossite / Landing Page", price: "R$ 400 a R$ 1.500", desc: "Empresas sem site próprio" },
    { p: o4, icon: "💬", title: "WhatsApp Business", price: "R$ 500 a R$ 2.000", desc: "Atendimento profissional" },
  ];

  return (
    <AbsoluteFill>
      <TechBackdrop accent="emerald" />

      <AbsoluteFill
        style={{
          padding: "68px 100px 135px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
        }}
      >
        <div style={{ textAlign: "center", opacity: headP, translate: `0px ${interpolate(headP, [0, 1], [24, 0])}px` }}>
          <span
            style={{
              display: "inline-block",
              background: "rgba(16, 185, 129, 0.2)",
              border: "1px solid rgba(52, 211, 153, 0.45)",
              color: "#34d399",
              fontFamily: FONT_BODY,
              fontSize: 21,
              fontWeight: 800,
              padding: "6px 20px",
              borderRadius: 999,
              marginBottom: 14,
            }}
          >
            DINHEIRO NA MESA TODOS OS DIAS
          </span>
          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 60,
              fontWeight: 900,
              color: COLORS.white,
              margin: 0,
            }}
          >
            Oferta certa para a <span style={{ color: COLORS.emeraldLight }}>dor exata do cliente</span>
          </h2>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "0.95fr 1.05fr", gap: 40, alignItems: "center" }}>
          <div
            style={{
              borderRadius: 24,
              overflow: "hidden",
              border: "2px solid rgba(52, 211, 153, 0.4)",
              boxShadow: "0 30px 65px -15px rgba(0,0,0,0.7)",
              position: "relative",
              height: 490,
              opacity: photoP,
              scale: `${interpolate(photoP, [0, 1], [0.92, 1])}`,
            }}
          >
            <Img
              src={staticFile("img/nfc-plaque.jpg")}
              style={{ width: "100%", height: "100%", objectFit: "cover", scale: `${imgScale}` }}
            />
            <div
              style={{
                position: "absolute",
                bottom: 20,
                left: 20,
                right: 20,
                background: "rgba(7, 13, 25, 0.9)",
                border: "1px solid rgba(52,211,153,0.4)",
                borderRadius: 14,
                padding: "14px 20px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span style={{ fontFamily: FONT_BODY, fontSize: 22, fontWeight: 700, color: "#fff" }}>
                ⭐ Oferta Campeã de Entrada
              </span>
              <span style={{ fontFamily: FONT_DISPLAY, fontSize: 25, fontWeight: 900, color: "#34d399" }}>
                R$ 150 a R$ 350
              </span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 18 }}>
            {offers.map((o, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(22, 34, 56, 0.92)",
                  border: "1px solid rgba(148, 163, 184, 0.25)",
                  borderRadius: 20,
                  padding: "22px 22px",
                  opacity: o.p,
                  translate: `0px ${interpolate(o.p, [0, 1], [28, 0])}px`,
                  scale: `${interpolate(o.p, [0, 1], [0.92, 1])}`,
                }}
              >
                <div style={{ fontSize: 38, marginBottom: 8 }}>{o.icon}</div>
                <div style={{ fontFamily: FONT_DISPLAY, fontSize: 24, fontWeight: 800, color: "#fff", marginBottom: 4 }}>
                  {o.title}
                </div>
                <div style={{ fontFamily: FONT_BODY, fontSize: 18, color: COLORS.muted, marginBottom: 12 }}>
                  {o.desc}
                </div>
                <div
                  style={{
                    display: "inline-block",
                    background: "rgba(16, 185, 129, 0.2)",
                    color: "#34d399",
                    fontFamily: FONT_DISPLAY,
                    fontSize: 20,
                    fontWeight: 800,
                    padding: "6px 14px",
                    borderRadius: 999,
                  }}
                >
                  {o.price}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div
          style={{
            margin: "0 auto",
            background: "linear-gradient(90deg, rgba(37,99,235,0.28), rgba(16,185,129,0.28))",
            border: "1px solid rgba(52,211,153,0.45)",
            borderRadius: 16,
            padding: "14px 38px",
            fontFamily: FONT_DISPLAY,
            fontSize: 28,
            fontWeight: 800,
            color: "#fff",
            opacity: roiP,
            scale: `${interpolate(roiP, [0, 1], [0.9, 1])}`,
          }}
        >
          💰 1 única venda já paga <span style={{ color: "#34d399" }}>o ano inteiro do sistema!</span>
        </div>
      </AbsoluteFill>

      <SubtitleBar text="Oferte Plaquinha NFC, Cardápio Digital, Biossite ou WhatsApp Business. Uma venda já paga o ano todo!" />
    </AbsoluteFill>
  );
};

