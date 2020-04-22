<script context='module'>
	export function preload({ params: {id}, query }) {
		return this.fetch(lookup[id].url)
			.then(r => r.text())
			.then(parseCSV(id))
			.then(data => ({data, id}))
	}
</script>

<script>
	import {writable} from 'svelte/store';
	import * as _ from 'lamb';
	import {extent, max} from 'd3-array';
	import {quadtree} from 'd3-quadtree';
	import {scaleLinear} from 'd3-scale';
	import {line, curveMonotoneX} from 'd3-shape';
	import {makeStyle, toPx} from '@svizzle/dom';
	import {
		applyFnMap,
		inclusiveRange,
		mergeObj,
		objectToKeyValueArray,
		transformValues,
	} from '@svizzle/utils';

	import { goto } from '@sapper/app';

	import Modal from 'app/components/Modal.svelte';
	import IconInfo from 'app/components/icons/IconInfo.svelte';
	import { lookup, yearExtent, yearRange } from 'app/data/groups';
	import groups from 'app/data/indicatorsGroups.json';
	import yearlyKeyToLabel from 'app/data/NUTS2_UK_labels';
	import {
		availableYearsStore,
		lookupStore,
		modalStore,
		resetModal,
		resetSelectedYear,
		safetyStore,
		timelineLayoutStore,
		toggleModal,
	} from 'app/stores';
	import {
		getIndicatorFormat,
		getNutsId,
		makeColorScale,
		makeValueAccessor,
		parseCSV,
		setIndexAsKey,
		sortAscByYear,
	} from 'app/utils';

	const makeSetOrderWith = accessor => _.pipe([
		_.groupBy(_.getKey('year')),
		_.mapValuesWith(_.pipe([
			_.sortWith([_.sorterDesc(accessor)]),
			setIndexAsKey('order')
		])),
		_.values,
		_.flatten,
	]);

	const makeTrends = _.pipe([
		_.groupBy(getNutsId),
		_.mapValuesWith(sortAscByYear),
		objectToKeyValueArray
	]);
	const getOrder = _.getKey('order');

	const gap = 4;
	const labelSafety = 75;
	const tooltipFontSize = 10;
	const tooltipPadding = 5;
	const tooltipShift = 1.5 * tooltipPadding + 0.5 * tooltipFontSize;

  export let data;
	export let id;

	let height;
	let highlightedKey;
	let width;
	let useOrderScale = false;

	$: id && resetSelectedYear();
	$: id && resetModal();
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
		source_name,
		source_url,
		year_range,
	} = $lookupStore[id] || {});

	$: formatFn = getIndicatorFormat(id, lookup);
	$: $availableYearsStore = inclusiveRange(year_range)
	$: layout = $timelineLayoutStore;

	$: getIndicatorValue = makeValueAccessor(id);
	$: setOrder = makeSetOrderWith(getIndicatorValue);
	$: rankedData = setOrder(data);
	$: maxOrder = max(rankedData, getOrder);
	$: valueExtext = extent(data, getIndicatorValue);
	$: trends = makeTrends(rankedData);
	$: radius = Math.min(layout.radius, 0.5 * (height / maxOrder) - gap);
	$: yMin = radius + gap;
	$: yMax = height - radius - gap;
	$: scaleY = useOrderScale
		? scaleLinear().domain([0, maxOrder]).range([yMin, yMax])
		: scaleLinear().domain(valueExtext).range([yMax, yMin]);
	$: ticks = scaleY && scaleY.ticks().map(value => ({
		label: useOrderScale ? value : formatFn(value),
		y: scaleY(value)
	}));
	$: getX = d => layout.scaleX(d.year);
	$: getY = d => useOrderScale ? scaleY(d.order) : scaleY(getIndicatorValue(d));
	$: lineGenerator =
		line()
		.x(getX)
		.y(getY)
		.curve(curveMonotoneX);
	$: trendLines = _.map(trends, transformValues({value: lineGenerator}));
	$: colorScale = makeColorScale(valueExtext);
	$: getStopOffset = d => `${100 * layout.scaleX(d.year) / width}%`;
	$: gradients = _.map(trends, transformValues({
		value: _.mapWith(applyFnMap({
			offset: getStopOffset,
			stopColor: _.pipe([getIndicatorValue, colorScale])
		}))
	}));

	$: X1 = layout.fullScaleX(year_range[0]);
	$: X2 = layout.fullScaleX(year_range[1]);
	$: x1 = layout.scaleX(year_range[0]);
	$: x2 = layout.scaleX(year_range[1]);

	/* tooltip */

	$: quadTree = rankedData &&
		quadtree()
		.x(getX)
		.y(getY)
		.addAll(rankedData)
		.extent([[x1, 0],[x2, height]]);

	const tooltipDefault = {isVisible: false};
	const tooltip = writable(tooltipDefault);

	const onMousemoved = event => {
		const {offsetX, offsetY} = event;

		if (offsetX < x1 || offsetX > x2) {
			tooltip.set(tooltipDefault);
			return;
		}

		const datum = quadTree.find(offsetX, offsetY);
		const {nuts_id, nuts_year_spec} = datum;

		highlightedKey = nuts_id;
		const keyToLabel = yearlyKeyToLabel[nuts_year_spec];
		const dotX = getX(datum);
		const dotY = getY(datum);
		const isRight = dotX > (X1 + X2) / 2;
		const shiftX = isRight ? -tooltipShift : tooltipShift;
		const shiftY =
			Math.max(yMin + tooltipShift, Math.min(dotY, yMax - tooltipShift)) - dotY;

		tooltip.update(mergeObj({
			isVisible: true,
			...datum,
			nuts_label: `${keyToLabel[nuts_id]} (${nuts_id})`,
			value: formatFn(getIndicatorValue(datum)),
			dotX,
			dotY,
			isRight,
			shiftX,
			shiftY,
		}));
	};
