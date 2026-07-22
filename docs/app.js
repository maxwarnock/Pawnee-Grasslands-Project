const DATA_URLS = {
  summary: "./data/summary.json",
  proposals: "./data/proposals.json",
  parcels: "./data/parcels.geojson",
  patches: "./data/federal-patches.geojson",
  master: "./data/master-boundary.geojson",
};

const COLORS = {
  federal: "#4f6e3a",
  state: "#3d708f",
  private: "#b68044",
  patch: "#e5c567",
  acquire: "#2f8f5b",
  release: "#bb513a",
  muted: "#a6a090",
  boundary: "#2a2318",
};

const VALUE_BREAKS = [0, 200, 400, 600, 800, 1000];
const VALUE_COLORS = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"];

const state = {
  summary: null,
  proposals: [],
  filteredProposals: [],
  selectedProposal: null,
  map: null,
  layers: {},
  parcelLayers: new Map(),
  patchLayers: new Map(),
  parcelById: new Map(),
  display: {
    showValueLayer: false,
  },
  filters: {
    ownership: "ALL",
    swapType: "ALL",
    patchId: "ALL",
    minGain: 0,
    maxAreaDiff: 10,
    maxDistanceKm: 10,
    limit: "5",
    stateContiguity: false,
    privateContiguity: false,
    excludeAcquireOilGas: false,
    excludeReleaseOilGas: false,
    bridgesOnly: false,
  },
};

const controls = {};

document.addEventListener("DOMContentLoaded", init);

async function init() {
  cacheDom();
  bindControls();

  try {
    const [summary, proposals, parcels, patches, master] = await Promise.all(
      Object.values(DATA_URLS).map((url) => fetch(url).then((response) => response.json())),
    );

    state.summary = summary;
    state.proposals = proposals;
    populatePatchFilterOptions();

    parcels.features.forEach((feature) => {
      state.parcelById.set(feature.properties.parcelId, feature);
    });

    renderSummaryCards();
    createMap(parcels, patches, master);
    applyFilters();
  } catch (error) {
    const target = document.getElementById("proposal-list");
    target.innerHTML = `<div class="empty-state">Unable to load map data. ${error.message}</div>`;
  }
}

function cacheDom() {
  controls.summaryCards = document.getElementById("summary-cards");
  controls.ownership = document.getElementById("ownership-filter");
  controls.swapType = document.getElementById("swap-type-filter");
  controls.patch = document.getElementById("patch-filter");
  controls.minGain = document.getElementById("min-gain-filter");
  controls.minGainOutput = document.getElementById("min-gain-output");
  controls.maxAreaDiff = document.getElementById("max-area-diff-filter");
  controls.maxAreaDiffOutput = document.getElementById("max-area-diff-output");
  controls.maxDistance = document.getElementById("max-distance-filter");
  controls.maxDistanceOutput = document.getElementById("max-distance-output");
  controls.limit = document.getElementById("proposal-limit");
  controls.stateContiguity = document.getElementById("state-contiguity-filter");
  controls.privateContiguity = document.getElementById("private-contiguity-filter");
  controls.excludeAcquireOilGas = document.getElementById("exclude-acquire-og-filter");
  controls.excludeReleaseOilGas = document.getElementById("exclude-release-og-filter");
  controls.bridgesOnly = document.getElementById("bridges-only-filter");
  controls.valueLayer = document.getElementById("value-layer-toggle");
  controls.resetView = document.getElementById("reset-view");
  controls.clearSelection = document.getElementById("clear-selection");
  controls.resultCount = document.getElementById("result-count");
  controls.proposalList = document.getElementById("proposal-list");
  controls.proposalDetail = document.getElementById("proposal-detail");
  controls.selectedTag = document.getElementById("selected-tag");
  controls.valueLegend = document.getElementById("value-legend");
  state.filters.limit = controls.limit.value;
  state.filters.maxDistanceKm = Number(controls.maxDistance.value);
}

