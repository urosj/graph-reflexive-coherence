import cytoscape from "cytoscape";
import {
  createIcons,
  Database,
  Download,
  Focus,
  GitBranch,
  Layers3,
  LocateFixed,
  LockKeyhole,
  Network,
  Pause,
  Play,
  RotateCcw,
  Search,
  StepForward,
} from "lucide";
import "./styles.css";
import { familyById, filterCatalog, projectionFor, sourceState, verifyBundle } from "./bundle.js";
import {
  alternativeById,
  candidateCareer,
  filterLocks,
  ghostForNode,
  ghostOpacity,
  lockById,
  locksForNode,
  verifyClaimCeilingLayer,
  visibleAlternatives,
} from "./ceilings.js";
import {
  canonicalScenarioText,
  playbackById,
  playbackFrame,
  playbackRows,
  reconstructionForClaim,
  reconstructionRows,
  scrubPosition,
  verifyLineagePlaybackLayer,
} from "./lineage.js";

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
  layer: null,
  lineageLayer: null,
  selectedNodeId: null,
  selectedLockId: null,
  selectedAlternativeId: null,
  familyId: "candidate_A",
  view: "catalog",
  query: "",
  tab: "details",
  mode: "source",
  surface: "explorer",
  alternativeVisibility: 0,
  cy: null,
  lineageCy: null,
  scrubIndex: 0,
  playbackId: null,
  playbackFrameIndex: 0,
  playbackTimer: null,
  reconstructionClaimId: "D10-CL-N-001",
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
          <div class="subline">Accepted design topology / ET-C8 lineage candidate</div>
        </div>
      </div>
      <div class="topbar-actions">
        <div class="surface-control" role="tablist" aria-label="Explorer surface">
          <button class="surface-button is-active" data-surface="explorer" role="tab">Explore</button>
          <button class="surface-button" data-surface="lineage" role="tab">Lineage</button>
        </div>
        <div class="mode-control" role="group" aria-label="Evidence mode">
          <button class="mode-button is-active" data-mode="source">Source</button>
          <button class="mode-button" data-mode="speculative">Speculative</button>
        </div>
        <div class="source-state source-state--${source.tone}" title="Standalone bundle state">
          <span class="source-state-dot"></span>${escapeHtml(source.label)}
        </div>
      </div>
    </header>
    <main id="explorer-workspace" class="workspace" data-mode="source">
      <aside class="navigation-panel" aria-label="Investigation navigation">
        <div class="search-wrap">
          <i data-lucide="search" aria-hidden="true"></i>
          <input id="search-input" type="search" placeholder="Search claims, objects, gates..." aria-label="Search investigation" autocomplete="off" />
        </div>
        <section class="family-section" aria-labelledby="family-heading">
          <div class="section-heading" id="family-heading">Object families</div>
          <div id="family-list" class="family-list"></div>
        </section>
        <section class="boundary-section" aria-labelledby="boundary-heading">
          <div class="section-heading" id="boundary-heading">Claim boundary</div>
          <div class="boundary-actions">
            <button class="boundary-view" data-view="locks"><i data-lucide="lock-keyhole" aria-hidden="true"></i><span>Locked claims</span><span class="count">${state.layer.population_counts.locks}</span></button>
            <button class="boundary-view" data-view="alternatives"><i data-lucide="layers-3" aria-hidden="true"></i><span>Alternatives</span><span class="count">${state.layer.population_counts.alternatives}</span></button>
          </div>
          <label class="visibility-control" for="alternative-visibility">
            <span>Alternative visibility</span><output id="visibility-value">0%</output>
            <input id="alternative-visibility" type="range" min="0" max="100" step="1" value="0" />
          </label>
          <div class="authority-populations" aria-label="Authority populations">
            <span><strong>${state.layer.authority_populations.current_debt_transformations}</strong> current transformations</span>
            <span><strong>${state.layer.authority_populations.verification_obligations}</strong> verification obligations</span>
            <span class="historical-count"><strong>${state.layer.authority_populations.historical_claims}</strong> historical claims</span>
          </div>
          <div class="ghost-legend"><span class="ghost-swatch"></span>Dashed = non-authoritative alternative</div>
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
          <button class="tab" data-tab="ceilings" role="tab">Locks</button>
        </div>
        <div id="inspector-content" class="inspector-content"></div>
      </aside>
    </main>
    <main id="lineage-workspace" class="lineage-workspace is-hidden" data-mode="source">
      <aside class="lineage-control-panel" aria-label="Lineage controls">
        <section class="scrub-section">
          <div class="section-heading">Accepted lineage position</div>
          <div id="scrub-receipt" class="scrub-receipt"></div>
          <input id="lineage-scrubber" class="lineage-scrubber" type="range" min="0" max="${state.lineageLayer.lineage.scrub_positions.length - 1}" step="1" value="0" aria-label="Accepted lineage position" />
          <div class="scrub-scale"><span>D0</span><span>D10.2</span></div>
        </section>
        <section class="marker-section">
          <div class="section-heading">Typed lineage overlays</div>
          <div id="lineage-markers" class="lineage-markers"></div>
        </section>
        <section class="orientation-section">
          <div class="section-heading">Substrate orientation</div>
          <div id="orientation-path" class="orientation-path"></div>
        </section>
      </aside>
      <section class="lineage-graph-panel" aria-label="Accepted lineage DAG">
        <div class="lineage-toolbar">
          <div>
            <div class="eyebrow">Accepted DAG / readable spine</div>
            <div id="lineage-summary" class="graph-summary"></div>
          </div>
          <button id="fit-lineage" class="icon-button" title="Center selected gate" aria-label="Center selected gate">
            <i data-lucide="locate-fixed" aria-hidden="true"></i>
          </button>
        </div>
        <div id="lineage-graph" role="img" aria-label="Accepted gate lineage with branch, correction, and supersession markers"></div>
        <div class="playback-bar">
          <div class="playback-buttons">
            <button id="reset-playback" class="icon-button" title="Reset playback" aria-label="Reset playback"><i data-lucide="rotate-ccw" aria-hidden="true"></i></button>
            <button id="play-playback" class="icon-button primary-action" title="Play precomputed frames" aria-label="Play precomputed frames"><i data-lucide="play" aria-hidden="true"></i></button>
            <button id="step-playback" class="icon-button" title="Next precomputed frame" aria-label="Next precomputed frame"><i data-lucide="step-forward" aria-hidden="true"></i></button>
          </div>
          <div id="frame-status" class="frame-status"></div>
          <div class="playback-authority">Precomputed ET-C5 rows only</div>
        </div>
      </section>
      <aside class="lineage-inspector" aria-label="Lineage and playback inspector">
        <section class="scenario-section">
          <div class="section-heading">Counterfactual fork</div>
          <label class="field-label" for="scenario-select">Canonical scenario</label>
          <select id="scenario-select" class="scenario-select" aria-label="Canonical scenario"></select>
          <div id="scenario-receipt" class="scenario-receipt"></div>
          <button id="export-scenario" class="command-button" type="button"><i data-lucide="download" aria-hidden="true"></i>Export exact scenario</button>
        </section>
        <section class="effect-section">
          <div class="effect-legend" aria-label="Playback state legend">
            <span class="legend-item direct">Direct</span>
            <span class="legend-item transitive">Transitive</span>
            <span class="legend-item reopening">Reopening gate</span>
            <span class="legend-item frontier">Unresolved frontier</span>
          </div>
          <div id="effect-list" class="effect-list"></div>
        </section>
        <section class="reconstruction-section">
          <div class="section-heading">Backward reconstruction</div>
          <select id="reconstruction-select" class="scenario-select" aria-label="Claim to reconstruct"></select>
          <div id="reconstruction-result" class="reconstruction-result"></div>
        </section>
      </aside>
    </main>
  `;
  createIcons({ icons: { Search, LocateFixed, Database, Focus, GitBranch, Network, LockKeyhole, Layers3, Play, Pause, StepForward, RotateCcw, Download } });
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
      state.view = "catalog";
      state.familyId = button.dataset.family;
      const family = familyById(state.bundle, state.familyId);
      if (family?.node_ids.length) selectNode(family.node_ids[0]);
      renderFamilies();
      renderBoundaryControls();
      renderSearchResults();
    });
  });
}

function renderSearchResults() {
  const catalogRows = filterCatalog(state.bundle, state.query, state.familyId).filter((row) => {
    const ghost = ghostForNode(state.layer, row.node_id);
    return !ghost || ghostOpacity(ghost, state.alternativeVisibility) > 0;
  });
  const rows = state.view === "locks"
    ? filterLocks(state.layer, state.query).slice(0, 80)
    : state.view === "alternatives"
      ? visibleAlternatives(state.layer, state.alternativeVisibility, state.query).slice(0, 80)
      : catalogRows.slice(0, 80);
  const container = document.querySelector("#search-results");
  container.innerHTML = rows.length
    ? rows
        .map(
          (row) => state.view === "locks" ? `
            <button role="option" class="result-row lock-result ${row.lock_id === state.selectedLockId ? "is-active" : ""}" data-lock-id="${escapeHtml(row.lock_id)}" aria-selected="${row.lock_id === state.selectedLockId}">
              <span class="lock-marker" aria-hidden="true"></span>
              <span class="result-copy">
                <span class="result-label">${escapeHtml(row.readable_annotation.text)}</span>
                <span class="result-meta">${escapeHtml(row.lock_class.replaceAll("_", " "))}</span>
              </span>
            </button>` : state.view === "alternatives" ? `
            <button role="option" class="result-row ghost-result ${row.alternative_id === state.selectedAlternativeId ? "is-active" : ""}" style="--ghost-opacity:${ghostOpacity(row, state.alternativeVisibility)}" data-alternative-id="${escapeHtml(row.alternative_id)}" aria-selected="${row.alternative_id === state.selectedAlternativeId}">
              <span class="ghost-marker" aria-hidden="true"></span>
              <span class="result-copy">
                <span class="result-label">${escapeHtml(row.label.replaceAll("_", " "))}</span>
                <span class="result-meta">${escapeHtml(row.alternative_class.replaceAll("_", " "))} / ${escapeHtml(row.immutable_status.replaceAll("_", " "))}</span>
              </span>
            </button>` : `
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
  container.querySelectorAll("[data-lock-id]").forEach((button) => {
    button.addEventListener("click", () => selectLock(button.dataset.lockId));
  });
  container.querySelectorAll("[data-alternative-id]").forEach((button) => {
    button.addEventListener("click", () => selectAlternative(button.dataset.alternativeId));
  });
}

