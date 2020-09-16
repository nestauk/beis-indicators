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
	import {geoEqualEarth as projectionFn} from 'd3-geo';
	import {writable} from 'svelte/store';
	import {topoToGeo, defaultGeometry} from '@svizzle/choropleth/src/utils';
	import ChoroplethG from '@svizzle/choropleth/src/ChoroplethG.svelte';
	import ColorBinsG from '@svizzle/legend/src/ColorBinsG.svelte';
	import BarchartVDiv from '@svizzle/barchart/src/BarchartVDiv.svelte';
	import {makeStyle, toPx} from '@svizzle/dom';
	import {
		applyFnMap,
		getValue,
		inclusiveRange,
		keyValueArrayAverage,
		keyValueArrayToObject,
		mergeObj,
	} from '@svizzle/utils';

	import {feature} from 'topojson-client';

	import GeoFilterModal from 'app/components/GeoFilterModal.svelte';
	import InfoModal from 'app/components/InfoModal/InfoModal.svelte';
	import IconChevronDown from 'app/components/icons/IconChevronDown.svelte';
	import IconChevronUp from 'app/components/icons/IconChevronUp.svelte';
	import IconGlobe from 'app/components/icons/IconGlobe.svelte';
	import IconInfo from 'app/components/icons/IconInfo.svelte';
	import Switch from 'app/components/Switch.svelte';
	import {lookup} from 'app/data/groups';
	import yearlyKeyToLabel from 'app/data/NUTS2_UK_labels';
	import {
		availableYearsStore,
		doFilterRegionsStore,
		geoModalStore,
		hideInfoModal,
		infoModalStore,
		lookupStore,
		nutsSelectionStore,
		preselectedNUTS2IdsStore,
		resetSafetyStore,
		selectedNUT2IdsStore,
		selectedYearStore,
		toggleGeoModal,
		toggleInfoModal,
	} from 'app/stores';
	import majorCities from 'app/data/majorCities';
	import topos from 'app/data/topojson';
	import types from 'app/data/types';
	import {
		getIndicatorFormat,
		getNutsId,
		getRefFormat,
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

	const defaultGray = '#f3f3f3';
	const markerRadius = 4;
	const labelsFontSize = 13;
	const labelPadding = labelsFontSize / 2;
	const labelDx = markerRadius + labelPadding;
	const legendBarThickness = 40;
	const topojsonId = 'NUTS'; // TODO pass this via data when we'll have LEPs

	let selectedKeys = [];

	$: legendHeight = height / 3;
	$: choroplethSafety = {...defaultGeometry, left: legendBarThickness * 2};
	$: id && year && hideInfoModal();
	$: $selectedYearStore = Number(year);
	$: formatFn = getIndicatorFormat(id, lookup);
	$: refFormatFn = getRefFormat(id, lookup);
	$: getIndicatorValue = makeValueAccessor(id);
	$: $availableYearsStore = inclusiveRange(year_extent);
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
		warning,
		year_extent,
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
	$: filteredItems = _.filter(items, ({key}) =>
		_.isIn($selectedNUT2IdsStore, key) || _.isIn($preselectedNUTS2IdsStore, key)
	);
	$: refs = [{
		key: 'National average',
		keyAbbr: 'Nat. avg.',
		value: keyValueArrayAverage(items),
		formatFn: refFormatFn
	}];

	// colors
	$: valueExtext = extent(data, getIndicatorValue);
	$: colorScale = makeColorScale(valueExtext);
	$: colorBins = makeColorBins(colorScale);
	$: makeKeyToColor = _.pipe([
		keyValueArrayToObject,
		_.mapValuesWith(colorScale)
	]);
	$: keyToColorAll = makeKeyToColor(items);
	$: keyToColorFiltered = makeKeyToColor(filteredItems);

	// map
	$: nuts_year_spec = yearData && yearData[0].nuts_year_spec
	$: keyToLabel = nuts_year_spec && yearlyKeyToLabel[nuts_year_spec];
	$: topojson =
		nuts_year_spec && topos[`NUTS_RG_03M_${nuts_year_spec}_4326_LEVL_2_UK`];
	$: baseGeojson = topojson && topoToGeo(topojson, topojsonId);
	$: featuresIndex = baseGeojson &&
		_.index(baseGeojson.features, _.getPath('properties.NUTS_ID'));
	$: filteredGeojson = baseGeojson && _.setPathIn(baseGeojson, 'features',
		_.reduce(selectedKeys, (acc, key) => {
			featuresIndex[key] && acc.push(featuresIndex[key]);
			return acc;
		}, [])
	);
	$: choroplethInnerHeight =
		height - choroplethSafety.top - choroplethSafety.bottom;
	$: choroplethInnerWidth =
		width - choroplethSafety.left - choroplethSafety.right;
	$: baseProjection = baseGeojson &&
		projectionFn()
		.fitSize([choroplethInnerWidth, choroplethInnerHeight], baseGeojson);
	$: filterProjection =
		filteredGeojson &&
		filteredGeojson.features.length &&
		projectionFn()
		.fitSize([choroplethInnerWidth, choroplethInnerHeight], filteredGeojson);
	$: projection = $doFilterRegionsStore ? filterProjection : baseProjection;

	// focus
	$: selectedKeys = $preselectedNUTS2IdsStore.concat($selectedNUT2IdsStore)
	$: focusedKey = $tooltip.isVisible ? $tooltip.regionId : undefined;

	// cities
	$: cities = selectedKeys.length > 0 && _.map(majorCities, obj => {
		const [x, y] = projection([obj.lng, obj.lat]);
		const X = x + choroplethSafety.left;
		const length = obj.name.length * labelsFontSize * 0.6;
		const isLeft =
			obj.isLeft && X - labelDx - length < choroplethSafety.left
				? false
				: X + labelDx + length > width - choroplethSafety.right
					? true
					: obj.isLeft;
		const dx = isLeft ? -labelDx : labelDx;
		const dy = obj.isBottom ? 2 * markerRadius : obj.isTop ? -2 * markerRadius : 0;

		return {
			...obj,
			dx,
			dy,
			isLeft,
			X,
			Y: y + choroplethSafety.top,
		}
	});

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
	const onEnteredRegion = ({detail: regionId}) => {
		const hasValue = _.has(keyToValue, regionId);
		const shouldShowValue = $doFilterRegionsStore
			? _.isIn(selectedKeys, regionId)
			: true;

		const value = shouldShowValue && hasValue
			? formatFn(keyToValue[regionId]) + (labelUnit ? ` ${labelUnit}` : '')
			: undefined;

		tooltip.update(mergeObj({
			isVisible: true,
			regionId,
			nuts_label: keyToLabel[regionId],
			style: makeTooltipStyle(event),
			value
		}))
	};
	const onExitedRegion = ({detail}) => {
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
		focusedKey = focusedBarKey;
	}
	const onExitedBar = ({detail: {id: focusedBarKey}}) => {
		focusedKey = null;
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
		<div on:click={toggleInfoModal}>
			<IconInfo
				size=30
				strokeWidth=1.5
			/>
		</div>
	</header>

	<section>
		<div class='controls'>
			<div class='optgroup'>
				<div
					class='globe clickable'
					on:click={toggleGeoModal}
				>
					<IconGlobe strokeWidth={1.5} size={28} />
					{#if $geoModalStore.isVisible}
					<IconChevronUp strokeWidth={1} size={24} />
					{:else}
					<IconChevronDown strokeWidth={1} size={24} />
					{/if}
				</div>

				<Switch
					initial={$doFilterRegionsStore ? 'Filter' : 'Highlight'}
					values={['Highlight', 'Filter']}
					on:toggled={event => {
						$doFilterRegionsStore = event.detail === 'Filter'
					}}
				/>
			</div>
		</div>

		<div class='geodistro'>

		<!-- col1 -->
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
				<ChoroplethG
					{focusedKey}
					{height}
					{projection}
					{selectedKeys}
					{topojson}
					{topojsonId}
					{width}
					geometry={{left: choroplethSafety.left}}
					isInteractive={true}
					key='NUTS_ID'
					keyToColor={$doFilterRegionsStore ? keyToColorFiltered : keyToColorAll}
					on:entered={onEnteredRegion}
					on:exited={onExitedRegion}
					theme={{
						defaultFill: defaultGray,
						defaultStroke: 'gray',
						defaultStrokeWidth: 0.25,
						focusedStroke: 'dodgerblue',
						focusedStrokeWidth: 1.5,
						selectedStroke: 'black',
						selectedStrokeWidth: 0.5,
					}}
				/>

				<!-- cities -->
				{#if cities}
				<g class='cities'>
					{#each cities as {isLeft, name, X, Y, dx, dy}}
						<g transform='translate({X},{Y})'>
							<circle r={markerRadius}/>
							<text
								{dx}
								{dy}
								class:isLeft
								class='background'
								font-size={labelsFontSize}
							>{name}</text>
							<text
								{dx}
								{dy}
								class:isLeft
								font-size={labelsFontSize}
							>{name}</text>
						</g>
					{/each}
				</g>
				{/if}

				<!-- legend -->
				<g transform='translate(0,{legendHeight})'>
					<ColorBinsG
						width={legendBarThickness}
						height={legendHeight}
						bins={colorBins}
						flags={{
							isVertical: true,
							withBackground: true,
						}}
						theme={{
							backgroundColor: 'white',
							backgroundOpacity: 0.5,
						}}
						ticksFormatFn={formatFn}
					/>
				</g>
			</svg>
			{/if}

			<!-- tooltip -->
			{#if $tooltip.isVisible}
			<div
				class="tooltip"
				style={$tooltip.style}
			>
				<header>
					<span>{$tooltip.regionId}</span>
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

		<!-- col2 -->
		<div class="col col2">
			<BarchartVDiv
				{focusedKey}
				{formatFn}
				{keyToLabel}
				{refs}
				{selectedKeys}
				isInteractive={true}
				items={$doFilterRegionsStore ? filteredItems : items}
				keyToColor={keyToColorAll}
				on:entered={onEnteredBar}
				on:exited={onExitedBar}
				shouldResetScroll={true}
				shouldScrollToFocusedKey={true}
				theme={{
					barDefaultColor: defaultGray,
					focusedKeyColor: 'rgb(211, 238, 253)',
					titleFontSize: '1.2rem',
				}}
				title={barchartTitle}
			/>
		</div>

		<!-- geo modal -->
		{#if $geoModalStore.isVisible}
		<GeoFilterModal
			{nutsSelectionStore}
			on:click={toggleGeoModal}
		/>
		{/if}

		</div>

		{#if $infoModalStore.isVisible}
		<InfoModal
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
			{year_extent}
			{warning}
			on:click={toggleInfoModal}
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
		display: grid;
		grid-template-columns: 100%;
		grid-template-rows: 4rem calc(100% - 4rem);
		height: calc(100% - var(--indicators-h1-height));
		overflow-y: auto;
		position: relative;
		width: 100%;
	}

	.controls {
		align-items: center;
		display: flex;
		height: 100%;
		justify-content: space-between;
		width: 100%;
	}

	.controls > div:not(:last-child) {
		margin-right: 0.5rem;
	}

	.globe {
		border: 1px solid lightgrey;
		margin-right: 0.25rem;
		padding: 0.25rem;
	}
	.optgroup {
		display: flex;
		align-items: center;
		padding: 0.25rem;
	}

	.geodistro {
		display: grid;
		grid-template-columns: 65% 35%;
		grid-template-rows: 100%;
		height: 100%;
		overflow-y: auto;
		position: relative;
		width: 100%;
	}

	.col {
		padding: var(--dim-padding-minor);
	}
	.col1 {
		grid-column: 1 / span 1;
		overflow-y: hidden;
		position: relative;
	}

	.col2 {
		grid-column: 2 / span 1;
	}


	:global(.col2 .BarchartVDiv header h2) {
		margin-bottom: 1rem;
	}

	/* cities */

	.cities {
		pointer-events: none;
	}
	.cities circle {
		fill: white;
		stroke: black;
	}
	.cities text {
		dominant-baseline: middle;
		fill: black;
		stroke: none;
	}
	.cities text.isLeft {
		text-anchor: end;
	}
	.cities text.background {
		fill: white;
		fill-opacity: 0.8;
		stroke: white;
		stroke-opacity: 0.8;
		stroke-width: 4;
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
