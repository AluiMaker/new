import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { fade } from "@remotion/transitions/fade";

import { HookScene } from "./scenes/HookScene";
import { RadarScene } from "./scenes/RadarScene";
import { OffersScene } from "./scenes/OffersScene";
import { CrmScene } from "./scenes/CrmScene";
import { ChatScene } from "./scenes/ChatScene";
import { CtaScene } from "./scenes/CtaScene";

export const SCENE_DURATIONS = {
  hook: 210,     // VO 6.22s
  radar: 385,    // VO 11.90s
  ofertas: 400,  // VO 12.50s
  crm: 245,      // VO 7.25s
  chat: 305,     // VO 9.26s
  cta: 375,      // VO 11.18s
  transition: 15,
};

export const TOTAL_VSL_FRAMES =
  SCENE_DURATIONS.hook +
  SCENE_DURATIONS.radar +
  SCENE_DURATIONS.ofertas +
  SCENE_DURATIONS.crm +
  SCENE_DURATIONS.chat +
  SCENE_DURATIONS.cta -
  5 * SCENE_DURATIONS.transition;

export const MapaLeadsVSL: React.FC = () => {
  const t = linearTiming({ durationInFrames: SCENE_DURATIONS.transition });

  return (
    <AbsoluteFill style={{ backgroundColor: "#070d19" }}>
      <Audio src={staticFile("audio/bg_music.wav")} volume={0.14} loop />

      <TransitionSeries>
        <TransitionSeries.Sequence name="1. Hook / Dor" durationInFrames={SCENE_DURATIONS.hook}>
          <HookScene />
          <Audio src={staticFile("audio/01_hook.mp3")} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={wipe({ direction: "from-left" })} timing={t} />

        <TransitionSeries.Sequence name="2. Radar Google" durationInFrames={SCENE_DURATIONS.radar}>
          <RadarScene />
          <Audio src={staticFile("audio/02_radar.mp3")} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={t} />

        <TransitionSeries.Sequence name="3. Ofertas & ROI" durationInFrames={SCENE_DURATIONS.ofertas}>
          <OffersScene />
          <Audio src={staticFile("audio/03_ofertas.mp3")} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={t} />

        <TransitionSeries.Sequence name="4. CRM Kanban" durationInFrames={SCENE_DURATIONS.crm}>
          <CrmScene />
          <Audio src={staticFile("audio/04_crm.mp3")} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={t} />

        <TransitionSeries.Sequence name="5. Chat Kommo" durationInFrames={SCENE_DURATIONS.chat}>
          <ChatScene />
          <Audio src={staticFile("audio/05_chat.mp3")} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={fade()} timing={t} />

        <TransitionSeries.Sequence name="6. Oferta & CTA" durationInFrames={SCENE_DURATIONS.cta}>
          <CtaScene />
          <Audio src={staticFile("audio/06_cta.mp3")} volume={1} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};

