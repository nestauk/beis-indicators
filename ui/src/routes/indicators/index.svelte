<script>
	import * as _ from 'lamb';
	import { linearScale } from 'yootils';
	import {inclusiveRange} from '@svizzle/utils';

	import { goto } from '@sapper/app';
	import { yearExtent, yearRange } from 'app/data/groups';
	import groups from 'app/data/indicatorsGroups.json';
	import {resetSelection} from 'app/stores';

	import { getContext } from 'svelte';

	const {timelineLayoutStore} = getContext('layout');
	const gap = 7;

	resetSelection();

	let height;
	let width;

	$: layout = $timelineLayoutStore;
	$: vStep = 2 * layout.radius + 3 * gap + layout.fontSize;
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
				<h2>{label}</h2>

				{#if width}
				<svg
					{width}
					height='{4 * layout.start + vStep * indicators.length}'
				>
					{#each yearRange as year}
					<g
						class='xref'
						transform='translate({layout.scaleX(year)},0)'
					>
						<line
							y1='{layout.start}'
							y2='{layout.start + vStep * indicators.length}'
						/>
						<text
							y='{2 * layout.start + vStep * indicators.length + gap}'
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
							x='{(layout.scaleX(year_range[0]) + layout.scaleX(year_range[1])) / 2}'
							dy='{-(layout.fontSize + gap)}'
							font-size={layout.fontSize}
						>{description_short}</text>
						<line
							x1='{layout.scaleX(year_range[0]) + layout.radius}'
							x2='{layout.scaleX(year_range[1]) - layout.radius}'
						/>
						{#each inclusiveRange(year_range) as year}
						<!-- FIXME using <a> in svg seems to give a bad URL hence reloading the page -->
						<!-- <a
							rel='prefetch'
							href='indicators/{schema.value.id}/{year}'
						> -->
							<circle
								cx='{layout.scaleX(year)}'
								r={layout.radius}
								on:click='{() => goto(`indicators/${schema.value.id}/${year}`)}'
							/>
						<!-- </a> -->
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

	/* a {
		text-decoration: none;
	} */

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
