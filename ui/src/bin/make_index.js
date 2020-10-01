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
import {tapMessage, tapWith} from '@svizzle/dev';
import {applyFnMap, isKeyOf, transformValues} from '@svizzle/utils';

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
}
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

const makeNeedsFormat = types => _.pipe([
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

const run = async () => {
	const types = await readFile(TYPES_PATH, 'utf-8').then(yaml.safeLoad);
	const needsFormat = makeNeedsFormat(types);

	// FIXME use a proper walker
	const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
	const refs = await Promise.all(
		_.map(dirNames, dirName =>
			readDir(path.resolve(DATA_DIR, dirName))
			.then(_.pipe([
				_.filterWith(_.allOf([isYamlFile, isNotNuts3File, isNotLepFile])),
				_.mapWith(applyFnMap({
					filepath: makePath(dirName),
					url: makeCsvUrl,
				}))
			]))
		)
	);
	const indicatorsGroups = await Promise.all(
		_.flatten(refs)
		.map(({filepath, url}) =>
			Promise.all([
				readFile(filepath, 'utf-8')
				.then(yaml.safeLoad)
				.then(tapWith([needsFormat, `needsFormat? ${filepath}`]))
				.then(setUrl(url)),

				readCsv(yamlToCsvPath(filepath), transformValues({year: Number}))
				.then(csv => extent(csv, _.getKey('year')))
			])
			.then(([spec, year_extent]) => _.setIn(spec, 'year_extent', year_extent))
		)
	).then(_.groupBy(_.getKey('framework_group')));

	const framework =
		await readJson(FRAMEWORK_PATH).then(_.sortWith([_.getKey('order')]));

	const index = _.map(framework, group => ({
		...group,
		indicators: indicatorsGroups[group.id]
	})).filter(obj => obj.indicators !== undefined);

	console.log(index);

	await saveIndex(index).then(tapMessage(`Saved ${GROUPS_PATH}`));
}

run().then(tapMessage('Done'))
