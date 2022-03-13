//Bundles all our Javascript code into one file 

const path = require("path");
const webpack = require("webpack");

// Take all Js files and output here 
module.exports = {
  entry: "./src/index.js",

  //Gets current directory we are in (frontend), and put into static/frontend folder as [name].js
  output: {
    path: path.resolve(__dirname, "./static/frontend"),
    filename: "[name].js",
  },

  //Exclude bundling the node_modules folder and use the babel-loader 
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
        },
      },
    ],
  },

  // Takes JS and minimizes it so it loads in browser quick and efficiently 
  optimization: {
    minimize: true,
  },

  //Optimizes also
  plugins: [
    new webpack.DefinePlugin({
      "process.env": {
        // This has effect on the react lib size
        NODE_ENV: JSON.stringify("production"),
      },
    }),
  ],
};