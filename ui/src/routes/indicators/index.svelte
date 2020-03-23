<script context="module">
	export function preload() {
		return this.fetch('indicatorsIndex.json')
			.then(r => r.json())
			.then(groups => ({groups}));
	}
</script>

<script>
	import * as _ from 'lamb';
	import { linearScale } from 'yootils';
	import {
		arrayMin,
		arrayMax,
		makeArrayTransformer
	} from '@svizzle/utils';
	import {tapValue} from '@svizzle/dev';

	import { inclusiveRange } from 'app/utils';

	const getYearExtent = _.pipe([
		_.pluckKey('indicators'),
		_.flatten,
		_.pluckKey('year_range'),
		_.transpose,
		makeArrayTransformer([arrayMin, arrayMax]),
	]);

	const radius = 5;
	const fontSize = 10;
	const gap = 7;
	const start = radius + gap;
	const vStep = 2 * radius + 3 * gap + fontSize;
	const vHalfStep = vStep / 2;

	export let groups;
	export let height;
	export let width;

	$: end = width - start;
	$: yearExtent = getYearExtent(groups);
	$: scaleX = linearScale(yearExtent, [start, end]);
	$: yearRange = inclusiveRange(yearExtent);
</script>

<svelte:head>
	<title>BEIS indicators - Timelines</title>
</svelte:head>

<div class="container">
	<header>
		<h1>Indicators</h1>
	</header>

	<div
		class="timedist"
		bind:clientHeight={height}
		bind:clientWidth={width}
	>
		<ul>
			{#each groups as {id, label, indicators}}
			<div class="group">
				<!-- <a
					rel='prefetch'
					href="group/{id}"
				> -->
					<h2>{label}</h2>
				<!-- </a> -->

				{#if width}
				<svg
					{width}
					height='{4 * start + vStep * indicators.length}'
				>
					{#each yearRange as year}
					<g
						class='xref'
						transform='translate({scaleX(year)},0)'
					>
						<line
							y1='{start}'
							y2='{start + vStep * indicators.length}'
						/>
						<text
							y='{2 * start + vStep * indicators.length + gap}'
						> {year}
						</text>
					</g>
					{/each}

					{#each indicators as {description_short, schema, year_range}, y}
					<g
						class='indicatorsrange'
						transform='translate(0,{vStep * (y + 1)})'
					>
						<text
							x='{(scaleX(year_range[0]) + scaleX(year_range[1])) / 2}'
							dy='{-(fontSize + gap)}'
							font-size={fontSize}
						>{description_short}</text>
						<line
							x1='{scaleX(year_range[0]) + radius}'
							x2='{scaleX(year_range[1]) - radius}'
						/>
						{#each inclusiveRange(year_range) as year}
						<circle
							cx='{scaleX(year)}'
							r={radius}
						/>
						<a
							rel='prefetch'
							href="indicators/{schema.value.id}--{year}"
						>
							<circle
								cx='{scaleX(year)}'
								r={radius}
							/>
						</a>
						{/each}
					</g>
					{/each}
				</svg>
				{/if}
			</div>
			{/each}
		</ul>
	</div>

</div>

<style>
	.container {
		--indicators-h1-height: 2rem;
		height: 100%;
		width: 100%;
	}

	.container header {
		height: var(--indicators-h1-height);
	}

	.container .timedist {
		height: calc(100% - var(--indicators-h1-height));
		width: 100%;
		overflow-y: auto;
	}

	ul {
		line-height: 1.5;
	}

	a {
		text-decoration: none;
	}

	.group {
		margin-top: 1rem;
	}

	svg .xref line {
		stroke: grey;
		stroke-dasharray: 2 2;
	}

	svg .xref text {
		stroke: none;
		fill: grey;
		dominant-baseline: hanging;
		text-anchor: middle;
		font-size: 10px;
		/* cursor: pointer; */
	}

	svg .indicatorsrange line {
		stroke: black;
		stroke-width: 0.7;
		pointer-events: none;
	}

	svg .indicatorsrange text {
		stroke: none;
		fill: rgb(70, 70, 70);
		dominant-baseline: middle;
		text-anchor: middle;
		pointer-events: none;
	}

	svg .indicatorsrange circle {
		fill-opacity: 1;
		fill: white;
		stroke: black;
		stroke-width: 1.5;
		cursor: pointer;
	}
</style>
