<script>
	import { setContext } from 'svelte';
	import { writable } from 'svelte/store';

	import groups from 'app/data/indicatorsGroups.json';
	import Timeline from 'app/components/Timeline.svelte';
	import {
		availableYearsStore,
		selectedYearStore,
		timelineHeightStore,
		timelineLayoutStore,
		timelineWidthStore,
	} from 'app/stores';
	import { inclusiveRange } from 'app/utils';

	setContext('layout', {
		timelineHeightStore,
		timelineWidthStore,
		timelineLayoutStore
	});

	export let segment;
</script>

<section class="container">
	<nav>
		{#each groups as {label, indicators}}
		<div class="distancer">
			<h2>{label}</h2>
			{#each indicators as {description_short, schema}}
			<a
				rel='prefetch'
				href='indicators/{schema.value.id}'
			>
				<p class:selected='{schema.value.id === segment}'>
					{description_short}
				</p>
			</a>
			{/each}
		</div>
		{/each}
	</nav>
	<section class="content">
		<section>
			<slot></slot>
		</section>
		<nav>
			<Timeline
				availableYears={$availableYearsStore}
				bind:height={$timelineHeightStore}
				bind:width={$timelineWidthStore}
				indicatorId={segment}
				selectedYear={$selectedYearStore}
			/>
		</nav>
	</section>
</section>

<style>
	.container {
		height: 100%;
		width: 100%;

		display: grid;
		grid-template-columns: 20% 80%;
		grid-template-rows: 100%;
	}
	.container > nav {
		height: 100%;
		width: 100%;
		padding: var(--dim-padding);
		overflow-y: auto;

		background-color: var(--color-main);
		border-right: 1px solid var(--color-main-lighter);
		color: white;
		font-weight: 200;
	}
	.container > nav a {
		text-decoration: none;
	}
	.container > nav p {
		line-height: 1.75rem;
		display: flex;
		align-items: center;
		padding-left: 0.5rem;
	}
	.container > nav p.selected {
		background-color: var(--color-main-desat-50) !important;
	}
	.container > nav p:hover {
		cursor: pointer;
		background-color: var(--color-selected);
		/* font-weight: 600; */
		/* background-color: var(--color-grey-lighter); */
	}

	.content {
		display: grid;
		grid-template-rows: calc(100% - 60px) 60px;
		grid-template-columns: 100%;
	}
	.content section {
		height: 100%;
		width: 100%;
		padding: var(--dim-padding) var(--dim-padding) 0 var(--dim-padding);
	}
	.content nav {
		height: 100%;
		width: 100%;
		background-color: #f9f7dd !important;
		padding: 0 var(--dim-padding);
	}
</style>
