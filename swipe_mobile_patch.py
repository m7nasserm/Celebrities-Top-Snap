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

# Mobile Safari is much more reliable when the selected music is fully preloaded
# instead of metadata-only. This only changes preview loading; export still uses
# the same deterministic decoded audio path.
s=s.replace('audio.preload = "metadata";', 'audio.preload = "auto";', 2)

old_playback='''  function stopPreview(){
    playing = false;
    playBtn.textContent = "▶ تشغيل المعاينة";
    if(rafId) cancelAnimationFrame(rafId);
    if(state.music.el){ state.music.el.pause(); }
    swipeVideo.pause();
  }

  function startPreview(){
    playing = true;
    playBtn.textContent = "⏸ إيقاف مؤقت";
    const startWall = performance.now() - previewT*DURATION*1000;

    if(state.music.el){
      state.music.el.currentTime = state.music.start + previewT*DURATION;
      state.music.el.volume = state.music.volume;
      state.music.el.play().catch(()=>{});
    }
    if(swipeReady){
      swipeVideo.currentTime = previewT*DURATION;
      swipeVideo.play().catch(()=>{});
    }

    function tick(now){
      if(!playing) return;
      let elapsed = (now-startWall)/1000;
      let t = elapsed/DURATION;

      if(t >= 1){
        previewT = 1;
        render(previewT);
        updateTimeUI();
        stopPreview();
        return;
      }

      previewT = t;
      render(previewT);
      updateTimeUI();
      if(state.music.el && Math.abs(state.music.el.currentTime - (state.music.start+t*DURATION)) > 0.35){
        state.music.el.currentTime = state.music.start + t*DURATION;
      }
      rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);
  }'''

new_playback='''  function stopPreview(){
    playing = false;
    playBtn.textContent = "▶ تشغيل المعاينة";
    if(rafId) cancelAnimationFrame(rafId);
    if(state.music.el){ state.music.el.pause(); }
    swipeVideo.pause();
  }

  function startPreview(){
    playing = true;
    playBtn.textContent = "⏸ إيقاف مؤقت";

    // Keep the selected soundtrack playing continuously on mobile. Previously
    // the RAF loop repeatedly corrected audio.currentTime whenever drift exceeded
    // 350ms. Safari turns those corrections into audible gaps. Seek only once at
    // preview start, then let audio be the playback clock while it is active.
    stopPreviewAudio();
    const startPreviewSeconds = previewT * DURATION;
    const startWall = performance.now();
    const audioEl = state.music.el || null;
    let audioClockSeen = false;
    let lastAudioSeconds = startPreviewSeconds;
    let lastAudioWall = startWall;

    if(audioEl){
      try{
        audioEl.currentTime = state.music.start + startPreviewSeconds;
        audioEl.volume = state.music.volume;
        audioEl.play().catch(()=>{});
      }catch(e){}
    }
    if(swipeReady){
      try{
        swipeVideo.currentTime = startPreviewSeconds;
        swipeVideo.play().catch(()=>{});
      }catch(e){}
    }

    function tick(now){
      if(!playing) return;

      let elapsed;
      if(audioEl && !audioEl.paused && !audioEl.ended && Number.isFinite(audioEl.currentTime)){
        const audioSeconds = audioEl.currentTime - state.music.start;
        if(audioSeconds >= -0.05 && audioSeconds <= DURATION + 0.5){
          elapsed = Math.max(0, audioSeconds);
          audioClockSeen = true;
          lastAudioSeconds = elapsed;
          lastAudioWall = now;
        }
      }

      // No music, failed playback, or the track ended before the 10-second
      // preview: continue smoothly from the most recent audio position.
      if(elapsed == null){
        elapsed = audioClockSeen
          ? lastAudioSeconds + (now - lastAudioWall)/1000
          : startPreviewSeconds + (now - startWall)/1000;
      }

      const t = elapsed / DURATION;
      if(t >= 1){
        previewT = 1;
        render(previewT);
        updateTimeUI();
        stopPreview();
        return;
      }

      previewT = Math.max(0, t);
      render(previewT);
      updateTimeUI();
      rafId = requestAnimationFrame(tick);
    }
    rafId = requestAnimationFrame(tick);
  }'''

if old_playback not in s:
    raise SystemExit('Preview playback block not found')
s=s.replace(old_playback,new_playback,1)

open(p,'w',encoding='utf-8').write(s)
print('Mobile swipe transparency and stable preview audio patch applied successfully')
