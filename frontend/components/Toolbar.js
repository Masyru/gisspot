import React, { useState } from "react";
import "./Toolbar.css";


function Button(props){
    const butt =
        <button type={'button'} title={props.title} onClick={props.setType} disabled={props.active} >
                <img src={`/static/cursors/${props.cursor}.svg`} alt="" width={props.width} height={props.height}/>
        </button>;

    return butt;
}

export const Toolbar = () => {
    // TODO need to indicate typeOfCursor and turn another mode for editting the map
    const [typeOfCursor, setTypeOfCursor] = useState(0);

    const toolbar =
        <div className={"toolbar"}>
            <Button active={typeOfCursor === 0} title={"Выбрать курсор"} width={"15px"} height={"15px"} cursor={"compass-light"} setType={() => setTypeOfCursor(0)}/>
            <Button active={typeOfCursor === 1} title={"Выбрать регион"} width={"20px"} height={"20px"} cursor={"selection"} setType={() => {setTypeOfCursor(1)}}/>
            <Button active={typeOfCursor === 2} title={"Сбросить"} width={"20px"} height={"20px"} cursor={"remove"}
                setType={() => {
                        setTypeOfCursor(2);
                        // TODO function to unzoom to first view on planet
                    }
                }
            />
        </div>;

    return(toolbar)
}
