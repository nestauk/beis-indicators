<script context="module">
	export function preload({ params: {id, year}, query }) {
		return this.fetch(lookup[id].url)
			.then(r => r.text())
			.then(parseCSV(id))
			.then(data => ({data, id, year}))
	}
</script>

<script>
	import * as _ from 'lamb';
	import {extent} from 'd3-array';
	import {writable} from 'svelte/store';
	import ChoroplethDiv from '@svizzle/choropleth/src/ChoroplethDiv.svelte';
	import BarchartVDiv from '@svizzle/barchart/src/BarchartVDiv.svelte';
	import {makeStyle, toPx} from '@svizzle/dom';
	import {
		applyFnMap,
		getValue,
		inclusiveRange,
		keyValueArrayToObject,
		mergeObj
	} from '@svizzle/utils';

	import Modal from 'app/components/Modal.svelte';
	import IconInfo from 'app/components/icons/IconInfo.svelte';
	import {lookup} from 'app/data/groups';
	import yearlyKeyToLabel from 'app/data/NUTS2_UK_labels';
	import {
		availableYearsStore,
		lookupStore,
		modalStore,
		resetModal,
		resetSafetyStore,
		selectedYearStore,
		toggleModal,
	} from 'app/stores';
	import topos from 'app/data/topojson';
	import types from 'app/data/types';
	import {
		getIndicatorFormat,
		getNutsId,
		makeColorScale,
		makeValueAccessor,
		parseCSV,
	} from 'app/utils';

	resetSafetyStore();

	export let data;
	export let id;
	export let year;
	export let width;
	export let height;

	let selectedKeys = [];

	$: id && year && resetModal();
	$: $selectedYearStore = Number(year);
	$: formatFn = getIndicatorFormat(id, lookup);
	$: getIndicatorValue = makeValueAccessor(id);
	$: $availableYearsStore = inclusiveRange(year_range);
	$: data && lookupStore.update(_.setPath(`${id}.data`, data));
	$: ({
		api_doc_url,
		api_type,
		auth_provider,
		data_date,
		description_short,
		description,
		endpoint_url,
		is_public,
		query,
		region,
		schema,
		source_name,
		source_url,
		url,
		year_range,
	} = $lookupStore[id] || {});

	$: labelUnit =
		schema.value.unit_string ||
		schema.value.type &&
		_.has(types, schema.value.type) &&
		_.has(types[schema.value.type], 'unit_string') &&
		types[schema.value.type].unit_string;
	$: barchartTitle = schema.value.label + (labelUnit ? ` [${labelUnit}]` : '');

	// $: indicatorData = $lookupStore[id].data;
	$: yearData = data && data.filter(obj => obj.year === year);
	$: makeKeyToValue = _.pipe([
		_.indexBy(getNutsId),
		_.mapValuesWith(getIndicatorValue)
	]);
	$: keyToValue = yearData && makeKeyToValue(yearData);

	$: makeItems = _.pipe([
		_.mapWith(applyFnMap({
			key: getNutsId,
			value: getIndicatorValue
		})),
		_.sortWith([_.sorterDesc(getValue)])
	]);
	$: items = yearData && makeItems(yearData);
	$: nuts_year_spec = yearData && yearData[0].nuts_year_spec
	$: topojson = nuts_year_spec && topos[`NUTS_RG_03M_${nuts_year_spec}_4326_LEVL_2_UK`];
	$: keyToLabel = yearlyKeyToLabel[nuts_year_spec];

	$: valueExtext = extent(data, getIndicatorValue);
	$: colorScale = makeColorScale(valueExtext);
	$: makeKeyToColor = _.pipe([
		keyValueArrayToObject,
		_.mapValuesWith(colorScale)
	]);
	$: keyToColor = makeKeyToColor(items);
	$: focusedKey = $tooltip.isVisible ? $tooltip.nuts_id : undefined;
	$: selectedKeys = $tooltip.isVisible ? [$tooltip.nuts_id] : [];

	/* map tooltip */

	const tooltip = writable({isVisible: false});

	const makeTooltipStyle = event => {
		const {layerX: X, layerY: Y} = event;

		const x = X < width / 2
		 	? {key: 'left', value: X + 20}
			: {key: 'right', value: width - X + 10};
		const y = Y < height / 2
		 	? {key: 'top', value: Y + 20}
			: {key: 'bottom', value: height - Y + 10};

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
			value: _.has(keyToValue, event.detail)
				? formatFn(keyToValue[event.detail])
					+ (labelUnit ? ` ${labelUnit}` : '')
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

	/* barchart hovering */

	const onEnteredBar = ({detail: {id: focusedBarKey}}) => {
		selectedKeys = [focusedBarKey];
	}
	const onExitedBar = ({detail: {id: focusedBarKey}}) => {
		selectedKeys = [];
	}
</script>

<svelte:head>
	<title>BEIS indicators - {description_short} ({year})</title>
</svelte:head>

<div class='container'>
	<header>
		<div>
			<h1>{description_short} ({year})</h1>
			<p>{description}</p>
		</div>
		<div on:click={toggleModal}>
			<IconInfo
				size=30
				strokeWidth=1.5
			/>
		</div>
	</header>
	<section>
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
			<BarchartVDiv
				{focusedKey}
				{formatFn}
				{items}
				{keyToColor}
				{keyToLabel}
				focusedKeyColor='rgb(196, 236, 255)'
				isInteractive={true}
				on:entered={onEnteredBar}
				on:exited={onExitedBar}
				shouldResetScroll={true}
				shouldScrollToFocusedKey={true}
				title={barchartTitle}
			/>
		</div>
		{#if $modalStore.isVisible}
		<Modal
			{api_doc_url}
			{api_type}
			{auth_provider}
			{data_date}
			{endpoint_url}
			{is_public}
			{query}
			{region}
			{source_name}
			{source_url}
			{url}
			{year_range}
			on:click={toggleModal}
		/>
		{/if}
	</section>
</div>

<style>
	.container {
		--indicators-h1-height: 4.5rem;
		height: 100%;
		width: 100%;
		user-select: none;
	}

	.container > header {
		height: var(--indicators-h1-height);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.container > header div:nth-child(1) {
		flex: 1;
	}
	.container > header div:nth-child(1) h1 {
		margin: 0;
	}
	.container > header div:nth-child(1) p {
		font-style: italic;
		font-size: 1rem;
		color: grey;
	}
	.container > header div:nth-child(2) {
		display: flex;
		align-items: center;
		justify-content: space-between;
		cursor: pointer;
	}

	section {
		height: calc(100% - var(--indicators-h1-height));
		width: 100%;
		overflow-y: auto;
		display: grid;
		grid-template-columns: 65% 35%;
		grid-template-rows: 100%;
		position: relative;
	}

	.col {
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

	:global(.col2 .BarchartVDiv header h2) {
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	/* tooltip */

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
