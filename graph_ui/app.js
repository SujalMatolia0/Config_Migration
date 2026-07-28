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
  module_root: "#990026",      // Crimson Module Root
  category_hub: "#D97706",     // Amber Category Hub
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
  workspacefield: "#3B82F6",   // Bright Blue
  object: "#9333EA"           // Purple
};
const DEFAULT_COLOR = "#6b7280";

const TYPE_LABELS = {
  module_root: "Module Root (Parent)",
  category_hub: "Category Hub (Child)",
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
  workspacefield: "Workspace Fields",
  object: "Parent Objects"
};

const GRAPH = window.GRAPH_DATA || { nodes: [], edges: [] };
const META = window.GRAPH_META || {};

const emptyState = document.getElementById("emptyState");
if (!GRAPH.nodes || !GRAPH.nodes.length) {
  emptyState.classList.add("show");
}

document.getElementById("metaLine").textContent =
  (META.serverVersion || "OSVC instance").split("\n")[0];

// Dynamic Multi-Tier Hierarchy State
const expandedModules = new Set();
const expandedHubs = new Set();
const coordinatesCache = {};

function getNodeModule(n) {
  if (n.data && n.data.module && n.data.module !== "Other" && n.data.module !== "None") {
    return n.data.module;
  }
  if (n.type === "object") {
    return n.label;
  }
  if (n.data && n.data.object) {
    const o = Array.isArray(n.data.object) ? n.data.object[0] : n.data.object;
    if (o && o !== "None" && o !== "Other") return o;
  }
  const label = (n.label || "").toLowerCase();
  if (label.includes("contact") || label.includes("call") || label.includes("sms")) return "Contact";
  if (label.includes("incident") || label.includes("note") || label.includes("clock") || label.includes("validation") || label.includes("sr")) return "Incident";
  if (label.includes("org") || label.includes("account") || label.includes("siebel")) return "Organization";
  if (label.includes("answer")) return "Answer";
  return "Other";
}

function getModuleRoots() {
  const modulesSet = new Set();
  (GRAPH.nodes || []).forEach(n => {
    const mod = getNodeModule(n);
    if (mod) modulesSet.add(mod);
  });
  if (!modulesSet.size) modulesSet.add("Other");

  return Array.from(modulesSet).sort().map(mod => ({
    id: `module:${mod.toLowerCase()}`,
    type: "module_root",
    label: `${mod} Module`,
    module: mod,
    r: 32
  }));
}

let nodes = [];
let edges = [];
let activeEdges = [];
let nodeById = {};

// Dynamic DOM Elements references
let edgeEls = [];
let nodeEls = [];

