<script>
	import {setContext, onMount} from 'svelte';

	import groups from 'app/data/indicatorsGroups.json';
	import Timeline from 'app/components/Timeline.svelte';
	import {
		availableYearsStore,
		selectedYearStore,
		timelineHeightStore,
		timelineLayoutStore,
		timelineWidthStore,
	} from 'app/stores';

	setContext('layout', {timelineLayoutStore});

	onMount(() => {
		current && current.scrollIntoView({
			block: 'nearest',
			behavior: 'smooth'
		});
	})

	export let current;
	export let scrollable;
	export let scrollableHeight;
	export let segment;

	function keepOnScreen(node, {id, segment, scrollableHeight}) {
		if (id === segment) {
			current = node;
		}

		return {
			update({id, segment, scrollableHeight}) {
				if (id === segment) {
					const {y: Y} = scrollable.getBoundingClientRect();
					const {y} = node.getBoundingClientRect();
					const yRel = y - Y;

					if (yRel < 0 || yRel > scrollableHeight) {
						scrollable.scrollTo({
							top: yRel,
							behavior: 'smooth'
						});
					}
				}
			}
		};
	}
</script>

<section class='layout'>
	<nav
		bind:this={scrollable}
		bind:clientHeight={scrollableHeight}
	>
		{#each groups as {label, indicators}}
		<div class='group'>
			<h2>{label}</h2>
			{#each indicators as {title, schema}}
			<a
				rel='prefetch'
				href='indicators/{schema.value.id}'
			>
				<p
					class:selected='{schema.value.id === segment}'
					use:keepOnScreen={{
						id: schema.value.id,
						segment,
						scrollableHeight
					}}
				>
				{title}
				</p>
			</a>
			{/each}
		</div>
		{/each}
	</nav>
	<section class='content'>
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
	.layout {
		height: 100%;
		width: 100%;

		--sidebarWidth: 340px;

		display: grid;
		grid-template-columns: var(--sidebarWidth) calc(100% - var(--sidebarWidth));
		grid-template-rows: 100%;
	}

	/* sidebar */

	nav {
		height: 100%;
		width: 100%;
		padding: var(--dim-padding);
		overflow-y: auto;

		background-color: var(--color-main);
		border-right: 1px solid var(--color-main-lighter);
		color: white;
		font-weight: var(--dim-fontsize-light);
	}

	nav .group:not(:last-child) {
		margin-bottom: 1rem;
	}
	nav .group:not(:first-child) {
		margin-top: 1rem;
	}

	nav h2 {
		font-family: 'Open Sans Semibold', sans-serif;
		margin-bottom: 1rem;
	}
	nav a {
		text-decoration: none;
	}
	nav p {
		line-height: 1.5rem;
		display: flex;
		align-items: center;
		padding: 0.4rem;
		margin-bottom: 0.5rem;
	}
	nav p.selected {
		background-color: var(--color-main-desat-50) !important;
		font-family: 'Open Sans Regular', sans-serif;
	}
	nav p:hover {
		cursor: pointer;
		background-color: var(--color-selected);
	}

	/* content */

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
		background-color: var(--color-paleyellow) !important;
		padding: 0 var(--dim-padding);
	}
</style>
