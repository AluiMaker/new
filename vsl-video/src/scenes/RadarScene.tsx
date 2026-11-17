import React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BrowserWindow, COLORS, FONT_BODY, FONT_DISPLAY, SubtitleBar, TechBackdrop, easeOut, popIn } from "../theme";

export const RadarScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const headP = popIn(frame, fps, 4);
  const winP = popIn(frame, fps, 14);
  const pill1 = popIn(frame, fps, 70);
  const pill2 = popIn(frame, fps, 140);
  const pill3 = popIn(frame, fps, 210);

  const leadsCounter = Math.round(easeOut(frame, 45, 290, 0, 147));
  const noSiteCounter = Math.round(easeOut(frame, 60, 290, 0, 89));
  const imgZoom = interpolate(frame, [0, 385], [1, 1.06], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill>
      <TechBackdrop accent="blue" />

      <AbsoluteFill
        style={{
          padding: "70px 100px 135px",
          display: "grid",
          gridTemplateColumns: "0.85fr 1.15fr",
          gap: 54,
          alignItems: "center",
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
              fontSize: 22,
              fontWeight: 800,
              padding: "8px 20px",
              borderRadius: 999,
              marginBottom: 20,
              opacity: headP,
            }}
          >
            MAPALEADS PRO · RADAR GOOGLE
          </div>

          <h2
            style={{
              fontFamily: FONT_DISPLAY,
              fontSize: 64,
              fontWeight: 900,
              lineHeight: 1.08,
              color: COLORS.white,
              margin: "0 0 28px",
              opacity: headP,
              translate: `0px ${interpolate(headP, [0, 1], [30, 0])}px`,
            }}
          >
            Varre ruas e cidades <span style={{ color: COLORS.emeraldLight }}>em segundos</span>
          </h2>

          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            {[
              { p: pill1, icon: "📍", title: "Busca por Rua Inteira, Bairro ou Cidade", sub: "Pega todas as empresas do mapa" },
              { p: pill2, icon: "📱", title: "Extrai WhatsApp e Telefone Limpo", sub: "Pronto para abordar sem perder tempo" },
              { p: pill3, icon: "🎯", title: "Detecta Falhas Digitais na Hora", sub: "Sem site ou poucas avaliações no Google" },
            ].map((item, i) => (
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
        </div>

        <div style={{ position: "relative" }}>
          <BrowserWindow
            url="https://mapaleadspro.online/app · Busca Ativa"
            style={{
              opacity: winP,
              scale: `${interpolate(winP, [0, 1], [0.92, 1])}`,
              translate: `0px ${interpolate(winP, [0, 1], [32, 0])}px`,
            }}
          >
            <div style={{ overflow: "hidden", height: 590 }}>
              <Img
                src={staticFile("img/ui-search.png")}
                style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "top left", scale: `${imgZoom}` }}
              />
            </div>
          </BrowserWindow>

          {/* Live animated radar KPI pill */}
          <div
            style={{
              position: "absolute",
              bottom: -24,
              right: 28,
              background: "linear-gradient(135deg, #059669, #10b981)",
              color: "#fff",
              borderRadius: 18,
              padding: "16px 28px",
              boxShadow: "0 20px 45px -10px rgba(16,185,129,0.65)",
              display: "flex",
              gap: 28,
              alignItems: "center",
              opacity: pill1,
            }}
          >
            <div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: 40, fontWeight: 900, lineHeight: 1 }}>
                +{leadsCounter}
              </div>
              <div style={{ fontFamily: FONT_BODY, fontSize: 16, fontWeight: 600, opacity: 0.92 }}>
                Empresas com WhatsApp
              </div>
            </div>
            <div style={{ width: 1, height: 46, background: "rgba(255,255,255,0.3)" }} />
            <div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: 40, fontWeight: 900, lineHeight: 1 }}>
                {noSiteCounter}
              </div>
              <div style={{ fontFamily: FONT_BODY, fontSize: 16, fontWeight: 600, opacity: 0.92 }}>
                Sem Site Próprio
              </div>
            </div>
          </div>
        </div>
      </AbsoluteFill>

      <SubtitleBar text="Conheça o MapaLeads PRO: varre ruas, bairros e cidades no Google, extrai o WhatsApp e detecta falhas digitais." />
    </AbsoluteFill>
  );
};

