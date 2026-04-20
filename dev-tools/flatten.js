// Runs inside the target page. Walks the DOM, captures geometry + computed styles,
// and returns a self-contained absolute-positioned HTML snapshot.
// Designed primarily for Flutter Web pages where most useful info lives in the
// rendered DOM (semantics layer + CanvasKit fallback). Works on plain HTML too.
(() => {
  const RELEVANT_STYLES = [
    'color', 'background-color', 'background-image', 'font-family', 'font-size',
    'font-weight', 'font-style', 'line-height', 'letter-spacing', 'text-align',
    'text-decoration', 'border-radius', 'box-shadow', 'opacity',
    'visibility', 'direction'
  ];
  // NOTE: We intentionally OMIT properties that affect geometry, since each
  // element is re-positioned absolutely with explicit left/top/width/height
  // taken from getBoundingClientRect (which already accounts for them):
  //   - transform, margin, padding, border (border affects box size)
  //   - display, overflow, z-index (handled by the wrapper / source order)

  const html = document.documentElement;
  const docW = Math.max(html.scrollWidth, window.innerWidth);
  const docH = Math.max(html.scrollHeight, window.innerHeight);

  const out = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  let node = walker.currentNode;

  function isVisible(el, style) {
    if (style.display === 'none' || style.visibility === 'hidden') return false;
    if (parseFloat(style.opacity) === 0) return false;
    return true;
  }

  while (node) {
    const el = node;
    const rect = el.getBoundingClientRect();
    const style = window.getComputedStyle(el);

    if (rect.width > 0 && rect.height > 0 && isVisible(el, style)) {
      const styleObj = {};
      for (const prop of RELEVANT_STYLES) {
        const v = style.getPropertyValue(prop);
        if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px') {
          styleObj[prop] = v;
        }
      }

      // Capture only direct text (not from children, to avoid duplication)
      let text = '';
      for (const child of el.childNodes) {
        if (child.nodeType === Node.TEXT_NODE) {
          const t = (child.textContent || '').trim();
          if (t) text += t + ' ';
        }
      }
      text = text.trim();

      // Capture images as src
      let imgSrc = null;
      if (el.tagName === 'IMG' && el.src) imgSrc = el.src;

      // Capture aria-label / role for Flutter semantics layer
      const ariaLabel = el.getAttribute('aria-label') || '';
      const role = el.getAttribute('role') || '';

      if (text || imgSrc || ariaLabel || Object.keys(styleObj).length > 2) {
        out.push({
          tag: el.tagName.toLowerCase(),
          x: Math.round(rect.left + window.scrollX),
          y: Math.round(rect.top + window.scrollY),
          w: Math.round(rect.width),
          h: Math.round(rect.height),
          text,
          ariaLabel,
          role,
          imgSrc,
          style: styleObj,
        });
      }
    }
    node = walker.nextNode();
  }

  return { docW, docH, elements: out, url: location.href, title: document.title };
})();