function bindControls() {
  controls.ownership.addEventListener("change", () => {
    state.filters.ownership = controls.ownership.value;
    applyFilters();
  });

  controls.swapType.addEventListener("change", () => {
    state.filters.swapType = controls.swapType.value;
    applyFilters();
  });

  controls.patch.addEventListener("change", () => {
    state.filters.patchId = controls.patch.value;
    applyFilters();
  });

  controls.minGain.addEventListener("input", () => {
    state.filters.minGain = Number(controls.minGain.value);
    controls.minGainOutput.value = Number(controls.minGain.value).toFixed(4);
    applyFilters();
  });

  controls.maxAreaDiff.addEventListener("input", () => {
    state.filters.maxAreaDiff = Number(controls.maxAreaDiff.value);
    controls.maxAreaDiffOutput.value = `${Number(controls.maxAreaDiff.value).toFixed(1)}%`;
    applyFilters();
  });

  controls.maxDistance.addEventListener("input", () => {
    state.filters.maxDistanceKm = Number(controls.maxDistance.value);
    controls.maxDistanceOutput.value = `${Number(controls.maxDistance.value).toFixed(1)} km`;
    applyFilters();
  });

  controls.limit.addEventListener("change", () => {
    state.filters.limit = controls.limit.value;
    applyFilters();
  });

  controls.stateContiguity.addEventListener("change", () => {
    state.filters.stateContiguity = controls.stateContiguity.checked;
    applyFilters();
  });

  controls.privateContiguity.addEventListener("change", () => {
    state.filters.privateContiguity = controls.privateContiguity.checked;
    applyFilters();
  });

  controls.excludeAcquireOilGas.addEventListener("change", () => {
    state.filters.excludeAcquireOilGas = controls.excludeAcquireOilGas.checked;
    applyFilters();
  });

  controls.excludeReleaseOilGas.addEventListener("change", () => {
    state.filters.excludeReleaseOilGas = controls.excludeReleaseOilGas.checked;
    applyFilters();
  });

  controls.bridgesOnly.addEventListener("change", () => {
    state.filters.bridgesOnly = controls.bridgesOnly.checked;
    applyFilters();
  });

  controls.valueLayer.addEventListener("change", () => {
    state.display.showValueLayer = controls.valueLayer.checked;
    syncOverlayVisibility();
    refreshLayerStyles();
    updateLegendVisibility();
  });

  controls.resetView.addEventListener("click", resetMapView);
  controls.clearSelection.addEventListener("click", () => {
    state.selectedProposal = null;
    renderProposalList();
    updateSelectionUI();
    refreshLayerStyles();
  });

  controls.minGainOutput.value = Number(controls.minGain.value).toFixed(4);
  controls.maxAreaDiffOutput.value = `${Number(controls.maxAreaDiff.value).toFixed(1)}%`;
  controls.maxDistanceOutput.value = `${Number(controls.maxDistance.value).toFixed(1)} km`;
}

