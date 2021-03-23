window.CESIUM_BASE_URL = '/Cesium/Cesium';

import * as Cesium from 'cesium';
import "./Cesium/Widgets/widgets.css";

// Grant CesiumJS access to your ion assets
Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjOGZiMDIxMi02NzYwLTQ5MzgtOTk0ZC02YTJiYWU5MTQyODUiLCJpZCI6MjE0MSwiaWF0IjoxNTMxNzI3NzUzfQ.cRJYZ0l7AOiA2BcvqzY-Z4kIJcyZd2G-ygod2Dw9ZtA";

let viewer = new Cesium.Viewer("cesiumContainer", {
  terrainProvider: new Cesium.CesiumTerrainProvider({
    url: Cesium.IonResource.fromAssetId(1),
  }),
});

// Add Cesium OSM Buildings.
let osmBuildings = viewer.scene.primitives.add(Cesium.createOsmBuildings());
// Fly the camera to San Francisco using longitude, latitude, and height.

viewer.animation.container.style.visibility = "hidden";
viewer.timeline.container.style.visibility = "hidden";

// Delete un-usage widgets
~(function (){
    document.querySelector("#cesiumContainer > div > div.cesium-viewer-bottom").remove();
    document.querySelector("#cesiumContainer > div > div.cesium-viewer-toolbar").remove();
})();
viewer.forceResize();

viewer.camera.flyTo({
  destination: Cesium.Cartesian3.fromDegrees(131.9113, 43.1332, 150000)
});


const Vladivostok = { longitude: 131.9113, latitude: 43.1332, height: 1000 };

const pointEntity = viewer.entities.add({
  description: `Vladivostok point at (${Vladivostok.longitude}, ${Vladivostok.latitude})`,
  position: Cesium.Cartesian3.fromDegrees(Vladivostok.longitude, Vladivostok.latitude, Vladivostok.height),
  point: { pixelSize: 5, color: Cesium.Color.RED },
  orientation : {
    heading : Cesium.Math.toRadians(0.0),
    pitch : Cesium.Math.toRadians(-15.0),
  }
});

