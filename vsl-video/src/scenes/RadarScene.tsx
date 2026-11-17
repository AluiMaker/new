import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BrowserWindow, COLORS, FONT_BODY, FONT_DISPLAY, KineticCaptions, SceneProps, SceneSfxCue, TechBackdrop, easeOut, popIn } from "../theme";

export const RadarScene: React.FC<SceneProps> = ({ mobile }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const winP = popIn(frame, fps, 12);
  const pill1 = popIn(frame, fps, 55);
  const pill2 = popIn(frame, fps, 125);
  const pill3 = popIn(frame, fps, 195);

  const leadsCounter = Math.round(easeOut(frame, 35, 260, 0, 147));
  const noSiteCounter = Math.round(easeOut(frame, 48, 260, 0, 89));
  const imgZoom = interpolate(frame, [0, 358], [1, 1.07], { extrapolateRight: "clamp" });

  const bullets = [
    { p: pill1, icon: "📍", title: "Rua Inteira, Bairro ou Cidade", sub: "Varre todas as empresas do mapa" },
    { p: pill2, icon: "📱", title: "Extrai WhatsApp do Dono", sub: "Telefones limpos e prontos" },
    { p: pill3, icon: "🎯", title: "Detecta Falhas na Hora", sub: "Sem site ou poucas avaliações" },
  ];

  return (
    <AbsoluteFill>
      <TechBackdrop accent="blue" />
      <SceneSfxCue file="audio/sfx_whoosh.wav" atFrame={0} volume={0.32} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={55} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={125} volume={0.25} />
      <SceneSfxCue file="audio/sfx_pop.wav" atFrame={195} volume={0.25} />
      <SceneSfxCue file="audio/sfx_tick.wav" atFrame={60} volume={0.18} />
      <SceneSfxCue file="audio/sfx_tick.wav" atFrame={95} volume={0.18} />
      <SceneSfxCue file="audio/sfx_tick.wav" atFrame={130} volume={0.18} />

      <AbsoluteFill
        style={{
          padding: mobile ? "160px 64px 330px" : "70px 100px 135px",
          display: mobile ? "flex" : "grid",
          flexDirection: mobile ? "column" : undefined,
          gridTemplateColumns: mobile ? undefined : "0.85fr 1.15fr",
          gap: mobile ? 30 : 54,
          alignItems: "center",
          justifyContent: mobile ? "center" : undefined,
        }}
      >
        <div style={{ width: "100%", textAlign: mobile ? "center" : "left" }}>
          <div
            style={{
              display: "inline-block",
              background: "rgba(37, 99, 235, 0.24)",
              border: "1px solid rgba(96, 165, 250, 0.5)",
              color: "#93c5fd",
              fontFamily: FONT_BODY,
              fontSize: mobile ? 23 : 22,
              fontWeight: 800,
              padding: "8px 20px",
              borderRadius: 999,
              marginBottom: 16,
              opacity: headP,
            }}
          >
            MAPALEADS PRO · RADAR GOOGLE
          </div>

          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: mobile ? 68 : 64,
              fontWeight: 900,
              lineHeight: 1.07,
              color: COLORS.white,
              margin: mobile ? "0 0 22px" : "0 0 28px",
              opacity: headP,
              translate: `0px ${interpolate(headP, [0, 1], [30, 0])}px`,
            }}
          >
            Varre ruas e cidades <span style={{ color: COLORS.emeraldLight }}>em segundos</span>
          </h2>

          {!mobile && (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              {bullets.map((item, i) => (
                <div
                  key={i}
                  style={{
                    background: "rgba(22, 34, 56, 0.9)",
                    border: "1px solid rgba(96, 165, 250, 0.28)",
                    borderRadius: 16,
                    padding: "16px 22px",
                    display: "flex",
                    alignItems: "center",
                    gap: 16,
                    opacity: item.p,
                    translate: `${interpolate(item.p, [0, 1], [-36, 0])}px 0px`,
                  }}
                >
                  <div style={{ fontSize: 32 }}>{item.icon}</div>
                  <div>
                    <div style={{ fontFamily: FONT_DISPLAY, fontSize: 23, fontWeight: 800, color: "#fff" }}>
                      {item.title}
                    </div>
                    <div style={{ fontFamily: FONT_BODY, fontSize: 19, color: COLORS.muted }}>{item.sub}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ position: "relative", width: "100%" }}>
          <BrowserWindow
            url="https://mapaleadspro.online/app · Radar Ativo"
            style={{
              opacity: winP,
              scale: `${interpolate(winP, [0, 1], [0.92, 1])}`,
              translate: `0px ${interpolate(winP, [0, 1], [32, 0])}px`,
            }}
          >
            <div style={{ overflow: "hidden", height: mobile ? 520 : 590 }}>
              <Img
                src={staticFile("img/ui-search.png")}
                style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top left", scale: `${imgZoom}` }}
              />
            </div>
          </BrowserWindow>

          <div
            style={{
              position: mobile ? "relative" : "absolute",
              bottom: mobile ? undefined : -24,
              right: mobile ? undefined : 28,
              marginTop: mobile ? 22 : 0,
              background: "linear-gradient(135deg, #059669, #10b981)",
              color: "#fff",
              borderRadius: 18,
              padding: mobile ? "18px 28px" : "16px 28px",
              boxShadow: "0 20px 45px -10px rgba(16,185,129,0.65)",
              display: "flex",
              gap: 28,
              alignItems: "center",
              justifyContent: "center",
              opacity: pill1,
            }}
          >
            <div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 46 : 40, fontWeight: 900, lineHeight: 1 }}>
                +{leadsCounter}
              </div>
              <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 19 : 16, fontWeight: 700, opacity: 0.94 }}>
                Empresas com WhatsApp
              </div>
            </div>
            <div style={{ width: 1, height: 48, background: "rgba(255,255,255,0.35)" }} />
            <div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: mobile ? 46 : 40, fontWeight: 900, lineHeight: 1 }}>
                {noSiteCounter}
              </div>
              <div style={{ fontFamily: FONT_BODY, fontSize: mobile ? 19 : 16, fontWeight: 700, opacity: 0.94 }}>
                Sem Site Próprio
              </div>
            </div>
          </div>

          {mobile && (
            <div style={{ display: "flex", flexDirection: "column", gap: 10, marginTop: 18 }}>
              {bullets.map((item, i) => (
                <div
                  key={i}
                  style={{
                    background: "rgba(22, 34, 56, 0.9)",
                    border: "1px solid rgba(96, 165, 250, 0.32)",
                    borderRadius: 14,
                    padding: "12px 18px",
                    display: "flex",
                    alignItems: "center",
                    gap: 14,
                    opacity: item.p,
                    translate: `0px ${interpolate(item.p, [0, 1], [18, 0])}px`,
                  }}
                >
                  <div style={{ fontSize: 30 }}>{item.icon}</div>
                  <div>
                    <div style={{ fontFamily: FONT_DISPLAY, fontSize: 24, fontWeight: 800, color: "#fff" }}>
                      {item.title}
                    </div>
                    <div style={{ fontFamily: FONT_BODY, fontSize: 19, color: COLORS.muted }}>{item.sub}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </AbsoluteFill>

      <KineticCaptions sceneKey="02_radar" mobile={mobile} />
    </AbsoluteFill>
  );
};
