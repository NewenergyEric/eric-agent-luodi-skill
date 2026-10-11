"""Package the completed Chinese film using the launch skill's unchanged media helpers."""
import argparse
from fractions import Fraction
import hashlib
import importlib
import json
from pathlib import Path
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--tools',type=Path,default=Path(__file__).parent/'tools')
    parser.add_argument('--webp-quality',type=int,default=78)
    args=parser.parse_args()
    sys.path.insert(0,str(args.tools.resolve()))
    package=importlib.import_module('package_media')
    checker=importlib.import_module('check_media')
    metadata=checker.probe(args.source)
    assert float(metadata['duration'])==24 and Fraction(metadata['avg_frame_rate'])==30
    args.out.mkdir(parents=True,exist_ok=False)
    mp4=args.out/'hero-zh.mp4'
    package.encode_film(args.source,mp4,21)
    package.run(['-i',str(mp4),'-vf','fps=20,scale=800:450:flags=lanczos','-c:v','libwebp_anim','-lossless','0','-quality',str(args.webp_quality),'-compression_level','6','-loop','0','-an',str(args.out/'hero-zh.webp')])
    package.run(['-i',str(mp4),'-filter_complex','[0:v]fps=20,scale=800:450:flags=lanczos,split[a][b];[a]palettegen=max_colors=24:reserve_transparent=0[p];[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle','-loop','0',str(args.out/'hero-zh.gif')])
    package.run(['-ss','2.7','-i',str(mp4),'-frames:v','1',str(args.out/'hero-zh.png')])
    assets={};observed=[];errors=[]
    for ext in ('mp4','webp','gif','png'):
        file=args.out/f'hero-zh.{ext}';data=file.read_bytes()
        assets[file.name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        if ext=='mp4':
            m=checker.probe(file)
            assert m['codec_name']=='h264' and m['pix_fmt']=='yuv420p'
            assert [m['width'],m['height']]==[1280,720] and Fraction(m['avg_frame_rate'])==30
            assert float(m['duration'])==24 and int(m['nb_frames'])==720 and checker.faststart(data)
            observed.append({'file':file.name,'fps':30,'frames':720,'duration_seconds':24,'faststart':True,'bytes':len(data)})
        elif ext in ('webp','gif'):
            width,height,delays=getattr(checker,ext)(data)
            assert [width,height]==[800,450] and len(delays)==480 and set(delays)=={50}
            budget=(3 if ext=='webp' else 6)*1024*1024
            if len(data)>budget:errors.append(f'{ext}_over_budget')
            observed.append({'file':file.name,'fps':20,'frames':len(delays),'duration_seconds':sum(delays)/1000,'bytes':len(data),'budget':budget})
    result={'schema_version':'1','default_language':'zh','languages':['zh'],'valid':not errors,'errors':errors,'assets':assets,'observed':observed,
            'validation':'Chinese-only scope using the original probe, faststart, gif and webp parsers. The bilingual check() wrapper is not applicable.',
            'helpers':{n:hashlib.sha256((args.tools/n).read_bytes()).hexdigest() for n in ('package_media.py','check_media.py')}}
    (args.out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result,indent=2))
    return bool(errors)


if __name__=='__main__':raise SystemExit(main())
