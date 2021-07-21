import fs from 'fs';
import * as _ from 'lamb';
import pa11y from 'pa11y';
import htmlReporter from 'pa11y-reporter-html';
import Queue from 'queue-promise';

import {lighthouseUrls, urlBases} from '../../src/node_modules/app/config';

const queue = new Queue({
	concurrent: 1
});

queue.on('end', () => {
	console.log('Done!');
});

const auditURL = async (id, url) => {
	const options = {
		standard: 'WCAG2AAA'
	};
	const runnerResult = await pa11y(
		urlBases.development + url,
		options
	);
	const reportHtml = await htmlReporter.results(runnerResult, url);

	// eslint-disable-next-line no-sync
	fs.writeFileSync(`static/audits/pa11y/${id}.html`, reportHtml);

	// `.lhr` is the Lighthouse Result as a JS object
	console.log(
		'Report is done for',
			runnerResult.pageUrl
	);
	console.log(
		'Issues found:',
		runnerResult.issues.length
	);
}

const enqueueTask = ([id, url]) =>
	queue.enqueue(async () => await auditURL(id, url));

const auditUrls = _.pipe([
	_.pairs,
	_.mapWith(enqueueTask)
]);

auditUrls(lighthouseUrls);
