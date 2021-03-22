const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    entry: {
        index: "./index.js",
    },
    output:{
        filename:"../static/js/[name].js",
        path: path.resolve()
    },
    module: {
        rules: [
            {
            test: /\.(js|jsx)$/,
            exclude: /node_modules/,
            loader: "babel-loader",
            options:{
              presets: ["@babel/preset-env", "@babel/preset-react"]
            }
            },
            {
            test: /\.css$/,
            exclude: /node_modules/,
            use: ['style-loader', 'css-loader']
            },
            {
                test: /\.s[ac]ss$/i,
                exclude: /node_modules/,
                use: ['style-loader', 'css-loader', 'sass-loader'],
            }
        ]
    },
    plugins: [
        new HtmlWebpackPlugin(),
    ]
};