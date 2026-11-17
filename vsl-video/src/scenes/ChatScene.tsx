import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BrowserWindow, COLORS, FONT_BODY, FONT_DISPLAY, KineticCaptions, SceneProps, SceneSfxCue, TechBackdrop, popIn } from "../theme";

export const ChatScene: React.FC<SceneProps> = ({ mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const winP = popIn(frame, fps, 14);
  const ch1 = popIn(frame, fps, 65);
  const ch2 = popIn(frame, fps, 120);
  const ch3 = popIn(frame, fps, 175);

  const imgZoom = interpolate(frame, [0, 317], [1, 1.05], { extrapolateRight: "clamp" });

  const channels = [
    { p: ch1, badge: "📱 WhatsApp QR Code", desc: "Conecte em 10s direto no painel", color: "#34d399" },
    { p: ch2, badge: "⚡ WhatsApp 1-Clique", desc: "Envio humano zero bloqueio", color: "#60a5fa" },
    { p: ch3, badge: "🚀 API Oficial Meta", desc: "Escala empresarial no mesmo Inbox", color: "#a78bfa" },
  ];

  return (
    <AbsoluteFill>
      <TechBackdrop accent="emerald" />
      <SceneSfxCue file="audio/sfx_whoosh.wav" atFrame={0} volume={0.32} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={65} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={120} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={175} volume={0.25} />

      <AbsoluteFill
        style={{
          padding: mobile ? "160px 64px 330px" : "64px 100px 135px",
          display: mobile ? "flex" : "grid",
          flexDirection: mobile ? "column" : undefined,
          gridTemplateColumns: mobile ? undefined : "1.18fr 0.82fr",
          gap: mobile ? 24 : 44,
          alignItems: "center",
          justifyContent: mobile ? "center" : undefined,
        }}
      >
        {mobile && (
          <div style={{ textAlign: "center", opacity: headP }}>
            <div
              style={{
                display: "inline-block",
                background: "rgba(16, 185, 129, 0.2)",
                border: "1px solid rgba(52, 211, 153, 0.45)",
                color: "#34d399",
                fontFamily: FONT_BODY,
                fontSize: 22,
                fontWeight: 800,
                padding: "7px 20px",
                borderRadius: 999,
                marginBottom: 14,
              }}
            >
              CENTRAL DE ATENDIMENTO
            </div>
            <h2 style={{ fontFamily: FONT_DISPLAY, fontSize: 64, fontWeight: 900, lineHeight: 1.08, color: COLORS.white, margin: 0 }}>
              Chat ao vivo <span style={{ color: COLORS.emeraldLight }}>estilo Kommo</span>
            </h2>
          </div>
        )}

        <BrowserWindow
          url="https://mapaleadspro.online/app · Chat / Conversas"
          style={{
            width: "100%",
            opacity: winP,
            scale: `${interpolate(winP, [0, 1], [0.92, 1])}`,
            translate: `0px ${interpolate(winP, [0, 1], [28, 0])}px`,
          }}
        >
          <div style={{ height: mobile ? 550 : 610, overflow: "hidden" }}>
            <Img
              src={staticFile("img/ui-chat.png")}
              style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: mobile ? "right top" : "top center", scale: `${imgZoom}` }}
            />
          </div>
        </BrowserWindow>

        <div style={{ width: "100%" }}>
          {!mobile && (
            <>
              <div
                style={{
                  display: "inline-block",
                  background: "rgba(16, 185, 129, 0.2)",
                  border: "1px solid rgba(52, 211, 153, 0.45)",
                  color: "#34d399",
                  fontFamily: FONT_BODY,
                  fontSize: 21,
                  fontWeight: 800,
                  padding: "7px 20px",
                  borderRadius: 999,
                  marginBottom: 18,
                  opacity: headP,
                }}
              >
                CENTRAL DE ATENDIMENTO
              </div>

              <h2
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 60,
                  fontWeight: 900,
                  lineHeight: 1.08,
                  color: COLORS.white,
                  margin: "0 0 28px",
                  opacity: headP,
                  translate: `0px ${interpolate(headP, [0, 1], [28, 0])}px`,
                }}
              >
                Chat ao vivo <span style={{ color: COLORS.emeraldLight }}>estilo Kommo</span>
              </h2>
            </>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: mobile ? 14 : 16 }}>
            {channels.map((ch, idx) => (
              <div
                key={idx}
                style={{
                  background: "rgba(22, 34, 56, 0.92)",
                  border: `1px solid ${ch.color}55`,
                  borderRadius: 18,
                  padding: mobile ? "16px 22px" : "18px 24px",
                  opacity: ch.p,
                  translate: `${mobile ? 0 : interpolate(ch.p, [0, 1], [40, 0])}px ${mobile ? interpolate(ch.p, [0, 1], [22, 0]) : 0}px`,
                }}
              >
                <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 27 : 25, fontWeight: 800, color: ch.color }}>
                  {ch.badge}
                </div>
                <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 21 : 19, color: "#cbd5e1", marginTop: 4 }}>
                  {ch.desc}
                </div>
              </div>
            ))}
          </div>
        </div>
      </AbsoluteFill>

      <KineticCaptions sceneKey="05_chat" mobile={mobile} />
    </AbsoluteFill>
  );
};