function rebuildGraphState() {
  // 1. Cache current node coordinates
  nodes.forEach(n => {
    coordinatesCache[n.id] = { x: n.x, y: n.y, vx: n.vx, vy: n.vy };
  });

  const nextNodes = [];
  const nextEdges = [];
  const roots = getModuleRoots();

  // 2. Add Tier 1 Parent Module Roots
  roots.forEach(root => {
    nextNodes.push({ ...root });
  });

  // 3. Add Tier 2 Child Category Hubs if Module Root is expanded
  roots.forEach(root => {
    if (expandedModules.has(root.id)) {
      const moduleComponents = GRAPH.nodes.filter(n => {
        return getNodeModule(n).toLowerCase() === root.module.toLowerCase();
      });

      const uniqueTypes = [...new Set(moduleComponents.map(n => n.type))];
      uniqueTypes.forEach(type => {
        const hubId = `hub:${root.module.toLowerCase()}/${type}`;
        const hubLabel = TYPE_LABELS[type] || type;

        nextNodes.push({
          id: hubId,
          type: "category_hub",
          label: hubLabel,
          module: root.module,
          hubType: type,
          r: 24
        });

        nextEdges.push({
          id: `edge-${root.id}-to-${hubId}`,
          source: root.id,
          target: hubId,
          label: "contains"
        });
      });
    }
  });

  // 4. Add Tier 3 Sub-Child Component Instances if Category Hub is expanded
  nextNodes.forEach(n => {
    if (n.type === "category_hub" && expandedHubs.has(n.id)) {
      const moduleInstances = GRAPH.nodes.filter(inst => {
        return getNodeModule(inst).toLowerCase() === n.module.toLowerCase() && inst.type === n.hubType;
      });

      moduleInstances.forEach(inst => {
        const baseR = inst.type === "object" ? 22 : 14;
        const r = Math.min(30, baseR + (inst.degree || 0) * 1.5);
        nextNodes.push({ ...inst, r: r });

        nextEdges.push({
          id: `edge-${n.id}-to-${inst.id}`,
          source: n.id,
          target: inst.id,
          label: "instance"
        });
      });
    }
  });

  // 5. Connect cross-component dependency edges if both endpoints are visible
  const visibleNodeIds = new Set(nextNodes.map(n => n.id));
  GRAPH.edges.forEach(e => {
    if (visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)) {
      nextEdges.push({ ...e });
    }
  });

  // 6. Position nodes smoothly or restore cached coordinates
  nextNodes.forEach(n => {
    if (coordinatesCache[n.id]) {
      n.x = coordinatesCache[n.id].x;
      n.y = coordinatesCache[n.id].y;
      n.vx = coordinatesCache[n.id].vx;
      n.vy = coordinatesCache[n.id].vy;
    } else {
      let parentNode = null;
      if (n.id.startsWith("hub:")) {
        parentNode = nextNodes.find(m => m.id === `module:${n.module.toLowerCase()}`);
      } else if (n.type !== "module_root") {
        parentNode = nextNodes.find(m => m.id === `hub:${(n.module || 'other').toLowerCase()}/${n.type}`);
      }

      const px = parentNode ? parentNode.x : W / 2;
      const py = parentNode ? parentNode.y : H / 2;
      n.x = px + (Math.random() - 0.5) * 120;
      n.y = py + (Math.random() - 0.5) * 120;
      n.vx = 0; n.vy = 0;
    }
  });

  nodes = nextNodes;
  edges = nextEdges;
  rebuildAdjacency();

  document.getElementById("hint").textContent =
    `${nodes.filter(n => n.type !== "module_root" && n.type !== "category_hub").length} components visible · ${edges.length} links`;
}

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

// ---------- layout: force simulation ----------
const W = 3000, H = 2000;

nodes.forEach((n, i) => {
  const baseR = n.type === "object" ? 22 : 14;
  n.r = Math.min(32, baseR + (n.degree || 0) * 1.5);
  const a = (i / nodes.length) * 2 * Math.PI;
  const r = 500 + 200 * (i % 4);
  n.x = W / 2 + r * Math.cos(a);
  n.y = H / 2 + r * Math.sin(a);
  n.vx = 0; n.vy = 0; n.fixed = false;
});

