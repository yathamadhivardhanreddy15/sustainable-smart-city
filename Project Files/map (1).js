// static/map.js

function drawRoutesOnMap(routes) {
  const map = L.map("map").setView([17.4, 78.45], 12); // Centered in Hyderabad

  // OpenStreetMap base layer
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);

  routes.forEach((route, index) => {
    const { lat1, lon1, lat2, lon2 } = route;
    const polyline = L.polyline(
      [
        [lat1, lon1],
        [lat2, lon2]
      ],
      {
        color: "blue",
        weight: 4,
        opacity: 0.7
      }
    ).addTo(map);

    polyline.bindPopup(`Route ${index + 1}`);
  });

  // Adjust view to fit all routes
  const bounds = routes.flatMap(r => [
    [r.lat1, r.lon1],
    [r.lat2, r.lon2]
  ]);
  map.fitBounds(bounds);
}
