import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { COLORS, FONT_BODY, FONT_DISPLAY, KineticCaptions, SceneProps, SceneSfxCue, TechBackdrop, popIn } from "../theme";

export const OffersScene: React.FC<SceneProps> = ({ mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const photoP = popIn(frame, fps, 14);
  const o1 = popIn(frame, fps, 55);
  const o2 = popIn(frame, fps, 95);
  const o3 = popIn(frame, fps, 135);
  const o4 = popIn(frame, fps, 175);
  const roiP = popIn(frame, fps, 240);

  const imgScale = interpolate(frame, [0, 406], [1, 1.08], { extrapolateRight: "clamp" });

  const offers = [
    { p: o1, icon: "⭐", title: "Plaquinha NFC 5★", price: "R$ 150–350", desc: "Poucas avaliações" },
    { p: o2, icon: "🍔", title: "Cardápio Digital", price: "R$ 97–297/mês", desc: "Sem taxas de app" },
    { p: o3, icon: "🌐", title: "Biossite / LP", price: "R$ 400–1.500", desc: "Quem está sem site" },
    { p: o4, icon: "💬", title: "WhatsApp Business", price: "R$ 500–2.000", desc: "Atendimento PRO" },
  ];

  return (
    <AbsoluteFill>
      <TechBackdrop accent="emerald" />
      <SceneSfxCue file="audio/sfx_whoosh.wav" atFrame={0} volume={0.32} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={55} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={95} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={135} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={175} volume={0.25} />
      <SceneSfxCue file="audio/sfx_boom.wav" atFrame={240} volume={0.4} />

      <AbsoluteFill
        style={{
          padding: mobile ? "160px 64px 330px" : "68px 100px 135px",
          display: "flex",
          flexDirection: "column",
          justifyContent: mobile ? "center" : "space-between",
          gap: mobile ? 26 : 0,
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
              fontSize: mobile ? 22 : 21,
              fontWeight: 800,
              padding: "7px 22px",
              borderRadius: 999,
              marginBottom: 14,
            }}
          >
            DINHEIRO NA MESA TODO DIA
          </span>
          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: mobile ? 62 : 60,
              fontWeight: 900,
              lineHeight: 1.08,
              color: COLORS.white,
              margin: 0,
            }}
          >
            Oferta certa para <span style={{ color: COLORS.emeraldLight }}>quem precisa</span>
          </h2>
        </div>

        <div
          style={{
            display: mobile ? "flex" : "grid",
            flexDirection: mobile ? "column" : undefined,
            gridTemplateColumns: mobile ? undefined : "0.95fr 1.05fr",
            gap: mobile ? 24 : 40,
            alignItems: "center",
          }}
        >
          <div
            style={{
              borderRadius: 24,
              overflow: "hidden",
              border: "2px solid rgba(52, 211, 153, 0.4)",
              boxShadow: "0 30px 65px -15px rgba(0,0,0,0.7)",
              position: "relative",
              height: mobile ? 400 : 490,
              width: "100%",
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
                bottom: 16,
                left: 16,
                right: 16,
                background: "rgba(7, 13, 25, 0.9)",
                border: "1px solid rgba(52,211,153,0.4)",
                borderRadius: 14,
                padding: "12px 18px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span style={{ fontFamily: FONT_BODY, fontSize: mobile ? 22 : 22, fontWeight: 700, color: "#fff" }}>
                ⭐ Oferta Campeã
              </span>
              <span style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 25 : 25, fontWeight: 900, color: "#34d399" }}>
                R$ 150 a R$ 350
              </span>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: mobile ? 16 : 18, width: "100%" }}>
            {offers.map((o, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(22, 34, 56, 0.92)",
                  border: "1px solid rgba(148, 163, 184, 0.25)",
                  borderRadius: 20,
                  padding: mobile ? "20px 18px" : "22px 22px",
                  opacity: o.p,
                  translate: `0px ${interpolate(o.p, [0, 1], [28, 0])}px`,
                  scale: `${interpolate(o.p, [0, 1], [0.92, 1])}`,
                }}
              >
                <div style={{ fontSize: mobile ? 36 : 38, marginBottom: 6 }}>{o.icon}</div>
                <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 25 : 24, fontWeight: 800, color: "#fff", marginBottom: 4 }}>
                  {o.title}
                </div>
                <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 19 : 18, color: COLORS.muted, marginBottom: 10 }}>
                  {o.desc}
                </div>
                <div
                  style={{
                    display: "inline-block",
                    background: "rgba(16, 185, 129, 0.2)",
                    color: "#34d399",
                    fontFamily: FONT_DISPLAY,
                    fontSize: mobile ? 21 : 20,
                    fontWeight: 800,
                    padding: "5px 14px",
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
            background: "linear-gradient(90deg, rgba(37,99,235,0.3), rgba(16,185,129,0.3))",
            border: "1px solid rgba(52,211,153,0.5)",
            borderRadius: 16,
            padding: mobile ? "16px 26px" : "14px 38px",
            fontFamily: FONT_DISPLAY,
            fontSize: mobile ? 28 : 28,
            fontWeight: 900,
            color: "#fff",
            textAlign: "center",
            opacity: roiP,
            scale: `${interpolate(roiP, [0, 1], [0.9, 1])}`,
          }}
        >
          💰 1 venda já paga <span style={{ color: "#34d399" }}>o ano todo!</span>
        </div>
      </AbsoluteFill>

      <KineticCaptions sceneKey="03_ofertas" mobile={mobile} />
    </AbsoluteFill>
  );
};