function renderBoundaryControls() {
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.classList.toggle("is-active", button.dataset.view === state.view);
  });
  const slider = document.querySelector("#alternative-visibility");
  slider.value = String(state.alternativeVisibility);
  document.querySelector("#visibility-value").textContent = `${state.alternativeVisibility}%`;
}

function setActiveTab(tab) {
  state.tab = tab;
  document.querySelectorAll("[data-tab]").forEach((row) => {
    row.classList.toggle("is-active", row.dataset.tab === tab);
  });
}

function graphElements(projection) {
  const visibleNodes = projection.focus.nodes.filter((node) => {
    const ghost = ghostForNode(state.layer, node.node_id);
    return !ghost || ghostOpacity(ghost, state.alternativeVisibility) > 0;
  });
  const visibleNodeIds = new Set(visibleNodes.map((node) => node.node_id));
  const nodes = visibleNodes.map((node) => {
    const ghost = ghostForNode(state.layer, node.node_id);
    const opacity = ghostOpacity(ghost, state.alternativeVisibility);
    const classes = [node.node_id === projection.focus.root_node_id ? "root" : "", ghost ? "ghost" : ""]
      .filter(Boolean)
      .join(" ");
    return {
    data: {
      id: node.node_id,
      label: node.label,
      kind: node.kind,
      isRoot: node.node_id === projection.focus.root_node_id,
      ghostOpacity: ghost ? opacity : 1,
      immutableStatus: ghost?.immutable_status ?? "current_source_node",
    },
    classes,
  };
  });
  const edges = projection.focus.edges.filter(
    (edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target),
  ).map((edge) => ({
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
        selector: "node.ghost",
        style: {
          "border-style": "dashed",
          "border-width": 4,
          shape: "round-rectangle",
          opacity: (node) => node.data("ghostOpacity"),
        },
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
  state.cy.nodes(".ghost").ungrabify();
  state.cy.on("tap", "node", (event) => selectNode(event.target.id()));
  const focus = projection.focus;
  document.querySelector("#graph-summary").textContent = `${state.cy.nodes().length} nodes / ${state.cy.edges().length} relationships`;
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

function sourceReceipt(source) {
  return `
    <dl class="detail-list source-receipt">
      <div class="detail-row"><dt>Record</dt><dd>${escapeHtml(source.record_id)}</dd></div>
      <div class="detail-row"><dt>Pointer</dt><dd>${escapeHtml(source.source_json_pointer)}</dd></div>
      <div class="detail-row"><dt>Digest</dt><dd class="mono-copy">${escapeHtml(source.record_digest)}</dd></div>
    </dl>`;
}

function renderCandidateCareer(node) {
  if (node.kind !== "candidate") return "";
  const career = candidateCareer(state.layer, node.identifier);
  if (!career) return "";
  return `
    <section class="career-block">
      <div class="section-heading">Source-exact candidate career</div>
      ${career.rows.slice(-14).map((row) => `
        <div class="career-row">
          <span class="career-status">${escapeHtml(row.classification.replaceAll("_", " "))}</span>
          <span>${escapeHtml(row.row_id)}</span>
        </div>`).join("")}
    </section>`;
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
    ${renderCandidateCareer(node)}
  `;
}

function renderLock(lock) {
  return `
    <section class="lock-surface" data-lock-status="accepted-source-lock">
      <div class="lock-banner"><span class="lock-marker" aria-hidden="true"></span>Accepted claim boundary / cannot promote</div>
      <div class="annotation-note"><strong>Readable annotation / non-authoritative</strong>${escapeHtml(lock.readable_annotation.text)}</div>
      <div class="section-heading">Stronger blocked claim</div>
      <ul class="machine-list">${lock.stronger_blocked_claims.map((value) => `<li>${escapeHtml(value)}</li>`).join("")}</ul>
      <div class="section-heading">Exact source reason</div>
      <div class="machine-value">${escapeHtml(lock.source_reason)}</div>
      <div class="source-pointer-line">${escapeHtml(lock.source_reason_ref.record_id)} ${escapeHtml(lock.source_reason_ref.source_json_pointer)}</div>
      ${lock.hardening ? `
        <div class="hardening-block">
          <div class="detail-row"><dt>Hardening key</dt><dd>${escapeHtml(lock.hardening.key)}</dd></div>
          <div class="detail-row"><dt>Machine value</dt><dd>${escapeHtml(lock.hardening.machine_value)}</dd></div>
        </div>` : ""}
      <div class="section-heading">Bearing debt</div>
      ${lock.bearing_debt_ids.length ? `<ul class="machine-list">${lock.bearing_debt_ids.map((value) => `<li>${escapeHtml(value)}</li>`).join("")}</ul>` : `<div class="empty-inline">No source-linked bearing debt</div>`}
      <div class="section-heading">Reopening boundary set</div>
      ${lock.reopening_boundary_set.length ? `<ul class="machine-list">${lock.reopening_boundary_set.map((row) => `<li><strong>${escapeHtml(row.boundary_kind)}</strong> ${escapeHtml(row.boundary_id)}</li>`).join("")}</ul>` : `<div class="empty-inline">Not named in the accepted source row</div>`}
      ${sourceReceipt(lock.source)}
    </section>`;
}

function renderAlternative(alternative) {
  const readmission = alternative.alternative_id === "routed:V4-B-independent-derived-carrier"
    ? state.layer.candidate_B_readmission
    : null;
  return `
    <section class="alternative-surface" data-promotion-allowed="false">
      <div class="ghost-banner"><span class="ghost-marker" aria-hidden="true"></span>Non-authoritative alternative / immutable</div>
      <dl class="detail-list">
        <div class="detail-row"><dt>Class</dt><dd>${escapeHtml(alternative.alternative_class.replaceAll("_", " "))}</dd></div>
        <div class="detail-row"><dt>Status</dt><dd>${escapeHtml(alternative.immutable_status.replaceAll("_", " "))}</dd></div>
        <div class="detail-row"><dt>Visibility</dt><dd>${alternative.visibility_threshold}% / staged disclosure only</dd></div>
        <div class="detail-row"><dt>Promotion</dt><dd>Forbidden by ET-C7 authority</dd></div>
      </dl>
      ${readmission ? `
        <section class="readmission-block">
          <div class="section-heading">Candidate B readmission boundary</div>
          <div class="machine-value">${escapeHtml(readmission.accepted_route_boundary)}</div>
          <div class="detail-row"><dt>Earliest counterfactual rerun</dt><dd>${escapeHtml(readmission.earliest_counterfactual_reexecution_gate_ids.join(", "))}</dd></div>
          <div class="detail-row"><dt>Outcome</dt><dd>${escapeHtml(readmission.outcome_status.replaceAll("_", " "))}</dd></div>
        </section>` : ""}
      <div class="section-heading">Source payload</div>
      <div class="machine-value">${escapeHtml(compact(alternative.payload))}</div>
      ${sourceReceipt(alternative.source)}
    </section>`;
}

function renderCeilings(projection) {
  const rows = locksForNode(state.layer, projection.selection.node_id);
  if (!rows.length) return `<div class="empty-state">No source-linked lock is compiled for this node</div>`;
  return rows.map(renderLock).join("");
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
  const selectedLock = state.selectedLockId ? lockById(state.layer, state.selectedLockId) : null;
  const selectedAlternative = state.selectedAlternativeId ? alternativeById(state.layer, state.selectedAlternativeId) : null;
  const node = projection.selection;
  document.querySelector("#selection-header").innerHTML = `
    <div class="selection-kind"><span class="kind-dot" style="--kind-color:${KIND_COLORS[node.kind] ?? "#687078"}"></span>${escapeHtml(selectedLock ? "locked boundary" : selectedAlternative ? "ghost alternative" : kindLabel(node.kind))}</div>
    <h2>${escapeHtml(selectedLock?.readable_annotation.text ?? selectedAlternative?.label.replaceAll("_", " ") ?? node.label)}</h2>
    <div class="selection-id">${escapeHtml(selectedLock?.lock_id ?? selectedAlternative?.alternative_id ?? node.identifier)}</div>
  `;
  const content = document.querySelector("#inspector-content");
  content.innerHTML = selectedLock
    ? renderLock(selectedLock)
    : selectedAlternative
      ? renderAlternative(selectedAlternative)
      : state.tab === "details"
        ? renderDetails(projection)
        : state.tab === "lenses"
          ? renderLenses(projection)
          : state.tab === "reach"
            ? renderReach(projection)
            : renderCeilings(projection);
  content.querySelectorAll("[data-related-node]").forEach((button) => {
    button.addEventListener("click", () => selectNode(button.dataset.relatedNode));
  });
}

function selectNode(nodeId) {
  const projection = projectionFor(state.bundle, nodeId);
  const returningFromVirtualSurface = Boolean(state.selectedLockId || state.selectedAlternativeId);
  state.selectedNodeId = nodeId;
  state.selectedLockId = null;
  state.selectedAlternativeId = null;
  if (returningFromVirtualSurface) setActiveTab("details");
  renderSearchResults();
  renderGraph(projection);
  renderInspector(projection);
}

function selectLock(lockId) {
  const lock = lockById(state.layer, lockId);
  if (!lock) throw new Error(`unknown lock: ${lockId}`);
  state.selectedLockId = lockId;
  state.selectedAlternativeId = null;
  setActiveTab("ceilings");
  const target = lock.target_node_ids.find((nodeId) => state.bundle.selection_projections[nodeId]);
  if (target) state.selectedNodeId = target;
  renderSearchResults();
  renderGraph(projectionFor(state.bundle, state.selectedNodeId));
  renderInspector(projectionFor(state.bundle, state.selectedNodeId));
}

function selectAlternative(alternativeId) {
  const alternative = alternativeById(state.layer, alternativeId);
  if (!alternative || ghostOpacity(alternative, state.alternativeVisibility) === 0) {
    throw new Error(`alternative is outside current visibility: ${alternativeId}`);
  }
  state.selectedAlternativeId = alternativeId;
  state.selectedLockId = null;
  setActiveTab("details");
  const target = alternative.target_node_id;
  if (target && state.bundle.selection_projections[target]) state.selectedNodeId = target;
  renderSearchResults();
  renderGraph(projectionFor(state.bundle, state.selectedNodeId));
  renderInspector(projectionFor(state.bundle, state.selectedNodeId));
}

function lineageNodeById(nodeId) {
  return state.lineageLayer.lineage.nodes.find((row) => row.node_id === nodeId) ?? null;
}

function selectedPlayback() {
  return state.playbackId ? playbackById(state.lineageLayer, state.playbackId) : null;
}

function renderOrientationPath() {
  const orientation = state.lineageLayer.orientation_path;
  document.querySelector("#orientation-path").innerHTML = `
    <div class="orientation-chain">
      ${orientation.steps.map((step, index) => `
        <div class="orientation-step">
          <strong>${escapeHtml(step.label)}</strong>
          <span>${escapeHtml(step.role.replaceAll("_", " "))}</span>
          <small>${step.object_ids.length} scoped objects</small>
        </div>
        ${index < orientation.edges.length ? `<div class="orientation-arrow"><span>→</span>${escapeHtml(orientation.edges[index].relation.replaceAll("_", " "))}</div>` : ""}
      `).join("")}
    </div>
    <div class="orientation-scope">${escapeHtml(orientation.scope.replaceAll("_", " "))}</div>`;
}

function renderLineageMarkers() {
  const lineage = state.lineageLayer.lineage;
  document.querySelector("#lineage-markers").innerHTML = `
    <div class="marker-count"><span class="marker-symbol branch"></span><strong>${lineage.population_counts.branch_nodes}</strong><span>accepted companion branches</span></div>
    <div class="marker-count"><span class="marker-symbol supersession"></span><strong>${lineage.population_counts.supersession_markers}</strong><span>v2 supersessions</span></div>
    <div class="marker-count"><span class="marker-symbol correction"></span><strong>${lineage.population_counts.correction_markers}</strong><span>post-v2 typed correction</span></div>
    <div class="correction-note">${escapeHtml(lineage.correction_markers[0].correction_scope.replaceAll("_", " "))}</div>`;
}

function renderScrubReceipt() {
  const position = scrubPosition(state.lineageLayer, state.scrubIndex);
  document.querySelector("#scrub-receipt").innerHTML = `
    <div class="scrub-gate">${escapeHtml(position.gate_id)}</div>
    <div class="scrub-record">${escapeHtml(position.record_id)}</div>
    <div class="scrub-digest">${escapeHtml(position.record_digest)}</div>`;
  document.querySelector("#lineage-scrubber").value = String(state.scrubIndex);
  document.querySelector("#lineage-scrubber").disabled = state.mode !== "source";
}

function sourceNodeState(node) {
  const position = state.lineageLayer.lineage.scrub_positions.find((row) => row.node_id === node.node_id);
  if (position?.index === state.scrubIndex) return "baseline_anchor";
  if (position && position.index > state.scrubIndex) return "accepted_later";
  return "accepted_unaffected";
}

function activeFrame() {
  const playback = selectedPlayback();
  if (state.mode !== "speculative" || !playback) return null;
  return playbackFrame(playback, state.playbackFrameIndex);
}

function lineageElements() {
  const lineage = state.lineageLayer.lineage;
  const frame = activeFrame();
  const frameStates = new Map(frame?.node_states.map((row) => [row.node_id, row.state]) ?? []);
  const nodes = lineage.nodes.map((node) => {
    const playbackState = frameStates.get(node.node_id) ?? sourceNodeState(node);
    const classes = [node.lineage_role, playbackState].join(" ");
    return {
      data: {
        id: node.node_id,
        label: node.gate_id,
        recordId: node.record_id,
        digest: node.record_digest,
        role: node.lineage_role,
        playbackState,
      },
      position: node.position,
      classes,
    };
  });
  const predecessorEdges = lineage.predecessor_edges.map((edge) => ({
    data: { id: edge.edge_id, source: edge.source, target: edge.target, relation: edge.relation },
    classes: `predecessor ${edge.lineage_role}`,
  }));
  const supersessions = lineage.supersession_markers.map((edge) => ({
    data: { id: `lineage-${edge.edge_id}`, source: edge.source, target: edge.target, relation: edge.relation },
    classes: "supersession",
  }));
  const corrections = lineage.correction_markers.map((marker) => ({
    data: { id: marker.marker_id, source: marker.anchor_node_id, target: marker.node_id, relation: marker.marker_class },
    classes: "correction",
  }));
  return [...nodes, ...predecessorEdges, ...supersessions, ...corrections];
}

function centerLineageSelection() {
  const position = scrubPosition(state.lineageLayer, state.scrubIndex);
  const selected = state.lineageCy?.getElementById(position.node_id);
  if (!selected?.length) return;
  state.lineageCy.zoom({ level: 0.78, renderedPosition: { x: 0, y: 0 } });
  state.lineageCy.center(selected);
}

function renderLineageGraph({ center = false } = {}) {
  if (state.lineageCy) state.lineageCy.destroy();
  state.lineageCy = cytoscape({
    container: document.querySelector("#lineage-graph"),
    elements: lineageElements(),
    wheelSensitivity: 0.2,
    minZoom: 0.25,
    maxZoom: 1.8,
    style: [
      {
        selector: "node",
        style: {
          width: 42,
          height: 42,
          shape: "ellipse",
          "background-color": "#3d6f9d",
          "border-width": 3,
          "border-color": "#f8fafb",
          label: "data(label)",
          "font-size": 9,
          "font-weight": 700,
          "text-wrap": "wrap",
          "text-max-width": 90,
          "text-valign": "bottom",
          "text-margin-y": 8,
          color: "#263238",
        },
      },
      { selector: "node.branch", style: { shape: "round-rectangle", "background-color": "#607b87" } },
      { selector: "node.correction", style: { shape: "diamond", "background-color": "#7a5a94", width: 48, height: 48 } },
      { selector: "node.accepted_later", style: { opacity: 0.58, "border-color": "#cbd4d8" } },
      { selector: "node.baseline_anchor", style: { width: 58, height: 58, "border-width": 5, "border-color": "#17242a", opacity: 1 } },
      { selector: "node.direct_effect", style: { "background-color": "#d18b2c", "border-color": "#6e4510", width: 52, height: 52 } },
      { selector: "node.transitive_effect", style: { "background-color": "#3e8798", "border-color": "#18515e" } },
      { selector: "node.reopening_gate", style: { shape: "hexagon", "background-color": "#b2493f", "border-color": "#6f211c", width: 62, height: 62 } },
      { selector: "node.evidence_frontier_unresolved", style: { shape: "round-rectangle", "background-color": "#d8dcde", "border-color": "#7f898e", "border-style": "dashed", opacity: 0.48 } },
      {
        selector: "edge",
        style: {
          width: 2,
          "line-color": "#9aa8ae",
          "target-arrow-color": "#7b8b92",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "arrow-scale": 0.75,
        },
      },
      { selector: "edge.branch", style: { "line-style": "dashed", "line-color": "#758a93" } },
      { selector: "edge.supersession", style: { "line-style": "dotted", "line-color": "#b05c3b", "target-arrow-color": "#b05c3b", width: 3 } },
      { selector: "edge.correction", style: { "line-style": "dashed", "line-color": "#7a5a94", "target-arrow-color": "#7a5a94", width: 3 } },
      { selector: ":selected", style: { "overlay-opacity": 0, "border-color": "#10191d", "border-width": 6 } },
    ],
    layout: { name: "preset", fit: false, animate: false },
  });
  state.lineageCy.nodes().ungrabify();
  state.lineageCy.on("tap", "node", (event) => {
    const position = state.lineageLayer.lineage.scrub_positions.find((row) => row.node_id === event.target.id());
    if (position && state.mode === "source") {
      state.scrubIndex = position.index;
      renderLineage({ center: true });
    }
  });
  document.querySelector("#lineage-summary").textContent = `${state.lineageCy.nodes().length} accepted records / ${state.lineageLayer.lineage.predecessor_edges.length} predecessor links`;
  if (center) centerLineageSelection();
}

function renderScenarioOptions() {
  const select = document.querySelector("#scenario-select");
  const rows = playbackRows(state.lineageLayer);
  if (!select.options.length) {
    select.innerHTML = rows.map((row) => `<option value="${escapeHtml(row.playback_id)}">${escapeHtml(`${row.source_scenario_id} / ${row.profile_id} / ${row.baseline_scrub_position.gate_id}`)}</option>`).join("");
  }
  select.value = state.playbackId;
  select.disabled = state.mode !== "speculative";
  const playback = selectedPlayback();
  document.querySelector("#scenario-receipt").innerHTML = playback ? `
    <div class="scenario-status">${escapeHtml(playback.result_statuses.join(" / ").replaceAll("_", " "))}</div>
    <div class="scrub-record">${escapeHtml(playback.scenario_digest)}</div>
    <div class="scrub-digest">${escapeHtml(playback.ripple_digest)}</div>` : "";
  document.querySelector("#export-scenario").disabled = state.mode !== "speculative" || !playback;
}

function consequenceRows(playback, frameId) {
  if (!playback || frameId === "baseline") return [];
  const direct = playback.direct_consequences.map((row) => ({ ...row, displayClass: "direct" }));
  if (frameId === "direct") return direct;
  const transitive = playback.transitive_consequences.map((row) => ({
    ...row,
    displayClass: row.category === "earliest_gates_to_reopen"
      ? "reopening"
      : row.category === "unknown_beyond_evidence_frontier"
        ? "frontier"
        : "transitive",
  }));
  if (frameId === "transitive") return [...direct, ...transitive.filter((row) => !["reopening", "frontier"].includes(row.displayClass))];
  return [...direct, ...transitive];
}

function renderPlaybackFrame() {
  const playback = selectedPlayback();
  const frame = activeFrame();
  const sourceMode = state.mode !== "speculative";
  document.querySelector("#reset-playback").disabled = sourceMode;
  document.querySelector("#play-playback").disabled = sourceMode;
  document.querySelector("#step-playback").disabled = sourceMode;
  document.querySelector("#frame-status").innerHTML = sourceMode
    ? `<strong>Source mode</strong><span>Playback cannot alter accepted lineage</span>`
    : `<strong>${escapeHtml(frame.label)}</strong><span>Frame ${state.playbackFrameIndex + 1} / ${playback.frames.length}</span>`;
  const rows = consequenceRows(playback, frame?.frame_id ?? "baseline");
  document.querySelector("#effect-list").innerHTML = rows.length
    ? rows.map((row) => `<div class="effect-row ${row.displayClass}"><strong>${escapeHtml(row.category.replaceAll("_", " "))}</strong><span>${escapeHtml(compact(row.identifier))}</span></div>`).join("")
    : `<div class="empty-state">${sourceMode ? "No speculative effects in source mode" : "Accepted baseline before the fork"}</div>`;
}

function renderReconstructionOptions() {
  const rows = reconstructionRows(state.lineageLayer);
  const select = document.querySelector("#reconstruction-select");
  select.innerHTML = rows.map((row) => `<option value="${escapeHtml(row.claim_id)}">${escapeHtml(`${row.claim_id} / ${row.claim_class}`)}</option>`).join("");
  if (!state.lineageLayer.claim_reconstructions[state.reconstructionClaimId]) {
    state.reconstructionClaimId = rows[0].claim_id;
  }
  select.value = state.reconstructionClaimId;
  const result = reconstructionForClaim(state.lineageLayer, state.reconstructionClaimId);
  document.querySelector("#reconstruction-result").innerHTML = `
    <div class="reconstruction-statement">${escapeHtml(result.statement.replaceAll("_", " "))}</div>
    <div class="reconstruction-counts"><span><strong>${result.node_ids.length}</strong> accepted nodes</span><span><strong>${result.edge_refs.length}</strong> support links</span></div>
    <details><summary>Source-bound path</summary><ul>${result.node_ids.map((value) => `<li>${escapeHtml(value)}</li>`).join("")}</ul></details>
    <div class="scrub-record">${escapeHtml(result.source.record_id)} ${escapeHtml(result.source.source_json_pointer)}</div>
    <div class="scrub-digest">${escapeHtml(result.trace_digest)}</div>`;
}

function stopPlayback() {
  if (state.playbackTimer) window.clearInterval(state.playbackTimer);
  state.playbackTimer = null;
}

function setPlayback(playbackId) {
  stopPlayback();
  const playback = playbackById(state.lineageLayer, playbackId);
  if (!playback) throw new Error(`unknown precomputed playback: ${playbackId}`);
  state.playbackId = playbackId;
  state.playbackFrameIndex = 0;
  state.scrubIndex = playback.baseline_scrub_position.index;
  renderLineage({ center: true });
}

function stepPlayback() {
  const playback = selectedPlayback();
  if (!playback || state.mode !== "speculative") return;
  state.playbackFrameIndex = Math.min(state.playbackFrameIndex + 1, playback.frames.length - 1);
  renderLineage({ center: false });
}

function playPlayback() {
  if (state.mode !== "speculative") return;
  stopPlayback();
  const playback = selectedPlayback();
  if (state.playbackFrameIndex >= playback.frames.length - 1) state.playbackFrameIndex = 0;
  renderLineage({ center: false });
  state.playbackTimer = window.setInterval(() => {
    if (state.playbackFrameIndex >= playback.frames.length - 1) {
      stopPlayback();
      return;
    }
    stepPlayback();
  }, 650);
}

function exportScenario() {
  const playback = selectedPlayback();
  const text = canonicalScenarioText(playback);
  const url = URL.createObjectURL(new Blob([text], { type: "application/json" }));
  const link = document.createElement("a");
  link.href = url;
  link.download = `${playback.playback_id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function renderLineage({ center = false } = {}) {
  renderScrubReceipt();
  renderScenarioOptions();
  renderLineageGraph({ center });
  renderPlaybackFrame();
  renderReconstructionOptions();
}

function setSurface(surface) {
  state.surface = surface;
  document.querySelector("#explorer-workspace").classList.toggle("is-hidden", surface !== "explorer");
  document.querySelector("#lineage-workspace").classList.toggle("is-hidden", surface !== "lineage");
  document.querySelectorAll("[data-surface]").forEach((button) => button.classList.toggle("is-active", button.dataset.surface === surface));
  if (surface === "lineage") renderLineage({ center: true });
}

function setMode(mode) {
  stopPlayback();
  state.mode = mode;
  state.playbackFrameIndex = 0;
  if (mode === "speculative") {
    state.scrubIndex = selectedPlayback().baseline_scrub_position.index;
  }
  document.querySelector("#explorer-workspace").dataset.mode = mode;
  document.querySelector("#lineage-workspace").dataset.mode = mode;
  document.querySelectorAll(".mode-button[data-mode]").forEach((row) => row.classList.toggle("is-active", row.dataset.mode === mode));
  renderInspector(projectionFor(state.bundle, state.selectedNodeId));
  renderLineage({ center: state.surface === "lineage" });
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
    const results = [...document.querySelectorAll("[data-node-id], [data-lock-id], [data-alternative-id]")];
    if (event.key === "Enter" && results[0]) results[0].click();
    if (event.key === "ArrowDown" && results[0]) {
      event.preventDefault();
      results[0].focus();
    }
  });
  document.querySelectorAll("[data-tab]").forEach((button) => {
    button.addEventListener("click", () => {
      state.tab = button.dataset.tab;
      setActiveTab(button.dataset.tab);
      renderInspector(projectionFor(state.bundle, state.selectedNodeId));
    });
  });
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.addEventListener("click", () => {
      state.view = button.dataset.view;
      state.selectedLockId = null;
      state.selectedAlternativeId = null;
      state.query = "";
      search.value = "";
      renderBoundaryControls();
      renderSearchResults();
    });
  });
  document.querySelector("#alternative-visibility").addEventListener("input", (event) => {
    state.alternativeVisibility = Number(event.target.value);
    const selected = state.selectedAlternativeId
      ? alternativeById(state.layer, state.selectedAlternativeId)
      : null;
    if (selected && ghostOpacity(selected, state.alternativeVisibility) === 0) {
      state.selectedAlternativeId = null;
    }
    renderBoundaryControls();
    renderSearchResults();
    const projection = projectionFor(state.bundle, state.selectedNodeId);
    renderGraph(projection);
    renderInspector(projection);
  });
  document.querySelectorAll(".mode-button[data-mode]").forEach((button) => {
    button.addEventListener("click", () => {
      setMode(button.dataset.mode);
    });
  });
  document.querySelectorAll("[data-surface]").forEach((button) => {
    button.addEventListener("click", () => setSurface(button.dataset.surface));
  });
  document.querySelector("#fit-graph").addEventListener("click", () => state.cy?.fit(undefined, 48));
  document.querySelector("#fit-lineage").addEventListener("click", centerLineageSelection);
  document.querySelector("#lineage-scrubber").addEventListener("input", (event) => {
    if (state.mode !== "source") return;
    state.scrubIndex = Number(event.target.value);
    renderLineage({ center: true });
  });
  document.querySelector("#scenario-select").addEventListener("change", (event) => setPlayback(event.target.value));
  document.querySelector("#reset-playback").addEventListener("click", () => {
    stopPlayback();
    state.playbackFrameIndex = 0;
    renderLineage({ center: false });
  });
  document.querySelector("#step-playback").addEventListener("click", stepPlayback);
  document.querySelector("#play-playback").addEventListener("click", playPlayback);
  document.querySelector("#export-scenario").addEventListener("click", exportScenario);
  document.querySelector("#reconstruction-select").addEventListener("change", (event) => {
    state.reconstructionClaimId = event.target.value;
    renderReconstructionOptions();
  });
}

async function boot() {
  try {
    const [bundleResponse, layerResponse, lineageResponse] = await Promise.all([
      fetch("/data/ETC6StaticNavigationBundle.json", { cache: "no-store" }),
      fetch("/data/ETC7ClaimCeilingAlternativeLayer.json", { cache: "no-store" }),
      fetch("/data/ETC8LineagePlaybackLayer.json", { cache: "no-store" }),
    ]);
    if (!bundleResponse.ok) throw new Error(`bundle request failed: ${bundleResponse.status}`);
    if (!layerResponse.ok) throw new Error(`claim-ceiling request failed: ${layerResponse.status}`);
    if (!lineageResponse.ok) throw new Error(`lineage playback request failed: ${lineageResponse.status}`);
    state.bundle = await verifyBundle(await bundleResponse.json());
    state.layer = await verifyClaimCeilingLayer(await layerResponse.json(), state.bundle);
    state.lineageLayer = await verifyLineagePlaybackLayer(await lineageResponse.json(), state.bundle, state.layer);
    state.scrubIndex = state.lineageLayer.lineage.scrub_positions.length - 1;
    state.playbackId = playbackRows(state.lineageLayer, "C1")[0]?.playback_id ?? playbackRows(state.lineageLayer)[0].playback_id;
    const source = sourceState(state.bundle);
    renderShell(source);
    if (!source.renderAllowed) {
      document.querySelector(".workspace").innerHTML = `<div class="blocked-surface"><h2>${escapeHtml(source.label)}</h2><p>${escapeHtml(source.state)}</p></div>`;
      return;
    }
    wireShell();
    renderFamilies();
    renderBoundaryControls();
    renderLineageMarkers();
    renderOrientationPath();
    renderLineage({ center: false });
    const family = familyById(state.bundle, state.familyId);
    selectNode(family.node_ids[0]);
    window.__ETC8__ = {
      layer: state.lineageLayer,
      getCanonicalScenarioText: (playbackId) => canonicalScenarioText(playbackById(state.lineageLayer, playbackId)),
      setSurface,
      setMode,
      setPlayback,
      stepPlayback,
      getRuntimeState: () => ({
        mode: state.mode,
        surface: state.surface,
        playbackId: state.playbackId,
        playbackFrameIndex: state.playbackFrameIndex,
        scrubIndex: state.scrubIndex,
      }),
    };
  } catch (error) {
    document.querySelector("#app").innerHTML = `<div class="fatal-state"><strong>Bundle rejected</strong><span>${escapeHtml(error.message)}</span></div>`;
  }
}

boot();
