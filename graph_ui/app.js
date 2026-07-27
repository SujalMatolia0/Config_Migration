// OSVC Dependency Graph viewer.
// Expects `window.GRAPH_DATA` = { nodes: [...], edges: [...] } and
// `window.GRAPH_META` = { serverVersion, ... } to already be defined
// (normally by a sibling data.js written by build.py) before this file runs.

// Initialize Mermaid with neutral theme matching the light dashboard
mermaid.initialize({
  startOnLoad: false,
  theme: 'neutral',
  securityLevel: 'loose',
  flowchart: { useMaxWidth: true, htmlLabels: true },
  themeVariables: {
    primaryColor: '#FAF5ED',
    primaryTextColor: '#2C070B',
    primaryBorderColor: '#990026',
    lineColor: '#7A6266',
    secondaryColor: '#F3ECE0',
    tertiaryColor: '#FDFBF7',
    background: '#FFFFFF',
    mainBkg: '#FAF5ED',
    nodeBorder: '#990026',
    clusterBkg: '#FFF8F0',
    titleColor: '#2C070B',
    edgeLabelBackground: '#FDFBF7',
    fontFamily: 'Inter, -apple-system, Segoe UI, sans-serif'
  }
});

// Custom marked renderer: intercept ```mermaid code blocks and output a
// placeholder div instead of a <pre><code> block. We render them into SVG
// after the markdown is injected into the DOM.
const _markedRenderer = new marked.Renderer();
const _origCode = _markedRenderer.code.bind(_markedRenderer);
_markedRenderer.code = function(code, lang) {
  // marked passes (code, lang) or a token object depending on version
  const language = (typeof lang === 'string' ? lang : (code && code.lang)) || '';
  const text = typeof code === 'string' ? code : (code && code.text) || '';
  if (language === 'mermaid') {
    // Encode to base64 so special chars survive innerHTML round-trip
    const encoded = btoa(unescape(encodeURIComponent(text)));
    return `<div class="mermaid-pending" data-mermaid="${encoded}"></div>`;
  }
  return _origCode(code, lang);
};
marked.setOptions({ renderer: _markedRenderer });

const TYPE_COLORS = {
  workspace: "#2563EB",        // Royal Blue
  report: "#059669",           // Emerald Green
  navigationset: "#D97706",    // Warm Amber
  businessrule: "#8B5CF6",    // Purple
  customscript: "#E11D48",    // Rose Red
  cpm: "#0D9488",             // Teal
  asynccpm: "#06B6D4",        // Cyan
  osvcobject: "#475569",      // Slate Gray
  externalendpoint: "#B45309",// Burnt Orange
  buiaddin: "#EA580C",        // Vivid Orange
  customfield: "#16A34A",     // Bright Green
  configsetting: "#CA8A04",   // Gold
  reportcolumn: "#047857",    // Deep Emerald
  cpmmappings: "#0F766E",     // Dark Teal
  workspacefield: "#3B82F6"   // Bright Blue
};
const DEFAULT_COLOR = "#6b7280";

const TYPE_LABELS = {
  workspace: "Workspaces",
  report: "Reports",
  navigationset: "Navigation Sets",
  businessrule: "Business Rules",
  customscript: "Custom Scripts",
  cpm: "CPM Handlers",
  asynccpm: "Async CPM Handlers",
  osvcobject: "OSVC Data Objects",
  externalendpoint: "External Endpoints",
  buiaddin: "BUI Add-Ins",
  customfield: "Custom Fields",
  configsetting: "Config Settings",
  reportcolumn: "Report Columns",
  cpmmappings: "CPM Mappings",
  workspacefield: "Workspace Fields"
};

const GRAPH = window.GRAPH_DATA || { nodes: [], edges: [] };
const META = window.GRAPH_META || {};

const emptyState = document.getElementById("emptyState");
if (!GRAPH.nodes || !GRAPH.nodes.length) {
  emptyState.classList.add("show");
}

document.getElementById("metaLine").textContent =
  (META.serverVersion || "OSVC instance").split("\n")[0];
document.getElementById("hint").textContent =
  `${GRAPH.nodes.length} components · ${GRAPH.edges.length} links`;

let nodes = GRAPH.nodes.map(n => ({ ...n }));
let edges = GRAPH.edges.map(e => ({ ...e }));
let activeEdges = [];
let nodeById = {};

