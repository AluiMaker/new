import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { Audio } from "@remotion/media";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { fade } from "@remotion/transitions/fade";

import { VO_DATA } from "./voData";
import { HookScene } from "./scenes/HookScene";
import { RadarScene } from "./scenes/RadarScene";
import { OffersScene } from "./scenes/OffersScene";
import { CrmScene } from "./scenes/CrmScene";
import { ChatScene } from "./scenes/ChatScene";
import { CtaScene } from "./scenes/CtaScene";

export const TRANSITION_FRAMES = 15;

export const SCENE_DURATIONS = {
  hook: VO_DATA["01_hook"].durationInFrames,
  radar: VO_DATA["02_radar"].durationInFrames,
  ofertas: VO_DATA["03_ofertas"].durationInFrames,
  crm: VO_DATA["04_crm"].durationInFrames,
  chat: VO_DATA["05_chat"].durationInFrames,
  cta: VO_DATA["06_cta"].durationInFrames,
};

export const TOTAL_VSL_FRAMES =
  SCENE_DURATIONS.hook +
  SCENE_DURATIONS.radar +
  SCENE_DURATIONS.ofertas +
  SCENE_DURATIONS.crm +
  SCENE_DURATIONS.chat +
  SCENE_DURATIONS.cta -
  5 * TRANSITION_FRAMES;

export const MapaLeadsVSL: React.FC<{ mobile?: boolean }> = ({ mobile = false }) => {
  const t = linearTiming({ durationInFrames: TRANSITION_FRAMES });

  return (
    <AbsoluteFill style={{ backgroundColor: "#070d19" }}>
      <Audio src={staticFile("audio/bg_music.wav")} volume={0.11} loop />

      <TransitionSeries>
        <TransitionSeries.Sequence name="1. Hook / Dor" durationInFrames={SCENE_DURATIONS.hook}>
          <HookScene mobile={mobile} />
          <Audio src={staticFile(VO_DATA["01_hook"].file)} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={wipe({ direction: "from-left" })} timing={t} />

        <TransitionSeries.Sequence name="2. Radar Google" durationInFrames={SCENE_DURATIONS.radar}>
          <RadarScene mobile={mobile} />
          <Audio src={staticFile(VO_DATA["02_radar"].file)} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={t} />

        <TransitionSeries.Sequence name="3. Ofertas & ROI" durationInFrames={SCENE_DURATIONS.ofertas}>
          <OffersScene mobile={mobile} />
          <Audio src={staticFile(VO_DATA["03_ofertas"].file)} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={slide({ direction: "from-bottom" })} timing={t} />

        <TransitionSeries.Sequence name="4. CRM Kanban" durationInFrames={SCENE_DURATIONS.crm}>
          <CrmScene mobile={mobile} />
          <Audio src={staticFile(VO_DATA["04_crm"].file)} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={slide({ direction: "from-right" })} timing={t} />

        <TransitionSeries.Sequence name="5. Chat Kommo" durationInFrames={SCENE_DURATIONS.chat}>
          <ChatScene mobile={mobile} />
          <Audio src={staticFile(VO_DATA["05_chat"].file)} volume={1} />
        </TransitionSeries.Sequence>

        <TransitionSeries.Transition presentation={fade()} timing={t} />

        <TransitionSeries.Sequence name="6. Oferta & CTA" durationInFrames={SCENE_DURATIONS.cta}>
          <CtaScene mobile={mobile} />
          <Audio src={staticFile(VO_DATA["06_cta"].file)} volume={1} />
        </TransitionSeries.Sequence>
      </TransitionSeries>
    </AbsoluteFill>
  );
};
