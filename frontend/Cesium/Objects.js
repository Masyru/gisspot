import * as Cesium from "cesium";

// Get current coords of place
export function getPointCoords(viewer){

    let handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
    handler.setInputAction(function(click){
        // Set vars of layer
        let ellipsoid = viewer.scene.globe.ellipsoid;
        let cartesian = viewer.camera.pickEllipsoid(click.position, ellipsoid);
        // Convert to lat and lon
        if (cartesian) {
            let cartographic = ellipsoid.cartesianToCartographic(cartesian);
            let longitude = Cesium.Math.toDegrees(cartographic.longitude).toFixed(2);
            let latitude= Cesium.Math.toDegrees(cartographic.latitude).toFixed(2);

            // someFetchFunc(JSON.strinjify(longitude, latitude));
        }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

}




// Fly to current location
// TODO Need to fix
export function flyToCurrentPos(viewer){

    let options = {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    };

    function success(pos) {
      let crd = pos.coords;

      console.log('Ваше текущее местоположение:');
      console.log(`Широта: ${crd.latitude}`);
      console.log(`Долгота: ${crd.longitude}`);

      let currentEntity = { longitude: crd.longitude, latitude: crd.latitude};
      viewer.flyTo(currentEntity)

    }

    function error(err) {
      console.warn(`ERROR(${err.code}): ${err.message}`);
    }

    navigator.geolocation.getCurrentPosition(success, error, options);
}

