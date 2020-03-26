#!/usr/bin/env node -r esm

import path from 'path';

import * as _ from 'lamb';
import yaml from 'js-yaml';
import {readDir, readFile, readJson, saveObj} from '@svizzle/file';
import {tapMessage} from '@svizzle/dev';
import {applyFnMap} from '@svizzle/utils';

const DATA_DIR = path.resolve(__dirname, '../../ds/data/processed');
const FRAMEWORK_PATH = path.resolve(__dirname, '../../ds/data/aux/framework.json');
const GITHUB_RAW_BASEURL =
  'https://raw.githubusercontent.com/nestauk/beis-indicators/dev/ds/data/processed';
const GROUPS_PATH = path.resolve(__dirname, '../src/node_modules/app/data/indicatorsGroups.json');

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const isYaml = name => path.parse(name).ext === '.yaml';
const makePath = dirName => filename => path.resolve(
  DATA_DIR,
  dirName,
  filename
);
const makeCsvUrl = dirName => filename => {
  const {name} = path.parse(filename);

  return `${GITHUB_RAW_BASEURL}/${dirName}/${name}.csv`;
}
const setUrl = url => obj => _.setIn(obj, 'url', url);
const saveIndex = saveObj(GROUPS_PATH, 2);

const process = async () => {
  // FIXME use a proper walker
  const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
  const refs = await Promise.all(
    _.map(dirNames, dirName =>
      readDir(path.resolve(DATA_DIR, dirName))
      .then(_.pipe([
        _.filterWith(isYaml),
        _.mapWith(applyFnMap({
          filepath: makePath(dirName),
          url: makeCsvUrl(dirName),
        }))
      ]))
    )
  );
  const indicatorsGroups = await Promise.all(
    _.flatten(refs)
    .map(({filepath, url}) =>
      readFile(filepath, 'utf-8')
      .then(yaml.safeLoad)
      .then(setUrl(url))
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

process().then(tapMessage('Done'))