function renderSummaryCards() {
  const summary = state.summary;
  const cards = [
    ["Mapped proposals", summary.proposalCount],
    ["Notebook total", summary.notebookProposalCount ?? summary.proposalCount],
    ["Acquire parcels", summary.uniqueAcquireCandidates],
    ["Mapped patches", summary.patchCount],
  ];

  controls.summaryCards.innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="stats-card">
          <span class="metric-label">${label}</span>
          <strong>${formatInteger(value)}</strong>
        </article>
      `,
    )
    .join("");
}

function createMap(parcels, patches, master) {
  const light = L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
  });

  const imagery = L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    {
      attribution: "&copy; Esri",
    },
  );

  state.map = L.map("map", {
    layers: [light],
    zoomControl: true,
  });

  state.layers.baseLayers = { light, imagery };

  state.layers.master = L.geoJSON(master, {
    style: {
      color: COLORS.boundary,
      weight: 2.1,
      opacity: 0.85,
      fillOpacity: 0,
      dashArray: "8 5",
    },
  }).addTo(state.map);

  state.layers.patches = L.geoJSON(patches, {
    style: patchStyle,
    onEachFeature(feature, layer) {
      state.patchLayers.set(feature.properties.patchId, layer);
      layer.bindPopup(patchPopup(feature.properties), { className: "popup" });
    },
  }).addTo(state.map);

  state.layers.parcels = L.geoJSON(parcels, {
    style: parcelStyle,
    onEachFeature(feature, layer) {
      state.parcelLayers.set(feature.properties.parcelId, layer);
      layer.bindPopup(parcelPopup(feature.properties), { className: "popup" });
      layer.on("click", () => {
        const matching = state.filteredProposals.find(
          (proposal) =>
            proposal.acquireParcelId === feature.properties.parcelId ||
            proposal.releaseParcelId === feature.properties.parcelId,
        );
        if (matching) {
          setSelectedProposal(matching, false);
        }
      });
    },
  }).addTo(state.map);

  state.layers.selectedLine = L.layerGroup().addTo(state.map);
  state.layers.selectedMarkers = L.layerGroup().addTo(state.map);

  L.control.layers(
    {
      "Carto Light": light,
      "Esri Imagery": imagery,
    },
    {
      "Federal patches": state.layers.patches,
      Parcels: state.layers.parcels,
      Boundary: state.layers.master,
    },
    { collapsed: true },
  ).addTo(state.map);

  syncOverlayVisibility();
  updateLegendVisibility();
  resetMapView();
}

function applyFilters() {
  let proposals = state.proposals.filter((proposal) => {
    if (state.filters.ownership !== "ALL" && proposal.acquireOwnership !== state.filters.ownership) {
      return false;
    }

    if (state.filters.swapType === "same" && !proposal.samePatch) {
      return false;
    }
    if (state.filters.swapType === "cross" && proposal.samePatch) {
      return false;
    }

    if (state.filters.patchId !== "ALL" && proposal.receivePatchId !== state.filters.patchId) {
      return false;
    }

    if (proposal.netGain < state.filters.minGain) {
      return false;
    }

    if (proposal.areaDiffPct > state.filters.maxAreaDiff) {
      return false;
    }

    if (!Number.isFinite(Number(proposal.distanceKm)) || Number(proposal.distanceKm) > state.filters.maxDistanceKm) {
      return false;
    }

    if (state.filters.stateContiguity || state.filters.privateContiguity) {
      const matchesState   = state.filters.stateContiguity   && proposal.landownerContiguityGain && proposal.acquireOwnership === "STATE";
      const matchesPrivate = state.filters.privateContiguity && proposal.landownerContiguityGain && proposal.acquireOwnership === "PRIVATE";
      if (!matchesState && !matchesPrivate) return false;
    }

    if (state.filters.excludeAcquireOilGas && proposal.acquireOilGasFlag) return false;
    if (state.filters.excludeReleaseOilGas && proposal.releaseOilGasFlag) return false;

    if (state.filters.bridgesOnly && !proposal.bridges) return false;

    return true;
  });

  proposals = proposals.sort((left, right) => left.rank - right.rank);
  if (state.filters.limit !== "ALL") {
    proposals = proposals.slice(0, Number(state.filters.limit));
  }

  state.filteredProposals = proposals;

  if (!proposals.length) {
    state.selectedProposal = null;
  } else if (!state.selectedProposal || !proposals.some((proposal) => proposal.rank === state.selectedProposal.rank)) {
    state.selectedProposal = proposals[0];
  }

  renderProposalList();
  updateSelectionUI();
  refreshLayerStyles();
}

function populatePatchFilterOptions() {
  const patchIds = [...new Set(
    state.proposals
      .map((proposal) => proposal.receivePatchId)
      .filter((patchId) => typeof patchId === "string" && patchId.length),
  )].sort((left, right) => left.localeCompare(right, undefined, { numeric: true }));

  controls.patch.innerHTML = [
    '<option value="ALL" selected>All patches</option>',
    ...patchIds.map((patchId) => `<option value="${patchId}">${patchId}</option>`),
  ].join("");
}

function renderProposalList() {
  const proposals = state.filteredProposals;
  controls.resultCount.textContent = `${formatInteger(proposals.length)} results`;

  if (!proposals.length) {
    controls.proposalList.innerHTML = `
      <div class="empty-state">
        No proposals match the current filters. Try widening the net gain or area difference range.
      </div>
    `;
    return;
  }

  controls.proposalList.innerHTML = proposals
    .map((proposal) => {
      const selectedClass =
        state.selectedProposal && state.selectedProposal.rank === proposal.rank ? "is-active" : "";
      return `
        <article class="proposal-item ${selectedClass}" data-rank="${proposal.rank}">
          <div class="proposal-title">
            <strong class="proposal-rank">#${proposal.rank}</strong>
            <strong>+${formatDecimal(proposal.contiguityGainAcres, 1)} ac</strong>
          </div>
          <p class="proposal-inline">
            <strong>Contiguity gain:</strong> +${formatDecimal(proposal.contiguityGainAcres, 1)} ac
            &middot; <strong>Net gain:</strong> +${proposal.netGain.toFixed(4)}
          </p>
          <p class="proposal-inline">
            <strong>${proposal.receivePatchId}</strong> acquires
            <strong>${proposal.acquireParcelId}</strong> and releases
            <strong>${proposal.releaseParcelId}</strong>.
          </p>
          <div class="proposal-meta">
            <div>
              <span>Acquire</span>
              ${proposal.acquireOwnership}${proposal.nfName ? ` &middot; ${proposal.nfName}` : ""} &middot; ${proposal.acquireAcres.toFixed(1)} ac
            </div>
            <div>
              <span>Release</span>
              ${proposal.releaseAcres.toFixed(1)} ac &middot; ${proposal.distanceKm.toFixed(2)} km
            </div>
          </div>
          <div class="proposal-badge-row">
            <span class="badge ${proposal.samePatch ? "same" : "cross"}">
              ${proposal.samePatch ? "Same patch" : "Cross patch"}
            </span>
            ${proposal.bridges ? '<span class="badge bridge">Bridge</span>' : ""}
            ${proposal.landownerContiguityGain ? '<span class="badge landowner">Contiguity</span>' : ""}
            ${(proposal.acquireOilGasFlag || proposal.releaseOilGasFlag) ? '<span class="badge oil">O&amp;G</span>' : ""}
            ${proposal.areaFlag ? '<span class="badge warn">Area warning</span>' : ""}
          </div>
        </article>
      `;
    })
    .join("");

  controls.proposalList.querySelectorAll(".proposal-item").forEach((element) => {
    element.addEventListener("click", () => {
      const proposal = state.filteredProposals.find(
        (item) => item.rank === Number(element.dataset.rank),
      );
      if (proposal) {
        setSelectedProposal(proposal, true);
      }
    });
  });
}

function setSelectedProposal(proposal, zoomToPair) {
  state.selectedProposal = proposal;
  renderProposalList();
  updateSelectionUI();
  refreshLayerStyles();
  if (zoomToPair) {
    zoomToSelectedProposal();
  }
}

function updateSelectionUI() {
  const proposal = state.selectedProposal;

  if (!proposal) {
    controls.selectedTag.textContent = "No selection";
    controls.proposalDetail.textContent =
      "Choose a ranked proposal to inspect its swap pair, patch change, and parcel values.";
    return;
  }

  controls.selectedTag.textContent = `Proposal #${proposal.rank}`;
  controls.proposalDetail.innerHTML = `
    <h3>${proposal.receivePatchId} swap</h3>
    <p>Contiguity gain: <strong>+${formatDecimal(proposal.contiguityGainAcres, 1)} ac</strong></p>
    <p>
      This proposal raises the receive patch exposure from
      <strong>${proposal.oldRatio.toFixed(4)}</strong> to
      <strong>${proposal.newRatio.toFixed(4)}</strong>.
    </p>
    <p>The swapped parcel exposure delta is: <strong>${formatDecimal(proposal.parcelExposureDelta, 4)}</strong>
       (acq ${formatDecimal(proposal.acqFraction, 4)} / rel ${formatDecimal(proposal.relFraction, 4)})</p>
    <div class="detail-grid">
      <div>
        <span>Acquire parcel</span>
        <strong>${proposal.acquireParcelId}</strong><br>
        ${proposal.acquireOwnership} &middot; ${proposal.acquireAcres.toFixed(1)} acres
        ${proposal.nfName ? `<br><em>${proposal.nfName}</em>` : ""}
      </div>
      <div>
        <span>Release parcel</span>
        <strong>${proposal.releaseParcelId}</strong><br>
        Federal &middot; ${proposal.releaseAcres.toFixed(1)} acres
      </div>
      <div>
        <span>Area difference</span>
        <strong>${proposal.areaDiffPct.toFixed(1)}%</strong>
      </div>
      <div>
        <span>Distance</span>
        <strong>${proposal.distanceKm.toFixed(2)} km</strong>
      </div>
    </div>
    <div class="detail-note">
      <span>Release patch effect</span>
      ${
        proposal.samePatch
          ? "This is a same-patch trade, so the release effect is already included in the receive patch change."
          : `Release patch ${proposal.releasePatchId} changes from ${proposal.releaseOldRatio.toFixed(4)} to ${proposal.releaseNewRatio.toFixed(4)}.`
      }
    </div>
    ${proposal.bridges ? `
    <div class="detail-note">
      <span>Bridge swap</span>
      This proposal connects two or more previously separate federal patches.
    </div>` : ""}
    ${proposal.landownerContiguityGain ? `
    <div class="detail-note">
      <span>Landowner contiguity</span>
      ${proposal.nfName || "The acquiring landowner"} receives land adjacent to existing holdings.
    </div>` : ""}
    ${proposal.acquireOilGasFlag ? `
    <div class="detail-note">
      <span>O&amp;G &mdash; acquire parcel</span>
      ${proposal.acquireOilGasFlag}
    </div>` : ""}
    ${proposal.releaseOilGasFlag ? `
    <div class="detail-note">
      <span>O&amp;G &mdash; release parcel</span>
      ${proposal.releaseOilGasFlag}
    </div>` : ""}
  `;
}

