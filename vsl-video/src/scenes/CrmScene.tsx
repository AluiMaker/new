import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BrowserWindow, COLORS, FONT_BODY, FONT_DISPLAY, KineticCaptions, SceneProps, SceneSfxCue, TechBackdrop, popIn } from "../theme";

export const CrmScene: React.FC<SceneProps> = ({ mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const winP = popIn(frame, fps, 14);
  const pill1 = popIn(frame, fps, 55);
  const pill2 = popIn(frame, fps, 115);
  const pill3 = popIn(frame, fps, 175);

  const imgPan = interpolate(frame, [0, 326], [1, 1.06], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <TechBackdrop accent="blue" />
      <SceneSfxCue file="audio/sfx_whoosh.wav" atFrame={0} volume={0.32} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={55} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={115} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={175} volume={0.25} />

      <AbsoluteFill
        style={{
          padding: mobile ? "160px 64px 330px" : "64px 100px 135px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          gap: mobile ? 24 : 0,
        }}
      >
        <div
          style={{
            display: "flex",
            flexDirection: mobile ? "column" : "row",
            justifyContent: "space-between",
            alignItems: mobile ? "center" : "flex-end",
            textAlign: mobile ? "center" : "left",
            marginBottom: mobile ? 6 : 24,
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
                fontSize: mobile ? 22 : 20,
                fontWeight: 800,
                padding: "7px 20px",
                borderRadius: 999,
                marginBottom: 12,
              }}
            >
              ORGANIZAÇÃO + ANTI-BLOQUEIO
            </div>
            <h2 style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 60 : 56, fontWeight: 900, lineHeight: 1.08, color: COLORS.white, margin: 0 }}>
              CRM Kanban + <span style={{ color: COLORS.primaryLight }}>Quebra-Gelo</span>
            </h2>
          </div>

          {!mobile && (
            <div style={{ display: "flex", gap: 12 }}>
              <div
                style={{
                  background: "rgba(22, 34, 56, 0.92)",
                  border: "1px solid rgba(96, 165, 250, 0.4)",
                  borderRadius: 14,
                  padding: "12px 18px",
                  color: "#fff",
                  fontFamily: FONT_BODY,
                  fontSize: 20,
                  fontWeight: 700,
                  opacity: pill1,
                  scale: `${interpolate(pill1, [0, 1], [0.85, 1])}`,
                }}
              >
                🏷️ Etiquetas Auto
              </div>
              <div
                style={{
                  background: "rgba(234, 88, 12, 0.2)",
                  border: "1px solid rgba(251, 146, 60, 0.45)",
                  borderRadius: 14,
                  padding: "12px 18px",
                  color: "#fdba74",
                  fontFamily: FONT_BODY,
                  fontSize: 20,
                  fontWeight: 700,
                  opacity: pill2,
                  scale: `${interpolate(pill2, [0, 1], [0.85, 1])}`,
                }}
              >
                📵 Limpa Sem WA
              </div>
              <div
                style={{
                  background: "rgba(16, 185, 129, 0.2)",
                  border: "1px solid rgba(52, 211, 153, 0.45)",
                  borderRadius: 14,
                  padding: "12px 18px",
                  color: "#34d399",
                  fontFamily: FONT_BODY,
                  fontSize: 20,
                  fontWeight: 700,
                  opacity: pill3,
                  scale: `${interpolate(pill3, [0, 1], [0.85, 1])}`,
                }}
              >
                🧊 Copys Anti-Bloqueio
              </div>
            </div>
          )}
        </div>

        <BrowserWindow
          url="https://mapaleadspro.online/app · CRM & Pipeline"
          style={{
            opacity: winP,
            scale: `${interpolate(winP, [0, 1], [0.94, 1])}`,
            translate: `0px ${interpolate(winP, [0, 1], [30, 0])}px`,
          }}
        >
          <div style={{ height: mobile ? 590 : 610, overflow: "hidden" }}>
            <Img
              src={staticFile("img/ui-crm.png")}
              style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top left", scale: `${imgPan}` }}
            />
          </div>
        </BrowserWindow>

        {mobile && (
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            {[
              { p: pill1, txt: "🏷️ Etiquetas Automáticas por Oferta", border: "rgba(96, 165, 250, 0.45)", color: "#fff" },
              { p: pill2, txt: "📵 Filtra e Exclui quem Não Tem WhatsApp", border: "rgba(251, 146, 60, 0.45)", color: "#fdba74" },
              { p: pill3, txt: "🧊 Modelos Curtos Anti-Bloqueio", border: "rgba(52, 211, 153, 0.45)", color: "#34d399" },
            ].map((b, i) => (
              <div
                key={i}
                style={{
                  background: "rgba(22, 34, 56, 0.92)",
                  border: `1px solid ${b.border}`,
                  borderRadius: 16,
                  padding: "18px 24px",
                  color: b.color,
                  fontFamily: FONT_BODY,
                  fontSize: 26,
                  fontWeight: 700,
                  opacity: b.p,
                  translate: `0px ${interpolate(b.p, [0, 1], [22, 0])}px`,
                }}
              >
                {b.txt}
              </div>
            ))}
          </div>
        )}
      </AbsoluteFill>

      <KineticCaptions sceneKey="04_crm" mobile={mobile} />
    </AbsoluteFill>
  );
};
