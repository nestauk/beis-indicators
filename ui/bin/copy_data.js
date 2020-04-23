#!/usr/bin/env node -r esm

import path from 'path';

import * as _ from 'lamb';
import cpy from 'cpy';
import {readDir} from '@svizzle/file';
import {tapMessage} from '@svizzle/dev';

const DATA_DIR = path.resolve(__dirname, '../../ds/data/processed');
const DATA_DIR_STATIC = path.resolve(__dirname, '../static/data');

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const isCsvFile = name => path.parse(name).ext === '.csv';
const isNotNuts3File = name => !path.parse(name).name.endsWith('.nuts3');
const makePath = dirName => filename => path.resolve(
  DATA_DIR,
  dirName,
  filename
);

const process = async () => {
  // FIXME use a proper walker
  const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
  const refs = await Promise.all(
    _.map(dirNames, dirName =>
      readDir(path.resolve(DATA_DIR, dirName))
      .then(_.pipe([
        _.filterWith(_.allOf([isCsvFile, isNotNuts3File])),
        _.mapWith(makePath(dirName))
      ]))
    )
  )
  .then(_.flatten);

  await cpy(refs, DATA_DIR_STATIC);
}

process().then(tapMessage(`Copied data to ${DATA_DIR_STATIC}`))
