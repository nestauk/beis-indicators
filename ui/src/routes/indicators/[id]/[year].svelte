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
	import {writable} from 'svelte/store';
	import ChoroplethDiv from '@svizzle/choropleth/src/ChoroplethDiv.svelte';
	import BarchartV from '@svizzle/barchart/src/BarchartV.svelte';
	import {
		applyFnMap,
		getValue,
		inclusiveRange,
		keyValueArrayToObject,
		mergeObj
	} from '@svizzle/utils';
	import {makeStyle, toPx} from '@svizzle/dom';

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

	const getNutsId = _.getKey('nuts_id');

	const makeValueAccessor = id => _.pipe([_.getKey(id), Number]);
	const makeItemsWithId = id => _.pipe([
		_.mapWith(applyFnMap({
			key: getNutsId,
			value: makeValueAccessor(id)
		})),
		_.sortWith([_.sorterDesc(getValue)])
	]);

	const colorRange = _.map(inclusiveRange([0, 1, 0.2]), interpolateWarm);
	let colorScale = scaleQuantize().range(colorRange);
	let selectedKeys = [];

	export let data;
	export let id;
	export let year;
	export let width;
	export let height;

	$: $selectedYearStore = Number(year);
	$: getIndicatorValue = makeValueAccessor(id);
	$: $availableYearsStore = inclusiveRange($lookupStore[id].year_range)
	$: data && lookupStore.update(_.setPath(`${id}.data`, data));
	$: description_short = $lookupStore[id].description_short;
	$: indicatorData = $lookupStore[id].data;
	$: yearData = indicatorData && indicatorData.filter(obj => obj.year === year);
	$: makeKeyToValue = _.pipe([
		_.indexBy(getNutsId),
		_.mapValuesWith(getIndicatorValue)
	]);
	$: keyToValue = yearData && makeKeyToValue(yearData);

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
	$: focusedKey = $tooltip.isVisible ? $tooltip.nuts_id : undefined;
	$: selectedKeys = $tooltip.isVisible ? [$tooltip.nuts_id] : [];

	const tooltip = writable({isVisible: false});

	const makeTooltipStyle = event => {
		const x = event.offsetX < width / 2
		 	? {key: 'left', value: event.offsetX + 20}
			: {key: 'right', value: width - event.offsetX + 10};
		const y = event.offsetY < height / 2
		 	? {key: 'top', value: event.offsetY + 20}
			: {key: 'bottom', value: height - event.offsetY + 10};

		return makeStyle({
			[x.key]: toPx(x.value),
			[y.key]: toPx(y.value),
			visibility: 'visible'
		});
	}
	const onEntered = event => {
		tooltip.update(mergeObj({
			isVisible: true,
			nuts_id: event.detail,
			nuts_label: keyToLabel[event.detail],
			style: makeTooltipStyle(event),
			value: keyToValue[event.detail]
				? formatFn(keyToValue[event.detail])
				: undefined
		}))
	};
	const onExited = ({detail}) => {
		tooltip.update(mergeObj({
			isVisible: false,
			style: 'visibility: hidden'
		}));
	};
	const onMousemoved = event => {
		$tooltip.isVisible && tooltip.update(mergeObj({
			style: makeTooltipStyle(event),
		}));
	};

	const onEnteredBar = ({detail: {id: focusedBarKey}}) => {
		selectedKeys = [focusedBarKey];
	}
	const onExitedBar = ({detail: {id: focusedBarKey}}) => {
		selectedKeys = [];
	}
</script>

<svelte:head>
	<title>BEIS indicators - {description_short}</title>
</svelte:head>

<main>
	<div class="distancer">
		<h1>{description_short} ({year})</h1>
	</div>
	<div
		class="col col1"
		on:mousemove={onMousemoved}
		bind:clientWidth={width}
		bind:clientHeight={height}
	>
		{#if topojson}
		<ChoroplethDiv
			{keyToColor}
			{selectedKeys}
			{topojson}
			colorDefaultFill='lightgrey'
			colorStroke='black'
			isInteractive={true}
			key='NUTS_ID'
			on:entered={onEntered}
			on:exited={onExited}
			projection='geoEqualEarth'
			sizeStroke=0.5
			topojsonId='NUTS'
		/>
		{/if}
		{#if $tooltip.isVisible}
		<div
			class="tooltip"
			style={$tooltip.style}
		>
			<header>
				<span>{$tooltip.nuts_id}</span>
				{#if $tooltip.value}
				<span>{$tooltip.value}</span>
				{/if}
			</header>
			<div>
				<span>{$tooltip.nuts_label}</span>
			</div>
		</div>
		{/if}
	</div>
	<div class="col col2">
		<BarchartV
			{focusedKey}
			{formatFn}
			{items}
			{keyToColor}
			{keyToLabel}
			focusedKeyColor='rgb(196, 236, 255)'
			isInteractive={true}
			on:entered={onEnteredBar}
			on:exited={onExitedBar}
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
		position: relative;
	}

	.col2 {
		grid-column: 2 / span 1;
	}

	.tooltip {
		position: absolute;
		pointer-events: none;
		border: 1px solid black;
		background-color: white;
		color: black;
	}
	.tooltip header {
		background-color: var(--color-grey-40);
		color: white;
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0.3rem;
	}
	.tooltip header span:nth-child(1) {
		margin-right: 1rem;
	}
	.tooltip div {
		display: flex;
		align-items: center;
		padding: 0.3rem;
	}
</style>
