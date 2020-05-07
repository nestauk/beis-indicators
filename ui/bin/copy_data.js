#!/usr/bin/env node -r esm

import path from 'path';

import {readDir} from '@svizzle/file';
import {tapMessage} from '@svizzle/dev';
import {zip} from 'zip-a-folder';
import * as _ from 'lamb';
import cpy from 'cpy';
import del from 'del';
import tempy from 'tempy';

import {isNotLepFile, isNotNuts3File} from './utils';
import {zipName} from '../src/node_modules/app/utils';

const DATA_DIR = path.resolve(__dirname, '../../ds/data/processed');
const DATA_DIR_STATIC = path.resolve(__dirname, '../static/data');

const isDir = name => !name.startsWith('.') && path.parse(name).ext === '';
const isCsvFile = name => path.parse(name).ext === '.csv';
const makePath = dirName => filename => path.resolve(
  DATA_DIR,
  dirName,
  filename
);

const process = async () => {

  /* delete the data dir */

  await del([DATA_DIR_STATIC]);

  /* copy the files */

  // FIXME use a proper walker
  const dirNames = await readDir(DATA_DIR).then(_.filterWith(isDir));
  const refs = await Promise.all(
    _.map(dirNames, dirName =>
      readDir(path.resolve(DATA_DIR, dirName))
      .then(_.pipe([
        _.filterWith(_.allOf([isCsvFile, isNotNuts3File, isNotLepFile])),
        _.mapWith(makePath(dirName))
      ]))
    )
  )
  .then(_.flatten);

  await cpy(refs, DATA_DIR_STATIC);

  /* zip them */

  const tmpZipPath = tempy.file({name: zipName});
  await zip(DATA_DIR_STATIC, tmpZipPath);
  await cpy(tmpZipPath, DATA_DIR_STATIC);
}

process().then(tapMessage(`Copied data to ${DATA_DIR_STATIC}`))