// Dynamic DOM Elements references
let edgeEls = [];
let nodeEls = [];

// Adjacency and degree mapping
function rebuildAdjacency() {
  nodeById = {};
  nodes.forEach(n => {
    nodeById[n.id] = n;
    n.out = [];
    n.inc = [];
    n.degree = 0;
  });
  
  activeEdges = edges.filter(e => nodeById[e.source] && nodeById[e.target]);
  
  activeEdges.forEach(e => {
    nodeById[e.source].out.push(e);
    nodeById[e.target].inc.push(e);
    nodeById[e.source].degree++;
    nodeById[e.target].degree++;
  });
}

//// ---------- layout: force simulation ----------
const W = 2000, H = 1400;
nodes.forEach((n, i) => {
  const a = (i / nodes.length) * 2 * Math.PI;
  const r = 380 + 160 * (i % 4);
  n.x = W / 2 + r * Math.cos(a); n.y = H / 2 + r * Math.sin(a);
  n.vx = 0; n.vy = 0; n.fixed = false;
});

function tick(alpha) {
  // Repulsion between nodes to prevent overlapping
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d2 = dx * dx + dy * dy || 1;
      
      if (d2 < 400000) {
        const f = 4500 * alpha / d2;
        const d = Math.sqrt(d2);
        dx /= d; dy /= d;
        a.vx += dx * f * 75; a.vy += dy * f * 75;
        b.vx -= dx * f * 75; b.vy -= dy * f * 75;
      }
    }
  }
  
  // Spring forces pulling connected nodes together
  activeEdges.forEach(e => {
    const s = nodeById[e.source], t = nodeById[e.target];
    if (!s || !t) return;
    let dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const targetDist = 220;
    const f = (d - targetDist) * 0.025 * alpha * 5;
    dx /= d; dy /= d;
    s.vx += dx * f; s.vy += dy * f;
    t.vx -= dx * f; t.vy -= dy * f;
  });
  
  // Centering force to keep graph clustered in viewport
  nodes.forEach(n => {
    n.vx += (W / 2 - n.x) * 0.001 * alpha * 5;
    n.vy += (H / 2 - n.y) * 0.001 * alpha * 5;
    if (!n.fixed) { n.x += n.vx; n.y += n.vy; }
    n.vx *= 0.65; n.vy *= 0.65;
  });
}

// Initial static ticks to stabilize layout
rebuildAdjacency();
for (let i = 0; i < 400; i++) tick(Math.max(0.05, 1 - i / 400));

// ---------- Interactive Animation Loop ----------
let alpha = 0;

function restartSimulation() {
  alpha = 1;
}

function simLoop() {
  alpha = Math.max(0.01, alpha * 0.94);
  tick(alpha);
  redraw();
  requestAnimationFrame(simLoop);
}

// Start continuous animation loop
simLoop();

// ---------- render ----------
const svg = document.getElementById("svg");
const viewport = document.getElementById("viewport");
const edgesG = document.getElementById("edges");
const nodesG = document.getElementById("nodes");
const NS = "http://www.w3.org/2000/svg";

function updateDOM() {
  edgesG.innerHTML = "";
  nodesG.innerHTML = "";

  edgeEls = activeEdges.map(e => {
    const line = document.createElementNS(NS, "line");
    line.setAttribute("class", "edge");
    const title = document.createElementNS(NS, "title");
    title.textContent = e.label || "";
    line.appendChild(title);
    edgesG.appendChild(line);
    return line;
  });

  nodeEls = nodes.map(n => {
    const g = document.createElementNS(NS, "g");
    
    let cls = "node";
    if (n.isOrphan) cls += " orphan";
    if (selected === n) cls += " selected";
    g.setAttribute("class", cls);

    const c = document.createElementNS(NS, "circle");
    let r = Math.min(32, 12 + n.degree * 2);
    c.setAttribute("r", r);
    c.setAttribute("fill", TYPE_COLORS[n.type] || DEFAULT_COLOR);

    const t = document.createElementNS(NS, "text");
    t.setAttribute("dy", -r - 5);
    t.setAttribute("text-anchor", "middle");
    t.textContent = n.label.length > 30 ? n.label.slice(0, 29) + "…" : n.label;

    const title = document.createElementNS(NS, "title");
    title.textContent = TYPE_LABELS[n.type] ? TYPE_LABELS[n.type].replace(/s$/, "") + ": " + n.label : n.label;

    g.appendChild(c); g.appendChild(t); g.appendChild(title);
    nodesG.appendChild(g);

    g.addEventListener("click", ev => {
      ev.stopPropagation();
      select(n);
    });

    g.addEventListener("mouseenter", ev => {
      if (!selected) {
        highlightNodeNeighbors(n);
      }
    });

    g.addEventListener("mouseleave", ev => {
      if (!selected) {
        clearHighlights();
      }
    });

    enableDrag(g, n);
    return g;
  });

  rebuildFilters();
  applyFilters();
  redraw();
}