function refreshLayerStyles() {
  state.layers.selectedLine.clearLayers();
  state.layers.selectedMarkers.clearLayers();

  state.layers.parcels.eachLayer((layer) => {
    layer.setStyle(parcelStyle({ properties: layer.feature.properties }));
    layer.setPopupContent(parcelPopup(layer.feature.properties), { className: "popup" });
  });

  state.layers.patches.eachLayer((layer) => {
    layer.setStyle(patchStyle({ properties: layer.feature.properties }));
  });

  if (state.selectedProposal) {
    drawProposalLine(state.selectedProposal);
  }

  renderSummaryCardsForFilters();
}

function renderSummaryCardsForFilters() {
  const proposals = state.filteredProposals;
  const acquireIds = new Set(proposals.map((proposal) => proposal.acquireParcelId));
  const releaseIds = new Set(proposals.map((proposal) => proposal.releaseParcelId));
  const topGain = proposals.length ? proposals[0].netGain.toFixed(4) : "0.0000";

  const cards = [
    ["Selected proposals", proposals.length],
    ["Possible parcel acquisitions", acquireIds.size],
    ["Possible parcel releases", releaseIds.size],
    ["Top visible gain", topGain],
  ];

  controls.summaryCards.innerHTML = cards
    .map(
      ([label, value]) => `
        <article class="stats-card">
          <span class="metric-label">${label}</span>
          <strong>${typeof value === "number" ? formatInteger(value) : value}</strong>
        </article>
      `,
    )
    .join("");
}