</script>

<svelte:head>
	<title>{description_short}</title>
</svelte:head>

<div class='container'>
	<header>
		<div>
			<h1>{description_short}</h1>
			<p>{description}</p>
		</div>
		<div on:click={toggleModal}>
			<IconInfo
				width=30
				height=30
				strokeWidth=1.5
			/>
		</div>
	</header>

	<section>
		<div class='controls'>
			<button
				on:click='{() => {useOrderScale = true}}'
				class:selected={useOrderScale}
			>Relative</button>
			<button
				class:selected={!useOrderScale}
				on:click='{() => {useOrderScale = false}}'
			>Absolute</button>
		</div>
		<div
			class='trends'
			bind:clientHeight={height}
			bind:clientWidth={width}
			on:mousemove={onMousemoved}
		>
			{#if width && trends}
			<svg
				{width}
				{height}
			>
				<defs>
					{#each gradients as {key, value}}
					<linearGradient
						id={key}
						gradientUnits='userSpaceOnUse'
					>
						{#each value as {offset, stopColor}}
						<stop {offset} stop-color={stopColor} />
						{/each}
					</linearGradient>
					{/each}
				</defs>

				<!-- axes -->
				<g>
					<g class='ref x'>
						{#each $availableYearsStore as year}
						<line
							x1={layout.scaleX(year)}
							x2={layout.scaleX(year)}
							y2={height}
						/>
						{/each}
					</g>
					{#each ticks as {label, y}}
					<g
						class='ref left'
						transform='translate({x1},0)'
					>
						<line x2='-10' y1={y} y2={y}/>
						<text dx='-15' dy={y}>{label}</text>
					</g>
					<g
						class='ref right'
						transform='translate({x2},0)'
					>
						<line x2='10' y1={y} y2={y}/>
						<text dx='15' dy={y}>{label}</text>
					</g>
					{/each}
				</g>

				<!-- curves -->
				<g>
					{#each trendLines as {key, value}}
					<path
						class:focused='{$tooltip.isVisible && highlightedKey === key}'
						class:dimmed='{$tooltip.isVisible && highlightedKey !== key}'
						stroke='url(#{key})'
						d={value}
					/>
					{/each}
				</g>

				<!-- single year: dots -->
				{#if $availableYearsStore.length === 1}
				<g>
				{#each trends as {key, value}}
					{#each value as d}
						<circle
							cx={getX(d)}
							cy={getY(d)}
							r={radius}
						/>
					{/each}
				{/each}
				</g>
				{/if}

				{#if $tooltip.isVisible}
				<g
					class='marker'
					transform='translate({$tooltip.dotX},{$tooltip.dotY})'
				>
					<circle r={radius} />
					<g
						class:right={$tooltip.isRight}
						transform='translate({$tooltip.shiftX},{$tooltip.shiftY})'
					>
						<text dy={-tooltipShift} class='bkg'>{$tooltip.value}</text>
						<text dy={-tooltipShift}>{$tooltip.value}</text>
						<text dy={tooltipShift} class='bkg'>{$tooltip.nuts_label}</text>
						<text dy={tooltipShift}>{$tooltip.nuts_label}</text>
					</g>
				</g>
				{/if}
			</svg>
			{/if}
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

	header {
		height: var(--indicators-h1-height);
		display: flex;
		align-items: center;
		justify-content: space-between;
	}
	header div:nth-child(1) {
		flex: 1;
	}
	header div:nth-child(1) h1 {
		margin: 0;
	}
	header div:nth-child(1) p {
		font-style: italic;
		font-size: 1rem;
		color: grey;
	}
	header div:nth-child(2) {
		align-items: center;
		cursor: pointer;
		display: flex;
		justify-content: space-between;
		margin-left: 1rem;
	}

	section {
		height: calc(100% - var(--indicators-h1-height));
		width: 100%;
		overflow-y: auto;
		display: grid;
		grid-template-columns: 100%;
		grid-template-rows: 3rem calc(100% - 3rem);
		position: relative;
	}

	.controls {
		height: 100%;
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: flex-end;
	}

	button {
		background-color: white;
		border: 1px solid var(--color-main);
		cursor: pointer;
		font-size: 1rem;
		padding: 0.5rem;
		user-select: none;
		margin-left: 1rem;
	}
	button.selected {
		background-color: var(--color-selected);
		color: white;
	}

	.trends {
		position: relative;
	}

	.trends, svg {
		height: 100%;
		width: 100%;
	}

	svg .ref line {
		stroke: var(--color-grey-180);
		pointer-events: none;
	}
	svg .x line {
		stroke-dasharray: 2 2;
		pointer-events: none;
	}
	svg text {
		fill: var(--color-grey-70);
		dominant-baseline: middle;
		font-weight: var(--dim-fontsize-light);
		stroke: none;
		pointer-events: none;
	}
	svg .left text {
		text-anchor: end;
	}
	svg .right text {
		text-anchor: start;
	}

	svg path {
		fill: none;
		pointer-events: none;
	}
	svg path.focused {
		stroke-width: 3;
	}
	svg path.dimmed {
		stroke-opacity: 0.5;
	}

	svg circle {
		fill: white;
		stroke: black;
		stroke-width: 1.5;
		pointer-events: none;
	}

	/* marker */

	svg .marker text {
		fill: black;
		dominant-baseline: middle;
		pointer-events: none;
	}
	svg .marker text.bkg {
		fill: none;
		stroke: white;
		stroke-width: 5;
		stroke-linecap: round;
		stroke-linecap: round;
	}
	svg .marker .right text {
		text-anchor: end;
	}
</style>
