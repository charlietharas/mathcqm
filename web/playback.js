/*
Helper for slide deck playback.
Keeps the outgoing frame visible until the next clip has decoded a frame.
Generated with GPT Sol 6.1.
*/
(() => {
  const host = Reveal.getRevealElement();
  const cover = document.createElement('canvas');
  cover.setAttribute('aria-hidden', 'true');
  Object.assign(cover.style, {
    position: 'absolute', inset: '0', width: '100%', height: '100%',
    objectFit: 'contain', background: '#000', pointerEvents: 'none', zIndex: '9',
  });
  cover.hidden = true;
  host.appendChild(cover);
  const context = cover.getContext('2d');
  let activeVideo = null;
  let navigation = 0;

  const videoFor = slide => slide?.slideBackgroundContentElement?.querySelector('video');
  const isAutomatic = slide => slide?.hasAttribute('data-autoslide');

  function freeze(video) {
    // A pending seek is already covered by the previous captured frame.
    if (!video || video.style.visibility === 'hidden' || video.readyState < 2) return;
    if (!video.videoWidth || !video.videoHeight || !context) return;
    try {
      cover.width = video.videoWidth;
      cover.height = video.videoHeight;
      context.drawImage(video, 0, 0);
      cover.hidden = false;
    } catch {
      // Normal playback remains available if a frame cannot be copied.
      cover.hidden = true;
    }
  }

  function holdAtEnd(video, slide, ticket) {
    // Loops must complete and repeat; auto-next clips must reach their end.
    if (video.loop || isAutomatic(slide)) return;
    const shouldHold = time => Number.isFinite(video.duration)
      && video.duration > 0 && time >= video.duration - 0.045;
    if ('requestVideoFrameCallback' in video) {
      const check = (_, frame) => {
        if (ticket !== navigation || video !== activeVideo) return;
        if (shouldHold(frame.mediaTime)) {
          video.pause();
          return;
        }
        if (!video.paused) video.requestVideoFrameCallback(check);
      };
      video.requestVideoFrameCallback(check);
    } else {
      const check = () => {
        if (ticket !== navigation) {
          video.removeEventListener('timeupdate', check);
        } else if (shouldHold(video.currentTime)) {
          video.pause();
          video.removeEventListener('timeupdate', check);
        }
      };
      video.addEventListener('timeupdate', check);
    }
  }

  function enter(event = {}) {
    const slide = event.currentSlide || Reveal.getCurrentSlide();
    const video = videoFor(slide);
    const previous = videoFor(event.previousSlide) || activeVideo;
    const ticket = ++navigation;
    freeze(previous);
    activeVideo = video;
    if (!video) {
      cover.hidden = true;
      return;
    }

    video.pause();
    video.muted = true;
    video.playsInline = true;
    video.preload = 'auto';
    video.loop = slide.hasAttribute('data-background-video-loop');
    video.style.visibility = 'hidden';

    const reveal = () => {
      if (ticket !== navigation) return;
      video.style.visibility = 'visible';
      cover.hidden = true;
      holdAtEnd(video, slide, ticket);
    };
    const playFromStart = () => {
      if (ticket !== navigation) return;
      // Wait for an actually decoded frame, rather than revealing on 'seeked'.
      if ('requestVideoFrameCallback' in video) {
        video.requestVideoFrameCallback(reveal);
      } else {
        video.addEventListener('playing', () => requestAnimationFrame(reveal), { once: true });
      }
      const playing = video.play();
      if (playing) playing.catch(() => {
        // Show the available first frame if browser playback is blocked.
        if (ticket === navigation && video.readyState >= 2) reveal();
      });
    };
    const reset = () => {
      if (ticket !== navigation) return;
      if (video.currentTime > 0 || video.ended) {
        video.addEventListener('seeked', playFromStart, { once: true });
        video.currentTime = 0;
      } else {
        playFromStart();
      }
    };
    if (video.readyState >= 1) reset();
    else video.addEventListener('loadedmetadata', reset, { once: true });
  }

  Reveal.configure({
    transition: 'none', backgroundTransition: 'none', autoSlideStoppable: false,
  });
  Reveal.on('slidechanged', enter);
  if (Reveal.isReady()) enter();
  else Reveal.on('ready', enter);
})();
