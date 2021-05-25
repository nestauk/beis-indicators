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

import {basename} from 'app/utils/assets';
import LEP_UK_labels from 'app/data/LEP_UK_labels';
import NUTS2_UK_labels from 'app/data/NUTS2_UK_labels';
import NUTS3_UK_labels from 'app/data/NUTS3_UK_labels';

import {
	isNotLepFile,
	isLepFile,
	isNotNuts3File,
	isNuts3File
} from './utils';

const DS_DATA_REL_PATH = '../../../ds/data';
const DATA_DIR = path.resolve(__dirname, DS_DATA_REL_PATH, 'processed');
const TYPES_PATH = path.resolve(__dirname, DS_DATA_REL_PATH, 'schema/types.yaml');
const DATA_DIR_STATIC = path.resolve(__dirname, '../../static/data');
const UK_REGIONS_LABELS = {
	NUTS2: NUTS2_UK_labels,
	NUTS3: NUTS3_UK_labels,
	LEP: LEP_UK_labels,
};

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const isCsvFile = name => path.parse(name).ext === '.csv';
const makePath = dirName => filename => path.resolve(
	DATA_DIR,
	dirName,
	filename
);
const csvToYamlPath = filepath => filepath.replace('.csv', '.yaml');

const makeSingleFileWith = async (condition, regionType) => {
	const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
	const csvFilepaths = await Promise.all(
		_.map(dirNames, dirName =>
			readDir(path.resolve(DATA_DIR, dirName))
			.then(_.pipe([
				_.filterWith(condition),
				_.mapWith(makePath(dirName))
			]))
		)
	)
	.then(_.flatten);

	const specs = await Promise.all(
		csvFilepaths.map(csvFilepath =>
			readFile(csvToYamlPath(csvFilepath), 'utf-8')
			.then(string =>
				_.setPathIn(yaml.safeLoad(string), 'csvFilepath', csvFilepath)
			)
		)
	);

	const types = await readFile(TYPES_PATH).then(yaml.safeLoad);
	const tmpAllIndicatorsCsvPath = tempy.file({
		name: `${basename}_${regionType}.csv`
	});

	await Promise.all(
		specs.map(spec => {
			const [yearHeader, regionIdHeader, regionYearSpecHeader,] = spec.order;

			return readCsv(spec.csvFilepath, transformValues({
				[yearHeader]: Number,
				[regionYearSpecHeader]: Number,
				[spec.schema.value.id]: Number,
			}))
			.then(_.mapWith(applyFnMap({
				indicator_id: () => spec.schema.value.id,
				title: () => spec.title,
				year: _.getKey(yearHeader),
				region_id: _.getKey(regionIdHeader),
				region_year_spec: _.getKey(regionYearSpecHeader),
				region_name: obj => {
					const yearSpec = regionType === 'LEP' && obj[regionYearSpecHeader] < 0
						? 2014
						: obj[regionYearSpecHeader];

					return UK_REGIONS_LABELS[regionType][yearSpec][obj[regionIdHeader]]
				},
				value: _.getKey(spec.schema.value.id),
				unit: _.adapter([
					_.always(spec.schema.value.unit_string),
					() => spec.schema.value.type &&
						types[spec.schema.value.type] &&
						types[spec.schema.value.type].unit_string,
					_.always('')
				]),
				subtitle: () => spec.subtitle,
			})))
		})
	)
	.then(_.flatten)
	.then(csvFormat)
	.then(saveString(tmpAllIndicatorsCsvPath));

	await cpy(tmpAllIndicatorsCsvPath, DATA_DIR_STATIC);
}


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

	/* make an all-indicators single file */

	await makeSingleFileWith(
		_.allOf([isCsvFile, isNotNuts3File, isNotLepFile]),
		'NUTS2'
	);

	/* zip them all */

	const tmpZipPath = tempy.file({name: `${basename}.zip`});
	await zip(DATA_DIR_STATIC, tmpZipPath);
	await cpy(tmpZipPath, DATA_DIR_STATIC);

	/* make remaining all-indicators single files */

	await makeSingleFileWith(
		_.allOf([isCsvFile, isNuts3File]),
		'NUTS3'
	);

	await makeSingleFileWith(
		_.allOf([isCsvFile, isLepFile]),
		'LEP'
	);
}

run().then(tapMessage(`Updated data in ${DATA_DIR_STATIC}`));
