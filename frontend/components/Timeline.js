import React, { useState, useEffect, useLayoutEffect } from "react";
import "./Timeline.css";
import { generateDateObject, startYear } from "../utils/utils";

const Card = (props) => {
    return(<div>card</div>)
};

const Line = (props) => {

};

export const Timeline = (props) => {

    const currentDate = new Date();
    const data = generateDateObject();
    const [currentData, setCurrentData] = useState(data[currentDate.getFullYear()][currentDate.getMonth()][currentDate.getDay()]);
    // TODO convert Date to seconds from 1970 and bind day, month and year to seconds const and divide it below
    const propsData = {
        log: console.log(this.data),
        data: data,
        callbackArrow: (typeArrow, target, data, year, month = 1, day = 1) => {
            typeArrow === "left" ?
                ~(() => {
                    if (target === "year"){
                        this.updateData(data[year - 1 >= startYear ? year : startYear][month][day])
                    } else if (target === "month"){
                        if (!(month - 1)){
                            this.callbackArrow("right", "year", data, year, 12, 1)
                        } else {
                            this.updateData(data[year][month - 1][day])
                        }
                    } else {
                        if (!(day - 1) && month !== 1){
                            let prevMonth = Object.assign(currentDate);
                            prevMonth.setMonth(month - 1);
                            this.callbackArrow("right", "month", data, year, month, prevMonth.getDate());
                        } else {
                            this.updateData(data[year][month][day - 1])
                        }
                    }
                })()
                :
                !(() => {
                    if (target === "year"){
                        this.updateData(data[year + 1 <= currentDate.getFullYear() ? year : currentDate.getFullYear()][month][day])
                    } else if (target === "month"){

                    } else {

                    }
                })();
        },
        updateData: (nextData) => setCurrentData(nextData),

    };

    let timeline =
        <div className={"timeline"}>

        </div>;

    return(timeline)
};
