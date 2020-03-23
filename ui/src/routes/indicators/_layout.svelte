<script context="module">
	export function preload() {
		return this.fetch('indicatorsIndex.json')
			.then(r => r.json())
			.then(groups => ({groups}));
	}
</script>

<script>
	import * as _ from 'lamb';

	export let groups;
	export let segment; // e.g. 'aps_econ_active_stem_associate_profs_data--2014'

	let indicatorId, year;
	$: if (segment){
		[indicatorId, year] = segment.split('--')
	}
</script>

<section>
	<nav>
		{#each groups as {label, indicators}}
		<div class="distancer">
			<h2>{label}</h2>
			{#each indicators as {description_short, schema}}
			<a
				rel='prefetch'
				href="indicators/{schema.value.id}"
			>
				<p class:selected='{schema.value.id === segment}'>
					{description_short}
				</p>
			</a>
			{/each}
		</div>
		{/each}
	</nav>
	<main>
		<slot></slot>
	</main>
</section>

<style>
	section {
		height: 100%;
		width: 100%;

		display: grid;
		grid-template-columns: 20% 80%;
		grid-template-rows: 100%;
	}

	nav {
		height: 100%;
		width: 100%;
		padding: var(--dim-padding);
		overflow-y: auto;

		background-color: var(--color-main);
		border-right: 1px solid var(--color-main-lighter);
		color: white;
		font-weight: 200;
	}

	nav a {
		text-decoration: none;
	}

	nav p {
		line-height: 1.75rem;
		display: flex;
		align-items: center;
		padding-left: 0.5rem;
	}

	nav p.selected {
		background-color: var(--color-main-lighter) !important;
	}

	nav p:hover {
		cursor: pointer;
		background-color: lightseagreen;
		/* font-weight: 600; */
		/* background-color: var(--color-grey-lighter); */
	}

	main {
		height: 100%;
		width: 100%;
		padding: var(--dim-padding);
	}
</style>
