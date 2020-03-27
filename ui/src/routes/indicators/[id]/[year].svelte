<script context="module">
	import {get} from 'svelte/store';
	import {csvParse} from 'd3-dsv';

	import {lookupStore} from 'app/stores';

	const log = x => console.log(`indicators/[id]/[year].svelte: ${x} =`, x);

	export async function preload({ params: {id, year}, query }) {
		log('year, id', id, year);

		const lookup = get(lookupStore);
		const indicator = lookup[id];
		log('indicator.data', indicator.data);

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

	import ChoroplethDiv from '@svizzle/choropleth/src/ChoroplethDiv.svelte';
	import BarchartV from '@svizzle/barchart/src/BarchartV.svelte';
	import {applyFnMap, getValue} from '@svizzle/utils';

	import yearlyKeyToLabel from 'app/data/NUTS2_UK_labels';
	import topos from 'app/data/topojson';
	import {availableYearsStore, selectedYearStore} from 'app/stores';
	import {inclusiveRange} from 'app/utils';

	const makeItemsWithId = id => _.pipe([
		_.mapWith(applyFnMap({
			key: _.getKey('nuts_id'),
			value: _.pipe([_.getKey(id), Number])
		})),
		_.sortWith([_.sorterDesc(getValue)])
	]);

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
			{topojson}
			colorDefaultFill='lightgrey'
			colorStroke='black'
			projection='geoEqualEarth'
			sizeStroke=0.5
			topojsonId='NUTS'
		/>
		<!-- key='NUTS_ID' -->
		<!-- {keyToColor} -->
		{/if}
	</div>
	<div class="col col2">
		<BarchartV
			{items}
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

	.distancer {
		margin-bottom: 1rem;
	}

	.row {
		display: flex;
		align-items: center;
		width: 100%;
		height: 2rem;
		margin-bottom: 1rem;
	}

	.row span:nth-child(1) {
		flex: 0 0 15%;
	}
	.row span:nth-child(2) {
		flex: 1;
	}

	button {
		padding: 0.5rem;
		margin-right: 0.5rem;
		font-size: 1.05rem;
	}

	button.active {
		background-color: var(--color-main);
		color: white;
		outline: 0 none; /* used for accessibility FIXME */
	}

	pre {
		width: 100%;
	}

	.col2 {
		grid-column: 2 / span 1;
		/* border-left: 1px solid var(--color-main); */
	}
</style>
