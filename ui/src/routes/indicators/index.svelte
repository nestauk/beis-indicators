<script>
	import * as _ from 'lamb';
	import {getContext} from 'svelte';

	import { goto } from '@sapper/app'; // dev

	import { yearRange } from 'app/data/groups';
	import groups from 'app/data/indicatorsGroups.json';
	import {resetSafetyStore, resetSelection} from 'app/stores';

	const {timelineLayoutStore} = getContext('layout');
	const gap = 7;

	resetSelection();
	resetSafetyStore();

	// when exporting, to crawl links in the svg, we need to have width defined
	let width = process.env.SAPPER_EXPORT && 1000;
	let height;

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
			{#each groups as {description, indicators, label}}
			<div class="group">
				<h2>{label}</h2>
				<p>{description}</p>

				{#if width}
				<svg
					{width}
					height='{4 * gap + layout.fontSize + vStep * indicators.length}'
				>
					<!-- global years range -->

					{#each yearRange as year}
						<g
							class='xref'
							transform='translate({layout.scaleX(year)},0)'
						>
							<line
								y1='{gap}'
								y2='{gap + vStep * indicators.length}'
							/>
							<text
								font-size={layout.fontSize}
								y='{2 * gap + vStep * indicators.length + layout.fontSize / 2}'
							> {year}
							</text>
						</g>
					{/each}

					<!-- indicators -->

					{#each indicators as {availableYears, title, schema, year_extent}, y}
					<g
						class='indicatorsrange'
						transform='translate(0,{vStep * (y + 1)})'
					>
						<text
							class='bkg'
							x='{(layout.scaleX(year_extent[0]) + layout.scaleX(year_extent[1])) / 2}'
							dy='{-(layout.fontSize + gap)}'
							font-size={layout.fontSize}
						>{title}</text>
						<text
							x='{(layout.scaleX(year_extent[0]) + layout.scaleX(year_extent[1])) / 2}'
							dy='{-(layout.fontSize + gap)}'
							font-size={layout.fontSize}
						>{title}</text>
						<line
							x1='{layout.scaleX(year_extent[0]) + layout.radius}'
							x2='{layout.scaleX(year_extent[1]) - layout.radius}'
						/>
						{#each availableYears as year}
							{#if process.env.SAPPER_EXPORT}
								<a rel='prefetch' href='/indicators/{schema.value.id}/{year}'>
									<circle
										cx='{layout.scaleX(year)}'
										r={layout.radius}
									/>
								</a>
							{:else}
								<circle
									cx='{layout.scaleX(year)}'
									r={layout.radius}
									on:click='{() => goto(`indicators/${schema.value.id}/${year}`)}'
								/>
							{/if}
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
	svg .indicatorsrange text.bkg {
		stroke: white;
		stroke-width: 5;
	}

	svg .indicatorsrange circle {
		fill-opacity: 1;
		fill: white;
		stroke: black;
		stroke-width: 1.5;
		cursor: pointer;
	}
</style>
