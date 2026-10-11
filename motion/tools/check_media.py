#!/usr/bin/env python3
"""Verify release bytes and encoding; visual quality and truthful claims need review."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct
import subprocess

def probe(path):
    r=subprocess.run(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=codec_name,pix_fmt,width,height,avg_frame_rate,nb_frames,duration','-of','json',str(path)],check=True,capture_output=True,text=True)
    return json.loads(r.stdout)['streams'][0]

def faststart(data):
    pos=0;atoms=[]
    while pos<len(data):
        if pos+8>len(data):raise ValueError('Truncated MP4 atom header')
        size=int.from_bytes(data[pos:pos+4],'big');kind=data[pos+4:pos+8];header=8
        if size==1:
            if pos+16>len(data):raise ValueError('Truncated extended MP4 atom')
            size=int.from_bytes(data[pos+8:pos+16],'big');header=16
        if size==0:size=len(data)-pos
        if size<header or pos+size>len(data):raise ValueError('Invalid MP4 atom size')
        atoms.append(kind);pos+=size
    return b'moov' in atoms and b'mdat' in atoms and atoms.index(b'moov')<atoms.index(b'mdat')

def webp(data):
    if data[:4]!=b'RIFF' or data[8:12]!=b'WEBP' or int.from_bytes(data[4:8],'little')+8!=len(data):raise ValueError('Invalid WebP container')
    pos=12;width=height=0;delays=[]
    while pos+8<=len(data):
        kind=data[pos:pos+4];size=int.from_bytes(data[pos+4:pos+8],'little');part=data[pos+8:pos+8+size]
        if len(part)!=size:raise ValueError('Truncated WebP chunk')
        if kind==b'VP8X':
            if len(part)<10:raise ValueError('Truncated VP8X')
            width=1+int.from_bytes(part[4:7],'little');height=1+int.from_bytes(part[7:10],'little')
        if kind==b'ANMF':
            if len(part)<16:raise ValueError('Truncated ANMF')
            delays.append(int.from_bytes(part[12:15],'little'))
        pos+=8+size+(size%2)
    if pos!=len(data):raise ValueError('Trailing/truncated WebP chunk')
    return width,height,delays

def gif(data):
    if len(data)<13 or data[:6] not in [b'GIF87a',b'GIF89a']:raise ValueError('Invalid GIF')
    width,height=struct.unpack_from('<HH',data,6);packed=data[10]
    pos=13+(3*2**((packed&7)+1) if packed&128 else 0);delay=0;delays=[]
    def skip(pos):
        while True:
            if pos>=len(data):raise ValueError('Truncated GIF block')
            size=data[pos];pos+=1
            if not size:return pos
            pos+=size
            if pos>len(data):raise ValueError('Truncated GIF payload')
    while pos<len(data):
        tag=data[pos];pos+=1
        if tag==0x3b:return width,height,delays
        if tag==0x21:
            if pos>=len(data):raise ValueError('Truncated GIF extension')
            label=data[pos];pos+=1
            if label==0xf9:
                if pos+6>len(data) or data[pos]!=4:raise ValueError('Invalid GIF control block')
                delay=int.from_bytes(data[pos+2:pos+4],'little')*10
            pos=skip(pos)
        elif tag==0x2c:
            if pos+10>len(data):raise ValueError('Truncated GIF image')
            packed=data[pos+8];pos+=9
            if packed&128:pos+=3*2**((packed&7)+1)
            pos=skip(pos+1);delays.append(delay);delay=0
        else:raise ValueError(f'Unexpected GIF block {tag}')
    raise ValueError('Missing GIF trailer')

def check(manifest_path):
    manifest_path=Path(manifest_path).resolve();root=manifest_path.parent
    m=json.loads(manifest_path.read_text(encoding='utf-8'));errors=[];observed=[]
    if m.get('schema_version')!='1':return ['Unsupported manifest schema'],[]
    if m.get('default_language') not in ('zh','en'):errors.append('Primary language must be zh or en')
    settings=m['settings'];assets=m['assets']
    expected={f'hero-{lang}.{ext}' for lang in ['en','zh'] for ext in ['mp4','webp','gif','png']}
    if set(assets)!=expected:errors.append('Expected exactly MP4, WebP, GIF and PNG for both en and zh')
    for name,e in assets.items():
        try:
            p=(root/name).resolve()
            if Path(name).is_absolute() or not p.is_relative_to(root):raise ValueError('Asset path escapes release directory')
            data=p.read_bytes()
            if len(data)!=e['bytes'] or hashlib.sha256(data).hexdigest()!=e['sha256']:raise ValueError('File size or SHA-256 mismatch')
            if p.suffix=='.mp4':
                s=probe(p);fps=float(Fraction(s['avg_frame_rate']));duration=float(s['duration'])
                if s['codec_name']!='h264' or s['pix_fmt']!='yuv420p':raise ValueError('Expected H.264/yuv420p')
                if [s['width'],s['height']]!=settings['film_dimensions'] or fps!=settings['film_fps']:raise ValueError('Film dimensions/FPS mismatch')
                if abs(duration-e['duration_seconds'])>.04 or not settings['duration_min']<=duration<=settings['duration_max']:raise ValueError('Film duration mismatch/outside configured range')
                if abs(int(s['nb_frames'])-duration*fps)>1:raise ValueError('Film frame count mismatch')
                if not faststart(data):raise ValueError('MP4 metadata is not before media')
                observed.append({'file':name,'fps':fps,'frames':int(s['nb_frames']),'seconds':duration,'bytes':len(data)})
            elif p.suffix in ['.gif','.webp']:
                width,height,delays=(gif if p.suffix=='.gif' else webp)(data)
                if [width,height]!=settings['preview_dimensions']:raise ValueError('Preview dimensions mismatch')
                step=1000/settings['preview_fps']
                if not delays or any(abs(t-step)>1 for t in delays):raise ValueError('Preview frame timing mismatch; inspect any optimized long holds')
                if abs(sum(delays)/1000-e['duration_seconds'])>.1:raise ValueError('Preview duration mismatch')
                budget=settings['gif_max_bytes' if p.suffix=='.gif' else 'webp_max_bytes']
                if len(data)>budget:raise ValueError(f'Preview exceeds {budget} byte budget')
                observed.append({'file':name,'frames':len(delays),'frame_ms':step,'seconds':sum(delays)/1000,'bytes':len(data)})
            else:
                if data[:8]!=b'\x89PNG\r\n\x1a\n' or list(struct.unpack_from('>II',data,16))!=settings['film_dimensions']:raise ValueError('Poster dimensions mismatch')
        except (OSError,ValueError,KeyError,IndexError,struct.error,subprocess.CalledProcessError,TypeError) as exc:errors.append(f'{name}: {exc}')
    return errors,observed

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('manifest',type=Path);a=p.parse_args()
    try:errors,observed=check(a.manifest)
    except (OSError,ValueError,KeyError,TypeError) as exc:errors=[str(exc)];observed=[]
    print(json.dumps({'valid':not errors,'errors':errors,'observed':observed,'limitation':'Encoding/integrity only; visual and claim review are separate.'},indent=2))
    return bool(errors)

if __name__=='__main__':raise SystemExit(main())
