import { Composition } from "remotion";
import { MapaLeadsVSL, TOTAL_VSL_FRAMES } from "./MapaLeadsVSL";
import { TutorialLesson } from "./TutorialLesson";
import { LESSONS_DATA } from "./lessonsData";
import { SalesAcademyVideo } from "./SalesAcademyVideo";
import { SALES_ACADEMY_VIDEOS } from "./salesAcademyData";
import { AdAngleId, AdCreative } from "./AdCreative";

const AD_ANGLES: AdAngleId[] = ["01", "02", "03", "04", "05"];

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
        defaultProps={{ mobile: false }}
      />
      <Composition
        id="MapaLeadsVSLMobile"
        component={MapaLeadsVSL}
        durationInFrames={TOTAL_VSL_FRAMES}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={{ mobile: true }}
      />
      {LESSONS_DATA.map((lesson) => (
        <Composition
          key={lesson.id}
          id={lesson.id}
          component={TutorialLesson}
          durationInFrames={lesson.durationFrames + 24}
          fps={30}
          width={1280}
          height={720}
          defaultProps={{ lessonId: lesson.id }}
        />
      ))}
      {SALES_ACADEMY_VIDEOS.map((item) => (
        <Composition
          key={item.id}
          id={item.id}
          component={SalesAcademyVideo}
          durationInFrames={item.durationFrames + 20}
          fps={30}
          width={1280}
          height={720}
          defaultProps={{ videoId: item.id, vertical: false }}
        />
      ))}
      {SALES_ACADEMY_VIDEOS.filter((item) => item.kind === "vsl").map((item) => (
        <Composition
          key={`${item.id}Stories`}
          id={`${item.id}Stories`}
          component={SalesAcademyVideo}
          durationInFrames={item.durationFrames + 20}
          fps={30}
          width={720}
          height={1280}
          defaultProps={{ videoId: item.id, vertical: true }}
        />
      ))}
      {AD_ANGLES.map((angle) => (
        <Composition
          key={`Ad${angle}-4x5`}
          id={`Ad${angle}-4x5`}
          component={AdCreative}
          durationInFrames={1}
          fps={30}
          width={1080}
          height={1350}
          defaultProps={{ angle, format: "4x5" as const }}
        />
      ))}
      {AD_ANGLES.map((angle) => (
        <Composition
          key={`Ad${angle}-9x16`}
          id={`Ad${angle}-9x16`}
          component={AdCreative}
          durationInFrames={1}
          fps={30}
          width={1080}
          height={1920}
          defaultProps={{ angle, format: "9x16" as const }}
        />
      ))}
    </>
  );
};
