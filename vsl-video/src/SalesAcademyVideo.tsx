import React from "react";
import {
  AbsoluteFill,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Audio } from "@remotion/media";
import { COLORS, FONT_BODY, FONT_DISPLAY, TechBackdrop } from "./theme";
import { SALES_ACADEMY_VIDEOS, SalesVideoSpec } from "./salesAcademyData";

const AUDIO_DELAY_FRAMES = 14;

const ACCENT_MAP: Record<SalesVideoSpec["accent"], { hex: string; soft: string; light: string }> = {
  blue: { hex: "#2563eb", soft: "rgba(37, 99, 235, 0.22)", light: "#93c5fd" },
  emerald: { hex: "#10b981", soft: "rgba(16, 185, 129, 0.22)", light: "#6ee7b7" },
  purple: { hex: "#7c3aed", soft: "rgba(124, 58, 237, 0.24)", light: "#c4b5fd" },
  amber: { hex: "#f59e0b", soft: "rgba(245, 158, 11, 0.22)", light: "#fde68a" },
};

export const SalesAcademyVideo: React.FC<{ videoId: string; vertical?: boolean }> = ({
  videoId,
  vertical = false,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const spec: SalesVideoSpec =
    SALES_ACADEMY_VIDEOS.find((v) => v.id === videoId) || SALES_ACADEMY_VIDEOS[0];
  const palette = ACCENT_MAP[spec.accent] || ACCENT_MAP.blue;

  const speechTime = Math.max(0, (frame - AUDIO_DELAY_FRAMES) / fps);
  const frac = Math.min(1, Math.max(0, frame / Math.max(1, durationInFrames)));
  const isVsl = spec.kind === "vsl";

  // 3-Act Visual Pacing
  const act1End = isVsl ? 0.27 : 0.22;
  const act2End = isVsl ? 0.74 : 0.72;

  const act1Alpha = interpolate(frame, [0, 8, act1End * durationInFrames - 10, act1End * durationInFrames + 6], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const act2Alpha = interpolate(
    frame,
    [act1End * durationInFrames - 6, act1End * durationInFrames + 10, act2End * durationInFrames - 10, act2End * durationInFrames + 6],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const act3Alpha = interpolate(frame, [act2End * durationInFrames - 6, act2End * durationInFrames + 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Smooth continuous cinema Ken Burns motion
  const bgScale1 = interpolate(frac, [0, act1End + 0.05], [1.03, 1.14], { extrapolateRight: "clamp" });
  const bgScale2 = interpolate(frac, [act1End, act2End + 0.05], [1.02, 1.12], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const bgScale3 = interpolate(frac, [act2End, 1], [1.04, 1.14], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // Staggered bullet timing inside Act 2
  const act2StartFrame = Math.floor(act1End * durationInFrames);
  const act3StartFrame = Math.floor(act2End * durationInFrames);

  // Kinetic caption matcher
  let activeGroup = spec.captions.length ? spec.captions[0] : null;
  if (activeGroup) {
    for (let i = 0; i < spec.captions.length; i++) {
      const g = spec.captions[i];
      const nextStart = i + 1 < spec.captions.length ? spec.captions[i + 1].start : spec.durationSec + 2;
      if (speechTime >= g.start - 0.06 && speechTime < nextStart - 0.04) {
        activeGroup = g;
        break;
      }
      if (speechTime >= nextStart - 0.04) {
        activeGroup = spec.captions[Math.min(i + 1, spec.captions.length - 1)];
      }
    }
  }

  // ==================== VERTICAL 9:16 STORIES / REELS / STATUS LAYOUT ====================
  if (vertical) {
    const ctaPulse = 1 + Math.sin(frame / 7) * 0.025;
    return (
      <AbsoluteFill style={{ backgroundColor: COLORS.bgDark, overflow: "hidden" }}>
        <TechBackdrop accent={spec.accent === "emerald" ? "emerald" : "blue"} />

        <Audio src={staticFile("audio/bg_music.wav")} volume={0.068} loop />
        <Sequence from={AUDIO_DELAY_FRAMES}>
          <Audio src={staticFile(spec.audioFile)} volume={1.0} />
        </Sequence>
        <Sequence from={Math.max(0, act2StartFrame - 4)}>
          <Audio src={staticFile("audio/sfx_whoosh.wav")} volume={0.35} />
        </Sequence>
        <Sequence from={Math.max(0, act3StartFrame - 4)}>
          <Audio src={staticFile("audio/sfx_whoosh.wav")} volume={0.32} />
        </Sequence>

        {/* ACT 1 VERTICAL: HOOK CINEMATOGRÁFICO */}
        {act1Alpha > 0.01 && (
          <AbsoluteFill style={{ opacity: act1Alpha }}>
            <Img
              src={staticFile("img/academy/problem-hero.jpg")}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                objectPosition: "center",
                transform: `scale(${bgScale1})`,
              }}
            />
            <AbsoluteFill
              style={{
                background:
                  "linear-gradient(180deg, rgba(7,13,25,0.88) 0%, rgba(7,13,25,0.58) 42%, rgba(7,13,25,0.92) 100%)",
              }}
            />
            <div
              style={{
                position: "absolute",
                top: 155,
                left: 44,
                right: 44,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
                gap: 22,
              }}
            >
              <div
                style={{
                  display: "inline-flex",
                  padding: "9px 20px",
                  borderRadius: 99,
                  background: "rgba(239, 68, 68, 0.26)",
                  border: "1.5px solid rgba(248, 113, 113, 0.7)",
                  color: "#fecaca",
                  fontFamily: FONT_BODY,
                  fontSize: 16,
                  fontWeight: 800,
                  letterSpacing: "0.05em",
                }}
              >
                {spec.kicker}
              </div>
              <div
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 50,
                  fontWeight: 800,
                  lineHeight: 1.1,
                  color: "#ffffff",
                  textShadow: "0 12px 32px rgba(0,0,0,0.75)",
                }}
              >
                Quantos clientes estão escolhendo o seu concorrente hoje?
              </div>
              <div
                style={{
                  padding: "13px 24px",
                  borderRadius: 16,
                  background: "rgba(15, 23, 42, 0.88)",
                  border: `2px solid ${palette.hex}`,
                  color: "#ffffff",
                  fontFamily: FONT_BODY,
                  fontSize: 22,
                  fontWeight: 800,
                  boxShadow: "0 14px 36px rgba(0,0,0,0.55)",
                }}
              >
                {spec.highlightMetric}
              </div>
            </div>
          </AbsoluteFill>
        )}

        {/* ACT 2 VERTICAL: FOTO HERO NO TOPO + CARD GLASS COM BULLETS */}
        {act2Alpha > 0.01 && (
          <AbsoluteFill style={{ opacity: act2Alpha }}>
            <Img
              src={staticFile(spec.heroImage)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${bgScale2})`,
                filter: "blur(10px) brightness(0.45)",
              }}
            />
            <AbsoluteFill
              style={{
                background:
                  "linear-gradient(180deg, rgba(7,13,25,0.65) 0%, rgba(7,13,25,0.88) 55%, rgba(7,13,25,0.96) 100%)",
              }}
            />

            {/* Quadro Hero nítido no topo (respeitando safe zone de 115px) */}
            <div
              style={{
                position: "absolute",
                top: 118,
                left: 36,
                right: 36,
                height: 365,
                borderRadius: 24,
                overflow: "hidden",
                border: `2px solid ${palette.light}`,
                boxShadow: "0 24px 60px rgba(0,0,0,0.65)",
              }}
            >
              <Img
                src={staticFile(spec.heroImage)}
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                  transform: `scale(${bgScale2})`,
                }}
              />
              <div
                style={{
                  position: "absolute",
                  bottom: 14,
                  left: 16,
                  padding: "7px 15px",
                  borderRadius: 99,
                  background: "rgba(7, 13, 25, 0.86)",
                  border: `1px solid ${palette.light}`,
                  color: "#ffffff",
                  fontFamily: FONT_BODY,
                  fontSize: 15,
                  fontWeight: 800,
                }}
              >
                {spec.highlightMetric}
              </div>
            </div>

            {/* Card Glass Estratégia abaixo do Hero */}
            <div
              style={{
                position: "absolute",
                top: 506,
                left: 36,
                right: 36,
                background: "rgba(15, 23, 42, 0.90)",
                border: `1.5px solid ${palette.light}`,
                borderRadius: 22,
                padding: "24px 24px",
                boxShadow: "0 24px 55px rgba(0,0,0,0.65)",
                display: "flex",
                flexDirection: "column",
                gap: 14,
              }}
            >
              <div style={{ fontFamily: FONT_BODY, fontSize: 13.5, fontWeight: 800, color: palette.light, letterSpacing: "0.05em" }}>
                {spec.kicker}
              </div>
              <div style={{ fontFamily: FONT_DISPLAY, fontSize: 31, fontWeight: 800, color: "#fff", lineHeight: 1.12 }}>
                {spec.title}
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 4 }}>
                {spec.bullets.map((b, i) => {
                  const enter = spring({
                    frame: Math.max(0, frame - (act2StartFrame + i * 22)),
                    fps,
                    config: { damping: 14, stiffness: 120 },
                  });
                  return (
                    <div
                      key={i}
                      style={{
                        opacity: enter,
                        transform: `translateY(${interpolate(enter, [0, 1], [18, 0])}px)`,
                        display: "flex",
                        alignItems: "center",
                        gap: 13,
                        background: "rgba(255,255,255,0.07)",
                        border: "1px solid rgba(255,255,255,0.12)",
                        borderRadius: 14,
                        padding: "13px 15px",
                      }}
                    >
                      <div
                        style={{
                          width: 28,
                          height: 28,
                          borderRadius: 99,
                          background: palette.hex,
                          color: "#fff",
                          display: "grid",
                          placeItems: "center",
                          fontFamily: FONT_DISPLAY,
                          fontSize: 15,
                          fontWeight: 800,
                          flexShrink: 0,
                        }}
                      >
                        ✓
                      </div>
                      <span style={{ fontFamily: FONT_BODY, fontSize: 19, fontWeight: 600, color: "#f8fafc", lineHeight: 1.3 }}>
                        {b}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </AbsoluteFill>
        )}

        {/* ACT 3 VERTICAL: PROVA SOCIAL & CTA PULSANTE */}
        {act3Alpha > 0.01 && (
          <AbsoluteFill style={{ opacity: act3Alpha }}>
            <Img
              src={staticFile(spec.uiImage)}
              style={{
                width: "100%",
                height: "100%",
                objectFit: "cover",
                objectPosition: "center",
                transform: `scale(${bgScale3})`,
              }}
            />
            <AbsoluteFill
              style={{
                background:
                  "linear-gradient(180deg, rgba(7,13,25,0.86) 0%, rgba(7,13,25,0.62) 48%, rgba(7,13,25,0.94) 100%)",
              }}
            />
            <div
              style={{
                position: "absolute",
                top: 230,
                left: 42,
                right: 42,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                textAlign: "center",
                gap: 24,
              }}
            >
              <div
                style={{
                  padding: "10px 22px",
                  borderRadius: 99,
                  background: "rgba(16, 185, 129, 0.24)",
                  border: "1.5px solid #34d399",
                  color: "#6ee7b7",
                  fontFamily: FONT_BODY,
                  fontSize: 16,
                  fontWeight: 800,
                  letterSpacing: "0.04em",
                }}
              >
                ENTREGA RÁPIDA &amp; RESULTADO IMEDIATO
              </div>
              <div
                style={{
                  fontFamily: FONT_DISPLAY,
                  fontSize: 50,
                  fontWeight: 800,
                  color: "#ffffff",
                  lineHeight: 1.12,
                  textShadow: "0 12px 35px rgba(0,0,0,0.75)",
                }}
              >
                Receba sua prévia personalizada ainda hoje
              </div>
              <div
                style={{
                  marginTop: 8,
                  padding: "20px 34px",
                  borderRadius: 18,
                  background: "linear-gradient(135deg, #10b981, #059669)",
                  color: "#ffffff",
                  fontFamily: FONT_DISPLAY,
                  fontSize: 25,
                  fontWeight: 800,
                  boxShadow: "0 20px 45px rgba(16, 185, 129, 0.5)",
                  transform: `scale(${ctaPulse})`,
                }}
              >
                Responda esta mensagem agora!
              </div>
            </div>
          </AbsoluteFill>
        )}

        {/* Legendas Dinâmicas na Zona Segura de Stories / Reels (bottom: 185px) */}
        {activeGroup && speechTime > 0 && (
          <div
            style={{
              position: "absolute",
              bottom: 182,
              left: 34,
              right: 34,
              display: "flex",
              justifyContent: "center",
              pointerEvents: "none",
              zIndex: 25,
            }}
          >
            <div
              style={{
                background: "rgba(7, 13, 25, 0.92)",
                border: "1.5px solid rgba(255,255,255,0.22)",
                borderRadius: 16,
                padding: "13px 22px",
                boxShadow: "0 16px 40px rgba(0,0,0,0.8)",
                display: "flex",
                flexWrap: "wrap",
                justifyContent: "center",
                gap: 9,
              }}
            >
              {activeGroup.words.map((w, idx) => {
                const isCurrent = speechTime >= w.start - 0.04 && speechTime <= w.end + 0.14;
                const spoken = speechTime >= w.start - 0.04;
                return (
                  <span
                    key={`${activeGroup!.start}-${idx}`}
                    style={{
                      fontFamily: FONT_DISPLAY,
                      fontSize: 26,
                      fontWeight: 800,
                      color: isCurrent ? COLORS.emeraldLight : spoken ? "#ffffff" : "#94a3b8",
                    }}
                  >
                    {w.word}
                  </span>
                );
              })}
            </div>
          </div>
        )}
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bgDark, overflow: "hidden" }}>
      <TechBackdrop accent={spec.accent === "emerald" ? "emerald" : "blue"} />

      {/* Audio Stack: Warm ambient bed + Studio-Mastered Voiceover + Crisp Transitions */}
      <Audio src={staticFile("audio/bg_music.wav")} volume={isVsl ? 0.065 : 0.045} loop />
      <Sequence from={AUDIO_DELAY_FRAMES}>
        <Audio src={staticFile(spec.audioFile)} volume={1.0} />
      </Sequence>
      <Sequence from={Math.max(0, act2StartFrame - 4)}>
        <Audio src={staticFile("audio/sfx_whoosh.wav")} volume={0.35} />
      </Sequence>
      <Sequence from={Math.max(0, act3StartFrame - 4)}>
        <Audio src={staticFile("audio/sfx_whoosh.wav")} volume={0.32} />
      </Sequence>

      {/* ============ ACT 1 ============ */}
      {act1Alpha > 0.01 && (
        <AbsoluteFill style={{ opacity: act1Alpha }}>
          <Img
            src={staticFile(isVsl ? "img/academy/problem-hero.jpg" : spec.heroImage)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${bgScale1})`,
            }}
          />
          <AbsoluteFill
            style={{
              background: isVsl
                ? "linear-gradient(90deg, rgba(7,13,25,0.88) 0%, rgba(7,13,25,0.52) 55%, rgba(7,13,25,0.22) 100%)"
                : "linear-gradient(135deg, rgba(7,13,25,0.88) 0%, rgba(15,23,42,0.68) 100%)",
            }}
          />
          <div
            style={{
              position: "absolute",
              left: 68,
              top: 120,
              maxWidth: 680,
              display: "flex",
              flexDirection: "column",
              gap: 16,
            }}
          >
            <div
              style={{
                display: "inline-flex",
                alignSelf: "flex-start",
                padding: "7px 16px",
                borderRadius: 99,
                background: isVsl ? "rgba(239, 68, 68, 0.22)" : palette.soft,
                border: `1px solid ${isVsl ? "rgba(248, 113, 113, 0.55)" : palette.light}`,
                color: isVsl ? "#fca5a5" : palette.light,
                fontFamily: FONT_BODY,
                fontSize: 15,
                fontWeight: 800,
                letterSpacing: "0.04em",
              }}
            >
              {spec.kicker}
            </div>
            <div
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 54,
                fontWeight: 800,
                lineHeight: 1.08,
                color: "#ffffff",
                textShadow: "0 10px 30px rgba(0,0,0,0.65)",
              }}
            >
              {isVsl ? "Quantos clientes estão escolhendo o seu concorrente hoje?" : spec.title}
            </div>
            <div
              style={{
                display: "inline-flex",
                alignSelf: "flex-start",
                padding: "9px 18px",
                borderRadius: 12,
                background: "rgba(15, 23, 42, 0.85)",
                border: `1px solid ${palette.hex}`,
                color: "#ffffff",
                fontFamily: FONT_BODY,
                fontSize: 20,
                fontWeight: 700,
              }}
            >
              {spec.highlightMetric}
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ============ ACT 2: HERO COMMERCIAL + FLOATING GLASS CARD ============ */}
      {act2Alpha > 0.01 && (
        <AbsoluteFill style={{ opacity: act2Alpha }}>
          <Img
            src={staticFile(spec.heroImage)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${bgScale2}) translateX(-5%)`,
            }}
          />
          <AbsoluteFill
            style={{
              background:
                "linear-gradient(90deg, rgba(7,13,25,0.18) 0%, rgba(7,13,25,0.52) 52%, rgba(7,13,25,0.92) 100%)",
            }}
          />

          {/* Right-side Glassmorphic Strategy / Value Card */}
          <div
            style={{
              position: "absolute",
              right: 34,
              top: 78,
              width: 480,
              background: "rgba(15, 23, 42, 0.86)",
              border: `1px solid ${palette.light}`,
              borderRadius: 20,
              padding: "24px 26px",
              boxShadow: "0 28px 65px rgba(0,0,0,0.65)",
              display: "flex",
              flexDirection: "column",
              gap: 14,
            }}
          >
            <div style={{ fontFamily: FONT_BODY, fontSize: 12.5, fontWeight: 800, color: palette.light, letterSpacing: "0.05em" }}>
              {spec.kicker}
            </div>
            <div style={{ fontFamily: FONT_DISPLAY, fontSize: 30, fontWeight: 800, color: "#fff", lineHeight: 1.12 }}>
              {spec.title}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12, marginTop: 4 }}>
              {spec.bullets.map((b, i) => {
                const enter = spring({
                  frame: Math.max(0, frame - (act2StartFrame + i * 24)),
                  fps,
                  config: { damping: 14, stiffness: 120 },
                });
                return (
                  <div
                    key={i}
                    style={{
                      opacity: enter,
                      transform: `translateX(${interpolate(enter, [0, 1], [24, 0])}px)`,
                      display: "flex",
                      alignItems: "center",
                      gap: 12,
                      background: "rgba(255,255,255,0.06)",
                      border: "1px solid rgba(255,255,255,0.10)",
                      borderRadius: 12,
                      padding: "11px 14px",
                    }}
                  >
                    <div
                      style={{
                        width: 26,
                        height: 26,
                        borderRadius: 99,
                        background: palette.hex,
                        color: "#fff",
                        display: "grid",
                        placeItems: "center",
                        fontFamily: FONT_DISPLAY,
                        fontSize: 14,
                        fontWeight: 800,
                        flexShrink: 0,
                      }}
                    >
                      ✓
                    </div>
                    <span style={{ fontFamily: FONT_BODY, fontSize: 17, fontWeight: 600, color: "#f1f5f9", lineHeight: 1.3 }}>
                      {b}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* ============ ACT 3: PROOF / RESULTS / CALL TO ACTION ============ */}
      {act3Alpha > 0.01 && (
        <AbsoluteFill style={{ opacity: act3Alpha }}>
          <Img
            src={staticFile(spec.uiImage)}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${bgScale3})`,
            }}
          />
          <AbsoluteFill
            style={{
              background: isVsl
                ? "linear-gradient(90deg, rgba(7,13,25,0.88) 0%, rgba(7,13,25,0.62) 55%, rgba(7,13,25,0.28) 100%)"
                : "linear-gradient(180deg, rgba(7,13,25,0.82) 0%, rgba(7,13,25,0.86) 100%)",
            }}
          />

          <div
            style={{
              position: "absolute",
              left: 68,
              right: 68,
              top: 125,
              display: "flex",
              flexDirection: "column",
              alignItems: isVsl ? "flex-start" : "center",
              textAlign: isVsl ? "left" : "center",
              gap: 18,
            }}
          >
            <div
              style={{
                padding: "8px 18px",
                borderRadius: 99,
                background: "rgba(16, 185, 129, 0.22)",
                border: "1px solid #34d399",
                color: "#6ee7b7",
                fontFamily: FONT_BODY,
                fontSize: 15,
                fontWeight: 800,
              }}
            >
              {isVsl ? "ENTREGA RÁPIDA & RESULTADO IMEDIATO" : "PRÓXIMO PASSO NO MAPALEADS PRO"}
            </div>
            <div
              style={{
                fontFamily: FONT_DISPLAY,
                fontSize: 50,
                fontWeight: 800,
                color: "#ffffff",
                maxWidth: 820,
                lineHeight: 1.1,
                textShadow: "0 12px 35px rgba(0,0,0,0.7)",
              }}
            >
              {isVsl
                ? "Receba sua prévia personalizada ainda hoje"
                : "Filtre os leads no CRM e envie sua copy + VSL agora"}
            </div>
            <div
              style={{
                marginTop: 6,
                padding: "16px 30px",
                borderRadius: 16,
                background: "linear-gradient(135deg, #10b981, #059669)",
                color: "#ffffff",
                fontFamily: FONT_DISPLAY,
                fontSize: 22,
                fontWeight: 800,
                boxShadow: "0 18px 40px rgba(16, 185, 129, 0.45)",
              }}
            >
              {isVsl ? "Responda esta mensagem agora!" : spec.highlightMetric}
            </div>
          </div>
        </AbsoluteFill>
      )}

      {/* Subtle course badge top-left ONLY for internal PRO course (never on downloadable White-Label VSL!) */}
      {!isVsl && (
        <div
          style={{
            position: "absolute",
            top: 22,
            left: 26,
            display: "flex",
            alignItems: "center",
            gap: 10,
            background: "rgba(7, 13, 25, 0.86)",
            border: "1px solid rgba(255,255,255,0.16)",
            padding: "7px 14px",
            borderRadius: 99,
            zIndex: 20,
          }}
        >
          <Img src={staticFile("img/app-icon-1024.png")} style={{ width: 22, height: 22, borderRadius: 6 }} />
          <span style={{ fontFamily: FONT_DISPLAY, fontSize: 13, fontWeight: 800, color: "#fde68a" }}>
            ACADEMIA DE VENDAS PRO
          </span>
        </div>
      )}

      {/* Crisp Lower-Third Subtitles */}
      {activeGroup && speechTime > 0 && (
        <div
          style={{
            position: "absolute",
            bottom: 24,
            left: 70,
            right: 70,
            display: "flex",
            justifyContent: "center",
            pointerEvents: "none",
            zIndex: 25,
          }}
        >
          <div
            style={{
              background: "rgba(7, 13, 25, 0.90)",
              border: "1px solid rgba(255,255,255,0.18)",
              borderRadius: 14,
              padding: "10px 24px",
              boxShadow: "0 14px 35px rgba(0,0,0,0.75)",
              display: "flex",
              flexWrap: "wrap",
              justifyContent: "center",
              gap: 9,
            }}
          >
            {activeGroup.words.map((w, idx) => {
              const isCurrent = speechTime >= w.start - 0.04 && speechTime <= w.end + 0.14;
              const spoken = speechTime >= w.start - 0.04;
              return (
                <span
                  key={`${activeGroup!.start}-${idx}`}
                  style={{
                    fontFamily: FONT_DISPLAY,
                    fontSize: 23,
                    fontWeight: 800,
                    color: isCurrent ? COLORS.emeraldLight : spoken ? "#ffffff" : "#94a3b8",
                  }}
                >
                  {w.word}
                </span>
              );
            })}
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};

