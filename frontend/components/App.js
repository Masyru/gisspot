import React from "react";
import "../Cesium/Main";
import { Toolbar } from "./Toolbar";
import { Timeline } from "./Timeline";

export const App = () => {
    // App menu
    let app =
        <>
            <Toolbar />
            <Timeline />
        </>;

    return(app);
};
