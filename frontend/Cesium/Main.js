const Cesium = require("cesium");
import { getPointCoords, flyToCurrentPos } from "./Objects";
import "../bundle/Cesium/Widgets/widgets.css";
import React from "react";
import WebSocketViewer from "../events/handleWebsocket";

window.CESIUM_BASE_URL = '/static/Cesium/';
// Grant CesiumJS access to your ion assets
Cesium.Ion.defaultAccessToken = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJjOGZiMDIxMi02NzYwLTQ5MzgtOTk0ZC02YTJiYWU5MTQyODUiLCJpZCI6MjE0MSwiaWF0IjoxNTMxNzI3NzUzfQ.cRJYZ0l7AOiA2BcvqzY-Z4kIJcyZd2G-ygod2Dw9ZtA";


export default class CesiumViewer extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            viewer: new Cesium.Viewer("cesiumContainer", {
                terrainProvider: new Cesium.CesiumTerrainProvider({
                  url: Cesium.IonResource.fromAssetId(1),
                  Animation: false, // whether to display the animation control
                  shouldAnimate : true,
                  homeButton: false, //Do you want to display the Home button?
                  fullscreenButton: false, // whether to display the full screen button
                  baseLayerPicker: false, // whether to display the layer selection control
                  Geocoder: false, // whether to display the place name lookup control
                  Timeline: false, // whether to display the timeline control
                  sceneModePicker: true, // whether to display the projection mode control
                  navigationHelpButton: false, //display help information control
                  infoBox: false, // whether to display the information displayed after clicking the feature
                  requestRenderMode: true, //Enable request rendering mode
                  scene3DOnly: false, //each geometry instance will only be rendered in 3D to save GPU memory
                  sceneMode: 3, //Initial scene mode 1 2D mode 2 2D loop mode 3 3D mode Cesium.SceneMode
                  fullscreenElement: document.body,
                }),
                imageryProvider : Cesium.createWorldImagery({
                      style : Cesium.IonWorldImageryStyle.AERIAL_WITH_LABELS
                }),
                baseLayerPicker : true
            }),
        };
    }

    componentDidMount() {
        const viewer = this.state.viewer;
        viewer.animation.container.style.visibility = "hidden";
        viewer.timeline.container.style.visibility = "hidden";

        // Delete un-usage widgets
        ~(function (){
            document.querySelector("#cesiumContainer > div > div.cesium-viewer-bottom").remove();
            document.querySelector("#cesiumContainer > div > div.cesium-viewer-toolbar").remove();
        })();
        viewer.forceResize();

        // Set zoom
        viewer.scene.screenSpaceCameraController.maximumZoomDistance = 20000000;
        viewer.scene.screenSpaceCameraController.minimumZoomDistance = 0;
        viewer.scene.screenSpaceCameraController.enableTilt = false;


        viewer.camera.flyTo({
          destination: Cesium.Cartesian3.fromDegrees(131.9113, 43.1332, 1500000)
        });

        getPointCoords(viewer);
        flyToCurrentPos(viewer);
    }

  render(){
        return(
            <WebSocketViewer>
              {
                  React.Children.forEach(this.props.children, child => {
                      React.cloneElement(child, {viewer: this.state.viewer})
                  })
              }
            </WebSocketViewer>
        )
    }
}







