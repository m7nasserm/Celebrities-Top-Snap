import re, sys
p=sys.argv[1]
s=open(p,encoding='utf-8').read()
pat=r'''  const swipeVideo = document\.createElement\("video"\);.*?  // preload preset background images'''
new='''  const swipeVideo = document.createElement("video");
  swipeVideo.src = "data:video/webm;base64," + SWIPE_B64;
  swipeVideo.preload = "auto";
  swipeVideo.muted = true;
  swipeVideo.defaultMuted = true;
  swipeVideo.playsInline = true;
  swipeVideo.setAttribute("playsinline", "");
  swipeVideo.setAttribute("webkit-playsinline", "");
  swipeVideo.setAttribute("muted", "");
  swipeVideo.loop = false;
  let swipeReady = false;
  let swipePrimed = false;

  // iOS can decode transparent WebM pixels as opaque black. Render the video
  // into this small helper canvas and remove dark pixels before compositing it.
  const swipeKeyCanvas = document.createElement("canvas");
  swipeKeyCanvas.width = Math.max(1, Math.round(SWIPE_RECT.w));
  swipeKeyCanvas.height = Math.max(1, Math.round(SWIPE_RECT.h));
  const swipeKeyCtx = swipeKeyCanvas.getContext("2d", { willReadFrequently:true });

  function markSwipeReady(){
    if(swipeVideo.readyState < 2) return;
    swipeReady = true;

    if(!swipePrimed){
      swipePrimed = true;
      try{
        const d = Number.isFinite(swipeVideo.duration) ? swipeVideo.duration : DURATION;
        swipeVideo.currentTime = Math.min(Math.max(0.001, previewT*DURATION), Math.max(0.001, d - 0.03));
      }catch(e){}
    }

    if(typeof swipeVideo.requestVideoFrameCallback === "function") {
      swipeVideo.requestVideoFrameCallback(()=>{ if(!exporting) renderCurrent(); });
    } else if(!exporting) {
      requestAnimationFrame(renderCurrent);
    }
  }

  ["loadedmetadata", "loadeddata", "canplay", "canplaythrough"].forEach(evt=>{
    swipeVideo.addEventListener(evt, markSwipeReady, { passive:true });
  });
  swipeVideo.addEventListener("seeked", ()=>{
    swipeReady = swipeVideo.readyState >= 2;
    if(!exporting) renderCurrent();
  });
  swipeVideo.addEventListener("error", ()=>{ swipeReady = false; });
  try{ swipeVideo.load(); }catch(e){}

  // preload preset background images'''
s,n=re.subn(pat,new,s,count=1,flags=re.S)
if n!=1: raise SystemExit('Swipe video source block not found')

old='''  function drawSwipeIcon(){
    if(!state.swipe.show || !swipeReady) return;
    try{
      ctx.drawImage(swipeVideo, SWIPE_RECT.x, SWIPE_RECT.y, SWIPE_RECT.w, SWIPE_RECT.h);
    }catch(e){}
  }'''
new_draw='''  function drawSwipeIcon(){
    if(!state.swipe.show || !swipeReady) return;
    try{
      const w = swipeKeyCanvas.width, h = swipeKeyCanvas.height;
      swipeKeyCtx.clearRect(0,0,w,h);
      swipeKeyCtx.drawImage(swipeVideo, 0, 0, w, h);

      const frame = swipeKeyCtx.getImageData(0,0,w,h);
      const px = frame.data;
      for(let i=0;i<px.length;i+=4){
        const r=px[i], g=px[i+1], b=px[i+2];
        const lum = Math.max(r,g,b);
        // Full transparency for black/dark background; feather the edge so
        // anti-aliased white icon/text remains smooth instead of jagged.
        if(lum <= 42){
          px[i+3] = 0;
        } else if(lum < 110){
          px[i+3] = Math.round(px[i+3] * (lum-42) / 68);
        }
      }
      swipeKeyCtx.putImageData(frame,0,0);
      ctx.drawImage(swipeKeyCanvas, SWIPE_RECT.x, SWIPE_RECT.y, SWIPE_RECT.w, SWIPE_RECT.h);
    }catch(e){
      // Never fall back to the raw frame here: on iOS that is exactly what
      // produces the opaque black rectangle.
    }
  }'''
if old not in s: raise SystemExit('Swipe draw block not found')
s=s.replace(old,new_draw,1)

open(p,'w',encoding='utf-8').write(s)
print('Mobile swipe video chroma-key transparency patch applied successfully')