function redraw() {
  activeEdges.forEach((e, i) => {
    const s = nodeById[e.source], t = nodeById[e.target];
    if (edgeEls[i] && s && t) {
      edgeEls[i].setAttribute("x1", s.x); edgeEls[i].setAttribute("y1", s.y);
      edgeEls[i].setAttribute("x2", t.x); edgeEls[i].setAttribute("y2", t.y);
    }
  });
  nodes.forEach((n, i) => {
    if (nodeEls[i]) {
      nodeEls[i].setAttribute("transform", `translate(${n.x},${n.y})`);
    }
  });
}

// ---------- zoom / pan ----------
let view = { x: 0, y: 0, k: 0.7 };
function applyView() {
  viewport.setAttribute("transform", `translate(${view.x},${view.y}) scale(${view.k})`);
}
function fit() {
  if (!nodes.length) return;
  const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const bw = svg.clientWidth || 1000, bh = svg.clientHeight || 700;
  view.k = Math.min(bw / (maxX - minX + 250), bh / (maxY - minY + 250), 1.1);
  view.x = bw / 2 - view.k * (minX + maxX) / 2;
  view.y = bh / 2 - view.k * (minY + maxY) / 2;
  applyView();
}

fit();

svg.addEventListener("wheel", ev => {
  ev.preventDefault();
  const f = ev.deltaY < 0 ? 1.12 : 0.89;
  const px = ev.offsetX, py = ev.offsetY;
  view.x = px - f * (px - view.x); view.y = py - f * (py - view.y);
  view.k *= f;
  applyView();
}, { passive: false });

let panning = null;
svg.addEventListener("mousedown", ev => {
  if (ev.target === svg || ev.target.id === "viewport") {
    panning = { x: ev.clientX, y: ev.clientY, vx: view.x, vy: view.y };
    svg.classList.add("panning");
  }
});
window.addEventListener("mousemove", ev => {
  if (panning) {
    view.x = panning.vx + ev.clientX - panning.x;
    view.y = panning.vy + ev.clientY - panning.y;
    applyView();
  }
});
window.addEventListener("mouseup", () => { panning = null; svg.classList.remove("panning"); });
svg.addEventListener("click", () => select(null));

// ---------- node drag ----------
function enableDrag(g, n) {
  g.addEventListener("mousedown", ev => {
    ev.stopPropagation();
    const start = { x: ev.clientX, y: ev.clientY, nx: n.x, ny: n.y };
    n.fixed = true;
    function move(e2) {
      n.x = start.nx + (e2.clientX - start.x) / view.k;
      n.y = start.ny + (e2.clientY - start.y) / view.k;
      restartSimulation();
    }
    function up() {
      n.fixed = false;
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
    }
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  });
}

// ---------- filters / search / orphans ----------
const activeTypes = new Set();
let filtersInitialized = false;

function rebuildFilters() {
  const typeCounts = {};
  nodes.forEach(n => typeCounts[n.type] = (typeCounts[n.type] || 0) + 1);
  
  if (!filtersInitialized) {
    Object.keys(typeCounts).forEach(t => activeTypes.add(t));
    filtersInitialized = true;
  }
  
  const filtersDiv = document.getElementById("filters");
  filtersDiv.innerHTML = "";
  
  Object.keys(typeCounts).sort().forEach(t => {
    const label = document.createElement("label");
    label.className = "filter";
    const checked = activeTypes.has(t) ? "checked" : "";
    label.innerHTML = `<input type="checkbox" ${checked} data-type="${t}">
      <span class="swatch" style="background:${TYPE_COLORS[t] || DEFAULT_COLOR}"></span>
      <span>${TYPE_LABELS[t] || t}</span><span class="count">${typeCounts[t]}</span>`;
    label.querySelector("input").addEventListener("change", ev => {
      ev.target.checked ? activeTypes.add(t) : activeTypes.delete(t);
      applyFilters();
    });
    filtersDiv.appendChild(label);
  });
}

