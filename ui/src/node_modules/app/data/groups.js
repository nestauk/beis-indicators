import {
	getYearExtent,
	makeIndicatorsLookup
} from '@svizzle/time_region_value/src/node_modules/utils/data';
import {inclusiveRange} from '@svizzle/utils';

import groups from './indicatorsGroups.json';

export const lookup = makeIndicatorsLookup(groups);
export const yearExtent = getYearExtent(groups);
export const yearRange = inclusiveRange(yearExtent);
