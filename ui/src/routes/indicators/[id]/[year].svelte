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
	import {geoEqualEarth} from 'd3-geo';
	import {writable} from 'svelte/store';
	import ChoroplethG from '@svizzle/choropleth/src/ChoroplethG.svelte';
	import ColorBinsG from '@svizzle/legend/src/ColorBinsG.svelte';
	import BarchartVDiv from '@svizzle/barchart/src/BarchartVDiv.svelte';
	import {makeStyle, toPx} from '@svizzle/dom';
	import {
		applyFnMap,
		getValue,
		inclusiveRange,
		keyValueArrayToObject,
		mergeObj
	} from '@svizzle/utils';

	import {feature} from 'topojson-client';
	import {setGeometryPrecision} from '@svizzle/geo';

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
	import majorCities from 'app/data/majorCities';
	import topos from 'app/data/topojson';
	import types from 'app/data/types';
	import {
		getIndicatorFormat,
		getNutsId,
		makeColorBins,
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

	const markerRadius = 4;
	const labelsFontSize = 13;
	const labelPadding = labelsFontSize / 2;
	const labelDx = markerRadius + labelPadding;
	const legendBarThickness = 40;
	const projection = geoEqualEarth();
	const topojsonId = 'NUTS'; // TODO pass this via data when we'll have LEPs

	/* TODO import {topoToGeo, defaultGeometry} from '@svizzle/choropleth/src/utils' @0.4.0 */
	const truncateGeojson = setGeometryPrecision(4);
	const topoToGeo = (topojson, id) =>
		truncateGeojson(feature(topojson, topojson.objects[id]));
	const defaultGeometry = {
		bottom: 10,
		left: 10,
		right: 10,
		top: 10,
	};

	let selectedKeys = [];

	$: legendHeight = height / 3;
	$: choroplethSafety = {...defaultGeometry, left: legendBarThickness * 2};
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
		description_long,
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
	$: keyToLabel = nuts_year_spec && yearlyKeyToLabel[nuts_year_spec];
	$: topojson =
		nuts_year_spec && topos[`NUTS_RG_03M_${nuts_year_spec}_4326_LEVL_2_UK`];
	$: geojson = topojson && topoToGeo(topojson, topojsonId);
	$: choroplethInnerHeight =
		height - choroplethSafety.top - choroplethSafety.bottom;
	$: choroplethInnerWidth =
		width - choroplethSafety.left - choroplethSafety.right;
	$: fitProjection =
		geojson &&
		projection.fitSize([choroplethInnerWidth, choroplethInnerHeight], geojson);
	$: places = _.map(majorCities, obj => {
		const [x, y] = fitProjection([obj.lng, obj.lat]);
		const X = x + choroplethSafety.left;
		const length = obj.name.length * labelsFontSize * 0.6;
		const isLeft =
			obj.isLeft && X - labelDx - length < choroplethSafety.left
				? isLeft = false
				: X + labelDx + length > width - choroplethSafety.right
					? true
					: obj.isLeft;
		const dx = isLeft ? -labelDx : labelDx;

		return {
			...obj,
			dx,
			isLeft,
			X,
			Y: y + choroplethSafety.top,
		}
	});

	$: valueExtext = extent(data, getIndicatorValue);
	$: colorScale = makeColorScale(valueExtext);
	$: colorBins = makeColorBins(colorScale);

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
			<svg
				{width}
				{height}
			>
				<!-- TODO /chropleth 0.4.0: projectionFn=fitProjection -->
				<ChoroplethG
					{height}
					{keyToColor}
					{selectedKeys}
					{topojson}
					{topojsonId}
					{width}
					geometry={{left: choroplethSafety.left}}
					isInteractive={true}
					key='NUTS_ID'
					on:entered={onEntered}
					on:exited={onExited}
					projection='geoEqualEarth'
					theme={{
						defaultFill: 'lightgrey',
						defaultStroke: 'black',
						defaultStrokeWidth: 0.5
					}}
				/>
				<g class='places'>
					{#each places as {isLeft, name, X, Y, dx}}
						<g transform='translate({X},{Y})'>
							<circle r={markerRadius}/>
							<text
								{dx}
								class:isLeft
								class='background'
								font-size={labelsFontSize}
							>{name}</text>
							<text
								{dx}
								class:isLeft
								font-size={labelsFontSize}
							>{name}</text>
						</g>
					{/each}
				</g>
				<g transform='translate(0,{legendHeight})'>
					<ColorBinsG
						width={legendBarThickness}
						height={legendHeight}
						bins={colorBins}
						flags={{isVertical: true}}
						ticksFormatFn={formatFn}
					/>
				</g>
			</svg>
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
			{description_long}
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

	/* TODO use `titleFontSize` with next @svizzle/barchart */
	:global(.col2 .BarchartVDiv header h2) {
		font-size: 1rem;
		margin-bottom: 1rem;
	}

	/* places */

	.places {
		pointer-events: none;
	}
	.places circle {
		fill: white;
		stroke: black;
	}
	.places text {
		dominant-baseline: middle;
		fill: black;
		stroke: none;
	}
	.places text.isLeft {
		text-anchor: end;
	}
	.places text.background {
		fill: white;
		fill-opacity: 0.8;
		stroke: white;
		stroke-opacity: 0.8;
		stroke-width: 5;
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
