import React, { useState, useEffect, useLayoutEffect } from "react";
import { generateDateObject, startYear, oneDay } from "../utils/utils";

const Preview = props => {

    const preview =
        <div className="photo-container-preview">
            {
                props.img.length && props.img
                    .map((item, index) => <div style={{
                        backgroundImage: `url('${item}')`,
                        backgroundPosition: 'center center',
                        backgroundSize: 'cover',
                    }} key={index} className={'item'}/>)
            }
        </div>;

    const card =
        <div className="card__item">
            {
                typeof(props.img) !== "undefined" && props.img != null ? preview : null
            }
            <div className="describe">
                {props.date}
            </div>
        </div>;

    return(card)
};

const Line = props => {
    let line = null;

    switch (props.type) {
        case 1:
            line =
                <>

                </>;
            break;
        case 2:
            break;
    }
    return(line);
};

export const Timeline = props => {

    const [currentDate, setCurrentDate] = useState(new Date());
    const data = generateDateObject();
    const [currentData, setCurrentData] = useState(data[currentDate.getFullYear()][currentDate.getMonth()][currentDate.getDay()]);


    let timeline =
        <div className={"timeline"}>
            <div className="left__arrow">
            </div>
            <div className="timeline__current__data">
                <Line />
            </div>
            <div className="right__arrow">
            </div>
        </div>;

    return(timeline)
};
