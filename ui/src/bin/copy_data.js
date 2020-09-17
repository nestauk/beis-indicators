#!/usr/bin/env node -r esm

import path from 'path';

import yaml from 'js-yaml';
import {readCsv, readDir, readFile, saveString} from '@svizzle/file';
import {tapMessage} from '@svizzle/dev';
import { applyFnMap, transformValues } from '@svizzle/utils';
import {zip} from 'zip-a-folder';
import {csvFormat} from 'd3-dsv';
import * as _ from 'lamb';
import cpy from 'cpy';
import del from 'del';
import tempy from 'tempy';

import {allIndicatorsCsvName, zipName} from 'app/utils';
import NUTS2_UK_labels from 'app/data/NUTS2_UK_labels';

import {isNotLepFile, isNotNuts3File} from './utils';

const DS_DATA_REL_PATH = '../../../ds/data';
const DATA_DIR = path.resolve(__dirname, DS_DATA_REL_PATH, 'processed');
const TYPES_PATH = path.resolve(__dirname, DS_DATA_REL_PATH, 'schema/types.yaml');
const DATA_DIR_STATIC = path.resolve(__dirname, '../../static/data');

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const isCsvFile = name => path.parse(name).ext === '.csv';
const makePath = dirName => filename => path.resolve(
	DATA_DIR,
	dirName,
	filename
);
const csvToYamlPath = filepath => filepath.replace('.csv', '.yaml');

const run = async () => {

	/* delete the data dir */

	await del([DATA_DIR_STATIC]);

	/* copy the indicator files */

	// FIXME use a proper walker
	const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
	const csvFilepaths = await Promise.all(
		_.map(dirNames, dirName =>
			readDir(path.resolve(DATA_DIR, dirName))
			.then(_.pipe([
				_.filterWith(_.allOf([isCsvFile, isNotNuts3File, isNotLepFile])),
				_.mapWith(makePath(dirName))
			]))
		)
	)
	.then(_.flatten);

	await cpy(csvFilepaths, DATA_DIR_STATIC);

	/* make a single indicators file */

	const specs = await Promise.all(
		csvFilepaths.map(csvFilepath =>
			readFile(csvToYamlPath(csvFilepath), 'utf-8')
			.then(string =>
				_.setPathIn(yaml.safeLoad(string), 'csvFilepath', csvFilepath)
			)
		)
	);

	const types = await readFile(TYPES_PATH).then(yaml.safeLoad);
	const tmpAllIndicatorsCsvPath = tempy.file({name: allIndicatorsCsvName});

	await Promise.all(
		specs.map(spec =>
			readCsv(spec.csvFilepath, transformValues({
				[spec.order[0]]: Number,
				[spec.order[2]]: Number,
				[spec.schema.value.id]: Number,
			}))
			.then(_.mapWith(applyFnMap({
				id: () => spec.schema.value.id,
				year: _.getKey('year'),
				nuts_id: _.getKey('nuts_id'),
				nuts_year_spec: _.getKey('nuts_year_spec'),
				nuts_name: obj => NUTS2_UK_labels[obj.nuts_year_spec][obj.nuts_id],
				value: _.getKey(spec.schema.value.id),
				unit_string: _.adapter([
					_.getKey(spec.schema.value.unit_string),
					() => spec.schema.value.type &&
						types[spec.schema.value.type] &&
						types[spec.schema.value.type].unit_string,
					_.always('')
				]),
				description_short: () => spec.description_short,
				description: () => spec.description,
			})))
		)
	)
	.then(_.flatten)
	.then(csvFormat)
	.then(saveString(tmpAllIndicatorsCsvPath));

	await cpy(tmpAllIndicatorsCsvPath, DATA_DIR_STATIC);

	/* zip them all */

	const tmpZipPath = tempy.file({name: zipName});
	await zip(DATA_DIR_STATIC, tmpZipPath);
	await cpy(tmpZipPath, DATA_DIR_STATIC);
}

run().then(tapMessage(`Copied data to ${DATA_DIR_STATIC}`));
