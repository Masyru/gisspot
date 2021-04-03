import React  from "react";
const port = ":8000";
const url = "ws://localhost" + port + "/ws/";

export const {Provider, Consumer} = React.createContext({});

export default class WebSocketViewer extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            arrayData: [],
            lastGotData: {},
        };

        this.wb = new WebSocket(url);
        this.sendJsonOnServer = this.sendJsonOnServer.bind(this);
    }

    componentDidMount() {
        // listen to onmessage event
        this.wb.onmessage = event => {
            // add the new message to state
            event.preventDefault();
            this.setState({
                arrayData : [...this.state.arrayData, event.data],
                lastGotData: JSON.parse(event.data),
            });
        };
    }

    sendJsonOnServer(data){
        this.wb.send(JSON.stringify(data));
    }

    render() {
        return(
            <Provider value=
                          {{
                              arrayData: this.state.arrayData,
                              lastGotData: this.state.lastGotData,
                              sendData: this.sendJsonOnServer,
                          }}
            >
                { this.props.children }
            </Provider>
        );
    }
}

