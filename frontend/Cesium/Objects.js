import * as Cesium from "cesium";

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

    // // remove the event
    // handler.removeInputAction(Cesium.ScreenSpaceEventType.LEFT_CLICK);

}