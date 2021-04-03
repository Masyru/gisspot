import React from "react";
import ReactDOM from "react-dom";
import App from "./components/App";
import CesiumViewer from "./Cesium/Main";

ReactDOM.render(
    <CesiumViewer>
        <App />
    </CesiumViewer>,
    document.getElementById('root')
);
