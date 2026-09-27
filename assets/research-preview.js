(() => {
  const slider = document.getElementById('memory-half-life');
  if (!slider) return;
  const curve = document.getElementById('memory-curve');
  const area = document.getElementById('memory-area');
  const dot = document.getElementById('memory-dot');
  function draw() {
    const h = Number(slider.value);
    const points = Array.from({length: 201}, (_, i) => {
      const s = i / 20;
      return `${(55 + 47 * s).toFixed(2)} ${(255 - 220 * 2 ** (-s / h)).toFixed(2)}`;
    });
    curve.setAttribute('d', 'M' + points.join(' L'));
    area.setAttribute('d', 'M55 255 L' + points.join(' L') + ' L525 255 Z');
    const weight = 2 ** (-4 / h);
    dot.setAttribute('cy', String(255 - 220 * weight));
    document.getElementById('memory-value').value = `${h.toFixed(1).replace('.0', '')} time units`;
    slider.setAttribute('aria-valuetext', `${h} time units`);
    const summary = `An observation 4 time units ago retains ${(100 * weight).toFixed(1).replace('.0', '')}% of its original weight.`;
    document.getElementById('memory-summary').textContent = summary;
    document.getElementById('memory-chart-desc').textContent = `Exponential decay with a half-life of ${h} time units. ${summary}`;
  }
  slider.disabled = false;
  slider.addEventListener('input', draw);
  draw();
})();
