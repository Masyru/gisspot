const path = require('path');

module.exports = {
    entry: {
        index: "./index.js",
    },
    output:{
        filename: './bundle/js/[name].js',
        path: path.resolve(),
    },
    module: {
        rules: [
            {
                test: /\.(png|svg|jpe?g|gif)$/i,
                exclude: /node_modules/,
                loader: 'file-loader',
                options: {
                    name: '[path][name].[ext]',
                },
            },
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
                loader: ['style-loader', 'css-loader'],
            },
            {
                test: /\.s[ac]ss$/i,
                exclude: /node_modules/,
                loader: ['style-loader', 'css-loader', 'sass-loader'],
            }
        ]
    },
};