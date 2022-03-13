import React, { Component } from "react";
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { Collapse } from "@material-ui/core";
import Alert from "@material-ui/lab/Alert"

export default class CreateRoomPage extends Component {
    static defaultProps ={
        votesToSkip: 2,
        guestCanPause: true,
        update: false,
        roomCode: null,
        updateCallback: () => {},
    };

     constructor(props) {
         super(props);

         // If we ever change state, it refreshed and causes component to update
         // When we hit Create Room button, look at current state and send info to backend to create the room 
         this.state = {
            guestCanPause: this.props.guestCanPause,
            votesToSkip: this.props.votesToSkip, //Set default values for the props 
            errorMsg: "",
            successMsg: "",
         };

         // Binds the method to the class 
         this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);
         this.handleVotesChange = this.handleVotesChange.bind(this);
         this.handleGuestCanPauseChange = this.handleGuestCanPauseChange.bind(this);
         this.handleUpdateButtonPressed = this.handleUpdateButtonPressed.bind(this);
     }

     // Handle when the number of votes changes 
     // Takes e, object that called function (text field)
     handleVotesChange(e) {
         // Use when we want to modify a state in react 
         this.setState({
             //Sets value in textfield to votesToSkip
             votesToSkip: e.target.value,
         });
     }

     // If the value is true, make guestCanPause true  
     handleGuestCanPauseChange(e) {
         this.setState({
             guestCanPause: e.target.value === 'true' ? true : false,
         });
     }

     // What happens when you press Create Room button 
     handleRoomButtonPressed() {
         const requestOptions = {
             method: "POST",
             headers: { "Content-Type": "application/json" },
             body: JSON.stringify({
                 votes_to_skip: this.state.votesToSkip,
                 guest_can_pause: this.state.guestCanPause, // Need to match what is in views.py
             }),
         };
         fetch("/api/create-room", requestOptions)
         .then((response) => response.json())
         .then((data) => this.props.history.push("/room/" + data.code)); //redirect user to room/roomcodenamehere
     }

    handleUpdateButtonPressed() {
        const requestOptions = {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                votes_to_skip: this.state.votesToSkip,
                guest_can_pause: this.state.guestCanPause, // Need to match what is in views.py
                code: this.props.roomCode
            }),
        };
        fetch("/api/update-room", requestOptions).then((response) => {
            if (response.ok) {
                this.setState({
                    successMsg: "Room updated successfully!",
                });
            } else {
                this.setState ({
                    errorMsg: "Error updating room...",
                });
            }
            this.props.updateCallback();
        });
    }

     renderCreateButtons() {
         return ( 
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Button 
                        color="primary" 
                        variant="contained" 
                        onClick={this.handleRoomButtonPressed}
                    >
                    Create A Room
                    </Button>
                </Grid>
                <Grid item xs={12} align="center">
                    <Button color="secondary" variant="contained" to="/" component={Link}>
                    Back
                    </Button>
                </Grid>
            </Grid>
         );
     }

     renderUpdateButtons() {
         return (
            <Grid item xs={12} align="center">
                <Button 
                    color="primary" 
                    variant="contained" 
                    onClick={this.handleUpdateButtonPressed}
                >
                Update Room
                </Button>
            </Grid>
         );
     }

     render() {
        const title = this.props.update ? "Update Room" : "Create a Room"

         return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Collapse in={this.state.errorMsg != "" || this.state.successMsg != ""}>
                        {this.state.successMsg != "" ? (
                            <Alert 
                                severity="success" 
                                onClose={() => {
                                this.setState({successMsg: "" }); //when we press x button, clear error message state
                                }}
                            >
                                {this.state.successMsg}
                            </Alert>
                        ) : (
                            <Alert 
                                severity="error" 
                                onClose={() => {
                                    this.setState({errorMsg: "" });
                                }}
                            >
                                {this.state.errorMsg}
                            </Alert>
                        )}
                    </Collapse>
                </Grid>
                <Grid item xs={12} align="center">
                    <Typography component='h4' variant='h4'>
                        {title}
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl component="fieldset"> 
                        <FormHelperText>
                            <div align="center">
                                Guest Control of Playback State
                            </div>
                        </FormHelperText>
                        <RadioGroup 
                            row 
                            defaultValue={this.props.guestCanPause.toString()}
                            onChange={this.handleGuestCanPauseChange}
                        >
                            <FormControlLabel value="true" 
                                control={<Radio color="primary" />}
                                label="Play/Pause"
                                labelPlacement="bottom" 
                            />
                            <FormControlLabel value="false" 
                                control={<Radio color="secondary" />}
                                label="No Control"
                                labelPlacement="bottom" 
                            />
                        </RadioGroup>
                    </FormControl>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField 
                            required={true} 
                            type="number" 
                            onChange={this.handleVotesChange} // when we modify textfield we update the state
                            defaultValue={this.state.votesToSkip}
                            inputProps={{
                                min: 1,
                                style: {textAlign: "center"},
                            }}
                        />
                        <FormHelperText>
                            <div align="center">
                                Votes Required to Skip Song
                            </div>
                        </FormHelperText>
                    </FormControl>
                </Grid>
                {this.props.update 
                    ? this.renderUpdateButtons() 
                    : this.renderCreateButtons()}
            </Grid>
         );    
     }
}