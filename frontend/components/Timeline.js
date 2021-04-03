import React, { useState, useEffect, useLayoutEffect } from "react";
import "./Timeline.css";
import { generateDateObject, startYear, oneDay } from "../utils/utils";
import { Consumer } from "../events/handleWebsocket";

let object = generateDateObject();


function Card(props){

    let card =
        <div className={`card__item${props.type ? '' : ' card__item-day'}`} onClick={props.changeData}>
            {
                props.showPreview && props.img !== undefined && props.img !== null &&  props.img.map((img, j) =>
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
    let nearby = props.nearbyToArea;
    let conversionLine =
        <>
            {
                props.data.length && props.data.map((item, k) =>
                    props.nearbyToArea < 3 ?
                        <Card
                            key={k}
                            text={item}
                            showPreview={props.showPreview}
                            img={props.currentArrayData[k]}
                            changeData={ () => { props.setNearbyToArea(props.nearbyToArea + 1)}}
                        />
                        :
                        <Card
                            key={k}
                            text={item}
                            showPreview={props.showPreview}
                            img={props.currentArrayData[k]}
                            changeData={
                                () => {
                                    props.setPhoto(item)
                                    props.nextPage();
                                }
                            }
                        />
                    )
            }
        </>;

    return(conversionLine);
}


export default class Timeline extends React.Component{
    // refDatetime - ссылки на год, месяц и день
    // timeMinus - в области работы есть дельта в секундах, которая используется для вычитания и получения новой даты
    // currentData - дата, которая хранится в объекте по индексу года, месяца или дня
    // dataShownAsArray - массив индексов, ссылок на дату
    // type - переменная для понимания нужно ли рендерить preview
    // datetime - дата по которой сейчас фильтруем снимки

    constructor(props) {
        super(props);
        this.state = {
            refDatetime: {
                year: null,
                month: null,
                day: null,
            },
            timeMinus: 0,
            currentData: null,
            nearbyToArea: 0,
            dataShownAsArray: null,
            type: true,
            datetime: null,
        };

        this.changeType = this.changeType.bind(this);
        this.setNearbyToArea = this.setNearbyToArea.bind(this);
        this.changeDatetime = this.changeDatetime.bind(this);
    }

    componentWillMount() {
        let currentDatetime = new Date();
        // Base defining the state
        this.setState({
            dataShownAsArray: Object.keys(object),
            datetime: currentDatetime,
            currentData: object,
            refDatetime: {
                year: currentDatetime.getFullYear(),
                month: currentDatetime.getMonth(),
                day: currentDatetime.getDay(),
            },
        })
    }

    setNearbyToArea(e){
        const thi$ = this;
        // this var is about to set const for render func in arrows onClick event
        // solve nearby var that
        e = e < 1 ? 1 : e;
        e = e > 3 ? 3 : e;
        let timeMinus = 0;
        let obj = object;
        let copyDate = Object.assign(thi$.state.datetime);

        switch (e){
            case 1:
                timeMinus = oneDay * 365;
                obj = obj[copyDate.getFullYear()];
                thi$.changeType(true);
                break;
            case 2:
                timeMinus = oneDay * copyDate.getDate();
                obj = obj[copyDate.getFullYear()][copyDate.getMonth()];
                thi$.changeType(true);
                break;
            case 3:
                timeMinus = oneDay;
                obj = obj[copyDate.getFullYear()][copyDate.getMonth()][copyDate.getDay()];
                thi$.changeType(false);
                break;
            default:
                throw new Error('Calling the setNearbyToArea with wrong value');
        }

        thi$.setState({
            nearbyToArea: e,
            timeMinus: timeMinus,
            dataShownAsArray: Object.keys(obj),
            currentData: obj,
        })
    }

    changeDatetime(op){
        let dateInSeconds = this.state.datetime.getTime();
        if(op === "+"){
            dateInSeconds += this.state.timeMinus
        } else if (op === "-"){
            dateInSeconds -= this.state.timeMinus
        }
        let newDatetime = new Date(dateInSeconds)
        this.setState({
            datetime: newDatetime,
            refDatetime: {
                year: newDatetime.getFullYear(),
                month: newDatetime.getMonth(),
                day: newDatetime.getDay(),
            }
        });
        this.setNearbyToArea(this.state.nearbyToArea);
    }

    changeType(val){
        this.setState({
            type: val,
        })
    }

    render(){

        let timeline =
            <div className="timeline">
                <div className="left__arrow" onClick={() => this.changeDatetime("-")}>
                    <img src={"/static/timeline/left-arrow.svg"} alt="влево"  width={'30px'} height={'30px'}/>
                </div>
                <div className={`timeline__current__data`}>
                    <ConversionLine
                        datetime={this.state.datetime}
                        data={this.state.dataShownAsArray}
                        showPreview={!this.state.type}
                        currentArrayData={this.state.currentData}
                        nearbyToArea={this.state.nearbyToArea}
                        setNearbyToArea={this.setNearbyToArea}
                        changeDataArrayFunc={this.changeDatetime}
                        setPhoto={this.props.setPhoto}
                        nextPage={this.props.nextPage}
                    />
                </div>
                <div className="right__arrow" onClick={() => this.changeDatetime("+")}>
                    <img src={"/static/timeline/right-arrow.svg"} alt="вправо" width={'30px'} height={'30px'}/>
                </div>
            </div>;

        return(timeline)
    }
};
