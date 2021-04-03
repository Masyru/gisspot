import React, { useState } from "react";
import { fixZoom } from "../Cesium/Objects";
import "./Toolbar.css";
import "./PhotoPreview.css";


const Button = props => {
    const butt =
        <button type={'button'} title={props.title} onClick={props.onClickFunc} disabled={props.active} >
                <img src={`/static/cursors/${props.cursor}.svg`} alt="" width={props.width} height={props.height}/>
        </button>;

    return butt;
}

export const ClearButton = props => {
    return(
        <div className="fix__region__btn">
            <Button active={false} title={"Сбросить регион"} width={"15px"} height={"15px"} cursor={"remove"}
                    onClickFunc={() => {
                            fixZoom(props.viewer, true)
                            props.onClickFunc();
                        }
                    }
            />
        </div>
    )
}


export const FixRegion = props => {
    return(
        <div className="fix__region__btn">
            <Button active={false} title={"Выбрать регион"} width={"15px"} height={"15px"} cursor={"zoom-in"}
                    onClickFunc={() => {
                        fixZoom(props.viewer, false)
                        props.onClickFunc(2);
                    }
            }/>
        </div>
    )
}

export const PreviewInfo = props => {
    return(
        <div className="preview__info">
            <div className="close-btn" onClick={props.returnToSecondPage}>
                <img src="/static/cursors/remove.svg" alt=""/>
            </div>
            <img src="" alt="Preview image"/>
            <p>{props.datetime}</p>
        </div>
    )
}

const Toolbar = props => {
    // TODO need to indicate typeOfCursor and turn another mode for editting the map
    const [typeOfCursor, setTypeOfCursor] = useState(0);

    const toolbar =
        <div className={"toolbar"}>
            <Button active={typeOfCursor === 0} title={"Выбрать курсор"} width={"15px"} height={"15px"} cursor={"compass-light"} onClickFunc={() => setTypeOfCursor(0)}/>
            <Button active={typeOfCursor === 1} title={"Выбрать регион"} width={"20px"} height={"20px"} cursor={"selection"} onClickFunc={() => {setTypeOfCursor(1)}}/>
            <Button active={typeOfCursor === 2} title={"Сбросить"} width={"20px"} height={"20px"} cursor={"remove"}
                onClickFunc={() => {
                        setTypeOfCursor(2);
                        // TODO function to unzoom to first view on planet
                    }
                }
            />
        </div>;

    return(toolbar)
}

export default Toolbar;
