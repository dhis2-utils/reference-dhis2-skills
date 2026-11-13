const globals = require("globals");
const js = require("@eslint/js");

module.exports = [
    js.configs.recommended,
    {
        languageOptions: {
            globals: {
                ...globals.browser,
                require: "readonly",
                __dirname: "readonly",
                process: "readonly",
                module: "readonly",
                DHIS_CONFIG: "readonly",
            },
            ecmaVersion: 2021,
            sourceType: "module"
        },
        rules: {
            indent: ["error", 4],
            quotes: ["error", "double"],
            semi: ["error", "always"],
            "no-console": "off"
        }
    }
];
