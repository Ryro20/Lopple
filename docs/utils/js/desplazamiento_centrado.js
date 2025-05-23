
document.addEventListener('DOMContentLoaded', () => {
  const OFFSET = 200;

  function fadeIn() {
    return new Promise((resolve) => {
      function onTransitionEnd(e) {
        if (e.propertyName === 'opacity') {
          resolve();
          document.body.removeEventListener('transitionend', onTransitionEnd);
        }
      }
      document.body.addEventListener('transitionend', onTransitionEnd);

      document.body.classList.remove('fade-out');
      setTimeout(() => document.body.classList.add('fade-in'), 20);

      setTimeout(() => {
        document.body.removeEventListener('transitionend', onTransitionEnd);
        resolve();
      }, 700);
    });
  }

  function fadeOut() {
    return new Promise((resolve) => {
      function onTransitionEnd(e) {
        if (e.propertyName === 'opacity') {
          resolve();
          document.body.removeEventListener('transitionend', onTransitionEnd);
        }
      }
      document.body.addEventListener('transitionend', onTransitionEnd);

      document.body.classList.remove('fade-in');
      setTimeout(() => document.body.classList.add('fade-out'), 20);

      setTimeout(() => {
        document.body.removeEventListener('transitionend', onTransitionEnd);
        resolve();
      }, 700);
    });
  }

  async function scrollToHash(hash) {
    const target = document.getElementById(hash);
    if (!target) return;

    const OFFSET = 200;
    const targetPosition = target.getBoundingClientRect().top + window.scrollY - OFFSET;

    window.scrollTo({ top: targetPosition, behavior: 'smooth' });

    // Esperar hasta que scrollY sea aproximadamente igual al destino o pase el timeout
    const checkInterval = 20;
    const timeout = 1000;
    let elapsed = 0;

    return new Promise((resolve) => {
      const interval = setInterval(() => {
        const distance = Math.abs(window.scrollY - targetPosition);

        if (distance < 2 || elapsed >= timeout) {
          clearInterval(interval);
          resolve();
        }

        elapsed += checkInterval;
      }, checkInterval);
    });
  }


  function scrollToTopSmooth() {
    return new Promise((resolve) => {
      const checkInterval = 20;
      const timeout = 1000;
      let elapsed = 0;

      window.scrollTo({ top: 0, behavior: 'smooth' });

      const intervalId = setInterval(() => {
        if (window.scrollY === 0) {
          clearInterval(intervalId);
          resolve();
        } else if (elapsed >= timeout) {
          clearInterval(intervalId);
          resolve();
        }
        elapsed += checkInterval;
      }, checkInterval);
    });
  }

  function blockScroll() {
    window.addEventListener('wheel', preventScroll, { passive: false });
    window.addEventListener('touchmove', preventScroll, { passive: false });
    window.addEventListener('keydown', preventArrowScroll, false);
  }

  function unblockScroll() {
    window.removeEventListener('wheel', preventScroll);
    window.removeEventListener('touchmove', preventScroll);
    window.removeEventListener('keydown', preventArrowScroll);
  }

  function preventScroll(e) {
    e.preventDefault();
  }

  function preventArrowScroll(e) {
    const keys = ['ArrowUp', 'ArrowDown', 'Space', 'PageUp', 'PageDown'];
    if (keys.includes(e.code)) {
      e.preventDefault();
    }
  }

  document.body.classList.add('fade-out');

  let currentHash = window.location.hash ? window.location.hash.substring(1) : null;
  if (currentHash) {
    history.replaceState(null, '', window.location.pathname);
  }

  let storedHash = sessionStorage.getItem('scrollToAnchor');

  setTimeout(async () => {
    const hashToScroll = storedHash || currentHash;
    if (hashToScroll) {
      await scrollToHash(hashToScroll);
      sessionStorage.removeItem('scrollToAnchor');
    }

    await fadeIn();
    unblockScroll();
  }, 50);


  document.body.addEventListener('click', async (e) => {
    const link = e.target.closest('a[href*="#"]');
    if (!link) return;

    const href = link.getAttribute('href');
    if (!href.includes('#')) return;

    let url;
    try {
      url = new URL(href, window.location.origin);
    } catch {
      return;
    }

    let targetHash = url.hash ? url.hash.substring(1).replace(/\//g, '') : null;

    function getPageFileName(path) {
      const parts = path.split('/');
      return parts[parts.length - 1];
    }

    let targetPage = url.pathname.replace(/^\//, '');
    let targetPageFile = getPageFileName(url.pathname);
    let currentPageFile = getPageFileName(window.location.pathname);

    if (targetPageFile !== currentPageFile && targetHash) {
      e.preventDefault();

      blockScroll();

      await fadeOut();
      await new Promise(resolve => setTimeout(resolve, 100));
      await scrollToTopSmooth();

      sessionStorage.setItem('scrollToAnchor', targetHash);
      window.location.href = targetPage;
      return;
    }

    if (targetPageFile === currentPageFile && targetHash) {
      e.preventDefault();
      scrollToHash(targetHash);
    }
  });
});
