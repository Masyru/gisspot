import React  from "react";
const port = ":8000";
const url = "ws://localhost" + port;

export const {Provider, Consumer} = React.createContext({});

export default class WebSocketViewer extends React.Component{
    constructor(props) {
        super(props);
        this.state = {
            arrayData: [],
            lastGotData: {},
        };

        this.wb = null;
    }

    componentDidMount() {

        this.wb = new WebSocket(url + '/ws');
        // listen to onmessage event
        this.wb.onmessage = event => {
          // add the new message to state
            this.setState({
                arrayData : [...this.state.arrayData, event.data],
                lastGotData: event.data,
            })
        };

        // for testing purposes: sending to the echo service which will send it back back
        setInterval( _ => {
            this.wb.send( String(Math.random()) )
        }, 2000 )
    }

    render() {
        return(
            <Provider value=
                          {{arrayData: this.state.arrayData,
                                lastGotData: this.state.lastGotData}}
            >
                {this.props.children}
            </Provider>
        );
    }
}

