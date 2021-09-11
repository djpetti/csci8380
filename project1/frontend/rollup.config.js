import {terser} from "rollup-plugin-terser";
import resolve from '@rollup/plugin-node-resolve';
import commonjs from "@rollup/plugin-commonjs";
import json from "@rollup/plugin-json";
import nodePolyfills from 'rollup-plugin-node-polyfills';
import sourcemaps from "rollup-plugin-sourcemaps";
import scss from "rollup-plugin-scss";

export default {
    input: 'build/index.js',
    output: [
        {
            file: 'bundled/project1.js',
            sourcemap: true,
            format: 'esm',
        },
        {
            file: 'bundled/project1.min.js',
            format: 'iife',
            name: 'version',
            plugins: [terser({
                module: true,
                warnings: true,
                mangle: {
                    properties: {
                        regex: /^__/,
                    },
                },
            }),
            ],
        },
    ],
    onwarn(warning) {
        if (warning.code !== 'THIS_IS_UNDEFINED') {
            console.error(`(!) ${warning.message}`);
        }
    },
    plugins: [sourcemaps(), commonjs(), nodePolyfills(), resolve(), json(),
        scss({sass: require('sass')})],
};