function tick(alpha) {
  // 1. Anti-overlap collision constraint (Hard circle + label margin collision)
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d = Math.sqrt(dx * dx + dy * dy) || 0.1;
      const minDist = a.r + b.r + 65; // Guaranteed clearance for circle and label card
      if (d < minDist) {
        const overlap = (minDist - d) / d;
        const f = overlap * 0.35 * alpha;
        dx *= f; dy *= f;
        a.vx += dx; a.vy += dy;
        b.vx -= dx; b.vy -= dy;
      }
    }
  }

  // 2. Global pair-wise repulsion (Coulomb force)
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d2 = Math.max(dx * dx + dy * dy, 1);
      if (d2 < 600000) {
        let d = Math.sqrt(d2);
        let f = Math.min(18000 * alpha / d2, 12);
        dx /= d; dy /= d;
        a.vx += dx * f; a.vy += dy * f;
        b.vx -= dx * f; b.vy -= dy * f;
      }
    }
  }

  // 3. Spring forces pulling connected nodes towards targetDist
  activeEdges.forEach(e => {
    const s = nodeById[e.source], t = nodeById[e.target];
    if (!s || !t) return;
    let dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const targetDist = Math.max(220, s.r + t.r + 140);
    const f = (d - targetDist) * 0.05 * alpha;
    dx /= d; dy /= d;
    s.vx += dx * f; s.vy += dy * f;
    t.vx -= dx * f; t.vy -= dy * f;
  });

  // 4. Gentle centering gravity & velocity clamping
  const MAX_V = 20;
  nodes.forEach(n => {
    n.vx += (W / 2 - n.x) * 0.0006 * alpha;
    n.vy += (H / 2 - n.y) * 0.0006 * alpha;
    n.vx *= 0.70; n.vy *= 0.70;
    n.vx = Math.max(-MAX_V, Math.min(MAX_V, n.vx));
    n.vy = Math.max(-MAX_V, Math.min(MAX_V, n.vy));
    if (!n.fixed) { n.x += n.vx; n.y += n.vy; }
    if (!isFinite(n.x) || !isFinite(n.y)) {
      n.x = W / 2 + (Math.random() - 0.5) * 400;
      n.y = H / 2 + (Math.random() - 0.5) * 400;
      n.vx = 0; n.vy = 0;
    }
  });
}

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
    line.setAttribute("marker-end", "url(#arrow)");
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
    c.setAttribute("r", n.r);
    c.setAttribute("fill", TYPE_COLORS[n.type] || DEFAULT_COLOR);
    c.setAttribute("filter", "url(#nodeShadow)");

    const labelText = n.label.length > 28 ? n.label.slice(0, 26) + "..." : n.label;
    const badgeW = Math.min(labelText.length * 7 + 16, 210);
    const badgeH = 19;

    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("class", "label-bg");
    rect.setAttribute("x", -badgeW / 2);
    rect.setAttribute("y", -n.r - 24);
    rect.setAttribute("width", badgeW);
    rect.setAttribute("height", badgeH);
    rect.setAttribute("rx", "4");

    const t = document.createElementNS(NS, "text");
    t.setAttribute("dy", -n.r - 10);
    t.setAttribute("text-anchor", "middle");
    t.textContent = labelText;

    const title = document.createElementNS(NS, "title");
    title.textContent = TYPE_LABELS[n.type] ? TYPE_LABELS[n.type].replace(/s$/, "") + ": " + n.label : n.label;

    g.appendChild(c);
    g.appendChild(rect);
    g.appendChild(t);
    g.appendChild(title);
    nodesG.appendChild(g);

    g.addEventListener("click", ev => {
      ev.stopPropagation();
      select(n);
      if (n.type === "module_root" || n.type === "category_hub") {
        if (n.type === "module_root") {
          expandedModules.has(n.id) ? expandedModules.delete(n.id) : expandedModules.add(n.id);
        } else if (n.type === "category_hub") {
          expandedHubs.has(n.id) ? expandedHubs.delete(n.id) : expandedHubs.add(n.id);
        }
        rebuildGraphState();
        updateDOM();
        restartSimulation();
      }
    });

    g.addEventListener("dblclick", ev => {
      ev.stopPropagation();
      if (n.type === "module_root") {
        if (expandedModules.has(n.id)) {
          expandedModules.delete(n.id);
        } else {
          expandedModules.add(n.id);
        }
        rebuildGraphState();
        updateDOM();
        restartSimulation();
      } else if (n.type === "category_hub") {
        if (expandedHubs.has(n.id)) {
          expandedHubs.delete(n.id);
        } else {
          expandedHubs.add(n.id);
        }
        rebuildGraphState();
        updateDOM();
        restartSimulation();
      }
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
      if (!isFinite(s.x) || !isFinite(s.y) || !isFinite(t.x) || !isFinite(t.y)) return;
      edgeEls[i].setAttribute("x1", s.x); edgeEls[i].setAttribute("y1", s.y);
      edgeEls[i].setAttribute("x2", t.x); edgeEls[i].setAttribute("y2", t.y);
    }
  });
  nodes.forEach((n, i) => {
    if (nodeEls[i] && isFinite(n.x) && isFinite(n.y)) {
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
  // Use getBoundingClientRect for reliable dimensions after layout
  const rect = svg.getBoundingClientRect();
  const bw = rect.width || svg.clientWidth || 1000;
  const bh = rect.height || svg.clientHeight || 700;
  view.k = Math.min(bw / (maxX - minX + 250), bh / (maxY - minY + 250), 1.1);
  view.x = bw / 2 - view.k * (minX + maxX) / 2;
  view.y = bh / 2 - view.k * (minY + maxY) / 2;
  applyView();
}

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
const activeObjects = new Set();
let filtersInitialized = false;

function getNodeObjects(n) {
  let objs = [];
  if (n.type === "object") {
    objs = [n.label];
  } else if (n.data && n.data.object) {
    objs = Array.isArray(n.data.object) ? n.data.object : [n.data.object];
  } else if (n.data && n.data.module && n.data.module !== "Other") {
    objs = [n.data.module];
  }
  if (!objs.length) objs = ["Other"];
  return objs;
}

function rebuildFilters() {
  const objectCounts = {};
  
  nodes.forEach(n => {
    const objs = getNodeObjects(n);
    objs.forEach(o => {
      objectCounts[o] = (objectCounts[o] || 0) + 1;
    });
  });
  
  if (!filtersInitialized) {
    Object.keys(objectCounts).forEach(o => activeObjects.add(o));
    filtersInitialized = true;
  }
  
  const filtersDiv = document.getElementById("filters");
  filtersDiv.innerHTML = "";
  
  const titleHeader = document.createElement("div");
  titleHeader.style.cssText = "font-size:11px;font-weight:700;color:var(--text-muted);margin:10px 0 6px;text-transform:uppercase;letter-spacing:0.05em;";
  titleHeader.textContent = "FILTER BY OSVC OBJECTS";
  filtersDiv.appendChild(titleHeader);
  
  Object.keys(objectCounts).sort().forEach(objName => {
    const label = document.createElement("label");
    label.className = "filter";
    const checked = activeObjects.has(objName) ? "checked" : "";
    label.innerHTML = `<input type="checkbox" ${checked} data-obj="${objName}">
      <span class="swatch" style="background:#9333EA"></span>
      <span>${objName}</span><span class="count">${objectCounts[objName]}</span>`;
    label.querySelector("input").addEventListener("change", ev => {
      ev.target.checked ? activeObjects.add(objName) : activeObjects.delete(objName);
      applyFilters();
      restartSimulation();
    });
    filtersDiv.appendChild(label);
  });
}

const searchBox = document.getElementById("search");
const orphansOnly = document.getElementById("orphansOnly");
const showLabels = document.getElementById("showLabels");
const focusModeToggle = document.getElementById("focusModeToggle");
const expandAllBtn = document.getElementById("expandAllBtn");
const collapseAllBtn = document.getElementById("collapseAllBtn");

if (expandAllBtn) {
  expandAllBtn.addEventListener("click", () => {
    getModuleRoots().forEach(root => {
      expandedModules.add(root.id);
      const moduleComponents = GRAPH.nodes.filter(n => {
        let mod = "Other";
        if (n.type === "object") mod = n.label;
        else if (n.data && n.data.module) mod = n.data.module;
        else if (n.data && n.data.object) mod = Array.isArray(n.data.object) ? n.data.object[0] : n.data.object;
        return mod.toLowerCase() === root.module.toLowerCase();
      });
      const uniqueTypes = [...new Set(moduleComponents.map(n => n.type))];
      uniqueTypes.forEach(type => {
        expandedHubs.add(`hub:${root.module.toLowerCase()}/${type}`);
      });
    });
    rebuildGraphState();
    updateDOM();
    restartSimulation();
  });
}

if (collapseAllBtn) {
  collapseAllBtn.addEventListener("click", () => {
    expandedModules.clear();
    expandedHubs.clear();
    rebuildGraphState();
    updateDOM();
    restartSimulation();
  });
}

let expandedNodeIds = new Set();

focusModeToggle.addEventListener("change", () => {
  expandedNodeIds.clear();
  applyFilters();
});

searchBox.addEventListener("input", applyFilters);
orphansOnly.addEventListener("change", applyFilters);
showLabels.addEventListener("change", () => {
  nodesG.querySelectorAll("text, rect.label-bg").forEach(el => el.style.display = showLabels.checked ? "" : "none");
});

function isNodeInSelectedObjects(n) {
  if (activeObjects.size === 0) return false;
  const activeLower = new Set(Array.from(activeObjects).map(o => String(o).toLowerCase()));
  const nodeObjs = getNodeObjects(n);
  return nodeObjs.some(o => activeLower.has(String(o).toLowerCase()));
}

function nodeVisible(n) {
  if (activeObjects.size > 0 && !isNodeInSelectedObjects(n)) return false;
  if (orphansOnly && orphansOnly.checked && !n.isOrphan) return false;

  const q = searchBox ? searchBox.value.trim().toLowerCase() : "";
  if (q && !n.label.toLowerCase().includes(q)) return false;

  // Focus Mode: when enabled, only show expanded parent nodes and their
  // direct neighbours. All other nodes are hidden until expanded.
  if (focusModeToggle.checked) {
    if (expandedNodeIds.size === 0) return true; // nothing expanded yet, show all
    // Always show expanded nodes themselves
    if (expandedNodeIds.has(n.id)) return true;
    // Show nodes that are a direct neighbour of any expanded node
    const isNeighbour = n.inc.some(e => expandedNodeIds.has(e.source)) ||
                        n.out.some(e => expandedNodeIds.has(e.target));
    if (!isNeighbour) return false;
  }

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
  const arrow = dir === "out" ? "->" : "<-";
  return `<div class="rel" data-node="${esc(otherId)}">
    <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color};margin-right:4px;"></span> ${arrow} <b>${esc(name)}</b>
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
  const detailsBtn = document.querySelector('.tab-btn[data-tab="details"]');
  
  if (!mdPath) {
    tabDoc.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No markdown report generated for this component type.</div>`;
    tabDiagram.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No architecture diagram available for this component type.</div>`;
    docBtn.style.display = "none";
    diagBtn.style.display = "none";
    detailsBtn.click();
    return;
  }
  
  docBtn.style.display = "inline-block";
  diagBtn.style.display = "inline-block";
  
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
  
  // If focus mode enabled, clicking a parent node toggles expanding its child branches
  if (n && focusModeToggle.checked) {
    if (expandedNodeIds.has(n.id)) {
      expandedNodeIds.delete(n.id);
    } else {
      expandedNodeIds.add(n.id);
    }
    applyFilters();
    restartSimulation();
  }

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
    
  if (n.isOrphan) html += `<div class="orphan-flag">[ORPHAN] Orphaned: ${esc(n.orphanReason || "unreferenced")}</div>`;

  html += `<div class="kv"><b>${n.inc.length}</b> inbound | <b>${n.out.length}</b> outbound link(s)</div>`;

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
    facts.push(["[RISK] Risks", riskText]);
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

// ---------- Interactive Animation Loop ----------
let alpha = 0;
let simRafId = null;

function restartSimulation() {
  alpha = 1;
  if (!simRafId) simLoop();
}

function simLoop() {
  simRafId = null;
  alpha *= 0.94;
  if (alpha < 0.002) {
    // Graph has settled — stop ticking to save CPU
    alpha = 0;
    return;
  }
  tick(alpha);
  redraw();
  simRafId = requestAnimationFrame(simLoop);
}

// Defer all initialization until after the browser has finished layout
// so that svg.getBoundingClientRect() returns correct dimensions.
requestAnimationFrame(() => {
  rebuildGraphState();
  for (let i = 0; i < 400; i++) tick(Math.max(0.05, 1 - i / 400));

  // Build DOM and fit the view
  updateDOM();
  fit();

  // Kick off the live simulation
  restartSimulation();
});
