import React, { Component } from "react";
import { render } from "react-dom";
import HomePage from './HomePage';

// Main component that returns something put the component in a div in index.html
export default class App extends Component {
    constructor(props) {
        super(props);

        // Store state on our components, define all stateful aspects we want to store
        // When state of compent modified will automatically re render the entire component 
        // Ex. when database updates and we need to re-render the website 
        //this.state = {

        //}
    }

    render() {
        // {this.props.name} embeds JS code into our html text use {} to wrap
        return (
            <div className="center">
                <HomePage />
            </div>
        );
    }
}

// Access the app container in index.html
const appDiv = document.getElementById("app");

// Render the App component inside appDiv 
// Pass properties to the components
render(<App />, appDiv); 