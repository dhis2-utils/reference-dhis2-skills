"use strict";

const path = require("path");
const webpack = require("webpack");
const CopyWebpackPlugin = require("copy-webpack-plugin");
const HTMLWebpackPlugin = require("html-webpack-plugin");

require("dotenv").config();
var dhisConfig;
if (process.env.DHIS2_BASE_URL) {
    dhisConfig = { baseUrl: process.env.DHIS2_BASE_URL };
    if (process.env.DHIS2_API_TOKEN) {
        dhisConfig.authorization = `ApiToken ${process.env.DHIS2_API_TOKEN}`;
    } else if (process.env.DHIS2_USERNAME && process.env.DHIS2_PASSWORD) {
        dhisConfig.authorization = `Basic ${Buffer.from(`${process.env.DHIS2_USERNAME}:${process.env.DHIS2_PASSWORD}`).toString("base64")}`;
    } else {
        console.warn("\nWARNING! DHIS2_BASE_URL is set but no credentials found. Set DHIS2_API_TOKEN or DHIS2_USERNAME+DHIS2_PASSWORD in .env");
        dhisConfig.authorization = "";
    }
} else {
    console.warn("\nWARNING! No .env file found or DHIS2_BASE_URL not set. Using default localhost config.");
    dhisConfig = {
        baseUrl: "http://localhost:8080/dhis",
        authorization: "Basic YWRtaW46ZGlzdHJpY3Q=", // admin:district
    };
}

const devServerPort = 8081;

let cookie = ""; // Store cookie globally
async function fetchSessionCookie() {
    try {
        const response = await fetch(dhisConfig.baseUrl + "/api/me", {
            headers: {
                "Authorization": dhisConfig.authorization
            },
            credentials: "include"
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        // Extract and store JSESSIONID from the Set-Cookie header
        const setCookieHeader = response.headers.get("set-cookie");
        if (setCookieHeader) {
            const jsessionIdCookie = setCookieHeader.split(",").find(header => header.includes("JSESSIONID"));
            if (jsessionIdCookie) {
                cookie = jsessionIdCookie.split(";")[0]; // Get only the `JSESSIONID=value` part
                console.log("JSESSIONID cookie successfully set:", cookie);
            }
        }
    } catch (error) {
        console.error("Failed to fetch JSESSIONID cookie:", error.message);
    }
}

async function initialize() {
    await fetchSessionCookie();
    console.log("Initialization has completed.");
}

// Call the initialize function to start the process
if (process.env.WEBPACK_SERVE) {
    initialize();
}

module.exports = (env = {}) => {
    const isDevBuild = Boolean(env.WEBPACK_SERVE);
    const webpackConfig = {
        context: __dirname,
        entry: "./src/app.js",
        devtool: "source-map",
        output: {
            path: __dirname + "/build",
            filename: "[name]-[contenthash].js",
            publicPath: isDevBuild ? "http://localhost:8081/" : "./"
        },
        module: {
            rules: [
                {
                    test: /\.css$/,
                    use: ["style-loader", "css-loader"]
                },
                {
                    test: /\.html$/,
                    use: ["html-loader"]
                },
                {
                    test: /\.png$/,
                    type: "asset",
                    parser: { dataUrlCondition: { maxSize: 100000 } }
                },
                {
                    test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/,
                    type: "asset",
                    parser: { dataUrlCondition: { maxSize: 10000 } }
                },
                {
                    test: /\.(ttf|otf|eot|svg)(\?v=[0-9]\.[0-9]\.[0-9])?|(jpg|gif)$/,
                    type: "asset/resource"
                },
            ]
        },
        plugins: [
            new HTMLWebpackPlugin({
                template: "src/index.html"
            }),
            new CopyWebpackPlugin({
                patterns: [
                    { from: "./src/css", to: "css" },
                    { from: "./src/img", to: "img" },
                    { from: "./src/resources/dhis-header-bar.js", to: "resources" }
                ]
            }),
            new webpack.DefinePlugin({
                DHIS_CONFIG: JSON.stringify(isDevBuild ? dhisConfig : {}),
            }),
        ],
        devServer: {
            port: devServerPort,
            compress: true,
            proxy: [
                {
                    context: () => true,
                    target: dhisConfig.baseUrl,
                    secure: false,
                    changeOrigin: true,
                    headers: {
                        "Authorization": dhisConfig.authorization,
                    },
                    onProxyReq: (proxyReq) => {
                        if (cookie) {
                            proxyReq.setHeader("Cookie", cookie);
                        } else {
                            console.warn("No cookie found");
                        }
                    },
                    onProxyRes: (proxyRes) => {
                        const setCookieHeader = proxyRes.headers["set-cookie"];
                        if (setCookieHeader) {
                            const jsessionIdCookie = setCookieHeader.find(header => header.includes("JSESSIONID"));
                            if (jsessionIdCookie) {
                                cookie = jsessionIdCookie.split(";")[0];
                            }
                        }
                    }
                }
            ]
        },
        mode: isDevBuild ? "development" : "production"
    };
    return webpackConfig;
};