const searchBox = document.getElementById("search");
const orphansOnly = document.getElementById("orphansOnly");
const showLabels = document.getElementById("showLabels");
searchBox.addEventListener("input", applyFilters);
orphansOnly.addEventListener("change", applyFilters);
showLabels.addEventListener("change", () => {
  nodesG.querySelectorAll("text").forEach(t => t.style.display = showLabels.checked ? "" : "none");
});

function nodeVisible(n) {
  if (!activeTypes.has(n.type)) return false;
  if (orphansOnly.checked && !n.isOrphan) return false;
  const q = searchBox.value.trim().toLowerCase();
  if (q && !n.label.toLowerCase().includes(q)) return false;
  return true;
}

function applyFilters() {
  const vis = {};
  nodes.forEach((n, i) => {
    vis[n.id] = nodeVisible(n);
    if (nodeEls[i]) {
      nodeEls[i].style.display = vis[n.id] ? "" : "none";
    }
  });
  activeEdges.forEach((e, i) => {
    if (edgeEls[i]) {
      edgeEls[i].style.display = (vis[e.source] && vis[e.target]) ? "" : "none";
    }
  });
}

// ---------- Node Highlighting Logic ----------
function highlightNodeNeighbors(n) {
  const near = new Set([n.id]);
  n.out.forEach(e => near.add(e.target));
  n.inc.forEach(e => near.add(e.source));
  
  nodes.forEach((m, i) => {
    if (nodeEls[i]) {
      nodeEls[i].classList.toggle("dim", !near.has(m.id));
      nodeEls[i].classList.toggle("hover-hl", m === n);
    }
  });
  
  activeEdges.forEach((e, i) => {
    const touches = e.source === n.id || e.target === n.id;
    if (edgeEls[i]) {
      edgeEls[i].classList.toggle("hl", touches);
      edgeEls[i].classList.toggle("dim", !touches);
    }
  });
}

function clearHighlights() {
  nodes.forEach((m, i) => {
    if (nodeEls[i]) {
      nodeEls[i].classList.remove("dim", "hover-hl");
    }
  });
  activeEdges.forEach((e, i) => {
    if (edgeEls[i]) {
      edgeEls[i].classList.remove("hl", "dim");
    }
  });
}

// ---------- tabs interaction ----------
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const tabName = btn.dataset.tab;
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".tab-content").forEach(tc => {
      tc.classList.toggle("active", tc.id === `tab-${tabName}`);
    });
  });
});

// ---------- inspector and markdown/mermaid loader ----------
const inspector = document.getElementById("inspector");
const closeBtn = document.getElementById("closeBtn");
closeBtn.addEventListener("click", () => select(null));

const tabDetails = document.getElementById("tab-details");
const tabDoc = document.getElementById("tab-doc");
const tabDiagram = document.getElementById("tab-diagram");

let selected = null;
let currentFetchController = null;
let mermaidCount = 0;

