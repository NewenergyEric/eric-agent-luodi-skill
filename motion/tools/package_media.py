#!/usr/bin/env python3
"""Package finished bilingual films in a new release directory with measured outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from fractions import Fraction
from check_media import probe,check

def run(args):subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-n',*args],check=True)

def encode_film(source,destination,crf=21):
    run(['-i',str(source),'-map','0:v:0','-map','0:a?','-c:a','aac','-b:a','128k','-vf','scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1','-r','30','-c:v','libx264','-crf',str(crf),'-pix_fmt','yuv420p','-movflags','+faststart',str(destination)])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--en',required=True,type=Path);p.add_argument('--zh',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--duration-min',type=float,default=18);p.add_argument('--duration-max',type=float,default=25)
    p.add_argument('--crf',type=int,default=21);p.add_argument('--webp-quality',type=int,default=82)
    p.add_argument('--default-language',choices=['zh','en'],default='zh',help='Primary release language (default: zh)')
    a=p.parse_args()
    if not 0<a.duration_min<=a.duration_max or not 0<=a.crf<=51 or not 1<=a.webp_quality<=100:p.error('Invalid duration or quality range')
    for lang in ['en','zh']:
        path=getattr(a,lang)
        if not path.is_file():p.error(f'Missing finished source: {path}')
        s=probe(path)
        if not a.duration_min<=float(s['duration'])<=a.duration_max:p.error(f'{lang}: source duration outside configured range')
        if float(Fraction(s['avg_frame_rate']))<20:p.error(f'{lang}: source below 20 FPS; rerender motion rather than duplicate frames')
    # A new directory avoids racing a renderer or overwriting a published baseline.
    a.out.mkdir(parents=True,exist_ok=False)
    settings={'film_dimensions':[1280,720],'film_fps':30,'preview_dimensions':[800,450],'preview_fps':20,'duration_min':a.duration_min,'duration_max':a.duration_max,'webp_max_bytes':3*1024*1024,'gif_max_bytes':6*1024*1024}
    manifest={'schema_version':'1','default_language':a.default_language,'settings':settings,'sources':{},'assets':{}}
    for lang in ['en','zh']:
        source=getattr(a,lang);mp4=a.out/f'hero-{lang}.mp4'
        manifest['sources'][lang]={'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'filename':source.name}
        encode_film(source,mp4,a.crf)
        duration=float(probe(mp4)['duration'])
        run(['-i',str(mp4),'-vf','fps=20,scale=800:450:flags=lanczos','-c:v','libwebp_anim','-lossless','0','-quality',str(a.webp_quality),'-compression_level','6','-loop','0','-an',str(a.out/f'hero-{lang}.webp')])
        run(['-i',str(mp4),'-filter_complex','[0:v]fps=20,scale=800:450:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:reserve_transparent=0[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle','-loop','0',str(a.out/f'hero-{lang}.gif')])
        run(['-ss',str(max(0,duration-1.3)),'-i',str(mp4),'-frames:v','1',str(a.out/f'hero-{lang}.png')])
        for ext in ['mp4','webp','gif','png']:
            name=f'hero-{lang}.{ext}';data=(a.out/name).read_bytes();entry={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
            if ext!='png':entry['duration_seconds']=duration
            manifest['assets'][name]=entry
        print(f'Packaged {lang}',flush=True)
    path=a.out/'manifest.json';path.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    errors,observed=check(path);report={'valid':not errors,'errors':errors,'observed':observed}
    (a.out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2));return bool(errors)

if __name__=='__main__':raise SystemExit(main())
