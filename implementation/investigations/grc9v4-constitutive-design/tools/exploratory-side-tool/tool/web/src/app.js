import cytoscape from "cytoscape";
import {
  createIcons,
  Database,
  Focus,
  GitBranch,
  LocateFixed,
  Network,
  Search,
} from "lucide";
import "./styles.css";
import { familyById, filterCatalog, projectionFor, sourceState, verifyBundle } from "./bundle.js";

const KIND_COLORS = {
  current_claim: "#1f766d",
  historical_claim: "#8a7a68",
  debt_transformation: "#b05c3b",
  gate_record: "#3d6f9d",
  profile: "#7a5a94",
  normative_object: "#287e9a",
  equation_contract: "#4f6570",
  source_record: "#687078",
  candidate: "#986124",
  realization: "#6169a4",
  verification_obligation: "#a34c62",
  annotation: "#8b9094",
};

const state = {
  bundle: null,
  selectedNodeId: null,
  familyId: "candidate_A",
  query: "",
  tab: "details",
  mode: "source",
  cy: null,
};

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function compact(value) {
  if (Array.isArray(value)) return value.join(", ");
  if (value && typeof value === "object") return JSON.stringify(value);
  return String(value ?? "-");
}

function kindLabel(kind) {
  return kind.replaceAll("_", " ");
}

function renderShell(source) {
  document.querySelector("#app").innerHTML = `
    <header class="topbar">
      <div class="brand-block">
        <div class="brand-mark" aria-hidden="true">G4</div>
        <div>
          <h1>GRCv4 Constitutive Explorer</h1>
          <div class="subline">Accepted design topology / ${escapeHtml(state.bundle.status.replaceAll("_", " "))}</div>
        </div>
      </div>
      <div class="topbar-actions">
        <div class="mode-control" role="group" aria-label="Evidence mode">
          <button class="mode-button is-active" data-mode="source">Source</button>
          <button class="mode-button" data-mode="speculative">Speculative</button>
        </div>
        <div class="source-state source-state--${source.tone}" title="Standalone bundle state">
          <span class="source-state-dot"></span>${escapeHtml(source.label)}
        </div>
      </div>
    </header>
    <main class="workspace" data-mode="source">
      <aside class="navigation-panel" aria-label="Investigation navigation">
        <div class="search-wrap">
          <i data-lucide="search" aria-hidden="true"></i>
          <input id="search-input" type="search" placeholder="Search claims, objects, gates..." aria-label="Search investigation" autocomplete="off" />
        </div>
        <section class="family-section" aria-labelledby="family-heading">
          <div class="section-heading" id="family-heading">Object families</div>
          <div id="family-list" class="family-list"></div>
        </section>
        <section class="result-section" aria-labelledby="result-heading">
          <div class="section-heading" id="result-heading">Selection</div>
          <div id="search-results" class="search-results" role="listbox"></div>
        </section>
      </aside>
      <section class="graph-panel" aria-label="Focused topology">
        <div class="graph-toolbar">
          <div>
            <div class="eyebrow">Bounded neighborhood</div>
            <div id="graph-summary" class="graph-summary"></div>
          </div>
          <button id="fit-graph" class="icon-button" title="Fit graph" aria-label="Fit graph">
            <i data-lucide="locate-fixed" aria-hidden="true"></i>
          </button>
        </div>
        <div id="graph" role="img" aria-label="Focused claim topology graph"></div>
        <div id="graph-boundary" class="graph-boundary"></div>
      </section>
      <aside class="inspector-panel" aria-label="Selection inspector">
        <div id="selection-header" class="selection-header"></div>
        <div class="tab-list" role="tablist">
          <button class="tab is-active" data-tab="details" role="tab">Details</button>
          <button class="tab" data-tab="lenses" role="tab">Lenses</button>
          <button class="tab" data-tab="reach" role="tab">Reach</button>
        </div>
        <div id="inspector-content" class="inspector-content"></div>
      </aside>
    </main>
  `;
  createIcons({ icons: { Search, LocateFixed, Database, Focus, GitBranch, Network } });
}

function renderFamilies() {
  const container = document.querySelector("#family-list");
  container.innerHTML = state.bundle.family_coverage
    .map(
      (family) => `
        <button class="family-row ${family.family_id === state.familyId ? "is-active" : ""}" data-family="${escapeHtml(family.family_id)}">
          <span>${escapeHtml(family.family_id.replaceAll("_", " "))}</span>
          <span class="count">${family.object_count}</span>
        </button>`,
    )
    .join("");
  container.querySelectorAll("[data-family]").forEach((button) => {
    button.addEventListener("click", () => {
      state.familyId = button.dataset.family;
      const family = familyById(state.bundle, state.familyId);
      if (family?.node_ids.length) selectNode(family.node_ids[0]);
      renderFamilies();
      renderSearchResults();
    });
  });
}

