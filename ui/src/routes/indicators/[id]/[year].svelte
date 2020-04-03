<script context="module">
	import {get} from 'svelte/store';
	import {csvParse} from 'd3-dsv';

	import {lookupStore} from 'app/stores';
	// import {lookup} from 'app/data/groups';

	export async function preload({ params: {id, year}, query }) {
		// const lookup = get(lookupStore);
		const indicator = lookup[id];

		// if (indicator.data) {
		//	 return Promise.resolve({id, year})
		// } else {
			return this.fetch(indicator.url)
				.then(r => r.text())
				.then(csvParse)
				.then(data => ({data, id, year}))
		// }
	}
</script>

<script>
	import * as _ from 'lamb';
	import {extent} from 'd3-array';
	import {format} from 'd3-format';
	import {scaleQuantize} from 'd3-scale';
	import {interpolateWarm} from 'd3-scale-chromatic';
	import ChoroplethDiv from '@svizzle/choropleth/src/ChoroplethDiv.svelte';
	import BarchartV from '@svizzle/barchart/src/BarchartV.svelte';
	import {
		applyFnMap,
		getValue,
		inclusiveRange,
		keyValueArrayToObject
	} from '@svizzle/utils';

	import yearlyKeyToLabel from 'app/data/NUTS2_UK_labels';
	import {lookup} from 'app/data/groups';
	import topos from 'app/data/topojson';
	import {availableYearsStore, selectedYearStore} from 'app/stores';

	const getIndicatorFormat = id => _.pipe([
	  _.getPath(`${id}.schema.value`),
		_.condition(
			_.hasKey('format'),
			value => format(value.format),
			value => _.identity,
		)
  ])(lookup);

	const makeItemsWithId = id => _.pipe([
		_.mapWith(applyFnMap({
			key: _.getKey('nuts_id'),
			value: _.pipe([_.getKey(id), Number])
		})),
		_.sortWith([_.sorterDesc(getValue)])
	]);

	const colorRange = _.map(inclusiveRange([0, 1, 0.2]), interpolateWarm);
	let colorScale = scaleQuantize().range(colorRange);

	export let data;
	export let id;
	export let year;

	$: $selectedYearStore = Number(year);
	$: $availableYearsStore = inclusiveRange($lookupStore[id].year_range)
	$: data && lookupStore.update(_.setPath(`${id}.data`, data));
	$: description_short = $lookupStore[id].description_short;
	$: indicatorData = $lookupStore[id].data;
	$: yearData = indicatorData && indicatorData.filter(obj => obj.year === year);
	$: makeItems = makeItemsWithId(id);
	$: items = yearData && makeItems(yearData);
	$: nuts_year_spec = yearData && yearData[0].nuts_year_spec
	$: topojson = nuts_year_spec && topos[`NUTS_RG_03M_${nuts_year_spec}_4326_LEVL_2_UK`];
	$: keyToLabel = yearlyKeyToLabel[nuts_year_spec];
	$: formatFn = getIndicatorFormat(id);

	$: valueExtext = extent(items, getValue);
	$: colorScale = colorScale.domain([0, valueExtext[1]]);
	$: makeKeyToColor = _.pipe([
		keyValueArrayToObject,
		_.mapValuesWith(colorScale)
	]);
	$: keyToColor = makeKeyToColor(items);
</script>

<svelte:head>
	<title>BEIS indicators - {description_short}</title>
</svelte:head>

<main>
	<div class="distancer">
		<h1>{description_short} ({year})</h1>
	</div>
	<div class="col col1">
		{#if topojson}
		<ChoroplethDiv
			{keyToColor}
			{topojson}
			colorDefaultFill='lightgrey'
			colorStroke='black'
			key='NUTS_ID'
			projection='geoEqualEarth'
			sizeStroke=0.5
			topojsonId='NUTS'
		/>
		{/if}
	</div>
	<div class="col col2">
		<BarchartV
			{formatFn}
			{items}
			{keyToColor}
			{keyToLabel}
		/>
	</div>
</main>

<style>
	main {
		display: grid;
		grid-template-columns: 65% 35%;
		grid-template-rows: 3rem calc(100% - 3rem);
		height: 100%;
		width: 100%;
	}

	.distancer {
		margin-bottom: 1rem;
	}

	h1 {
		grid-column: 1 / span 2;
		grid-row: 1 / span 1;
		margin: 0;
		width: 100%;
	}

	.col {
		grid-row: 2 / span 1;
		padding: var(--dim-padding-minor);
	}
	.col1 {
		grid-column: 1 / span 1;
		overflow-y: auto;
	}

	.col2 {
		grid-column: 2 / span 1;
		/* border-left: 1px solid var(--color-main); */
	}
</style>