function parcelStyle(feature) {
  const props = feature.properties;
  const proposal = state.selectedProposal;
  const filteredAcquire = new Set(state.filteredProposals.map((item) => item.acquireParcelId));
  const filteredRelease = new Set(state.filteredProposals.map((item) => item.releaseParcelId));

  if (state.display.showValueLayer) {
    return valueParcelStyle(props, proposal, filteredAcquire, filteredRelease);
  }

  if (proposal) {
    if (props.parcelId === proposal.acquireParcelId) {
      return {
        color: COLORS.acquire,
        weight: 3.5,
        fillColor: COLORS.acquire,
        fillOpacity: 0.68,
        opacity: 1,
      };
    }

    if (props.parcelId === proposal.releaseParcelId) {
      return {
        color: COLORS.release,
        weight: 3.5,
        fillColor: COLORS.release,
        fillOpacity: 0.66,
        opacity: 1,
      };
    }
  }

  if (filteredAcquire.has(props.parcelId)) {
    return {
      color: COLORS.acquire,
      weight: 1.9,
      fillColor: COLORS.acquire,
      fillOpacity: 0.42,
      opacity: 0.95,
    };
  }

  if (filteredRelease.has(props.parcelId)) {
    return {
      color: COLORS.release,
      weight: 1.9,
      fillColor: COLORS.release,
      fillOpacity: 0.38,
      opacity: 0.95,
    };
  }

  const baseColor = ownershipColor(props.ownership);

  return {
    color: baseColor,
    weight: props.ownership === "FEDERAL" ? 0.9 : 0.7,
    fillColor: baseColor,
    fillOpacity: props.ownership === "FEDERAL" ? 0.1 : 0.05,
    opacity: 0.45,
  };
}

