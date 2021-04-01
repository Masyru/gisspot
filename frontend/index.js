import React from "react";
import ReactDOM from "react-dom";
import { App } from "./components/App";
import "./Cesium/Main";
import { initNewAPI } from "./utils/utils";

ReactDOM.render(
    <App />,
    document.getElementById('root')
);

initNewAPI();
