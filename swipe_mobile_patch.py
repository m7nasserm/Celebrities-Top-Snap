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

  function markSwipeReady(){
    if(swipeVideo.readyState < 2) return;
    swipeReady = true;

    // Mobile Safari/Chrome can report loaded metadata/data before a drawable
    // frame is actually available to canvas. Prime a tiny seek so a decoded
    // frame exists, then redraw as soon as that seek/frame completes.
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
open(p,'w',encoding='utf-8').write(s)
print('Mobile swipe video patch applied successfully')
