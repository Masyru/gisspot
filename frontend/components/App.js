import React, { useState } from "react";
import Toolbar, { FixRegion, ClearButton, PreviewInfo } from "./Toolbar";
import Timeline  from "./Timeline";
import PhotoPreview from "./PhotoPreview";
import { getViewer } from "../Cesium/Main";

const defaults = {
    lon1: null,
    lat1: null,
    lon2: null,
    lat2: null,
    firstPhoto: null,
    secondPhoto: null,
};

const Page = props => {
    let page = null;
    const [activePage, setActivePage] = useState(1);

    switch (activePage){
        case 1:
            // TODO: Func to stop fixing the zoom
            page = <FixRegion onClickFunc={setActivePage}/>;
            break;
        case 2:
            page =
                <>
                    <ClearButton
                        onClickFunc={() => {
                                setActivePage(1);
                                props.resetToDefaults();
                            }
                        }
                    />
                    <Timeline
                        nextPage={() => setActivePage(3)}
                        setPhoto={(obj) => props.setPhoto(1, obj)}
                    />
                </>;
            break;
        case 3:
            page =
                <>
                    <Toolbar />
                    <PreviewInfo returnToSecondPage={() => setActivePage(2)}/>
                    <Timeline
                        nextPage={() => setActivePage(4)}
                        setPhoto={(obj) => props.setPhoto(1, obj)}
                    />
                </>
            break;
        case 4:
            page = <PhotoPreview photos={props.photos}/>
            break;
    }

    return(page);
}

export default class App extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            lon1: null,
            lat1: null,
            lon2: null,
            lat2: null,
            firstPhoto: null,
            secondPhoto: null,
        };

        this.resetToDefaults = this.resetToDefaults.bind(this);
        this.setPhoto = this.setPhoto.bind(this);
    }

    setPhoto(which, obj){
        if (which === 1){
            this.setState({
                firstPhoto: obj,
            })
        } else if(which === 2){
            this.setState({
                secondPhoto: obj,
            })
        }
    }

    resetToDefaults(){
        this.setState(defaults);
    }

    render(){
        // App menu
        let app = <Page resetToDefaults={this.resetToDefaults} setPhoto={this.setPhoto} photos={this.state}/>;
        return(app);
    }
};
