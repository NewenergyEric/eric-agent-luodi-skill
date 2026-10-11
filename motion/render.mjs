import{createRequire}from'node:module';import path from'node:path';import{mkdir,writeFile}from'node:fs/promises';
const dep=process.env.LAUNCH_DEPENDENCIES;const req=createRequire(dep?path.join(dep,'package.json'):import.meta.url);
const{bundle}=req('@remotion/bundler'),{getCompositions,openBrowser,renderStill,renderMedia}=req('@remotion/renderer');
const mode=process.argv[2]||'qa';if(!['qa','films'].includes(mode))throw Error('Use qa or films');await mkdir('out',{recursive:true});const logs=[];
const log=e=>{if(e.text?.includes('FONT_AUDIT')){logs.push(e.text);console.log(e.text)}};
const serveUrl=await bundle({entryPoint:path.resolve('src/index.ts'),publicDir:path.resolve('public'),webpackOverride:c=>dep?({...c,resolve:{...c.resolve,modules:[path.join(dep,'node_modules'),'node_modules']},resolveLoader:{...c.resolveLoader,modules:[path.join(dep,'node_modules'),'node_modules']},cache:false}):c});
const browser=await openBrowser('chrome',{browserExecutable:process.env.REMOTION_BROWSER_EXECUTABLE||undefined});
try{for(const composition of await getCompositions(serveUrl,{puppeteerInstance:browser,onBrowserLog:log})){
if(process.argv[3]&&composition.id!=='launch-'+process.argv[3])continue;
if(mode==='qa'){for(const frame of [0,80,108,180,228,310,360,430,474,550,612,680,719])await renderStill({composition,serveUrl,frame,output:path.resolve(`out/${composition.id}-${frame}.png`),puppeteerInstance:browser,imageFormat:'png',overwrite:true,onBrowserLog:log});console.log('qa',composition.id)}
else{let last=-1;await renderMedia({composition,serveUrl,outputLocation:path.resolve(`out/${composition.id}.mp4`),codec:'h264',crf:21,pixelFormat:'yuv420p',imageFormat:'png',concurrency:3,puppeteerInstance:browser,overwrite:true,onBrowserLog:log,onProgress:({progress})=>{const pct=Math.floor(progress*10)*10;if(pct!==last){last=pct;console.log(composition.id,pct+'%')}}});console.log('Rendered',composition.id)}}
await writeFile(`out/font-runtime-${mode}.json`,JSON.stringify(logs,null,2));}finally{await browser.close({silent:true})}
