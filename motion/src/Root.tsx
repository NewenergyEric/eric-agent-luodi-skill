import React from 'react';
import {Composition} from 'remotion';
import {LaunchFilm} from './LaunchFilm';

export const Root: React.FC=()=> <>{(['zh','en'] as const).map(lang=><Composition key={lang} id={`launch-${lang}`} component={LaunchFilm} defaultProps={{lang}} durationInFrames={720} fps={30} width={1280} height={720}/>)}</>;