function valueParcelStyle(props, proposal, filteredAcquire, filteredRelease) {
  const fillColor = valuePerGisAcreColor(props.valuePerGisAcre);
  const baseStyle = {
    color: ownershipColor(props.ownership),
    weight: props.ownership === "FEDERAL" ? 1 : 0.8,
    fillColor,
    fillOpacity: 0.72,
    opacity: 0.82,
  };

  if (proposal) {
    if (props.parcelId === proposal.acquireParcelId) {
      return {
        ...baseStyle,
        color: COLORS.acquire,
        weight: 3.4,
        opacity: 1,
      };
    }

    if (props.parcelId === proposal.releaseParcelId) {
      return {
        ...baseStyle,
        color: COLORS.release,
        weight: 3.4,
        opacity: 1,
      };
    }
  }

  if (filteredAcquire.has(props.parcelId)) {
    return {
      ...baseStyle,
      color: COLORS.acquire,
      weight: 1.9,
      opacity: 0.96,
    };
  }

  if (filteredRelease.has(props.parcelId)) {
    return {
      ...baseStyle,
      color: COLORS.release,
      weight: 1.9,
      opacity: 0.96,
    };
  }

  return baseStyle;
}

function patchStyle(feature) {
  const props = feature.properties;
  const ratio = Number(props.interiorEdgeRatio || 0);
  const selected = state.selectedProposal && state.selectedProposal.receivePatchId === props.patchId;

  return {
    color: selected ? COLORS.boundary : "#7f6736",
    weight: selected ? 2.2 : 1,
    fillColor: patchColor(ratio),
    fillOpacity: selected ? 0.42 : 0.2,
    opacity: selected ? 0.95 : 0.55,
  };
}

function patchColor(ratio) {
  if (ratio >= 0.40) return "#6d8a43";
  if (ratio >= 0.32) return "#94a84e";
  if (ratio >= 0.24) return "#c6bc5c";
  if (ratio >= 0.15) return "#d9ab63";
  return "#d58b64";
}

function parcelPopup(props) {
  const ranks = props.proposalRanks.length ? props.proposalRanks.join(", ") : "None";
  const ownerLine = props.ownerName ? ` &middot; ${props.ownerName}` : "";
  return `
    <div class="popup">
      <h3>${props.parcelId}</h3>
      <p><strong>${props.ownership}</strong> parcel${ownerLine}</p>
      <p>GIS acres: ${formatDecimal(props.gisAcres, 1)}</p>
      <p>Total market value (TOTALACT): ${formatCurrency(props.totalAct)}</p>
      <p>Value per GIS acre: ${formatCurrency(props.valuePerGisAcre)}</p>
      <p>Proposal ranks: ${ranks}</p>
    </div>
  `;
}

