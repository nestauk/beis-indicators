import sirv from 'sirv';
import polka from 'polka';
import compression from 'compression';
import * as sapper from '@sapper/server';

import {isDev} from 'app/config';

const { PORT } = process.env;

polka()
	.use(
		compression({ threshold: 0 }),
		sirv('static', { dev: isDev }),
		sapper.middleware()
	)
	.listen(PORT, err => {
		if (err) {
			console.log('error', err)
		}
	});
