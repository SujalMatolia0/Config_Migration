// OSVC Dependency Graph viewer.
// Expects `window.GRAPH_DATA` = { nodes: [...], edges: [...] } and
// `window.GRAPH_META` = { serverVersion, ... } to already be defined
// (normally by a sibling data.js written by build.py) before this file runs.

// Keep in sync with analyser/graph_builder.py TYPE_COLORS.
const TYPE_COLORS = {
  workspace: "#1e6091",
  report: "#38761d",
  navigationset: "#b45309",
  businessrule: "#7c3aed",
  customscript: "#be123c",
  cpm: "#0f766e",
  asynccpm: "#0891b2",
  osvcobject: "#475569",
  externalendpoint: "#a16207",
  buiaddin: "#c2410c",
  customfield: "#4d7c0f",
  configsetting: "#854d0e",
  reportcolumn: "#166534",
  cpmmappings: "#134e4a",
  workspacefield: "#1d4ed8",
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
  workspacefield: "Workspace Fields",
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

const nodes = GRAPH.nodes.map(n => ({ ...n }));
const nodeById = {};
nodes.forEach(n => (nodeById[n.id] = n));
const edges = GRAPH.edges.filter(e => nodeById[e.source] && nodeById[e.target]);

// adjacency for inspector + highlighting
nodes.forEach(n => { n.out = []; n.inc = []; n.degree = 0; });
edges.forEach(e => {
  nodeById[e.source].out.push(e); nodeById[e.target].inc.push(e);
  nodeById[e.source].degree++; nodeById[e.target].degree++;
});

// ---------- layout: simple force simulation ----------
const W = 1600, H = 1000;
nodes.forEach((n, i) => {
  const a = (i / nodes.length) * 2 * Math.PI;
  const r = 250 + 150 * (i % 3);
  n.x = W / 2 + r * Math.cos(a); n.y = H / 2 + r * Math.sin(a);
  n.vx = 0; n.vy = 0; n.fixed = false;
});
function tick(alpha) {
  // repulsion (O(n^2) — fine for config graphs)
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = a.x - b.x, dy = a.y - b.y;
      let d2 = dx * dx + dy * dy || 1;
      if (d2 < 250000) {
        const f = 2600 * alpha / d2;
        const d = Math.sqrt(d2);
        dx /= d; dy /= d;
        a.vx += dx * f * 60; a.vy += dy * f * 60;
        b.vx -= dx * f * 60; b.vy -= dy * f * 60;
      }
    }
  }
  // springs
  edges.forEach(e => {
    const s = nodeById[e.source], t = nodeById[e.target];
    let dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const f = (d - 160) * 0.02 * alpha * 6;
    dx /= d; dy /= d;
    s.vx += dx * f; s.vy += dy * f;
    t.vx -= dx * f; t.vy -= dy * f;
  });
  // centering + integrate
  nodes.forEach(n => {
    n.vx += (W / 2 - n.x) * 0.0015 * alpha * 6;
    n.vy += (H / 2 - n.y) * 0.0015 * alpha * 6;
    if (!n.fixed) { n.x += n.vx; n.y += n.vy; }
    n.vx *= 0.6; n.vy *= 0.6;
  });
}
for (let i = 0; i < 400; i++) tick(Math.max(0.05, 1 - i / 400));

// ---------- render ----------
const svg = document.getElementById("svg");
const viewport = document.getElementById("viewport");
const edgesG = document.getElementById("edges");
const nodesG = document.getElementById("nodes");
const NS = "http://www.w3.org/2000/svg";

const edgeEls = edges.map(e => {
  const line = document.createElementNS(NS, "line");
  line.setAttribute("class", "edge");
  const title = document.createElementNS(NS, "title");
  title.textContent = e.label || "";
  line.appendChild(title);
  edgesG.appendChild(line);
  return line;
});

const nodeEls = nodes.map(n => {
  const g = document.createElementNS(NS, "g");
  g.setAttribute("class", "node" + (n.isOrphan ? " orphan" : ""));
  const c = document.createElementNS(NS, "circle");
  c.setAttribute("r", Math.min(26, 9 + n.degree * 1.6));
  c.setAttribute("fill", TYPE_COLORS[n.type] || DEFAULT_COLOR);
  const t = document.createElementNS(NS, "text");
  t.setAttribute("dy", -Math.min(26, 9 + n.degree * 1.6) - 4);
  t.setAttribute("text-anchor", "middle");
  t.textContent = n.label.length > 34 ? n.label.slice(0, 33) + "…" : n.label;
  const title = document.createElementNS(NS, "title");
  title.textContent = TYPE_LABELS[n.type] ? TYPE_LABELS[n.type].replace(/s$/, "") + ": " + n.label : n.label;
  g.appendChild(c); g.appendChild(t); g.appendChild(title);
  nodesG.appendChild(g);
  g.addEventListener("click", ev => { ev.stopPropagation(); select(n); });
  enableDrag(g, n);
  return g;
});

