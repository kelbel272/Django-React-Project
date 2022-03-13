// HELP PAGE
// Basic page that has 2 pages on the page
import React, { useState, useEffect } from "react";
import { Grid, Button, Typography, IconButton } from "@material-ui/core";
import NavigateBeforeIcon from "@material-ui/icons/NavigateBefore";
import NavigateNextIcon from "@material-ui/icons/NavigateNext";
import { Link } from "react-router-dom";

//Set up States 
const pages = {
    JOIN: "pages.join",
    CREATE: "pages.create",
};

export default function Info(props) {
    //Show JOIN page 
    const [page, setPage] = useState(pages.JOIN);

    function joinInfo() {
        return "Join page";
    }

    function createInfo() {
        return "Create page";
    }

    // Everything that happens in the body of this function, is what would happen if we hooked into the lifecycle methods componentWillUnmount & componentWillMount
    // Where we would call something that would happens/changes
    useEffect(() => {
        console.log("ran");
        return () => console.log("cleanup");
    });

    return (
    //CONTAINER FOR INFO PAGE
    <Grid container spacing={1}>
        {/* APP TITLE CONTAINER*/}
        <Grid item xs={12} align="center">
            {/* DISPLAY QUESTION */}
            <Typography component="h4" variant="h4">
                What is House Party?
            </Typography>
        </Grid>
        <Grid item xs={12} align="center">
            <Typography variant="body1">
                {/*  IF CURRENT PAGE IS pages.JOIN, call joinInfo PAGE IF NOT call createINFO PAGE*/}
                { page === pages.JOIN ? joinInfo() : createInfo() }
            </Typography>
        </Grid>
        <Grid item xs={12} align="center">
            <IconButton 
                onClick={() => {
                page === pages.CREATE ? setPage(pages.JOIN) : setPage(pages.CREATE);
                }}>
                     {/* DISPLAY ICON BASED ON WHAT PAGE WE ARE ON */}
                    {page === pages.CREATE ? <NavigateBeforeIcon/> : <NavigateNextIcon/>}
            </IconButton>
        </Grid>
        {/* BACK BUTTON CONTAINER*/}
        <Grid item xs={12} align="center">
            {/* DISPLAY BUTTON*/}
            <Button color="secondary" variant="contained" to="/" component={Link}>
                Back
            </Button>
        </Grid>
    </Grid>
    );
}