function renderSearchResults() {
  const rows = filterCatalog(state.bundle, state.query, state.familyId).slice(0, 80);
  const container = document.querySelector("#search-results");
  container.innerHTML = rows.length
    ? rows
        .map(
          (row) => `
            <button role="option" class="result-row ${row.node_id === state.selectedNodeId ? "is-active" : ""}" data-node-id="${escapeHtml(row.node_id)}" aria-selected="${row.node_id === state.selectedNodeId}">
              <span class="kind-dot" style="--kind-color:${KIND_COLORS[row.kind] ?? "#687078"}"></span>
              <span class="result-copy">
                <span class="result-label">${escapeHtml(row.label)}</span>
                <span class="result-meta">${escapeHtml(kindLabel(row.kind))} / ${escapeHtml(row.identifier)}</span>
              </span>
            </button>`,
        )
        .join("")
    : `<div class="empty-state">No matching compiled nodes</div>`;
  container.querySelectorAll("[data-node-id]").forEach((button) => {
    button.addEventListener("click", () => selectNode(button.dataset.nodeId));
  });
}

function graphElements(projection) {
  const nodes = projection.focus.nodes.map((node) => ({
    data: {
      id: node.node_id,
      label: node.label,
      kind: node.kind,
      isRoot: node.node_id === projection.focus.root_node_id,
    },
    classes: node.node_id === projection.focus.root_node_id ? "root" : "",
  }));
  const edges = projection.focus.edges.map((edge) => ({
    data: {
      id: edge.edge_id,
      source: edge.source,
      target: edge.target,
      relation: edge.relation,
      support: edge.support_semantic ?? "display_only",
    },
    classes: edge.support_semantic === "negative_boundary" ? "negative" : "",
  }));
  return [...nodes, ...edges];
}

function renderGraph(projection) {
  if (state.cy) state.cy.destroy();
  state.cy = cytoscape({
    container: document.querySelector("#graph"),
    elements: graphElements(projection),
    wheelSensitivity: 0.22,
    minZoom: 0.35,
    maxZoom: 2.2,
    style: [
      {
        selector: "node",
        style: {
          width: 34,
          height: 34,
          "background-color": (node) => KIND_COLORS[node.data("kind")] ?? "#687078",
          "border-width": 2,
          "border-color": "#ffffff",
          label: (node) => node.data("label"),
          "font-size": 9,
          "text-wrap": "ellipsis",
          "text-max-width": 112,
          "text-valign": "bottom",
          "text-margin-y": 8,
          color: "#263238",
        },
      },
      {
        selector: "node.root",
        style: { width: 48, height: 48, "border-width": 4, "border-color": "#17242a", "font-weight": 700 },
      },
      {
        selector: "edge",
        style: {
          width: 1.3,
          "line-color": "#aeb9be",
          "target-arrow-color": "#89969c",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "arrow-scale": 0.7,
          opacity: 0.82,
        },
      },
      { selector: "edge.negative", style: { "line-style": "dashed", "line-color": "#b05c3b", "target-arrow-color": "#b05c3b" } },
      { selector: ":selected", style: { "overlay-opacity": 0, "border-color": "#10191d", "border-width": 5 } },
    ],
    layout: {
      name: "concentric",
      animate: false,
      fit: true,
      padding: 48,
      minNodeSpacing: 42,
      concentric: (node) => (node.data("isRoot") ? 3 : 1),
      levelWidth: () => 1,
    },
  });
  state.cy.on("tap", "node", (event) => selectNode(event.target.id()));
  const focus = projection.focus;
  document.querySelector("#graph-summary").textContent = `${focus.nodes.length} nodes / ${focus.edges.length} relationships`;
  document.querySelector("#graph-boundary").textContent =
    focus.omitted_direct_neighbor_count || focus.omitted_incident_edge_count
      ? `${focus.omitted_direct_neighbor_count} neighbors and ${focus.omitted_incident_edge_count} relationships outside this bounded view`
      : "Complete direct neighborhood within the bounded view";
}

function attributeRows(attributes) {
  return Object.entries(attributes)
    .slice(0, 24)
    .map(
      ([key, value]) => `<div class="detail-row"><dt>${escapeHtml(key.replaceAll("_", " "))}</dt><dd>${escapeHtml(compact(value))}</dd></div>`,
    )
    .join("");
}

function renderDetails(projection) {
  const node = projection.selection;
  const ripple = projection.selected_ripple_row;
  return `
    <dl class="detail-list">
      <div class="detail-row"><dt>Node ID</dt><dd>${escapeHtml(node.node_id)}</dd></div>
      <div class="detail-row"><dt>Source record</dt><dd>${escapeHtml(node.source_record_id)}</dd></div>
      <div class="detail-row"><dt>JSON pointer</dt><dd>${escapeHtml(node.source_json_pointer)}</dd></div>
      ${attributeRows(node.attributes)}
    </dl>
    ${state.mode === "speculative" ? `
      <section class="receipt-block">
        <div class="section-heading">Compiled scenario receipt</div>
        ${ripple ? `
          <div class="receipt-status">${escapeHtml(ripple.result_class)}</div>
          <div class="mono-line">${escapeHtml(ripple.scenario.scenario_id)}</div>
          <div class="mono-line">${escapeHtml(ripple.ripple_digest)}</div>
        ` : `<div class="empty-state">No ET-C5 ripple row is compiled for this selection</div>`}
      </section>` : ""}
  `;
}

