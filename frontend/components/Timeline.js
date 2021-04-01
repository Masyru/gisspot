import React, { useState, useEffect, useLayoutEffect } from "react";
import "./Timeline.css";
import { generateDateObject, startYear, oneDay } from "../utils/utils";

let object = generateDateObject();


function Card(props){

    let card =
        <div className={`card__item${props.type ? '' : ' card__item-day'}`}>
            {
                props.showPreview && props.img.map((img, j) =>
                    <div className="preview" key={j}>
                        <img src={img} alt="..."/>
                    </div>
                )
            }
            <div className="describe">
                {props.text}
            </div>
        </div>

    return(card);
}


function ConversionLine(props){
    // Item must be the index as 2020 or 2010 if it is about years
    // also if it is about days it must contain new attr 'img'
    let conversionLine =
        <>
            {
                props.data.length && props.data.map((item, k) =>
                        <Card
                            key={k}
                            text={item}
                            showPreview={props.showPreview}
                            img={props.currentArrayData[k]}
                            changeData={
                                props.showPreview ?
                                    () => {

                                    } :
                                    () => {

                                    }
                            }
                        />
                    )
            }
        </>

    return(conversionLine);
}


export default class Timeline extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            timeMinus: 0,
            currentData: null,
            nearbyToArea: 0,
            dataShownAsArray: null,
            type: true,
            datetime: null,
        }

        this.changeType = this.changeType.bind(this);
        this.setNearbyToArea = this.setNearbyToArea.bind(this);
    }

    componentWillMount() {
        let currentDatetime = new Date();
        // Base defining the state
        this.setState({
            dataShownAsArray: Object.keys(object),
            datetime: currentDatetime,
            currentData: object,
        })
    }

    setNearbyToArea(e){
        const thi$ = this;
        // this var is about to set const for render func in arrows onClick event
        e = e < 1 ? 1 : e;
        e = e < 5 ? e : 4;
        let timeMinus = 0;
        let obj = object;
        let copyDate = Object.assign(this.state.currentData);

        switch (e){
            case 1:
                thi$.changeType(true);
                break;
            case 2:
                timeMinus = oneDay * 365;
                obj = obj[copyDate.getFullYear()]
                thi$.changeType(true);
                break;
            case 3:
                timeMinus = oneDay * copyDate.monthDays();
                obj = obj[copyDate.getFullYear()][copyDate.getMonth()]
                thi$.changeType(true);
                break;
            case 4:
                timeMinus = oneDay;
                obj = obj[copyDate.getFullYear()][copyDate.getMonth()][copyDate.getDay()]
                thi$.changeType(false);
                break;
            default:
                throw new Error('Calling the setNearbyToArea with wrong value');
        }

        this.setState({
            nearbyToArea: e,
            timeMinus: timeMinus,
            dataShownAsArray: Object.keys(obj),
            currentData: obj,
        })
    }

    changeDatetime(minus){
        console.log('work')
    }

    changeType(val){
        this.setState({
            type: val,
        })
    }

    render(){

        let timeline =
            <div className="timeline">
                <div className="left__arrow">
                    <img src={"/static/timeline/left-arrow.svg"} alt="влево"  width={'30px'} height={'30px'}/>
                </div>
                <div className={`timeline__current__data`}>
                    <ConversionLine
                        data={this.state.dataShownAsArray}
                        showPreview={!this.state.type}
                        currentArrayData={this.state.currentData}
                        setNearbyToArea={this.setNearbyToArea}
                        changeDataArrayFunc={this.changeDatetime}
                    />
                </div>
                <div className="right__arrow">
                    <img src={"/static/timeline/right-arrow.svg"} alt="вправо" width={'30px'} height={'30px'}/>
                </div>
            </div>;

        return(timeline)
    }
};
