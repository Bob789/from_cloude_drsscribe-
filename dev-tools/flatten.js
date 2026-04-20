// Runs inside the target page and returns a single static HTML document that
// preserves the visual layout by inlining computed styles for every element.
// It also converts <canvas> to <img data:...> so rendered output is preserved
// for CanvasKit/Flutter pages.
(() => {
  const ABS_URL_ATTRS = ['src', 'href', 'poster'];

  function toCssText(style) {
    const out = [];
    for (let i = 0; i < style.length; i += 1) {
      const prop = style[i];
      const val = style.getPropertyValue(prop);
      if (!val) continue;
      const prio = style.getPropertyPriority(prop);
      out.push(`${prop}:${val}${prio ? ' !important' : ''};`);
    }
    return out.join('');
  }

  function absolutizeUrl(urlLike) {
    if (!urlLike) return urlLike;
    try {
      return new URL(urlLike, document.baseURI).href;
    } catch {
      return urlLike;
    }
  }

  function absolutizeCssUrls(value) {
    if (!value || value.indexOf('url(') === -1) return value;
    return value.replace(/url\((['"]?)(.*?)\1\)/g, (m, q, raw) => {
      const trimmed = (raw || '').trim();
      if (!trimmed || trimmed.startsWith('data:') || trimmed.startsWith('blob:') || trimmed.startsWith('#')) {
        return m;
      }
      return `url(${q}${absolutizeUrl(trimmed)}${q})`;
    });
  }

  const cloneRoot = document.documentElement.cloneNode(true);
  const srcEls = document.documentElement.querySelectorAll('*');
  const dstEls = cloneRoot.querySelectorAll('*');

  for (let i = 0; i < srcEls.length; i += 1) {
    const src = srcEls[i];
    const dst = dstEls[i];
    if (!dst) continue;

    const computed = window.getComputedStyle(src);
    let cssText = toCssText(computed);
    cssText = absolutizeCssUrls(cssText);
    if (cssText) dst.setAttribute('style', cssText);

    for (const attr of ABS_URL_ATTRS) {
      if (src.hasAttribute(attr)) {
        const v = src.getAttribute(attr);
        if (v) dst.setAttribute(attr, absolutizeUrl(v));
      }
    }

    if (src.tagName === 'IMG') {
      const img = src;
      if (img.currentSrc) dst.setAttribute('src', img.currentSrc);
    }

    if (src.tagName === 'A') {
      const anchor = src;
      if (anchor.href) dst.setAttribute('href', anchor.href);
    }

    if (src.tagName === 'CANVAS') {
      try {
        const canvas = src;
        const dataUrl = canvas.toDataURL('image/png');
        const imgEl = document.createElement('img');
        imgEl.setAttribute('src', dataUrl);
        imgEl.setAttribute('width', String(canvas.width));
        imgEl.setAttribute('height', String(canvas.height));
        imgEl.setAttribute('style', cssText || '');
        dst.replaceWith(imgEl);
      } catch {
        // Keep canvas as-is if export is blocked (e.g. tainted canvas).
      }
    }

    if (src.tagName === 'INPUT' || src.tagName === 'TEXTAREA') {
      const value = src.value;
      if (typeof value === 'string') dst.setAttribute('value', value);
    }

    if (src.tagName === 'SELECT') {
      const selectedIndex = src.selectedIndex;
      const options = dst.querySelectorAll('option');
      options.forEach((opt, idx) => {
        if (idx === selectedIndex) opt.setAttribute('selected', 'selected');
        else opt.removeAttribute('selected');
      });
    }
  }

  cloneRoot.querySelectorAll('script').forEach((el) => el.remove());

  // External stylesheets are not needed after computed-style inlining.
  cloneRoot.querySelectorAll('link[rel="stylesheet"]').forEach((el) => el.remove());

  const head = cloneRoot.querySelector('head');
  if (head) {
    const metaCharset = document.createElement('meta');
    metaCharset.setAttribute('charset', 'utf-8');
    head.prepend(metaCharset);
  }

  const htmlDoc = `<!doctype html>${cloneRoot.outerHTML}`;
  return {
    html: htmlDoc,
    url: location.href,
    title: document.title,
    width: Math.max(document.documentElement.scrollWidth, window.innerWidth),
    height: Math.max(document.documentElement.scrollHeight, window.innerHeight),
  };
})();
