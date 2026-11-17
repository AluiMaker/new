import { Composition } from "remotion";
import { MapaLeadsVSL, TOTAL_VSL_FRAMES } from "./MapaLeadsVSL";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="MapaLeadsVSL"
        component={MapaLeadsVSL}
        durationInFrames={TOTAL_VSL_FRAMES}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
