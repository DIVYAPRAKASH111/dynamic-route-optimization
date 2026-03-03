let map = L.map("map").setView([51.5, -0.1], 7);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap",
}).addTo(map);

let locations = [];
let markers = [];
let polylines = [];
let urgentMode = false;

const colors = ["red", "blue", "green", "orange", "purple"];

map.on("click", function (e) {
  if (urgentMode) {
    addUrgentOrder(e.latlng);
    urgentMode = false;
    return;
  }

  addLocation(e.latlng);
});

function addLocation(latlng) {
  locations.push([latlng.lat, latlng.lng]);

  let marker = L.marker(latlng).addTo(map);
  markers.push(marker);
}

function clearRoutes() {
  polylines.forEach((line) => map.removeLayer(line));
  polylines = [];
}

function drawRoutes(routes) {
  clearRoutes();

  routes.forEach((route, index) => {
    let coords = route.map((i) => locations[i]);
    let line = L.polyline(coords, {
      color: colors[index % colors.length],
      weight: 4,
    }).addTo(map);

    polylines.push(line);
  });
}

function updateSummary(data) {
  let html = `
        Vehicles used: ${data.routes.length}<br>
        Total distance: ${data.total_distance}<br>
        Total time: ${data.total_time}
    `;

  data.routes.forEach((r, i) => {
    html += `<br><br>Vehicle ${i + 1}: ${r.join(" → ")}`;
  });

  document.getElementById("summary-content").innerHTML = html;
}

document.getElementById("optimize-btn").addEventListener("click", async () => {
  const vehicleCount = parseInt(document.getElementById("vehicle-count").value);

  const res = await fetch("/optimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      locations: locations,
      vehicle_count: vehicleCount,
    }),
  });

  const data = await res.json();

  drawRoutes(data.routes);
  updateSummary(data);
});

document.getElementById("traffic-btn").addEventListener("click", async () => {
  const res = await fetch("/simulate-traffic", {
    method: "POST",
  });

  const data = await res.json();

  drawRoutes(data.routes);
  updateSummary(data);
});

document.getElementById("urgent-btn").addEventListener("click", () => {
  alert("Click on map to place urgent order");
  urgentMode = true;
});

async function addUrgentOrder(latlng) {
  locations.push([latlng.lat, latlng.lng]);

  L.marker(latlng, {
    icon: L.icon({
      iconUrl: "https://maps.google.com/mapfiles/ms/icons/yellow-dot.png",
      iconSize: [32, 32],
    }),
  }).addTo(map);

  const res = await fetch("/add-order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      location: [latlng.lat, latlng.lng],
    }),
  });

  const data = await res.json();

  drawRoutes(data.routes);
  updateSummary(data);
}