function renderLenses(projection) {
  if (!projection.triangulation.length) return `<div class="empty-state">No admitted lenses for this node family</div>`;
  return projection.triangulation
    .map(
      (lens) => `
        <section class="lens-block">
          <div class="lens-heading"><span>${escapeHtml(lens.label)}</span><span class="count">${lens.edge_count}</span></div>
          ${lens.rows
            .slice(0, 30)
            .map(
              (row) => `<button class="lens-row" data-related-node="${escapeHtml(row.neighbor.node_id)}">
                <span class="relation-tag">${escapeHtml(row.edge.relation)}</span>
                <span>${escapeHtml(row.neighbor.label)}</span>
                <span class="direction">${escapeHtml(row.direction)}</span>
              </button>`,
            )
            .join("")}
        </section>`,
    )
    .join("");
}

function renderReach(projection) {
  const rows = Object.entries(projection.dependency_reach.by_support_semantic);
  return `
    <div class="reach-note">Dependency counts / not importance or priority</div>
    <div class="reach-grid">
      ${rows
        .map(
          ([semantic, reach]) => `<div class="reach-row">
            <span>${escapeHtml(semantic.replaceAll("_", " "))}</span>
            <span><strong>${reach.direct_count}</strong> direct</span>
            <span><strong>${reach.transitive_count}</strong> transitive</span>
          </div>`,
        )
        .join("")}
      <div class="reach-row annotation-reach">
        <span>annotation / display only</span>
        <span><strong>${projection.dependency_reach.annotation_display_only.direct_count}</strong> direct</span>
        <span><strong>0</strong> transitive</span>
      </div>
    </div>
  `;
}

function renderInspector(projection) {
  const node = projection.selection;
  document.querySelector("#selection-header").innerHTML = `
    <div class="selection-kind"><span class="kind-dot" style="--kind-color:${KIND_COLORS[node.kind] ?? "#687078"}"></span>${escapeHtml(kindLabel(node.kind))}</div>
    <h2>${escapeHtml(node.label)}</h2>
    <div class="selection-id">${escapeHtml(node.identifier)}</div>
  `;
  const content = document.querySelector("#inspector-content");
  content.innerHTML = state.tab === "details" ? renderDetails(projection) : state.tab === "lenses" ? renderLenses(projection) : renderReach(projection);
  content.querySelectorAll("[data-related-node]").forEach((button) => {
    button.addEventListener("click", () => selectNode(button.dataset.relatedNode));
  });
}

function selectNode(nodeId) {
  const projection = projectionFor(state.bundle, nodeId);
  state.selectedNodeId = nodeId;
  renderSearchResults();
  renderGraph(projection);
  renderInspector(projection);
}

function wireShell() {
  const search = document.querySelector("#search-input");
  search.addEventListener("input", () => {
    state.query = search.value;
    if (state.query) state.familyId = "all";
    renderFamilies();
    renderSearchResults();
  });
  search.addEventListener("keydown", (event) => {
    const results = [...document.querySelectorAll("[data-node-id]")];
    if (event.key === "Enter" && results[0]) results[0].click();
    if (event.key === "ArrowDown" && results[0]) {
      event.preventDefault();
      results[0].focus();
    }
  });
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      state.tab = button.dataset.tab;
      document.querySelectorAll("[data-tab]").forEach((row) => row.classList.toggle("is-active", row === button));
      renderInspector(projectionFor(state.bundle, state.selectedNodeId));
    });
  });
  document.querySelectorAll("[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      state.mode = button.dataset.mode;
      document.querySelector(".workspace").dataset.mode = state.mode;
      document.querySelectorAll("[data-mode]").forEach((row) => row.classList.toggle("is-active", row === button));
      renderInspector(projectionFor(state.bundle, state.selectedNodeId));
    });
  });
  document.querySelector("#fit-graph").addEventListener("click", () => state.cy?.fit(undefined, 48));
}

async function boot() {
  try {
    const response = await fetch("/data/ETC6StaticNavigationBundle.json", { cache: "no-store" });
    if (!response.ok) throw new Error(`bundle request failed: ${response.status}`);
    state.bundle = await verifyBundle(await response.json());
    const source = sourceState(state.bundle);
    renderShell(source);
    if (!source.renderAllowed) {
      document.querySelector(".workspace").innerHTML = `<div class="blocked-surface"><h2>${escapeHtml(source.label)}</h2><p>${escapeHtml(source.state)}</p></div>`;
      return;
    }
    wireShell();
    renderFamilies();
    const family = familyById(state.bundle, state.familyId);
    selectNode(family.node_ids[0]);
  } catch (error) {
    document.querySelector("#app").innerHTML = `<div class="fatal-state"><strong>Bundle rejected</strong><span>${escapeHtml(error.message)}</span></div>`;
  }
}

boot();