function redraw() {
  edges.forEach((e, i) => {
    const s = nodeById[e.source], t = nodeById[e.target];
    edgeEls[i].setAttribute("x1", s.x); edgeEls[i].setAttribute("y1", s.y);
    edgeEls[i].setAttribute("x2", t.x); edgeEls[i].setAttribute("y2", t.y);
  });
  nodes.forEach((n, i) => nodeEls[i].setAttribute("transform", `translate(${n.x},${n.y})`));
}
redraw();

// ---------- zoom / pan ----------
let view = { x: 0, y: 0, k: 0.7 };
function applyView() {
  viewport.setAttribute("transform", `translate(${view.x},${view.y}) scale(${view.k})`);
}
(function fit() {
  if (!nodes.length) return;
  const xs = nodes.map(n => n.x), ys = nodes.map(n => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const bw = svg.clientWidth || 1000, bh = svg.clientHeight || 700;
  view.k = Math.min(bw / (maxX - minX + 200), bh / (maxY - minY + 200), 1.2);
  view.x = bw / 2 - view.k * (minX + maxX) / 2;
  view.y = bh / 2 - view.k * (minY + maxY) / 2;
  applyView();
})();
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
      redraw();
    }
    function up() {
      window.removeEventListener("mousemove", move);
      window.removeEventListener("mouseup", up);
    }
    window.addEventListener("mousemove", move);
    window.addEventListener("mouseup", up);
  });
}

// ---------- filters / search / orphans ----------
const typeCounts = {};
nodes.forEach(n => typeCounts[n.type] = (typeCounts[n.type] || 0) + 1);
const activeTypes = new Set(Object.keys(typeCounts));
const filtersDiv = document.getElementById("filters");
Object.keys(typeCounts).sort().forEach(t => {
  const label = document.createElement("label");
  label.className = "filter";
  label.innerHTML = `<input type="checkbox" checked data-type="${t}">
    <span class="swatch" style="background:${TYPE_COLORS[t] || DEFAULT_COLOR}"></span>
    <span>${TYPE_LABELS[t] || t}</span><span class="count">${typeCounts[t]}</span>`;
  label.querySelector("input").addEventListener("change", ev => {
    ev.target.checked ? activeTypes.add(t) : activeTypes.delete(t);
    applyFilters();
  });
  filtersDiv.appendChild(label);
});
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
    nodeEls[i].style.display = vis[n.id] ? "" : "none";
  });
  edges.forEach((e, i) => {
    edgeEls[i].style.display = (vis[e.source] && vis[e.target]) ? "" : "none";
  });
}

// ---------- inspector ----------
const inspector = document.getElementById("inspector");
const inspBody = document.getElementById("inspBody");
document.getElementById("closeBtn").addEventListener("click", () => select(null));
let selected = null;

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
function select(n) {
  selected = n;
  nodes.forEach((m, i) => nodeEls[i].classList.toggle("selected", m === n));
  if (n) {
    const near = new Set([n.id]);
    n.out.forEach(e => near.add(e.target));
    n.inc.forEach(e => near.add(e.source));
    nodes.forEach((m, i) => nodeEls[i].classList.toggle("dim", !near.has(m.id)));
    edges.forEach((e, i) => {
      const touches = e.source === n.id || e.target === n.id;
      edgeEls[i].classList.toggle("hl", touches);
      edgeEls[i].classList.toggle("dim", !touches);
    });
  } else {
    nodes.forEach((m, i) => nodeEls[i].classList.remove("dim"));
    edges.forEach((e, i) => { edgeEls[i].classList.remove("hl", "dim"); });
  }
  inspector.classList.toggle("open", !!n);
  if (!n) return;

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
  inspBody.innerHTML = html;
  inspBody.querySelectorAll(".rel").forEach(el => {
    el.addEventListener("click", () => {
      const target = nodeById[el.dataset.node];
      if (target) select(target);
    });
  });
}
