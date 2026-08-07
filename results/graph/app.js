// OSVC Dependency Graph viewer.
// Expects `window.GRAPH_DATA` = { nodes: [...], edges: [...] } and
// `window.GRAPH_META` = { serverVersion, ... } to already be defined
// (normally by a sibling data.js written by build.py) before this file runs.

// Initialize Mermaid with neutral theme matching the light dashboard
mermaid.initialize({
  startOnLoad: false,
  maxTextSize: 1000000,
  maxEdges: 5000,
  theme: 'neutral',
  securityLevel: 'loose',
  flowchart: { useMaxWidth: false, htmlLabels: true, curve: 'basis' },
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
_markedRenderer.code = function (code, lang) {
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
  module_root: "#2563EB",      // Royal Blue Entity Root
  category_hub: "#D97706",     // Warm Amber Category Hub
  workspace: "#9333EA",        // High-Contrast Deep Purple Workspace File
  report: "#059669",           // Emerald Green
  navigationset: "#D97706",    // Warm Amber
  businessrule: "#6D28D9",    // Dark Violet
  customscript: "#E11D48",    // Rose Red
  cpm: "#0D9488",             // Unified Teal Base Fill for CPM Handlers
  asynccpm: "#0D9488",        // Unified Teal Base Fill (Highlighted via Pink Border Stroke)
  osvcobject: "#475569",      // Slate Gray
  externalendpoint: "#B45309",// Burnt Orange
  buiaddin: "#EA580C",        // Vivid Orange
  customfield: "#10B981",     // Bright Emerald/Lime Green for Custom Fields (c$...)
  configsetting: "#CA8A04",   // Gold
  reportcolumn: "#047857",    // Deep Emerald
  cpmmappings: "#0F766E",     // Dark Teal
  workspacefield: "#0284C7",   // Electric Sky Blue for Standard Fields
  object: "#2563EB"           // Royal Blue Object
};
const DEFAULT_COLOR = "#6b7280";

const TYPE_LABELS = {
  module_root: "Entity",
  category_hub: "Category",
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
  object: "Objects"
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
const expandedWorkspaces = new Set();
const coordinatesCache = {};

function getNodeModule(n) {
  if (n.data && n.data.module && n.data.module !== "Other" && n.data.module !== "None" && n.data.module !== "Unknown") {
    return n.data.module;
  }
  if (n.data && n.data.object && n.data.object !== "Other" && n.data.object !== "None" && n.data.object !== "Unknown") {
    const o = Array.isArray(n.data.object) ? n.data.object[0] : n.data.object;
    if (o && o !== "None" && o !== "Other" && o !== "Unknown") return String(o);
  }
  if (n.type === "object" || n.type === "module_root") {
    return n.label;
  }

  const checkText = ((n.label || "") + " " + (n.id || "")).toLowerCase();
  if (checkText.includes("contact") || checkText.includes("call") || checkText.includes("sms")) return "Contact";
  if (checkText.includes("incident") || checkText.includes("note") || checkText.includes("clock") || checkText.includes("validation") || checkText.includes("sr")) return "Incident";
  if (checkText.includes("org") || checkText.includes("account") || checkText.includes("siebel")) return "Organization";
  if (checkText.includes("test_record") || checkText.includes("testrecord")) return "Test_Record";

  return "Other";
}

function getModuleRoots() {
  const modulesSet = new Set();
  (GRAPH.nodes || []).forEach(n => {
    const mod = getNodeModule(n);
    if (mod) modulesSet.add(mod);
  });
  if (!modulesSet.size) modulesSet.add("Other");

  return Array.from(modulesSet).sort().map(mod => {
    const cleanMod = mod.charAt(0).toUpperCase() + mod.slice(1);
    return {
      id: `module:${mod.toLowerCase()}`,
      type: "module_root",
      label: mod,
      module: mod,
      r: 32,
      data: {
        mdPath: `../COMPLETE_SYSTEM_MAPPING_${cleanMod}.md`,
        type: "ModuleRoot",
        label: mod,
        module: mod
      }
    };
  });
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

  // 6 Core Category Hub types under parent Entity roots (Excluding workspacefield)
  const CORE_HUB_TYPES = ["cpm", "report", "buiaddin", "workspace", "customscript", "businessrule"];

  // 2. Add Tier 1 Parent Entity Roots
  roots.forEach(root => {
    nextNodes.push({ ...root });
  });

  // 3. Add Tier 2 Child Category Hubs (The 6 core categories) if Entity Root is expanded
  roots.forEach(root => {
    if (expandedModules.has(root.id)) {
      CORE_HUB_TYPES.forEach(type => {
        const hasComponents = GRAPH.nodes.some(n => {
          const mod = getNodeModule(n).toLowerCase();
          if (mod !== root.module.toLowerCase()) return false;
          if (type === "workspace") return n.type === "workspace";
          if (type === "buiaddin") return n.type === "buiaddin" || n.type === "bui_addin" || n.type === "bui";
          if (type === "cpm") return n.type === "cpm" || n.type === "asynccpm";
          return n.type === type;
        });

        if (hasComponents) {
          const hubId = `hub:${root.module.toLowerCase()}/${type}`;
          const hubLabel = TYPE_LABELS[type] || type;

          const cleanMod = root.module.charAt(0).toUpperCase() + root.module.slice(1);
          let hubMdPath = null;
          if (type === "cpm") {
            hubMdPath = `../cpm/report_CPM_${cleanMod}.md`;
          } else if (type === "businessrule") {
            hubMdPath = `../rules/report_Business_Rules_${cleanMod}.md`;
          } else if (type === "customscript") {
            hubMdPath = `../scripts/report_Custom_Scripts.md`;
          } else if (type === "buiaddin") {
            hubMdPath = `../bui_addins/report_BUI_Addins.md`;
          } else {
            hubMdPath = `../COMPLETE_SYSTEM_MAPPING_${cleanMod}.md`;
          }

          nextNodes.push({
            id: hubId,
            type: "category_hub",
            label: hubLabel,
            module: root.module,
            hubType: type,
            r: 24,
            data: {
              mdPath: hubMdPath,
              type: "Category",
              label: hubLabel,
              module: root.module
            }
          });

          nextEdges.push({
            id: `edge-${root.id}-to-${hubId}`,
            source: root.id,
            target: hubId,
            label: ""
          });
        }
      });
    }
  });

  // 4. Add Tier 3 Component Instances if Category Hub is expanded
  nextNodes.forEach(n => {
    if (n.type === "category_hub" && expandedHubs.has(n.id)) {
      const moduleInstances = GRAPH.nodes.filter(inst => {
        const mod = getNodeModule(inst).toLowerCase();
        const targetHubType = (n.hubType || "").toLowerCase();
        const instType = (inst.type || "").toLowerCase();
        const isMatchingType = instType === targetHubType || 
          (targetHubType === "cpm" && (instType === "cpm" || instType === "asynccpm")) ||
          (targetHubType === "buiaddin" && (instType === "buiaddin" || instType === "bui_addin" || instType === "bui"));
        return mod === n.module.toLowerCase() && isMatchingType;
      });

      moduleInstances.forEach(inst => {
        const baseR = inst.type === "object" ? 22 : 14;
        const r = Math.min(30, baseR + (inst.degree || 0) * 1.5);
        if (!nextNodes.some(m => m.id === inst.id)) {
          nextNodes.push({ ...inst, r: r });
        }

        nextEdges.push({
          id: `edge-${n.id}-to-${inst.id}`,
          source: n.id,
          target: inst.id,
          label: ""
        });
      });
    }
  });

  // 6. Connect cross-component dependency edges if both endpoints are visible
  const visibleNodeIds = new Set(nextNodes.map(n => n.id));
  GRAPH.edges.forEach(e => {
    if (visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target)) {
      nextEdges.push({ ...e });
    }
  });

  // 7. Initial positioning relative to parent nodes
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
      n.x = px + (Math.random() - 0.5) * 160;
      n.y = py + (Math.random() - 0.5) * 160;
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

  // 3. Relaxed Spring forces allowing long, natural link lengths (No collapsing inward)
  activeEdges.forEach(e => {
    const s = nodeById[e.source], t = nodeById[e.target];
    if (!s || !t) return;
    let dx = t.x - s.x, dy = t.y - s.y;
    const d = Math.sqrt(dx * dx + dy * dy) || 1;
    const targetDist = Math.max(380, s.r + t.r + 220);
    const f = (d - targetDist) * 0.015 * alpha;
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

  // 5. Strict Equal Angle Geometric Constraint (360/N deg full 360 circle for Root Parent Nodes & 140 deg Outward Sector Arc for Child Hubs)
  nodes.forEach(parent => {
    if (!parent.out || parent.out.length === 0) return;
    const children = parent.out
      .filter(e => !e.isCrossLink && (!e.label || e.label === "contains" || e.label === "instance" || e.label === "fields" || e.label === "field"))
      .map(e => nodeById[e.target])
      .filter(c => c && c !== parent && !c.fixed);
    const N = children.length;
    if (N === 0) return;

    // Sort children deterministically by ID so layout is 100% stable
    children.sort((a, b) => (a.id || "").localeCompare(b.id || ""));

    const isRootObject = parent.type === "module_root" || (parent.id && parent.id.startsWith("module:"));

    if (isRootObject) {
      // FULL 360 DEGREE EQUAL ANGLE STARBURST CIRCLE (0 deg, 60 deg, 120 deg, 180 deg, 240 deg, 300 deg around parent)
      const angleStep = (2 * Math.PI) / N; // Exact 360 / N degrees (60 deg for 6 hubs)
      const targetRadius = Math.max(340, 40 * N);

      children.forEach((child, idx) => {
        // Start at -Math.PI / 2 (-90 deg) so Child 0 points straight UP (12 o'clock)!
        const targetAngle = -Math.PI / 2 + idx * angleStep;
        const tx = parent.x + targetRadius * Math.cos(targetAngle);
        const ty = parent.y + targetRadius * Math.sin(targetAngle);

        child.x += (tx - child.x) * 0.70;
        child.y += (ty - child.y) * 0.70;
      });
    } else {
      // Find true primary structural parent node
      let inParentNode = null;
      if (parent.inc && parent.inc.length) {
        const structEdge = parent.inc.find(e => 
          e.label === "contains" || e.label === "instance" || e.label === "fields" || !e.label || 
          (nodeById[e.source] && (nodeById[e.source].type === "module_root" || nodeById[e.source].type === "category_hub" || nodeById[e.source].type === "workspace"))
        ) || parent.inc[0];
        inParentNode = nodeById[structEdge.source] || null;
      }

      const isFieldHub = (parent.id && parent.id.toLowerCase().includes("field")) ||
                         children.every(c => c.type === "workspacefield" || c.type === "customfield" || c.type === "object_field");

      if (isFieldHub) {
        // SPACIOUS ALTERNATING RADIUS ARC FOR FIELDS (200 deg Arc, Inner 220px, Outer 310px)
        const dirAngle = inParentNode ? Math.atan2(parent.y - inParentNode.y, parent.x - inParentNode.x) : Math.PI;
        const arcSpan = (200 * Math.PI) / 180;
        const step = N > 1 ? arcSpan / (N - 1) : 0;
        const startAngle = dirAngle - arcSpan / 2;

        children.forEach((child, idx) => {
          const targetAngle = startAngle + idx * step;
          const radius = (idx % 2 === 0) ? 220 : 310;
          const tx = parent.x + radius * Math.cos(targetAngle);
          const ty = parent.y + radius * Math.sin(targetAngle);

          child.x += (tx - child.x) * 0.95;
          child.y += (ty - child.y) * 0.95;
        });
      } else if (inParentNode && inParentNode !== parent) {
        // CHILD HUB NODE: Restricted Outward Sector Arc (140 deg facing away from parent)
        const dirAngle = Math.atan2(parent.y - inParentNode.y, parent.x - inParentNode.x);
        const arcSpan = (140 * Math.PI) / 180;
        const radius = Math.min(260, Math.max(180, 16 * N));

        if (N === 1) {
          const tx = parent.x + radius * Math.cos(dirAngle);
          const ty = parent.y + radius * Math.sin(dirAngle);
          children[0].x += (tx - children[0].x) * 0.95;
          children[0].y += (ty - children[0].y) * 0.95;
        } else {
          const step = arcSpan / (N - 1);
          const startAngle = dirAngle - arcSpan / 2;

          children.forEach((child, idx) => {
            const targetAngle = startAngle + idx * step;
            const tx = parent.x + radius * Math.cos(targetAngle);
            const ty = parent.y + radius * Math.sin(targetAngle);

            child.x += (tx - child.x) * 0.95;
            child.y += (ty - child.y) * 0.95;
          });
        }
      }
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
    const g = document.createElementNS(NS, "g");
    g.setAttribute("class", "edge-group");

    const line = document.createElementNS(NS, "line");
    line.setAttribute("class", "edge");

    if (e.isCrossLink || (e.id && e.id.startsWith("cross-"))) {
      line.classList.add("cross-link-edge");
      line.setAttribute("stroke-dasharray", "8,5");
      line.setAttribute("marker-end", "url(#arrow-cross)");
    } else if (e.label === "contains" || e.label === "instance" || e.label === "fields" || e.label === "field" || !e.label) {
      line.classList.add("parent-edge");
      line.setAttribute("marker-end", "url(#arrow)");
    } else {
      line.classList.add("mapping-edge");
      line.setAttribute("stroke-dasharray", "6,4");
      line.setAttribute("marker-end", "url(#arrow-mapping)");
    }

    const title = document.createElementNS(NS, "title");
    title.textContent = e.label || "";
    line.appendChild(title);
    g.appendChild(line);

    if (e.label && e.label !== "contains" && e.label !== "instance" && e.label !== "fields" && e.label !== "field") {
      const labelText = e.label.length > 28 ? e.label.slice(0, 26) + "..." : e.label;
      const bw = Math.min(labelText.length * 6.5 + 14, 180);
      const bh = 17;

      const rect = document.createElementNS(NS, "rect");
      rect.setAttribute("class", "edge-label-bg");
      rect.setAttribute("width", bw);
      rect.setAttribute("height", bh);
      rect.setAttribute("rx", "3");

      const t = document.createElementNS(NS, "text");
      t.setAttribute("class", "edge-label-text");
      t.textContent = labelText;

      g.appendChild(rect);
      g.appendChild(t);
      g.rectEl = rect;
      g.textEl = t;
      g.badgeW = bw;
      g.badgeH = bh;
    }

    g.lineEl = line;

    // Edge Interaction Event Listeners
    g.addEventListener("click", ev => {
      ev.stopPropagation();
      selectEdge(e);
    });

    g.addEventListener("mouseenter", () => {
      if (!selectedEdge && !selected) {
        highlightEdge(e);
      }
    });

    g.addEventListener("mouseleave", () => {
      if (!selectedEdge && !selected) {
        clearHighlights();
      }
    });

    edgesG.appendChild(g);
    return g;
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

    // BORDER STROKE VARIANT HIGHLIGHTING (Unified Fill Color, Distinct Highlight Borders)
    const isRuleInvoked = (n.data && (n.data.is_rule_invoked || n.data._fallback)) || (n.label && n.label.includes("(Rule Invoked)"));
    if (isRuleInvoked) {
      // Rule-Invoked CPMs: Gold/Amber Dashed Highlight Border
      c.setAttribute("stroke", "#f59e0b");
      c.setAttribute("stroke-width", "3.5");
      c.setAttribute("stroke-dasharray", "4,2");
    } else if (n.type === "asynccpm") {
      // Async CPMs: Pink/Magenta Solid Highlight Border
      c.setAttribute("stroke", "#ec4899");
      c.setAttribute("stroke-width", "3.5");
    } else if (n.type === "customfield") {
      c.setAttribute("stroke", "#059669");
      c.setAttribute("stroke-width", "2");
    } else {
      c.setAttribute("stroke", "rgba(255,255,255,0.4)");
      c.setAttribute("stroke-width", "1.5");
    }

    const labelText = n.label.length > 32 ? n.label.slice(0, 30) + "..." : n.label;
    const badgeW = Math.min(labelText.length * 7 + 16, 230);
    const badgeH = 19;

    const rect = document.createElementNS(NS, "rect");
    rect.setAttribute("class", "label-bg");
    rect.setAttribute("x", -badgeW / 2);
    rect.setAttribute("y", -n.r - 24);
    rect.setAttribute("width", badgeW);
    rect.setAttribute("height", badgeH);
    rect.setAttribute("rx", "4");
    if (isRuleInvoked) {
      rect.setAttribute("stroke", "#f59e0b");
      rect.setAttribute("stroke-width", "1.5");
    }

    const t = document.createElementNS(NS, "text");
    t.setAttribute("dy", -n.r - 10);
    t.setAttribute("text-anchor", "middle");
    t.textContent = labelText;

    const title = document.createElementNS(NS, "title");
    title.textContent = TYPE_LABELS[n.type] ? TYPE_LABELS[n.type].replace(/s$/, "") + ": " + n.label : n.label;

    // Center Eye Icon badge inside the node circle
    const eyeGroup = document.createElementNS(NS, "g");
    eyeGroup.setAttribute("class", "node-eye-btn");
    eyeGroup.setAttribute("transform", "translate(0, 0)");

    const eyeRadius = Math.min(11, Math.max(8, n.r * 0.45));
    const eyeBg = document.createElementNS(NS, "circle");
    eyeBg.setAttribute("class", "eye-bg");
    eyeBg.setAttribute("r", eyeRadius);

    const eyeIcon = document.createElementNS(NS, "path");
    eyeIcon.setAttribute("class", "eye-icon");
    eyeIcon.setAttribute("d", "M -5,0 C -3,-3.2 3,-3.2 5,0 C 3,3.2 -3,3.2 -5,0 Z");

    const eyePupil = document.createElementNS(NS, "circle");
    eyePupil.setAttribute("class", "eye-pupil");
    eyePupil.setAttribute("cx", "0");
    eyePupil.setAttribute("cy", "0");
    eyePupil.setAttribute("r", "1.8");

    const eyeTitle = document.createElementNS(NS, "title");
    eyeTitle.textContent = `Click to view documentation for ${n.label}`;

    eyeGroup.appendChild(eyeBg);
    eyeGroup.appendChild(eyeIcon);
    eyeGroup.appendChild(eyePupil);
    eyeGroup.appendChild(eyeTitle);

    eyeGroup.addEventListener("click", ev => {
      ev.stopPropagation();
      select(n, { openInspector: true, openTab: "doc" });
    });

    g.appendChild(c);
    g.appendChild(eyeGroup);
    g.appendChild(rect);
    g.appendChild(t);

    // Dedicated [+] / [-] branch expansion toggle badge on parent nodes
    const isParentNode = n.type === "module_root" || n.type === "category_hub";
    if (isParentNode) {
      let isExpanded = false;
      if (n.type === "module_root") isExpanded = expandedModules.has(n.id);
      else if (n.type === "category_hub") isExpanded = expandedHubs.has(n.id);

      const toggleGroup = document.createElementNS(NS, "g");
      toggleGroup.setAttribute("class", "node-toggle-badge");
      const toggleX = Math.round(n.r * 0.70);
      const toggleY = Math.round(n.r * 0.70);
      toggleGroup.setAttribute("transform", `translate(${toggleX}, ${toggleY})`);

      const toggleBg = document.createElementNS(NS, "circle");
      toggleBg.setAttribute("r", "9");

      const toggleTxt = document.createElementNS(NS, "text");
      toggleTxt.setAttribute("dy", "1");
      toggleTxt.textContent = isExpanded ? "−" : "+";

      const toggleTitle = document.createElementNS(NS, "title");
      toggleTitle.textContent = isExpanded ? `Collapse ${n.label} branch` : `Expand ${n.label} branch`;

      toggleGroup.appendChild(toggleBg);
      toggleGroup.appendChild(toggleTxt);
      toggleGroup.appendChild(toggleTitle);

      toggleGroup.addEventListener("click", ev => {
        ev.stopPropagation();
        if (n.type === "module_root") {
          expandedModules.has(n.id) ? expandedModules.delete(n.id) : expandedModules.add(n.id);
        } else if (n.type === "category_hub") {
          expandedHubs.has(n.id) ? expandedHubs.delete(n.id) : expandedHubs.add(n.id);
        }
        rebuildGraphState();
        updateDOM();
        restartSimulation();
      });

      g.appendChild(toggleGroup);
    }

    g.appendChild(title);
    nodesG.appendChild(g);

    g.addEventListener("click", ev => {
      ev.stopPropagation();
      select(n, { openInspector: true, openTab: "doc" });
    });

    g.addEventListener("dblclick", ev => {
      ev.stopPropagation();
      select(n, { openInspector: true, openTab: "doc" });
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
    const elGroup = edgeEls[i];
    if (elGroup && s && t) {
      if (!isFinite(s.x) || !isFinite(s.y) || !isFinite(t.x) || !isFinite(t.y)) return;
      elGroup.lineEl.setAttribute("x1", s.x); elGroup.lineEl.setAttribute("y1", s.y);
      elGroup.lineEl.setAttribute("x2", t.x); elGroup.lineEl.setAttribute("y2", t.y);

      if (elGroup.rectEl && elGroup.textEl) {
        const mx = (s.x + t.x) / 2;
        const my = (s.y + t.y) / 2;
        elGroup.rectEl.setAttribute("x", mx - elGroup.badgeW / 2);
        elGroup.rectEl.setAttribute("y", my - elGroup.badgeH / 2);
        elGroup.textEl.setAttribute("x", mx);
        elGroup.textEl.setAttribute("y", my);
      }
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
  const visibleNodes = nodes.filter(n => nodeVisible(n) && isFinite(n.x) && isFinite(n.y));
  if (!visibleNodes.length) return;

  const xs = visibleNodes.map(n => n.x), ys = visibleNodes.map(n => n.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);

  const rect = svg.getBoundingClientRect();
  const bw = rect.width || svg.clientWidth || 1000;
  const bh = rect.height || svg.clientHeight || 700;

  const dx = Math.max(maxX - minX, 240);
  const dy = Math.max(maxY - minY, 240);

  const kw = (bw - 160) / dx;
  const kh = (bh - 160) / dy;

  let targetK = Math.min(kw, kh);
  if (visibleNodes.length <= 3) {
    targetK = Math.min(targetK, 1.15);
  } else if (visibleNodes.length <= 10) {
    targetK = Math.min(targetK, 0.95);
  } else {
    targetK = Math.min(targetK, 0.85);
  }

  view.k = Math.max(0.45, Math.min(targetK, 1.25));
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
const activeComponentTypes = new Set();
let filtersInitialized = false;

function getNodeObjects(n) {
  let objs = [];
  if (n.type === "module_root") {
    objs = [n.module];
  } else if (n.type === "category_hub") {
    objs = [n.module];
  } else {
    const mod = getNodeModule(n);
    if (mod) objs = [mod];
  }
  if (!objs.length) objs = ["Other"];
  return objs;
}

function rebuildFilters() {
  const objectCounts = {};
  const componentTypeCounts = {};

  nodes.forEach(n => {
    const objs = getNodeObjects(n);
    objs.forEach(o => {
      objectCounts[o] = (objectCounts[o] || 0) + 1;
    });

    if (n.type !== "module_root" && n.type !== "category_hub") {
      const typeKey = (n.type || "unknown").toLowerCase();
      componentTypeCounts[typeKey] = (componentTypeCounts[typeKey] || 0) + 1;
    }
  });

  if (!filtersInitialized) {
    (GRAPH.nodes || []).forEach(n => {
      if (n.type && n.type !== "module_root" && n.type !== "category_hub") {
        activeComponentTypes.add(n.type.toLowerCase());
      }
    });

    const sortedObjectNames = Object.keys(objectCounts).sort();
    if (sortedObjectNames.length > 0) {
      activeObjects.add(sortedObjectNames[0]);
    }
    filtersInitialized = true;
  }

  const filtersDiv = document.getElementById("filters");
  filtersDiv.innerHTML = "";

  // 1. FILTER BY OSVC OBJECTS
  const objectTitle = document.createElement("div");
  objectTitle.style.cssText = "font-size:11px;font-weight:700;color:var(--text-muted);margin:10px 0 6px;text-transform:uppercase;letter-spacing:0.05em;";
  objectTitle.textContent = "FILTER BY OSVC OBJECTS";
  filtersDiv.appendChild(objectTitle);

  Object.keys(objectCounts).sort().forEach(objName => {
    const label = document.createElement("label");
    label.className = "filter";
    const checked = activeObjects.has(objName) ? "checked" : "";
    const color = TYPE_COLORS[objName.toLowerCase()] || TYPE_COLORS.module_root;
    label.innerHTML = `<input type="checkbox" ${checked} data-obj="${objName}">
      <span class="swatch" style="background:${color}"></span>
      <span>${objName}</span><span class="count">${objectCounts[objName]}</span>`;
    label.querySelector("input").addEventListener("change", ev => {
      ev.target.checked ? activeObjects.add(objName) : activeObjects.delete(objName);
      applyFilters();
      restartSimulation();
    });
    filtersDiv.appendChild(label);
  });

  // 2. FILTER BY COMPONENT TYPE (With Color Swatches & Checkboxes)
  if (Object.keys(componentTypeCounts).length > 0) {
    const typeTitle = document.createElement("div");
    typeTitle.style.cssText = "font-size:11px;font-weight:700;color:var(--text-muted);margin:16px 0 6px;text-transform:uppercase;letter-spacing:0.05em;border-top:1px solid var(--border-subtle);padding-top:10px;";
    typeTitle.textContent = "FILTER BY COMPONENT TYPE";
    filtersDiv.appendChild(typeTitle);

    Object.keys(componentTypeCounts).sort().forEach(typeKey => {
      const label = document.createElement("label");
      label.className = "filter";
      const checked = activeComponentTypes.has(typeKey) ? "checked" : "";
      const color = TYPE_COLORS[typeKey] || DEFAULT_COLOR;
      const typeLabel = TYPE_LABELS[typeKey] || typeKey;

      label.innerHTML = `<input type="checkbox" ${checked} data-type="${typeKey}">
        <span class="swatch" style="background:${color}"></span>
        <span>${typeLabel}</span><span class="count">${componentTypeCounts[typeKey]}</span>`;
      label.querySelector("input").addEventListener("change", ev => {
        ev.target.checked ? activeComponentTypes.add(typeKey) : activeComponentTypes.delete(typeKey);
        applyFilters();
        restartSimulation();
      });
      filtersDiv.appendChild(label);
    });
  }
}

const searchBox = document.getElementById("search");
const orphansOnly = document.getElementById("orphansOnly");
const showLabels = document.getElementById("showLabels");
const showEdgeLabels = document.getElementById("showEdgeLabels");
const focusModeToggle = document.getElementById("focusModeToggle");

if (showEdgeLabels) {
  showEdgeLabels.addEventListener("change", () => {
    const disp = showEdgeLabels.checked ? "inline" : "none";
    document.querySelectorAll(".edge-label-bg, .edge-label-text").forEach(el => {
      el.style.display = disp;
    });
  });
}
const expandAllBtn = document.getElementById("expandAllBtn");
const collapseAllBtn = document.getElementById("collapseAllBtn");

if (expandAllBtn) {
  expandAllBtn.addEventListener("click", () => {
    getModuleRoots().forEach(root => {
      expandedModules.add(root.id);
      ["cpm", "report", "buiaddin", "workspace", "customscript", "businessrule"].forEach(type => {
        expandedHubs.add(`hub:${root.module.toLowerCase()}/${type}`);
      });
    });
    GRAPH.nodes.filter(n => n.type === "workspace").forEach(ws => {
      expandedWorkspaces.add(ws.id);
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
    expandedWorkspaces.clear();
    rebuildGraphState();
    updateDOM();
    restartSimulation();
  });
}

// ---------- Export SVG / PNG Handlers ----------
function prepareExportableSvg(svgEl) {
  const clone = svgEl.cloneNode(true);

  // 1. Ensure XML namespaces
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  clone.setAttribute("xmlns:xlink", "http://www.w3.org/1999/xlink");

  // 2. Compute tight bounding box with padding
  let bbox = { x: -100, y: -100, width: 1600, height: 1000 };
  try {
    const rawBox = svgEl.getBBox();
    if (rawBox && rawBox.width > 0 && rawBox.height > 0) {
      bbox = rawBox;
    }
  } catch (err) {
    console.warn("Could not compute getBBox, using fallback bounds", err);
  }

  const pad = 60;
  const vx = Math.floor(bbox.x - pad);
  const vy = Math.floor(bbox.y - pad);
  const vw = Math.max(800, Math.ceil(bbox.width + pad * 2));
  const vh = Math.max(600, Math.ceil(bbox.height + pad * 2));

  clone.setAttribute("viewBox", `${vx} ${vy} ${vw} ${vh}`);
  clone.setAttribute("width", vw);
  clone.setAttribute("height", vh);

  // 3. Add clean solid background
  const bgRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  bgRect.setAttribute("x", vx);
  bgRect.setAttribute("y", vy);
  bgRect.setAttribute("width", vw);
  bgRect.setAttribute("height", vh);
  bgRect.setAttribute("fill", "#FAF8F5");
  clone.insertBefore(bgRect, clone.firstChild);

  // 4. Embed self-contained CSS style block inside exported SVG
  const styleEl = document.createElementNS("http://www.w3.org/2000/svg", "style");
  styleEl.textContent = `
    svg { background-color: #FAF8F5 !important; }
    .node rect.label-bg { fill: #FFFFFF !important; fill-opacity: 0.96 !important; stroke: #CBD5E1 !important; stroke-width: 1.2px !important; rx: 4px; ry: 4px; }
    .edge-label-bg { fill: #FFFFFF !important; fill-opacity: 0.95 !important; stroke: #CBD5E1 !important; stroke-width: 1px !important; rx: 3px; ry: 3px; }
    text { fill: #0F172A !important; font-size: 11px !important; font-weight: 600 !important; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; text-anchor: middle !important; }
    text.edge-label-text { fill: #334155 !important; font-size: 9.5px !important; font-weight: 600 !important; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important; text-anchor: middle !important; }
    .node circle { stroke-width: 2.5px !important; }
    .node.selected rect.label-bg { fill: #FFFFFF !important; stroke: #990026 !important; stroke-width: 2px !important; }
    .node.selected text { fill: #990026 !important; font-weight: 700 !important; }
    line.edge, path.edge-line { fill: none !important; stroke-width: 1.8px !important; }
    marker path { opacity: 1 !important; }
  `;
  clone.insertBefore(styleEl, clone.firstChild);

  // 5. Apply explicit inline presentation attributes ONLY to node/edge rects, text, and lines (EXCLUDING defs/markers)
  clone.querySelectorAll(".node rect, .edge-group rect").forEach(rect => {
    rect.setAttribute("fill", "#FFFFFF");
    rect.setAttribute("fill-opacity", "0.95");
    rect.setAttribute("stroke", "#CBD5E1");
    rect.setAttribute("stroke-width", "1");
    rect.setAttribute("rx", "4");
    rect.setAttribute("ry", "4");
  });

  clone.querySelectorAll("text").forEach(txt => {
    if (txt.classList.contains("edge-label-text")) {
      txt.setAttribute("fill", "#334155");
      txt.setAttribute("font-size", "9.5");
      txt.setAttribute("font-weight", "600");
      txt.setAttribute("font-family", "Inter, -apple-system, sans-serif");
      txt.setAttribute("text-anchor", "middle");
    } else {
      txt.setAttribute("fill", "#0F172A");
      txt.setAttribute("font-size", "11");
      txt.setAttribute("font-weight", "600");
      txt.setAttribute("font-family", "Inter, -apple-system, sans-serif");
      txt.setAttribute("text-anchor", "middle");
    }
  });

  // Ensure line/path edge elements preserve stroke & marker-end without wiping arrowhead fills
  clone.querySelectorAll("line.edge, path.edge-line, .edge").forEach(edgeEl => {
    edgeEl.setAttribute("fill", "none");
    if (!edgeEl.getAttribute("stroke")) {
      edgeEl.setAttribute("stroke", "#94A3B8");
    }
    edgeEl.setAttribute("stroke-width", "1.8");
  });

  // Preserve marker arrowhead fills explicitly
  const markerFills = { "arrow": "#64748B", "arrow-mapping": "#2563EB", "arrow-cross": "#E11D48", "arrowHl": "#2563EB" };
  clone.querySelectorAll("marker").forEach(m => {
    const mid = m.getAttribute("id");
    const mPath = m.querySelector("path");
    if (mPath) {
      const c = markerFills[mid] || "#64748B";
      mPath.setAttribute("fill", c);
      mPath.setAttribute("opacity", "1");
    }
  });

  return { clone, width: vw, height: vh };
}

const exportSvgBtn = document.getElementById("exportSvgBtn");
if (exportSvgBtn) {
  exportSvgBtn.addEventListener("click", () => {
    const svgEl = document.getElementById("svg");
    const { clone } = prepareExportableSvg(svgEl);
    const serializer = new XMLSerializer();
    const source = '<?xml version="1.0" encoding="utf-8"?>\n' + serializer.serializeToString(clone);
    const blob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "osvc_dependency_graph.svg";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  });
}

const exportPngBtn = document.getElementById("exportPngBtn");
if (exportPngBtn) {
  exportPngBtn.addEventListener("click", () => {
    const svgEl = document.getElementById("svg");
    const { clone, width, height } = prepareExportableSvg(svgEl);
    const serializer = new XMLSerializer();
    const source = '<?xml version="1.0" encoding="utf-8"?>\n' + serializer.serializeToString(clone);
    const img = new Image();
    img.width = width;
    img.height = height;
    const svgBlob = new Blob([source], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      const scale = 2; // High-DPI 2x resolution
      const canvas = document.createElement("canvas");
      canvas.width = width * scale;
      canvas.height = height * scale;
      const ctx = canvas.getContext("2d");
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = "high";
      ctx.scale(scale, scale);
      ctx.fillStyle = "#FAF8F5";
      ctx.fillRect(0, 0, width, height);
      ctx.drawImage(img, 0, 0, width, height);
      URL.revokeObjectURL(url);

      const pngUrl = canvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.href = pngUrl;
      a.download = "osvc_dependency_graph.png";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    };
    img.src = url;
  });
}

// ---------- View Master Report Handler ----------
const viewMasterReportBtn = document.getElementById("viewMasterReportBtn");
if (viewMasterReportBtn) {
  viewMasterReportBtn.addEventListener("click", () => {
    fetch("/results/COMPLETE_SYSTEM_MAPPING.md")
      .then(res => res.text())
      .then(async md => {
        const inspector = document.getElementById("inspector");
        const tabDetails = document.getElementById("tab-details");
        const tabDoc = document.getElementById("tab-doc");
        const tabDiagram = document.getElementById("tab-diagram");

        // 1. Build Details Tab
        const totalNodes = nodes.length;
        const totalEdges = edges.length;
        const orphanCount = nodes.filter(n => n.isOrphan).length;

        if (tabDetails) {
          tabDetails.innerHTML = `<h2>Master System Architecture</h2>
            <span class="type-chip" style="background:#7C3AED;">System Mapping Report</span>
            <div class="kv" style="margin-top:12px;"><b>${totalNodes}</b> total components | <b>${totalEdges}</b> active linkages</div>
            ${orphanCount > 0 ? `<div class="orphan-flag">SYSTEM AUDIT: ${orphanCount} Orphaned Component(s) Flagged</div>` : ""}
            <h3>Environment Summary</h3>
            <div class="kv">Total Graph Nodes: <b>${totalNodes}</b></div>
            <div class="kv">Total Dependency Edges: <b>${totalEdges}</b></div>
            <div class="kv">Orphaned Components: <b>${orphanCount}</b></div>
            <p style="font-size:11px;color:var(--text-muted);margin-top:12px;">
              Select individual nodes in the dependency graph to inspect component-level details, or click the <b>Documentation</b> tab for the complete mapping report.
            </p>`;
        }

        // 2. Build Documentation Tab
        if (tabDoc) {
          tabDoc.innerHTML = typeof marked !== "undefined"
            ? `<div style="padding:16px;">${marked.parse(md)}</div>`
            : `<pre style="padding:16px;white-space:pre-wrap;">${md}</pre>`;
          await renderMermaidBlocksInContainer(tabDoc);
          renderHtmlPreviewsInContainer(tabDoc);
        }

        // 3. Build Rich, Informative Layered System Architecture Flowchart
        if (tabDiagram) {
          let sysCode = "flowchart TD\n";
          sysCode += '  subgraph Contact_Pipeline ["Contact Data Pipeline & Integrations"]\n';
          sysCode += '    WS_Contact["Contact Workspace<br/>(9 Fields | 5 Tabs | Business Rules)"] -->|Renders UI| OBJ_Contact["Contact Object<br/>(Core Schema Root)"]\n';
          sysCode += '    BUI_Contact["ContactOrgLookup BUI Add-In<br/>(Reads: c$siebel_id, OrgId)"] -->|UI Extension| WS_Contact\n';
          sysCode += '    BUI_Contact -->|SOAP Call| EP_Siebel["Siebel CRM Integration Service<br/>(urn:soap:RegisterContact)"]\n';
          sysCode += '    OBJ_Contact -->|On Create/Update| CPM_ContactSync["contact_create / contact_update CPM<br/>(Synchronous PHP Event Handler)"]\n';
          sysCode += '    CPM_ContactSync -->|Queues Async Event| CPM_ContactAsync["ContactAsync CPM<br/>(Asynchronous Execution Queue)"]\n';
          sysCode += '    CPM_ContactAsync -->|Executes Script| SCR_Cityworks["cityworksapicall.php<br/>(Custom REST Integration Script)"]\n';
          sysCode += '    SCR_Cityworks -->|HTTP POST| EP_Cityworks["CityWorks Active Calls API<br/>(http://209.91.135.228/api/listactivecalls)"]\n';
          sysCode += '  end\n\n';

          sysCode += '  subgraph Incident_Pipeline ["Incident Lifecycle & Automated Routing"]\n';
          sysCode += '    WS_Incident["Incident Workspace<br/>(Split Panel Layout)"] -->|Renders UI| OBJ_Incident["Incident Object<br/>(Core Schema Root)"]\n';
          sysCode += '    WS_Incident -->|On Save Validation| SCR_Notes["closing_notes.php / duplicate_incidents.php"]\n';
          sysCode += '    OBJ_Incident -->|On Create| CPM_IncCreate["incident_create CPM<br/>(Synchronous Handler)"]\n';
          sysCode += '    CPM_IncCreate -->|Queues Async Routing| CPM_IncRouting["incident_routing CPM<br/>(Automated Incident Routing)"]\n';
          sysCode += '    CPM_IncRouting -->|Spawns Child| SCR_ChildInc["child_incident_create.php"]\n';
          sysCode += '  end\n\n';

          sysCode += '  subgraph Audit_Orphans ["Audit-Critical Orphaned Components (0 Linkages)"]\n';
          sysCode += '    ORPH_1["address_validation.php<br/>(Orphan Script: 0 Callers)"]\n';
          sysCode += '    ORPH_2["bluebox_greencart_validation.php<br/>(Orphan Script: 0 Callers)"]\n';
          sysCode += '    ORPH_3["eventclock.php / sms_integration 1.php<br/>(Orphan Script: 0 Callers)"]\n';
          sysCode += '  end\n';

          await renderMermaidDiagram(tabDiagram, sysCode);

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
        }

        // Show inspector and activate Documentation tab by default
        inspector.classList.add("open");
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        const docBtn = document.querySelector('.tab-btn[data-tab="doc"]');
        if (docBtn) docBtn.classList.add("active");
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
        if (tabDoc) tabDoc.classList.add("active");
      })
      .catch(err => alert("Master Report not found. Run analysis first."));
  });
}

const downloadMasterReportBtn = document.getElementById("downloadMasterReportBtn");
if (downloadMasterReportBtn) {
  downloadMasterReportBtn.addEventListener("click", () => {
    fetch("/results/COMPLETE_SYSTEM_MAPPING.md")
      .then(res => {
        if (!res.ok) throw new Error("File not found");
        return res.blob();
      })
      .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "COMPLETE_SYSTEM_MAPPING.md";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      })
      .catch(err => {
        window.location.href = "/api/download-master-report";
      });
  });
}
const selectAllObjectsBtn = document.getElementById("selectAllObjectsBtn");
const deselectAllObjectsBtn = document.getElementById("deselectAllObjectsBtn");

if (selectAllObjectsBtn) {
  selectAllObjectsBtn.addEventListener("click", () => {
    (GRAPH.nodes || []).forEach(n => {
      const objs = getNodeObjects(n);
      objs.forEach(o => activeObjects.add(o));
    });
    rebuildFilters();
    applyFilters();
    restartSimulation();
  });
}

if (deselectAllObjectsBtn) {
  deselectAllObjectsBtn.addEventListener("click", () => {
    activeObjects.clear();
    rebuildFilters();
    applyFilters();
    restartSimulation();
  });
}

let expandedNodeIds = new Set();

focusModeToggle.addEventListener("change", () => {
  expandedNodeIds.clear();
  applyFilters();
});

searchBox.addEventListener("input", () => {
  applyFilters();
  const q = searchBox.value.trim().toLowerCase();
  if (q) {
    const matches = nodes.filter(n => {
      const labelMatch = (n.label || "").toLowerCase().includes(q);
      const idMatch = (n.id || "").toLowerCase().includes(q);
      return labelMatch || idMatch;
    });
    if (matches.length > 0) {
      zoomToFit(matches);
    }
  }
});

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

function isNodeInSelectedComponentTypes(n) {
  if (n.type === "module_root" || n.type === "category_hub") return true;
  if (activeComponentTypes.size === 0) return false;
  const typeKey = (n.type || "").toLowerCase();
  return activeComponentTypes.has(typeKey);
}

function nodeVisible(n) {
  if (activeObjects.size > 0 && !isNodeInSelectedObjects(n)) return false;
  if (activeComponentTypes.size > 0 && !isNodeInSelectedComponentTypes(n)) return false;
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
  fit();
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
      edgeEls[i].lineEl.classList.toggle("hl", touches);
      edgeEls[i].classList.toggle("dim", !touches);
      edgeEls[i].lineEl.classList.toggle("dim", !touches);
    }
  });
}

let selectedEdge = null;

function highlightEdge(targetEdge) {
  const edgeNodes = new Set([targetEdge.source, targetEdge.target]);
  nodes.forEach((m, i) => {
    if (nodeEls[i]) {
      nodeEls[i].classList.toggle("dim", !edgeNodes.has(m.id));
      nodeEls[i].classList.toggle("hover-hl", edgeNodes.has(m.id));
    }
  });

  activeEdges.forEach((e, i) => {
    const isTarget = e === targetEdge;
    if (edgeEls[i]) {
      edgeEls[i].classList.toggle("hl", isTarget);
      edgeEls[i].lineEl.classList.toggle("hl", isTarget);
      edgeEls[i].classList.toggle("dim", !isTarget);
      edgeEls[i].lineEl.classList.toggle("dim", !isTarget);
    }
  });
}

function clearHighlights() {
  selectedEdge = null;
  nodes.forEach((m, i) => {
    if (nodeEls[i]) {
      nodeEls[i].classList.remove("dim", "hover-hl");
    }
  });
  activeEdges.forEach((e, i) => {
    if (edgeEls[i]) {
      edgeEls[i].classList.remove("hl", "dim");
      edgeEls[i].lineEl.classList.remove("hl", "dim");
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

function extractMermaidCode(markdown, node) {
  if (!markdown) return null;
  const blocks = [];
  const regex = /```mermaid([\s\S]*?)```/g;
  let match;
  while ((match = regex.exec(markdown)) !== null) {
    blocks.push(match[1].trim());
  }
  if (!blocks.length) return null;

  // 1. For CPM reports or CPM nodes: prioritize the master multi-layer Flow Diagram (Mappings_Layer / Procedures_Layer)
  for (const b of blocks) {
    if (b.includes("Mappings_Layer") || b.includes("Procedures_Layer") || b.includes("Objects_Layer")) {
      return b;
    }
  }

  // 2. Otherwise match node-specific block if present
  if (node && (node.label || node.id || (node.data && node.data.name))) {
    const term = (node.label || node.id || (node.data && node.data.name) || "").toLowerCase();
    for (const b of blocks) {
      if (b.toLowerCase().includes(term)) {
        return b;
      }
    }
  }

  // 3. Fallback to last or first block
  return blocks[blocks.length - 1] || blocks[0];
}

function attachDiagramLegendOverlay(container, isModal = false) {
  if (!container || container.querySelector(".diagram-vertical-legend")) return;

  const legend = document.createElement("div");
  legend.className = "diagram-vertical-legend";
  const topPos = isModal ? "70px" : "10px";
  const rightPos = isModal ? "24px" : "10px";

  legend.style.cssText = `
    position: absolute;
    top: ${topPos};
    right: ${rightPos};
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(153, 0, 38, 0.22);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border-radius: 8px;
    padding: 10px 12px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    font-size: 11px;
    font-family: 'Inter', -apple-system, sans-serif;
    z-index: 100;
    display: flex;
    flex-direction: column;
    gap: 5px;
    pointer-events: auto;
    max-width: 165px;
  `;

  legend.innerHTML = `
    <div style="font-weight: 800; color: #990026; font-size: 10px; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 2px;">COLOR MAP LEGEND</div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#2563eb;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">Rule States</span></div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#7c3aed;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">Functions &amp; Rules</span></div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#059669;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">Set Field</span></div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#3b82f6;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">State Transition</span></div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#d97706;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">Execute CPM</span></div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#ec4899;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">Call Function</span></div>
    <div style="display:flex;align-items:center;gap:6px;"><span style="width:10px;height:10px;border-radius:2px;background:#64748b;display:inline-block;flex-shrink:0;"></span><span style="color:#1e293b;font-weight:600;">Other Actions</span></div>
  `;

  if (getComputedStyle(container).position === "static") {
    container.style.position = "relative";
  }
  container.appendChild(legend);
}

async function renderMermaidDiagram(container, mermaidCode) {
  try {
    container.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">Generating diagram...</div>`;
    const uniqueId = `mermaid-svg-${++mermaidCount}`;
    const { svg } = await mermaid.render(uniqueId, mermaidCode);
    container.innerHTML = `<div class="mermaid" style="position:relative;">${svg}</div>`;
    attachDiagramLegendOverlay(container.querySelector(".mermaid"));
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

function generateDynamicMermaidForNode(n) {
  let code = "flowchart LR\n";
  const safeId = (id) => "N_" + String(id).replace(/[^a-zA-Z0-9_]/g, "_");
  const safeLabel = (lbl) => '"' + String(lbl || "").replace(/"/g, "'") + '"';

  const ntype = (n.type || "").toLowerCase();
  const data = n.data || {};

  if (ntype === "cpm" || ntype === "asynccpm") {
    if (data && data.flow_diagram) {
      return data.flow_diagram;
    }
    const name = n.label || data.name || n.id;
    const obj = data.object_type || n.module || "Object";
    const evt = data.operations_label || data.script_type || "Event Trigger";
    const isAsync = data.is_async || ntype === "asynccpm" ? "Async Execution Queue" : "Synchronous Event Handler";
    const entry = data.entry_point || "ObjectProcedure::apply";

    code += `  classDef crudNode fill:#2563eb,stroke:#1d4ed8,color:#fff,font-weight:bold;\n`;
    code += `  classDef soapNode fill:#10b981,stroke:#047857,color:#fff;\n\n`;

    code += `  subgraph CPM_Proc ["CPM Procedure: ${name}"]\n`;
    code += `    EVT["Trigger Event: ${evt}"] -->|Fires on| OBJ["Entity Object: ${obj}"]\n`;
    code += `    OBJ -->|Executes| PROC["${isAsync}<br/>(Entry: ${entry})"]\n`;
    code += `  end\n\n`;

    const crudOps = data.internal_crud_ops || [];
    if (crudOps.length) {
      crudOps.forEach((cop, idx) => {
        const cId = `CRUD_${idx}`;
        code += `  ${cId}["CRUD API: ${String(cop).replace(/"/g, "'")}"]:::crudNode\n`;
        code += `  PROC -->|Executes CRUD| ${cId}\n`;
      });
    }

    const soaps = data.soap_actions || [];
    if (soaps.length) {
      soaps.forEach((soap, idx) => {
        const sId = `SOAP_${idx}`;
        code += `  ${sId}["SOAP Action: ${String(soap).replace(/"/g, "'")}"]:::soapNode\n`;
        code += `  PROC -->|Outbound Call| ${sId}\n`;
      });
    }

    let hasLinks = false;
    if (n.inc && n.inc.length) {
      n.inc.forEach(e => {
        const src = nodeById[e.source];
        if (src) {
          hasLinks = true;
          const lbl = e.label ? `|"${String(e.label).replace(/"/g, "'")}"|` : "|inbound|";
          code += `  ${safeId(src.id)}[${safeLabel(src.label)}] -->${lbl} PROC\n`;
        }
      });
    }

    if (n.out && n.out.length) {
      n.out.forEach(e => {
        const tgt = nodeById[e.target];
        if (tgt) {
          hasLinks = true;
          const lbl = e.label ? `|"${String(e.label).replace(/"/g, "'")}"|` : "|outbound|";
          code += `  PROC -->${lbl} ${safeId(tgt.id)}[${safeLabel(tgt.label)}]\n`;
        }
      });
    }

    return code;
  }

  if (ntype === "businessrule") {
    const mod = n.module || (data && data.module) || "Incident";
    code = "flowchart LR\n";
    code += `  classDef stateNode fill:#2563eb,stroke:#1d4ed8,color:#fff,font-weight:bold;\n`;
    code += `  classDef funcNode fill:#7c3aed,stroke:#5b21b6,color:#fff,font-weight:bold;\n`;
    code += `  classDef actNode fill:#059669,stroke:#047857,color:#fff;\n`;
    code += `  classDef actTrans fill:#3b82f6,stroke:#1d4ed8,color:#fff;\n`;
    code += `  classDef actCpm fill:#d97706,stroke:#b45309,color:#fff,font-weight:bold;\n\n`;

    code += `  subgraph Legend ["Color Map Legend"]\n`;
    code += `    direction TB\n`;
    code += `    LEG_ST["Blue: Rule States"]:::stateNode\n`;
    code += `    LEG_FN["Purple: Functions & Rules"]:::funcNode\n`;
    code += `    LEG_SET["Green: Set Field"]:::actNode\n`;
    code += `    LEG_TR["Sky Blue: State Trans"]:::actTrans\n`;
    code += `    LEG_CPM["Orange: Execute CPM"]:::actCpm\n`;
    code += `    LEG_ST --- LEG_FN\n`;
    code += `    LEG_FN --- LEG_SET\n`;
    code += `    LEG_SET --- LEG_TR\n`;
    code += `    LEG_TR --- LEG_CPM\n`;
    code += `  end\n\n`;

    code += `  subgraph Tier1 ["1. States (Start)"]\n`;
    code += `    ST_INIT["State: Initial State"]:::stateNode\n`;
    code += `    ST_OBJ["State: ${mod} Rules"]:::stateNode\n`;
    code += `  end\n\n`;

    code += `  subgraph Tier2 ["2. Functions & Rules"]\n`;
    code += `    FN_ROUTE["Rule/Func: Auto-Route & Assignment"]:::funcNode\n`;
    code += `    FN_FIELD["Rule/Func: Field Validation & Defaults"]:::funcNode\n`;
    code += `  end\n\n`;

    code += `  subgraph Tier3 ["3. Related Action Types"]\n`;
    code += `    ACT_SET["Action: SetField (Status / Queue)"]:::actNode\n`;
    code += `    ACT_TRANS["Action: TransitionState"]:::actTrans\n`;
    code += `    ACT_CPM["Action: Execute CPM Handler"]:::actCpm\n`;
    code += `  end\n\n`;

    code += `  ST_INIT -->|"contains"| FN_ROUTE\n`;
    code += `  ST_OBJ -->|"contains"| FN_FIELD\n`;
    code += `  FN_ROUTE -->|"action (SetField)"| ACT_SET\n`;
    code += `  FN_ROUTE -->|"action (TransitionState)"| ACT_TRANS\n`;
    code += `  FN_FIELD -->|"action (CPMCall)"| ACT_CPM\n`;

    return code;
  }

  code += `  ${safeId(n.id)}[${safeLabel(n.label)}]\n`;
  code += `  style ${safeId(n.id)} fill:#7C3AED,stroke:#4C1D95,color:#fff,stroke-width:2px\n`;

  let hasLinks = false;
  if (n.inc && n.inc.length) {
    n.inc.forEach(e => {
      const src = nodeById[e.source];
      if (src) {
        hasLinks = true;
        const lbl = e.label ? `|"${String(e.label).replace(/"/g, "'")}"|` : "";
        code += `  ${safeId(src.id)}[${safeLabel(src.label)}] -->${lbl} ${safeId(n.id)}\n`;
      }
    });
  }

  if (n.out && n.out.length) {
    n.out.forEach(e => {
      const tgt = nodeById[e.target];
      if (tgt) {
        hasLinks = true;
        const lbl = e.label ? `|"${String(e.label).replace(/"/g, "'")}"|` : "";
        code += `  ${safeId(n.id)} -->${lbl} ${safeId(tgt.id)}[${safeLabel(tgt.label)}]\n`;
      }
    });
  }

  if (!hasLinks) {
    code += `  N_SYSTEM["OSVC Accelerator Subsystem"] --> ${safeId(n.id)}\n`;
  }

  return code;
}

async function loadDocsAndDiagrams(node) {
  tabDoc.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">Loading documentation...</div>`;
  tabDiagram.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:10px;">Loading architecture diagram...</div>`;

  let mdPath = node.data && node.data.mdPath;
  const nType = (node.type || "").toLowerCase();
  const mod = node.module || (node.data && (node.data.module || node.data.object)) || "Contact";
  const cleanMod = mod.charAt(0).toUpperCase() + mod.slice(1);

  if (nType === "cpm" || nType === "asynccpm") {
    const rawLabel = node.label || (node.data && node.data.name) || "Procedure";
    const safeLabel = rawLabel.replace(/ /g, "_");
    mdPath = `../cpm/report_CPM_${cleanMod}_${safeLabel}.md`;
  } else if (!mdPath && node) {
    if (node.type === "category_hub") {
      const hType = node.hubType;
      if (hType === "cpm") {
        mdPath = `../cpm/report_CPM_${cleanMod}.md`;
      } else if (hType === "businessrule") {
        mdPath = `../rules/report_Business_Rules_${cleanMod}.md`;
      } else if (hType === "customscript") {
        mdPath = `../scripts/report_Custom_Scripts.md`;
      } else if (hType === "buiaddin") {
        mdPath = `../bui_addins/report_BUI_Addins.md`;
      } else {
        mdPath = `../COMPLETE_SYSTEM_MAPPING_${cleanMod}.md`;
      }
    } else if (node.type === "module_root") {
      mdPath = `../COMPLETE_SYSTEM_MAPPING_${cleanMod}.md`;
    }
  }

  const docBtn = document.querySelector('.tab-btn[data-tab="doc"]');
  const diagBtn = document.querySelector('.tab-btn[data-tab="diagram"]');
  const aiTabBtn = document.getElementById("aiTabBtn");
  const meta = window.GRAPH_META || {};

  if (docBtn) docBtn.style.display = "inline-block";
  if (diagBtn) diagBtn.style.display = "inline-block";
  if (aiTabBtn) {
    if (meta && meta.useAiSummary === true) {
      aiTabBtn.style.display = "inline-block";
    } else {
      aiTabBtn.style.display = "none";
    }
  }

  if (currentFetchController) {
    currentFetchController.abort();
  }
  currentFetchController = new AbortController();

  let mermaidCode = null;
  let mdText = null;

  if (mdPath) {
    const cleanPath = mdPath.replace(/^\.\.\//, "");
    const fileName = cleanPath.split("/").pop();
    const cleanFileName = fileName.replace(/ /g, "_");
    const spaceFileName = fileName.replace(/_/g, " ");

    const candidateUrls = [
      mdPath,
      "/results/" + cleanPath,
      "/results/" + cleanPath.replace(/ /g, "_"),
      "/results/markdown/" + cleanPath,
      "/results/markdown/" + cleanPath.replace(/ /g, "_"),
      "/results/bui_addins/" + fileName,
      "/results/bui_addins/" + cleanFileName,
      "/results/reports/" + fileName,
      "/results/reports/" + cleanFileName,
      "/results/workspaces/" + fileName,
      "/results/workspaces/" + cleanFileName,
      "/results/cpm/" + fileName,
      "/results/cpm/" + cleanFileName,
      "/results/rules/" + fileName,
      "/results/rules/" + cleanFileName,
      "/results/scripts/" + fileName,
      "/results/scripts/" + cleanFileName,
      "/results/scripts/" + spaceFileName
    ];

    for (const url of candidateUrls) {
      try {
        const fetchUrl = url + (url.includes("?") ? "&" : "?") + "_t=" + Date.now();
        const response = await fetch(fetchUrl, { signal: currentFetchController.signal });
        if (response.ok) {
          const txt = await response.text();
          if (txt && txt.trim() && !txt.trim().toLowerCase().startsWith("<!doctype html>")) {
            mdText = txt;
            break;
          }
        }
      } catch (err) {
        if (err.name === "AbortError") return;
      }
    }
  }

function attachAccordionToggleBar(container) {
  if (!container || container.querySelector(".accordion-toggle-bar")) return;
  const detailsEls = container.querySelectorAll("details");
  if (!detailsEls || !detailsEls.length) return;

  const bar = document.createElement("div");
  bar.className = "accordion-toggle-bar";
  bar.style.cssText = `
    display: flex;
    gap: 8px;
    margin: 0 0 14px 0;
    align-items: center;
  `;

  bar.innerHTML = `
    <button class="btn-expand-all" style="background: linear-gradient(180deg, #2563eb, #1d4ed8); color: #ffffff; border: 1px solid #1e40af; padding: 5px 14px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.12); display: inline-flex; align-items: center; gap: 4px;">+ Expand</button>
    <button class="btn-collapse-all" style="background: linear-gradient(180deg, #475569, #334155); color: #ffffff; border: 1px solid #1e293b; padding: 5px 14px; border-radius: 6px; font-size: 11px; font-weight: 600; cursor: pointer; transition: all 0.15s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.12); display: inline-flex; align-items: center; gap: 4px;">&minus; Collapse</button>
  `;

  bar.querySelector(".btn-expand-all").addEventListener("click", () => {
    container.querySelectorAll("details").forEach(d => d.open = true);
  });
  bar.querySelector(".btn-collapse-all").addEventListener("click", () => {
    container.querySelectorAll("details").forEach(d => d.open = false);
  });

  container.insertBefore(bar, container.firstChild);
}

  if (mdText) {
    tabDoc.innerHTML = typeof marked !== "undefined" ? marked.parse(mdText) : `<pre style="white-space:pre-wrap;">${esc(mdText)}</pre>`;
    await renderMermaidBlocksInContainer(tabDoc);
    renderHtmlPreviewsInContainer(tabDoc);
    attachAccordionToggleBar(tabDoc);
    mermaidCode = extractMermaidCode(mdText, node);
  }

  if (!tabDoc.innerHTML || tabDoc.innerHTML.includes("Loading documentation")) {
    tabDoc.innerHTML = `<div style="padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">
      <h3>${esc(node.label)}</h3>
      <p><b>Component Type:</b> ${esc(TYPE_LABELS[node.type] || node.type)}</p>
      <p><b>Associated Module:</b> ${esc(node.module || "General")}</p>
      <p><b>Inbound Connections:</b> ${node.inc ? node.inc.length : 0}</p>
      <p><b>Outbound Connections:</b> ${node.out ? node.out.length : 0}</p>
      ${node.isOrphan ? `<div style="color:#E11D48;font-weight:700;margin-top:8px;">ORPHAN WARNING: ${esc(node.orphanReason || "Unreferenced component")}</div>` : ""}
    </div>`;
  }

  if (!mermaidCode) {
    mermaidCode = generateDynamicMermaidForNode(node);
  }

  if (mermaidCode) {
    await renderMermaidDiagram(tabDiagram, mermaidCode);
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
  }

  // Populate AI Assist Tab if enabled
  renderAiAssistTab(node, mdText);
}

let configFetchedApiKey = "";
try {
  fetch("/api/config-key")
    .then(res => res.json())
    .then(d => {
      if (d && d.apiKey) configFetchedApiKey = d.apiKey;
    })
    .catch(() => {});
} catch (e) {}

function renderAiAssistTab(node, mdText) {
  const tabAi = document.getElementById("tab-ai");
  if (!tabAi) return;

  const configKey = configFetchedApiKey || (window.GRAPH_META && (window.GRAPH_META.apiKey || window.GRAPH_META.api_key)) || "";
  const savedKey = localStorage.getItem("gemini_api_key") || configKey || "";
  const isFromConfig = !!configKey && savedKey === configKey;

  tabAi.innerHTML = `
    <div style="padding: 14px; font-size: 13px;">
      <div style="font-weight: 700; font-size: 14px; margin-bottom: 6px; color: var(--accent-primary, #a855f7); display: flex; align-items: center; gap: 8px;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:18px;height:18px;min-width:18px;max-width:18px;max-height:18px;display:inline-block;"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>
        AI Assist (Gemini & LLM Summary)
      </div>
      <div style="color: var(--text-muted); font-size: 12px; margin-bottom: 14px; line-height: 1.4;">
        Generate an intelligent executive summary for <b>${esc(node.label || node.id)}</b> using your API Key based on the component's markdown documentation.
      </div>

      <div style="background: var(--panel2); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 12px; margin-bottom: 14px;">
        <label style="display: block; font-weight: 700; font-size: 11px; margin-bottom: 6px; color: var(--text-main); text-transform: uppercase; letter-spacing: 0.5px;">API KEY (CONFIG / GEMINI / GROQ):</label>
        <div style="display: flex; gap: 8px;">
          <input type="password" id="geminiApiKeyInput" value="${esc(savedKey)}" placeholder="AIzaSy... or gsk_..." style="flex: 1; padding: 6px 10px; font-size: 12px; border: 1px solid var(--border-subtle); border-radius: 6px; background: var(--panel); color: var(--text-main);" />
          <button id="saveApiKeyBtn" style="padding: 6px 12px; font-size: 11px; font-weight: 700; background: var(--accent-primary); color: #fff; border: none; border-radius: 6px; cursor: pointer;">Save Key</button>
        </div>
        <div id="keyStatusMsg" style="font-size: 11px; color: #10b981; margin-top: 6px; display: ${savedKey ? 'block' : 'none'};">
          ${isFromConfig ? 'Loaded automatically from config (.env)' : 'Saved in browser storage'}
        </div>
      </div>

      <button id="generateAiSummaryBtn" style="width: 100%; padding: 10px 14px; font-size: 12px; font-weight: 700; background: linear-gradient(135deg, #a855f7, #7c3aed); color: #fff; border: none; border-radius: 6px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.15); transition: opacity 0.15s;">
        <span>Generate AI Summary</span>
      </button>

      <div id="aiOutputArea" style="margin-top: 16px;"></div>
    </div>
  `;

  const saveBtn = document.getElementById("saveApiKeyBtn");
  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      const keyVal = (document.getElementById("geminiApiKeyInput").value || "").trim();
      if (keyVal) {
        localStorage.setItem("gemini_api_key", keyVal);
        const msg = document.getElementById("keyStatusMsg");
        if (msg) {
          msg.style.display = "block";
          msg.textContent = "Saved in browser storage";
        }
      }
    });
  }

  const genBtn = document.getElementById("generateAiSummaryBtn");
  if (genBtn) {
    genBtn.addEventListener("click", async () => {
      const keyInput = document.getElementById("geminiApiKeyInput");
      const keyVal = (keyInput ? keyInput.value.trim() : "") || localStorage.getItem("gemini_api_key") || configKey;
      const outputArea = document.getElementById("aiOutputArea");
      if (!keyVal) {
        if (outputArea) {
          outputArea.innerHTML = `<div style="padding: 10px; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; font-size: 12px;">Please enter and save your API Key first.</div>`;
        }
        return;
      }

      if (outputArea) {
        outputArea.innerHTML = `<div style="padding: 12px; color: var(--text-muted); font-size: 12px; font-weight: 600;">Analyzing component documentation with AI...</div>`;
      }

      try {
        const slicedDoc = (mdText || "No detailed markdown content available.").slice(0, 2500);
        const promptText = `Provide a concise, 2 to 3 sentence executive AI summary for the following Oracle Service Cloud component documentation. Highlight main purpose, execution flow, and any risk flags:\n\nComponent: ${node.label || node.id}\nDocumentation:\n${slicedDoc}`;

        let generatedMd = null;

        if (keyVal.startsWith("gsk_")) {
          // Call Groq API endpoint with high token limit model (llama-3.1-8b-instant)
          let res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Authorization": `Bearer ${keyVal}`
            },
            body: JSON.stringify({
              model: "llama-3.1-8b-instant",
              messages: [{ role: "user", content: promptText }]
            })
          });
          let resData = await res.json();

          // Fallback if llama-3.1-8b-instant returns rate limit
          if (resData.error && resData.error.code === "rate_limit_exceeded") {
            res = await fetch("https://api.groq.com/openai/v1/chat/completions", {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${keyVal}`
              },
              body: JSON.stringify({
                model: "mixtral-8x7b-32768",
                messages: [{ role: "user", content: promptText }]
              })
            });
            resData = await res.json();
          }

          if (resData.error) {
            if (outputArea) {
              const errDetails = resData.error.message || "Rate limit reached";
              outputArea.innerHTML = `<div style="padding: 12px; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #b91c1c; border-radius: 6px; font-size: 12px; line-height: 1.4;">
                <b>Groq API Rate Limit:</b> ${esc(errDetails)}<br/><br/>
                <i>Tip: Enter a Google Gemini API Key (starts with <b>AIzaSy</b>) in the input box above for higher token capacity.</i>
              </div>`;
            }
            return;
          }
          generatedMd = resData.choices && resData.choices[0] && resData.choices[0].message && resData.choices[0].message.content;
        } else {
          // Call Gemini API endpoint
          const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${encodeURIComponent(keyVal)}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              contents: [{ parts: [{ text: promptText }] }]
            })
          });
          const resData = await res.json();
          if (resData.error) {
            if (outputArea) {
              outputArea.innerHTML = `<div style="padding: 10px; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; font-size: 12px;">Gemini API Error: ${esc(resData.error.message || "Failed to generate summary")}</div>`;
            }
            return;
          }
          generatedMd = resData.candidates && resData.candidates[0] && resData.candidates[0].content && resData.candidates[0].content.parts[0] && resData.candidates[0].content.parts[0].text;
        }

        if (generatedMd && outputArea) {
          outputArea.innerHTML = `<div style="background: var(--panel2); border: 1px solid var(--border-subtle); border-radius: 8px; padding: 14px; font-size: 12px; line-height: 1.5;" class="ai-summary-content">` + (typeof marked !== "undefined" ? marked.parse(generatedMd) : `<pre style="white-space:pre-wrap;">${esc(generatedMd)}</pre>`) + `</div>`;
        } else if (outputArea) {
          outputArea.innerHTML = `<div style="padding: 10px; color: var(--text-muted); font-size: 12px;">No summary response received from API.</div>`;
        }
      } catch (err) {
        if (outputArea) {
          outputArea.innerHTML = `<div style="padding: 10px; background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; color: #ef4444; border-radius: 6px; font-size: 12px;">Error connecting to API: ${esc(err.message)}</div>`;
        }
      }
    });
  }
}

function select(n, options = {}) {
  selected = n;
  selectedEdge = null;

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

  const shouldOpen = options && options.openInspector !== undefined ? options.openInspector : true;
  inspector.classList.toggle("open", !!shouldOpen && !!n);
  if (!n) return;

  if (options && options.openTab) {
    const targetTabBtn = document.querySelector(`.tab-btn[data-tab="${options.openTab}"]`);
    if (targetTabBtn) {
      targetTabBtn.click();
    }
  }

  // Build Details Tab
  let html = `<h2>${esc(n.label)}</h2>
    <span class="type-chip" style="background:${TYPE_COLORS[n.type] || DEFAULT_COLOR}">
    ${esc(TYPE_LABELS[n.type] ? TYPE_LABELS[n.type].replace(/s$/, "") : n.type)}</span>`;



  if (n.isOrphan) html += `<div class="orphan-flag">ORPHAN: ${esc(n.orphanReason || "unreferenced")}</div>`;

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
    facts.push(["Risks", riskText]);
  }

  if (facts.length) {
    html += "<h3>Details</h3>" + facts.map(([k, v]) =>
      `<div class="kv">${esc(k)}: <b>${esc(v)}</b></div>`).join("");
  }

  tabDetails.innerHTML = html;
  tabDetails.querySelectorAll(".rel").forEach(el => {
    el.addEventListener("click", () => {
      const target = nodeById[el.dataset.node];
      if (target) select(target, { openInspector: true });
    });
  });



  if (options && options.openTab === "doc") {
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
    const docBtn = document.querySelector('.tab-btn[data-tab="doc"]');
    if (docBtn) docBtn.classList.add("active");
    document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
    if (tabDoc) tabDoc.classList.add("active");
  }

  // Async fetch markdown documentation and compile Mermaid
  loadDocsAndDiagrams(n);
}

function selectEdge(e) {
  selected = null;
  selectedEdge = e;

  const srcNode = nodeById[e.source];
  const tgtNode = nodeById[e.target];

  highlightEdge(e);
  inspector.classList.add("open");

  const edgeLabel = e.label || "Dependency Relationship";
  let html = `<h2>${esc(edgeLabel)}</h2>
    <span class="type-chip" style="background:#EF4444">Dependency Link</span>
    <div class="kv" style="margin-top:10px;">Connected between <b>${esc(srcNode ? srcNode.label : e.source)}</b> and <b>${esc(tgtNode ? tgtNode.label : e.target)}</b></div>`;

  html += `<h3 style="margin-top:14px;">Connection Details</h3>`;
  if (srcNode) {
    html += `<div class="rel" data-node="${esc(srcNode.id)}">
      <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${TYPE_COLORS[srcNode.type] || DEFAULT_COLOR};margin-right:4px;"></span>
      <b>Source:</b> ${esc(srcNode.label)}
      <div class="via">${esc(TYPE_LABELS[srcNode.type] || srcNode.type)}</div>
    </div>`;
  }
  if (tgtNode) {
    html += `<div class="rel" data-node="${esc(tgtNode.id)}">
      <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${TYPE_COLORS[tgtNode.type] || DEFAULT_COLOR};margin-right:4px;"></span>
      <b>Target:</b> ${esc(tgtNode.label)}
      <div class="via">${esc(TYPE_LABELS[tgtNode.type] || tgtNode.type)}</div>
    </div>`;
  }

  html += `<h3 style="margin-top:14px;">Documentation Quick-Jump</h3>`;
  if (srcNode && srcNode.data && srcNode.data.mdPath) {
    html += `<button class="tab-btn edge-doc-btn" data-node="${esc(srcNode.id)}" style="width:100%;margin-bottom:6px;background:var(--accent-primary);color:#fff;font-weight:600;">View Source Docs (${esc(srcNode.label)})</button>`;
  }
  if (tgtNode && tgtNode.data && tgtNode.data.mdPath) {
    html += `<button class="tab-btn edge-doc-btn" data-node="${esc(tgtNode.id)}" style="width:100%;background:var(--panel);border:1px solid var(--border-subtle);color:var(--text-main);font-weight:600;">View Target Docs (${esc(tgtNode.label)})</button>`;
  }

  tabDetails.innerHTML = html;

  tabDetails.querySelectorAll(".rel").forEach(el => {
    el.addEventListener("click", () => {
      const target = nodeById[el.dataset.node];
      if (target) select(target);
    });
  });

  tabDetails.querySelectorAll(".edge-doc-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const target = nodeById[btn.dataset.node];
      if (target) select(target);
    });
  });

  const docTargetNode = (tgtNode && tgtNode.data && tgtNode.data.mdPath) ? tgtNode : (srcNode && srcNode.data && srcNode.data.mdPath ? srcNode : null);
  if (docTargetNode) {
    loadDocsAndDiagrams(docTargetNode);
  } else {
    tabDoc.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No markdown documentation generated for these structural nodes.</div>`;
    tabDiagram.innerHTML = `<div style="color:var(--text-muted); font-size:12px; padding:12px; border:1px solid var(--border-subtle); border-radius:6px; background:var(--panel);">No architecture diagram available for these structural nodes.</div>`;
  }
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

  // Attach non-intrusive floating vertical legend overlay
  attachDiagramLegendOverlay(diagramModal, true);

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
