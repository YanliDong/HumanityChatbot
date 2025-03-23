const path = require("path");
module.exports = {
    entry: "./static/chat-widget.jsx",
    output: {path: path.resolve(__dirname, "build")},
    mode: 'production',
    module: {
        rules: [
            {
                test: /.(js|jsx)$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader",
                    options: {
                        presets: ["@babel/preset-env", "@babel/preset-react"],
                    }
                },
            },
        ],
    },
};