function esc(s) {
  return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function relRow(otherId, via, dir) {
  const other = nodeById[otherId];
  const name = other ? other.label : otherId;
  const color = other ? (TYPE_COLORS[other.type] || DEFAULT_COLOR) : DEFAULT_COLOR;
  const arrow = dir === "out" ? "→" : "←";
  return `<div class="rel" data-node="${esc(otherId)}">
    <span style="color:${color}">●</span> ${arrow} <b>${esc(name)}</b>
    <div class="via">${esc(via)}</div></div>`;
}

function extractMermaidCode(markdown) {
  if (!markdown) return null;
  const match = markdown.match(/```mermaid([\s\S]*?)```/);
  return match ? match[1].trim() : null;
}

async function renderMermaidDiagram(container, mermaidCode) {
  try {
    container.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">Generating diagram...</div>`;
    const uniqueId = `mermaid-svg-${++mermaidCount}`;
    const { svg } = await mermaid.render(uniqueId, mermaidCode);
    container.innerHTML = `<div class="mermaid">${svg}</div>`;
  } catch (err) {
    console.error("Mermaid Render Error:", err);
    container.innerHTML = `<div style="color:#DC2626; padding: 12px; font-size: 12px; border:1px solid rgba(220,38,38,0.2); border-radius:6px; background:#FFF5F5;">
      <b>Unable to render diagram.</b><br>
      <pre style="font-size:10px; margin-top:8px; color:var(--text-muted); background:var(--panel); padding:8px; border-radius:4px; overflow-x:auto; border:1px solid var(--border-subtle);">${esc(err.message || err)}</pre>
    </div>`;
  }
}

/**
 * Scan a container element for all .mermaid-pending placeholder divs
 * (written by the custom marked renderer above) and replace each with
 * a rendered Mermaid SVG inline. Each diagram also gets a View Fullscreen
 * button that opens the fullscreen modal.
 */
async function renderMermaidBlocksInContainer(container) {
  const pendingBlocks = container.querySelectorAll(".mermaid-pending");
  for (const placeholder of pendingBlocks) {
    const encoded = placeholder.getAttribute("data-mermaid");
    if (!encoded) continue;
    let mermaidCode;
    try {
      mermaidCode = decodeURIComponent(escape(atob(encoded)));
    } catch (e) {
      mermaidCode = encoded;
    }
    if (!mermaidCode.trim()) continue;
    try {
      const uniqueId = `mermaid-inline-${++mermaidCount}`;
      const { svg } = await mermaid.render(uniqueId, mermaidCode);
      const div = document.createElement("div");
      div.className = "mermaid";
      div.style.position = "relative";
      div.innerHTML = svg;

      // Fullscreen button overlaid on each inline diagram
      const fsBtn = document.createElement("button");
      fsBtn.textContent = "View Fullscreen";
      fsBtn.style.cssText = [
        "position:absolute", "top:8px", "right:8px",
        "font-size:10px", "font-weight:700",
        "background:var(--accent-primary)", "color:#fff",
        "border:none", "border-radius:4px", "padding:4px 10px",
        "cursor:pointer", "opacity:0.9", "z-index:10"
      ].join(";");
      fsBtn.addEventListener("click", () => {
        const svgEl = div.querySelector("svg");
        if (!svgEl) return;
        modalViewport.innerHTML = "";
        const clone = svgEl.cloneNode(true);
        clone.style.maxWidth = "none";
        clone.style.maxHeight = "none";
        clone.style.transformOrigin = "center center";
        clone.style.cursor = "inherit";
        modalViewport.appendChild(clone);
        modalView = { x: 0, y: 0, k: 0.85 };
        updateModalTransform();
        diagramModal.classList.add("open");
      });
      div.appendChild(fsBtn);
      placeholder.replaceWith(div);
    } catch (err) {
      console.warn("Inline Mermaid render failed:", err.message);
      // Replace placeholder with a readable error instead of raw code
      const errDiv = document.createElement("div");
      errDiv.style.cssText = "color:#DC2626;padding:10px;font-size:11px;border:1px solid rgba(220,38,38,0.2);border-radius:6px;background:#FFF5F5;margin:10px 0;";
      errDiv.innerHTML = `<b>Mermaid render failed:</b> ${esc(err.message)}<br><pre style="margin-top:6px;font-size:10px;overflow-x:auto;">${esc(mermaidCode)}</pre>`;
      placeholder.replaceWith(errDiv);
    }
  }
}

/**
 * Scan a container for .html-preview-pending placeholder divs
 * (written by the python report generator as base64-encoded HTML)
 * and replace each with a sandboxed live-preview iframe.
 */
function renderHtmlPreviewsInContainer(container) {
  const previews = container.querySelectorAll(".html-preview-pending");
  for (const placeholder of previews) {
    const encoded = placeholder.getAttribute("data-html");
    const title = placeholder.getAttribute("data-title") || "HTML Preview";
    if (!encoded) continue;

    let htmlContent;
    try {
      htmlContent = decodeURIComponent(escape(atob(encoded)));
    } catch (e) {
      htmlContent = atob(encoded);
    }

    // Wrapper card
    const wrapper = document.createElement("div");
    wrapper.style.cssText = "border:1px solid var(--border-subtle);border-radius:10px;overflow:hidden;margin:12px 0;box-shadow:0 2px 8px rgba(153,0,38,0.06);";

    // Toolbar
    const toolbar = document.createElement("div");
    toolbar.style.cssText = "display:flex;align-items:center;justify-content:space-between;padding:8px 12px;background:var(--panel2);border-bottom:1px solid var(--border-subtle);";

    const titleEl = document.createElement("span");
    titleEl.style.cssText = "font-size:11px;font-weight:700;color:var(--text-muted);font-family:'JetBrains Mono',monospace;";
    titleEl.textContent = title;

    const btnGroup = document.createElement("div");
    btnGroup.style.cssText = "display:flex;gap:6px;";

    const makeToolBtn = (label) => {
      const b = document.createElement("button");
      b.textContent = label;
      b.style.cssText = "font-size:10px;font-weight:700;padding:3px 8px;border-radius:4px;border:1px solid var(--border-accent);background:var(--panel);color:var(--text-main);cursor:pointer;";
      return b;
    };

    const srcBtn = makeToolBtn("View Source");
    const fsBtn = makeToolBtn("Fullscreen");
    fsBtn.style.background = "var(--accent-primary)";
    fsBtn.style.color = "#fff";
    fsBtn.style.borderColor = "var(--accent-primary)";
    btnGroup.appendChild(srcBtn);
    btnGroup.appendChild(fsBtn);
    toolbar.appendChild(titleEl);
    toolbar.appendChild(btnGroup);

    // Iframe
    const iframe = document.createElement("iframe");
    iframe.setAttribute("sandbox", "allow-scripts allow-same-origin");
    iframe.setAttribute("title", title);
    iframe.style.cssText = "width:100%;height:340px;border:none;display:block;background:#fff;";
    iframe.srcdoc = htmlContent;

    // Source code panel (hidden by default)
    const srcPanel = document.createElement("pre");
    srcPanel.style.cssText = "display:none;margin:0;padding:14px;background:#1E1E2E;color:#CDD6F4;font-size:11px;font-family:'JetBrains Mono',monospace;overflow-x:auto;max-height:340px;";
    srcPanel.textContent = htmlContent;

    // Toggle source/preview
    let showingSource = false;
    srcBtn.addEventListener("click", () => {
      showingSource = !showingSource;
      iframe.style.display = showingSource ? "none" : "block";
      srcPanel.style.display = showingSource ? "block" : "none";
      srcBtn.textContent = showingSource ? "View Preview" : "View Source";
    });

    // Fullscreen: open iframe content in new tab
    fsBtn.addEventListener("click", () => {
      const blob = new Blob([htmlContent], { type: "text/html" });
      const url = URL.createObjectURL(blob);
      window.open(url, "_blank");
    });

    wrapper.appendChild(toolbar);
    wrapper.appendChild(iframe);
    wrapper.appendChild(srcPanel);
    placeholder.replaceWith(wrapper);
  }
}

async function loadDocsAndDiagrams(node) {
  tabDoc.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">Loading documentation...</div>`;
  tabDiagram.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">Loading architecture diagram...</div>`;
  
  const mdPath = node.data && node.data.mdPath;
  const docBtn = document.querySelector('.tab-btn[data-tab="doc"]');
  const diagBtn = document.querySelector('.tab-btn[data-tab="diagram"]');
  
  if (!mdPath) {
    tabDoc.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No markdown report generated for this component type. Try workspace, report, CPM, or BUI Add-In nodes.</div>`;
    tabDiagram.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No architecture diagram available for this component type.</div>`;
    docBtn.style.opacity = "0.4";
    diagBtn.style.opacity = "0.4";
    return;
  }
  
  docBtn.style.opacity = "1";
  diagBtn.style.opacity = "1";
  
  if (currentFetchController) {
    currentFetchController.abort();
  }
  currentFetchController = new AbortController();
  
  try {
    const response = await fetch(mdPath, { signal: currentFetchController.signal });
    if (!response.ok) throw new Error(`HTTP status ${response.status}`);
    const mdText = await response.text();
    
    // Render markdown to HTML
    tabDoc.innerHTML = marked.parse(mdText);

    // Post-process: find all mermaid code blocks in the rendered markdown
    // and replace them with rendered SVG diagrams inline
    await renderMermaidBlocksInContainer(tabDoc);

    // Post-process: replace html-preview-pending placeholders with live iframes
    renderHtmlPreviewsInContainer(tabDoc);
    
    // Extract and render Mermaid diagram for the Architecture tab
    const mermaidCode = extractMermaidCode(mdText);
    if (mermaidCode) {
      await renderMermaidDiagram(tabDiagram, mermaidCode);
      
      // Create and inject Fullscreen Button
      const fsBtn = document.createElement("button");
      fsBtn.className = "tab-btn";
      fsBtn.style.marginTop = "12px";
      fsBtn.style.background = "var(--accent-primary)";
      fsBtn.style.border = "1px solid var(--accent-primary)";
      fsBtn.style.color = "#fff";
      fsBtn.style.width = "100%";
      fsBtn.style.fontWeight = "600";
      fsBtn.textContent = "View Fullscreen (Zoom + Pan)";
      fsBtn.addEventListener("click", openFullscreenDiagram);
      tabDiagram.appendChild(fsBtn);
    } else {
      tabDiagram.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No Mermaid architecture diagram found in this report.</div>`;
    }
  } catch (err) {
    if (err.name === "AbortError") return;
    console.error("Documentation loading error:", err);
    tabDoc.innerHTML = `<div style="color:#DC2626; padding:10px; font-size:12px; border:1px solid rgba(220,38,38,0.2); border-radius:6px; background:#FFF5F5;">Failed to load documentation: ${esc(err.message)}</div>`;
    tabDiagram.innerHTML = `<div style="color:#DC2626; padding:10px; font-size:12px; border:1px solid rgba(220,38,38,0.2); border-radius:6px; background:#FFF5F5;">Failed to load diagram: ${esc(err.message)}</div>`;
  }
}

function select(n) {
  selected = n;
  nodes.forEach((m, i) => {
    if (nodeEls[i]) {
      nodeEls[i].classList.toggle("selected", m === n);
    }
  });
  
  if (n) {
    highlightNodeNeighbors(n);
  } else {
    clearHighlights();
  }
  
  inspector.classList.toggle("open", !!n);
  if (!n) return;

  // Build Details Tab
  let html = `<h2>${esc(n.label)}</h2>
    <span class="type-chip" style="background:${TYPE_COLORS[n.type] || DEFAULT_COLOR}">
    ${esc(TYPE_LABELS[n.type] ? TYPE_LABELS[n.type].replace(/s$/, "") : n.type)}</span>`;
    
  if (n.isOrphan) html += `<div class="orphan-flag">⚠ Orphaned: ${esc(n.orphanReason || "unreferenced")}</div>`;
  
  html += `<div class="kv"><b>${n.inc.length}</b> inbound · <b>${n.out.length}</b> outbound link(s)</div>`;

  if (n.inc.length) {
    html += "<h3>Used by</h3>" + n.inc.map(e => relRow(e.source, e.label, "in")).join("");
  }
  if (n.out.length) {
    html += "<h3>Uses</h3>" + n.out.map(e => relRow(e.target, e.label, "out")).join("");
  }
  
  const d = n.data || {};
  const facts = [];
  
  if (d.type) facts.push(["Record type", d.type]);
  if (d.id) facts.push(["ID", d.id]);
  if (d.object_type) facts.push(["Object", d.object_type]);
  if (d.tabs) facts.push(["Tabs", d.tabs.length]);
  if (d.fields) facts.push(["Fields", d.fields.length]);
  if (d.rules) facts.push(["Rules", d.rules.length]);
  if (d.columns) facts.push(["Columns", d.columns.length]);
  if (d.filters) facts.push(["Filters", d.filters.length]);
  if (d.hooks) facts.push(["Hooks", d.hooks.join(", ")]);
  if (d.script_type) facts.push(["Script type", d.script_type]);

  // CPM procedure specifics
  if (d.operations_label) facts.push(["Operations", d.operations_label]);
  if (typeof d.is_async === "boolean") facts.push(["Async", d.is_async ? "Yes" : "No"]);
  if (d.php_version) facts.push(["PHP version", d.php_version]);
  if (d.soap_actions && d.soap_actions.length) facts.push(["SOAP actions", d.soap_actions.join(", ")]);
  if (d.custom_fields_read && d.custom_fields_read.length) facts.push(["Custom fields read", d.custom_fields_read.join(", ")]);
  if (d.custom_fields_written && d.custom_fields_written.length) facts.push(["Custom fields written", d.custom_fields_written.join(", ")]);
  if (d.config_vars && d.config_vars.length) facts.push(["Config vars", d.config_vars.join(", ")]);

  // BUI Add-In specifics
  if (d.entry_point) facts.push(["Entry point", d.entry_point]);
  if (d.osvc_fields_read && d.osvc_fields_read.length) facts.push(["Fields read", d.osvc_fields_read.join(", ")]);
  if (d.osvc_fields_written && d.osvc_fields_written.length) facts.push(["Fields written", d.osvc_fields_written.join(", ")]);
  if (d.api_calls && d.api_calls.length) facts.push(["API calls", d.api_calls.length]);
  if (d.modal_views && d.modal_views.length) facts.push(["Modal views", d.modal_views.join(", ")]);
  if (d.lifecycle_listeners && d.lifecycle_listeners.length) facts.push(["Lifecycle hooks", d.lifecycle_listeners.join(", ")]);
  if (d.external_libraries && d.external_libraries.length) facts.push(["External libraries", d.external_libraries.join(", ")]);

  if (d.risk_flags && d.risk_flags.length) {
    const riskText = d.risk_flags.map(r => (typeof r === "string" ? r : (r.type || r.detail || String(r)))).join("; ");
    facts.push(["⚠ Risks", riskText]);
  }
  
  if (facts.length) {
    html += "<h3>Details</h3>" + facts.map(([k, v]) =>
      `<div class="kv">${esc(k)}: <b>${esc(v)}</b></div>`).join("");
  }
  
  tabDetails.innerHTML = html;
  tabDetails.querySelectorAll(".rel").forEach(el => {
    el.addEventListener("click", () => {
      const target = nodeById[el.dataset.node];
      if (target) select(target);
    });
  });
  
  // Async fetch markdown documentation and compile Mermaid
  loadDocsAndDiagrams(n);
}

// ---------- Fullscreen Modal zoom & pan ----------
const diagramModal = document.getElementById("diagramModal");
const modalViewport = document.getElementById("modalViewport");
const modalClose = document.getElementById("modalClose");
const modalZoomIn = document.getElementById("modalZoomIn");
const modalZoomOut = document.getElementById("modalZoomOut");
const modalReset = document.getElementById("modalReset");

let modalView = { x: 0, y: 0, k: 1 };

function updateModalTransform() {
  const svgEl = modalViewport.querySelector("svg");
  if (svgEl) {
    svgEl.style.transform = `translate(${modalView.x}px, ${modalView.y}px) scale(${modalView.k})`;
  }
}

function openFullscreenDiagram() {
  const sourceSvg = tabDiagram.querySelector(".mermaid svg");
  if (!sourceSvg) return;
  
  modalViewport.innerHTML = "";
  const clone = sourceSvg.cloneNode(true);
  clone.style.transition = "transform 0.05s ease-out";
  modalViewport.appendChild(clone);
  
  // Center and scale to 1.1x initial size
  modalView = { x: 0, y: 0, k: 1.1 };
  updateModalTransform();
  
  diagramModal.classList.add("open");
}

function closeFullscreenDiagram() {
  diagramModal.classList.remove("open");
  modalViewport.innerHTML = "";
}

modalClose.addEventListener("click", closeFullscreenDiagram);

// Drag pan interaction on modal
let modalPanning = null;
modalViewport.addEventListener("mousedown", ev => {
  if (ev.target.id === "modalViewport" || modalViewport.contains(ev.target)) {
    modalPanning = { x: ev.clientX, y: ev.clientY, vx: modalView.x, vy: modalView.y };
    modalViewport.classList.add("dragging");
  }
});

window.addEventListener("mousemove", ev => {
  if (modalPanning) {
    modalView.x = modalPanning.vx + (ev.clientX - modalPanning.x);
    modalView.y = modalPanning.vy + (ev.clientY - modalPanning.y);
    updateModalTransform();
  }
});

window.addEventListener("mouseup", () => {
  if (modalPanning) {
    modalPanning = null;
    modalViewport.classList.remove("dragging");
  }
});

// Scrollwheel zoom interaction on modal
modalViewport.addEventListener("wheel", ev => {
  ev.preventDefault();
  const factor = ev.deltaY < 0 ? 1.15 : 0.85;
  modalView.k = Math.max(0.15, Math.min(6, modalView.k * factor));
  updateModalTransform();
}, { passive: false });

// Zoom control buttons
modalZoomIn.addEventListener("click", () => {
  modalView.k = Math.min(6, modalView.k * 1.25);
  updateModalTransform();
});

modalZoomOut.addEventListener("click", () => {
  modalView.k = Math.max(0.15, modalView.k * 0.8);
  updateModalTransform();
});

modalReset.addEventListener("click", () => {
  modalView = { x: 0, y: 0, k: 1.1 };
  updateModalTransform();
});

// Initial render
updateDOM();
