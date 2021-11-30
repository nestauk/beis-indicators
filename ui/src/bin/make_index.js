#!/usr/bin/env node -r esm

import path from 'path';

import * as _ from 'lamb';
import yaml from 'js-yaml';
import {extent} from 'd3-array';
import {
	readDir,
	readCsv,
	readFile,
	readJson,
	saveObj
} from '@svizzle/file';
import {tapMessage} from '@svizzle/dev';
import {
	applyFnMap,
	isIterableNotEmpty,
	isKeyOf,
	pickIfTruthy,
	transformValues,
} from '@svizzle/utils';

import {isNotLepFile, isNotNuts3File} from './utils';

const DS_DATA_REL_PATH = '../../../ds/data';
const DATA_DIR = path.resolve(__dirname, DS_DATA_REL_PATH, 'processed');
const TYPES_PATH = path.resolve(__dirname, DS_DATA_REL_PATH, 'schema/types.yaml');
const FRAMEWORK_PATH = path.resolve(__dirname, DS_DATA_REL_PATH, 'aux/framework.json');
const GROUPS_PATH =
	path.resolve(__dirname, '../node_modules/app/data/indicatorsGroups.json');

const saveIndex = saveObj(GROUPS_PATH, 2);
const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const isYamlFile = name => path.parse(name).ext === '.yaml';
const makePath = dirName => filename => path.resolve(
	DATA_DIR,
	dirName,
	filename
);
const makeCsvUrl = filename => {
	const {name} = path.parse(filename);

	return `/data/${name}.csv`;
};
const setUrl = url => obj => _.setIn(obj, 'url', url);
const yamlToCsvPath = filepath => filepath.replace('.yaml', '.csv')

const isFloatNoFormat = obj =>
	!obj.format &&
	obj.data_type &&
	obj.data_type === 'float';

const datatypeIsNotInt = obj =>
	obj.data_type &&
	obj.data_type !== 'int';

const hasNoDatatype = _.not(_.hasKey('data_type'));

const makeAvailableYears = _.pipe([_.pluck('year'), _.uniques]);

const makeGroups = _.pipe([
	_.groupBy(_.getKey('framework_group')),
	_.mapValuesWith(_.sortWith([_.getKey('title')]))
]);

/* utils to check specs */

// utils to check missing `format`

const makeTypeIsFloatNoFormat = types => _.allOf([
	_.not(_.hasKey('format')),
	_.hasKey('type'),
	_.pipe([
		_.getKey('type'),
		_.allOf([
			isKeyOf(types),
			_.pipe([
				type => types[type].data_type,
				data_type => data_type.includes('float'),
			]),
		]),
	]),
]);

const makeDoesSpecNeedFormat = types => _.pipe([
	_.getPath('schema.value'),
	_.anyOf([
		isFloatNoFormat,
		_.allOf([
			hasNoDatatype,
			makeTypeIsFloatNoFormat(types),
		]),
		_.allOf([
			datatypeIsNotInt,
			makeTypeIsFloatNoFormat(types),
		]),
	])
]);

const makeGetMissingFormatLog = doesSpecNeedFormat => _.pipe([
	_.reduceWith(
		(acc, spec) => {
			const doesSpecMissFormat = doesSpecNeedFormat(spec);

			if (doesSpecMissFormat) {
				acc.push(`-- id: ${spec.schema.value.id}`);
			}

			return acc;
		},
		[]
	),
	_.joinWith('\n')
]);

const getMissingFormatReport = async indicatorsSpecs => {
	const types = await readFile(TYPES_PATH, 'utf-8').then(yaml.safeLoad);
	const doesSpecNeedFormat = makeDoesSpecNeedFormat(types);
	const getMissingFormatLog = makeGetMissingFormatLog(doesSpecNeedFormat);
	const missingFormatReport = getMissingFormatLog(indicatorsSpecs);

	return missingFormatReport;
};

// utils to check the copy length

const maxLengths = {
	subtitle: 140,
	title: 60,
};
const getLongCopyKeys = _.pipe([
	applyFnMap({
		subtitle: s => s.subtitle && s.subtitle.length > maxLengths.subtitle,
		title: s => s.title && s.title.length > maxLengths.title,
	}),
	pickIfTruthy,
	_.keys,
]);

const getLongCopyReport = _.pipe([
	_.reduceWith(
		(acc, spec) => {
			const buggedCopyKeys = getLongCopyKeys(spec);

			if (isIterableNotEmpty(buggedCopyKeys)) {
				acc.push(`-- id: ${spec.schema.value.id}`);

				_.forEach(buggedCopyKeys, key => {
					spec[key] && acc.push(` |- ${key}: ${spec[key].length}`)
				})
			}

			return acc;
		},
		[]
	),
	_.joinWith('\n')
]);

// report and exit if some specs are malformed

const reportBadSpecs = async indicatorsSpecs => {
	console.log('\n=> Checking missing `format` specs...');
	const missingFormatReport = await getMissingFormatReport(indicatorsSpecs);
	console.log(missingFormatReport);

	console.log('\n=> Checking copy lengths...');
	const longCopyReport = getLongCopyReport(indicatorsSpecs);
	console.log(longCopyReport);

	if (isIterableNotEmpty(missingFormatReport + longCopyReport)) {
		console.log('\n=> Errors, please checking the specs!');

		// eslint-disable-next-line no-process-exit
		process.exit(1);
	}
};

/* run */

const run = async () => {

	/* read file paths */

	// FIXME use a proper walker
	const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
	const refs = await Promise.all(
		_.map(dirNames, dirName =>
			readDir(path.resolve(DATA_DIR, dirName))
			.then(_.pipe([
				_.filterWith(_.allOf([isYamlFile, isNotNuts3File, isNotLepFile])),
				_.mapWith(applyFnMap({
					specFilepath: makePath(dirName),
					url: makeCsvUrl,
				}))
			]))
		)
	);

	/* read specs */

	const indicatorsSpecs = await Promise.all(
		_.flatten(refs)
		.map(({specFilepath, url}) =>
			Promise.all([
				readFile(specFilepath, 'utf-8')
				.then(yaml.safeLoad)
				.then(setUrl(url)),

				readCsv(yamlToCsvPath(specFilepath), transformValues({year: Number}))
				.then(csvData => ({
					year_extent: extent(csvData, _.getKey('year')),
					availableYears: makeAvailableYears(csvData)
				}))
			])
			.then(([spec, {year_extent, availableYears}]) =>
				_.merge(spec, {year_extent, availableYears})
			)
		)
	);

	/* exit if we encounter errors in the specs */

	await reportBadSpecs(indicatorsSpecs);

	/* process the rest */

	// groups

	const indicatorsGroups = makeGroups(indicatorsSpecs);

	// framework

	const framework =
		await readJson(FRAMEWORK_PATH).then(_.sortWith([_.getKey('order')]));

	const index =
		_.map(framework, group => ({
			...group,
			indicators: indicatorsGroups[group.id]
		}))
		.filter(obj => obj.indicators !== undefined);

	// console.log(index);

	await saveIndex(index).then(tapMessage(`Saved ${GROUPS_PATH}`));

	console.log('Done');
};

run();
