import {babel} from '@rollup/plugin-babel';
import commonjs from '@rollup/plugin-commonjs';
import dsv from '@rollup/plugin-dsv';
import json from '@rollup/plugin-json';
import resolve from '@rollup/plugin-node-resolve';
import replace from '@rollup/plugin-replace';
import cleanup from "rollup-plugin-cleanup";
import svelte from 'rollup-plugin-svelte';
import {terser} from 'rollup-plugin-terser';
import yaml from '@rollup/plugin-yaml';

import config from 'sapper/config/rollup.js';
import pkg from './package.json';

const mode = process.env.NODE_ENV;
const isExported = process.env.SAPPER_EXPORT;
const dev = mode === 'development';
const legacy = Boolean(process.env.SAPPER_LEGACY_BUILD);
const removeComments = cleanup({
	extensions: ['js', 'mjs']
});

const onwarn = (warning, _onwarn) => {
	const doRun =
		warning.code === 'MISSING_EXPORT' &&
			(/'preload'/u).test(warning.message) ||

		warning.code === 'CIRCULAR_DEPENDENCY' &&
			(/[/\\]@sapper[/\\]/u).test(warning.message) ||

		warning.code !== 'CIRCULAR_DEPENDENCY';

	return doRun && _onwarn(warning)
};

export default {
	client: {
		input: config.client.input(),
		output: config.client.output(),
		preserveEntrySignatures: false,
		plugins: [
			replace({
				'process.browser': true,
				'process.env.NODE_ENV': JSON.stringify(mode),
				'process.env.SAPPER_EXPORT': JSON.stringify(isExported)
			}),
			svelte({
				compilerOptions: {
					dev,
					hydratable: true,
				},
				emitCss: true,
			}),
			resolve({
				// browser: true,
				dedupe: ['svelte']
			}),
			commonjs(),
			dsv(),
			json(),
			yaml(),
			removeComments,

			legacy && babel({
				babelHelpers: 'runtime',
				exclude: ['node_modules/@babel/**'],
				extensions: ['.js', '.mjs', '.html', '.svelte'],
				plugins: [
					'@babel/plugin-syntax-dynamic-import',
					['@babel/plugin-transform-runtime', {
						useESModules: true
					}]
				],
				presets: [
					['@babel/preset-env', {
						targets: '> 0.25%, not dead'
					}]
				],
			}),

			!dev && terser({
				module: true
			})
		],

		onwarn,
	},

	server: {
		input: config.server.input(),
		output: config.server.output(),
		preserveEntrySignatures: false,
		plugins: [
			replace({
				'process.browser': false,
				'process.env.NODE_ENV': JSON.stringify(mode),
				'process.env.SAPPER_EXPORT': JSON.stringify(isExported)
			}),
			svelte({
				compilerOptions: {
					generate: 'ssr',
					dev,
				},
			}),
			resolve({
				dedupe: ['svelte']
			}),
			commonjs(),
			dsv(),
			json(),
			yaml(),
			removeComments,
		],
		external:
			Object.keys(pkg.dependencies)
			.filter(name => ![
				'@svizzle/barchart',
				'@svizzle/choropleth',
				'@svizzle/utils',
			].includes(name))
			.concat(
				require('module').builtinModules ||
				Object.keys(process.binding('natives'))
			),

		onwarn,
	},

	serviceworker: {
		input: config.serviceworker.input(),
		output: config.serviceworker.output(),
		preserveEntrySignatures: false,
		plugins: [
			resolve(),
			replace({
				'process.browser': true,
				'process.env.NODE_ENV': JSON.stringify(mode),
				'process.env.SAPPER_EXPORT': JSON.stringify(isExported)
			}),
			commonjs(),
			dsv(),
			json(),
			yaml(),
			removeComments,
			!dev && terser()
		],

		onwarn,
	}
};
