import React, { useState, useEffect, useLayoutEffect } from "react";
import "./Timeline.css";
import { generateDateObject, startYear, oneDay } from "../utils/utils";


function Card(props){

    let card =
        <div className="card__item">
            {
                props.showPreview && props.img.map((item, j) =>
                    <div className="preview" key={j}>
                        <img src={item} alt="..."/>
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

    console.log(props.children)
    let conversionLine =
        <div className="conversion">
            {
                props.children
            }
        </div>

    return(conversionLine);
}


export default class Timeline extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            currentData: null,
            nearbyToArea: 1,
            dataShownAsArray: null,
            type: true,
            datetime: null,
        }

        this.changeType = this.changeType.bind(this);
        this.setNearbyToArea = this.setNearbyToArea.bind(this);
    }

    componentDidMount() {
        let currentDatetime = new Date();
        let object = generateDateObject();

        this.setState({
            dataShownAsArray: object,
            datetime: currentDatetime,
            currentData: object[currentDatetime.getFullYear()]
        })
    }

    setNearbyToArea(e){
        e = e < 0 ? 0 : e;
        e = e < 5 ? e : 4;

        this.setState({
            nearbyToArea: e,
        })
    }

    changeType(){
        this.setState({
            type: !this.state.type,
        })
    }

    render(){

        let timeline =
            <div className="timeline">
                <div className="left__arrow">
                    <img src={"/static/timeline/left-arrow.svg"} alt="влево"  width={'30px'} height={'30px'}/>
                </div>
                <div className="timeline__current__data">
                    {
                        this.state.type ?
                            <ConversionLine
                                data={this.state.dataShownAsArray}
                                showPreview={false}
                                currentArrayData={this.state.currentData}
                                setNearbyToArea={this.setNearbyToArea}
                            /> :
                            <ConversionLine
                                data={this.state.dataShownAsArray}
                                showPreview={true}
                                currentArrayData={this.state.currentData}
                                setNearbyToArea={this.setNearbyToArea}
                            />
                    }
                </div>
                <div className="right__arrow">
                    <img src={"/static/timeline/right-arrow.svg"} alt="вправо" width={'30px'} height={'30px'}/>
                </div>
            </div>;

        return(timeline)
    }
};
