import React, { useState } from "react";
import "./Timeline.css";
import { generateDateObject } from "../utils/utils";

export const Card = (props) => {
    return(<div>card</div>)
}


export const Timeline = (props) => {

    console.log(generateDateObject())

    let timeline =
        <div className={"timeline"}>
            Timeline
        </div>;

    return(timeline)
}

