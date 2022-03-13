import React, { Component } from "react";
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from './Room';
import { Grid, Button, ButtonGroup, Typography} from '@material-ui/core'
import { 
    BrowserRouter as Router,
    Switch, // Used to be "Switch", is now Routes
    Route, 
    Link, 
    Redirect,
} from "react-router-dom"
import Info from './Info';


export default class HomePage extends Component {
     constructor(props) {
         super(props);
         this.state = {
             roomCode: null,
         };
         this.clearRoomCode = this.clearRoomCode.bind(this);
     }

     // Async does something before it loads 
     //Component just rendered for the first time on the screen 
     // Asynchrous operation in componentDidMount 
     // if async not there, need to wait for everything to happen before doing anything else 
     async componentDidMount() {
         // Call api/user-in-room, returns room code if in room, get json from response, get json object and parse to get room code  
        fetch("/api/user-in-room")
            .then((response) => response.json())
            .then((data) => {
                this.setState({
                    roomCode: data.code, //Forces component to re-render
                });
            });
     }

     renderHomePage() {
         return (
            <Grid container spacing={3}>
                <Grid item xs={12} align="center">
                    {/* DISPLAY HOUSE PARTY */}
                    <Typography variant="h3" compact="h3">
                        House Party
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <ButtonGroup disableElevation variant="contained" color="primary">
                        {/* JOIN A ROOM BUTTON*/}
                        <Button color="primary" to='/join' component={ Link }>
                            Join a Room
                        </Button>
                        {/* CREATE A INFO BUTTON*/}
                        <Button color="default" to='/info' component={ Link }>
                            Info
                        </Button>
                        {/* CREATE A ROOM BUTTON*/}
                        <Button color="secondary" to='/create' component={ Link }>
                            Create a Room
                        </Button>
                    </ButtonGroup>
                </Grid>
            </Grid>
         );
     }

     // Set the states so our room code is empty 
     clearRoomCode() {
        this.setState({
            roomCode: null,
        });
     }


     render() {
         return (
         <Router>
            <Switch>
                <Route 
                    exact 
                    path='/' 
                    render={() => {
                        // Redirect user to room session if active session
                        return this.state.roomCode ? (
                            <Redirect to={`/room/${this.state.roomCode}`} />
                        ) : (
                            this.renderHomePage()
                        );
                    }}
                />
                <Route path='/join' component={RoomJoinPage} />
                <Route path='/info' component={Info} />
                <Route path='/create' component={CreateRoomPage} />
                <Route 
                    path="/room/:roomCode"
                    render={(props) => {
                        return <Room {...props} leaveRoomCallback={this.clearRoomCode} />;
                    }}
                />
            </Switch>
         </Router>
        );
     }
}