function patchPopup(props) {
  return `
    <div class="popup">
      <h3>${props.patchId}</h3>
      <p>Area: ${formatDecimal(props.areaAcres, 1)} acres</p>
      <p>Parcels: ${formatInteger(props.parcelCount)}</p>
      <p>Interior fraction: ${formatDecimal(props.interiorEdgeRatio, 4)}</p>
    </div>
  `;
}

function drawProposalLine(proposal) {
  const acquire = L.latLng(proposal.acquireCentroid[0], proposal.acquireCentroid[1]);
  const release = L.latLng(proposal.releaseCentroid[0], proposal.releaseCentroid[1]);

  L.polyline([acquire, release], {
    color: "#413223",
    weight: 2,
    dashArray: "6 6",
    opacity: 0.95,
  }).addTo(state.layers.selectedLine);

  L.circleMarker(acquire, {
    radius: 7,
    color: "#ffffff",
    weight: 2,
    fillColor: COLORS.acquire,
    fillOpacity: 1,
  }).addTo(state.layers.selectedMarkers);

  L.circleMarker(release, {
    radius: 7,
    color: "#ffffff",
    weight: 2,
    fillColor: COLORS.release,
    fillOpacity: 1,
  }).addTo(state.layers.selectedMarkers);
}

function zoomToSelectedProposal() {
  if (!state.selectedProposal) {
    return;
  }

  const acquireLayer = state.parcelLayers.get(state.selectedProposal.acquireParcelId);
  const releaseLayer = state.parcelLayers.get(state.selectedProposal.releaseParcelId);

  if (acquireLayer && releaseLayer) {
    const bounds = acquireLayer.getBounds().extend(releaseLayer.getBounds());
    state.map.fitBounds(bounds.pad(0.35), { animate: true });
  }
}

function resetMapView() {
  if (!state.layers.master) {
    return;
  }
  state.map.fitBounds(state.layers.master.getBounds().pad(0.08), { animate: true });
}

function syncOverlayVisibility() {
  if (!state.map || !state.layers.parcels || !state.layers.patches || !state.layers.master) {
    return;
  }

  if (!state.map.hasLayer(state.layers.parcels)) {
    state.map.addLayer(state.layers.parcels);
  }

  if (state.display.showValueLayer) {
    if (state.map.hasLayer(state.layers.patches)) {
      state.map.removeLayer(state.layers.patches);
    }
    if (state.map.hasLayer(state.layers.master)) {
      state.map.removeLayer(state.layers.master);
    }
    return;
  }

  if (!state.map.hasLayer(state.layers.patches)) {
    state.map.addLayer(state.layers.patches);
  }
  if (!state.map.hasLayer(state.layers.master)) {
    state.map.addLayer(state.layers.master);
  }
}

function updateLegendVisibility() {
  controls.valueLegend.classList.toggle("is-hidden", !state.display.showValueLayer);
}

function ownershipColor(ownership) {
  if (ownership === "FEDERAL") return COLORS.federal;
  if (ownership === "STATE") return COLORS.state;
  return COLORS.private;
}

function valuePerGisAcreColor(value) {
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) {
    return COLORS.muted;
  }

  const clamped = Math.max(VALUE_BREAKS[0], Math.min(VALUE_BREAKS[VALUE_BREAKS.length - 1], numeric));
  for (let index = VALUE_BREAKS.length - 1; index > 0; index -= 1) {
    if (clamped >= VALUE_BREAKS[index - 1]) {
      return VALUE_COLORS[index - 1];
    }
  }

  return VALUE_COLORS[0];
}

function formatInteger(value) {
  return new Intl.NumberFormat("en-US").format(value);
}

function formatDecimal(value, digits) {
  if (value === null || value === undefined) return "N/A";
  return Number(value).toFixed(digits);
}

function formatCurrency(value) {
  if (value === null || value === undefined) return "N/A";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}
