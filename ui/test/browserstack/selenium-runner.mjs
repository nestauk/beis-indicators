import fs from 'fs/promises';
import path from 'path';
import * as _ from 'lamb';

import fetch from 'node-fetch';
import Queue from 'queue-promise';
import webdriver from 'selenium-webdriver';

import {capitalize} from '@svizzle/utils';
import * as options from './options.mjs';

// import {environments} from './environments.mjs';

const {until, By} = webdriver;

const username = process.env.BROWSERSTACK_USERNAME;
const key = process.env.BROWSERSTACK_ACCESS_KEY;
const localIdentifier = process.env.BROWSERSTACK_LOCAL_IDENTIFIER;
const projectName = process.env.BROWSERSTACK_PROJECT_NAME;
const buildName = process.env.BROWSERSTACK_BUILD_NAME;
const timeout = (promise, time, exception) => {
	let timer;
	return Promise.race([
		promise,
		new Promise((_resolve, reject) => 
			timer = setTimeout(reject, time, exception)
		)
	]).finally(() => clearTimeout(timer));
}
const browsersUrl = 'api.browserstack.com/5/browsers?flat=true';
async function getBrowsers () {
	const response = await fetch(`https://${username}:${key}@${browsersUrl}`);
	return response.json();
}

const url = 'hub-cloud.browserstack.com/wd/hub';
const tests = 'test/browserstack/scripts/automate';
const target = 'http://localhost:3000';
const report = 'test/data/selenium-report.json';
const browserstackURL = `https://${username}:${key}@${url}`;
const optionsKey = 'bstack:options';
const results = [];

// utilities
function buildHeader (capabilities) {
	const logHeader = [];
	const isMobile = Boolean(capabilities.device);
	logHeader.push(capabilities.device || capabilities[optionsKey].os);
	if (isMobile) {
		logHeader.push(capabilities.deviceOrientation);
	} else {
		logHeader.push(capabilities[optionsKey].osVersion);
		logHeader.push(capabilities.resolution);
	}
	logHeader.push(capabilities.browserName);
	logHeader.push(capabilities.browserVersion);
	return logHeader.join('-');
}
function log (capabilities, ...message) {
	console.log(buildHeader(capabilities), ...message);
}
function err (capabilities, error) {
	console.error(buildHeader(capabilities), error)
}

function fail (driver, message) {
	// TODO notify faliure
}

const TIMEOUT_ERROR = Symbol();
async function run (test, capabilities) {
	let driver;
	try {
		driver = await new webdriver.Builder()
		.usingServer(browserstackURL)
		.withCapabilities(capabilities)
		.build();

		const testResult = await timeout(
			test({
				capabilities,
				driver,
				By,
				until,
				target,
				fail: (...message) => fail(driver, ...message),
				log: (...message) => log(capabilities, ...message)
			}),
			60000,
			TIMEOUT_ERROR
		);

		return testResult
	} catch (e) {
		if (e === TIMEOUT_ERROR) {
			e = 'Timeout!'
		}
		err(capabilities, e);
		return {
			passed: false,
			exception: e,
			trace: e.stack
		};
	} finally {
		driver && driver.quit();
	}
}

// Task runner
// 1. initialize task runner
const queue = new Queue({
	concurrent: 5,
	interval: 20000
});

queue.on('end', async () =>{
	await fs.writeFile(report, JSON.stringify(results, null, 2));
	console.log('Done!');
});

function runTest (caps, tasks) {
	const platform = {
		capabilities: caps,
		results: []
	};
	results.push(platform);
	tasks.forEach(async ([id, task]) => {
		const doTest = extra => async () => {
			const output = await run(task, {
				...caps,
				...extra
			});
			platform.results.push({
				id,
				result: output
			});
		};
		if (caps.device) {
			queue.enqueue(doTest({deviceOrientation: 'portrait'}));
			queue.enqueue(doTest({deviceOrientation: 'landscape'}));
		} else {
			const {os, osVersion} = caps[optionsKey];
			const resolutionsByOsVersions = options.operatingSystems[os];
			const resolutions = resolutionsByOsVersions[osVersion];
			resolutions.forEach(resolution => {
				queue.enqueue(doTest({resolution}));
			});
		}
	});
}

// 2. load and run tests
async function runAll() {
	// 2a. Get filtered capabilities through Browserstack API
	const devicesCaps = await getBrowsers();
	// const devicesCaps = environments;

	// 2b. Convert to Selenium 4 format
	const s4caps = devicesCaps.map(deviceCaps => ({
		device: deviceCaps.device,
		browserName: capitalize(deviceCaps.browser),
		browserVersion: deviceCaps.browser_version,
		[optionsKey]: {
			os: deviceCaps.os,
			osVersion: deviceCaps.os_version,
			consoleLogs: 'errors',
			local: true,
			localIdentifier,
			projectName,
			buildName
		}
	})).filter(caps => {
		if (caps.device) {
			return true;
		}
		const minV = parseFloat(options.minVersions[caps.browserName]);
		const currV = parseFloat(caps.browserVersion);
		return minV < currV;
	}).filter(caps =>
		[
			'Chrome',
			'Safari',
			'Firefox',
			'Edge',
			'Android Browser',
			'Mobile Safari'
		].includes(caps.browserName)
	);
	console.log('Configurations:', s4caps.length);

	const files = await fs.readdir(tests);

	const modulePromises = files.map(file => import(path.resolve(tests, file)));
	const modules = (await Promise.all(modulePromises))
		.map(module => module.default);
	const tasks = _.zip(files, modules);
	console.log('Tests loaded:', modules.length);
	s4caps.forEach(caps => runTest(caps, tasks));
}

runAll();
