function getCoordinatesFromGoogleMapsUrl (url)  {
  const result = url
    .split(":0x")
    [url.split(":0x").length - 1].split("!3d")?.[1]
    ?.split("!");
  if (!result) return [null, null];
  const lat = result[0];
  const lng = result[1].slice(2);
  return [lat, lng];
};

document.addEventListener('DOMContentLoaded', function () {
    const mapsInput = document.getElementById('id_google_maps_url');
    const lat_input = document.getElementById('id_lat');
    const lon_input = document.getElementById('id_lon');

    if (mapsInput && lat_input && lon_input) {
        mapsInput.addEventListener('change', function () {
            const url = mapsInput.value;
            const [lat,lon] = getCoordinatesFromGoogleMapsUrl(url)
            lat_input.value = lat
            lon_input.value = lon
        });
    }
});