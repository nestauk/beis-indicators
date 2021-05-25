<script context="module">
	import {availableDownloadIds, basename} from 'app/utils/assets';

	const maxIndex = availableDownloadIds.length - 1;

	export async function preload({params: {id}}) {
		if (availableDownloadIds.includes(id)) {
			return this.redirect(302, `/data/${basename}_${id}.csv`);
		}
	}
</script>

<section class='layout'>
	<h2>Sorry, the file you're looking for is not available.</h2>
	<p>Please try one of
		{#each availableDownloadIds as availableId, index}
			<a href='/download/{availableId}'>{availableId}</a>
			{#if index < maxIndex},{/if}
		{/each}
		or find the collection of all indicators <a href='/download'>here</a>.
	</p>
</section>

<style>
	.layout {
		padding: 1rem;
	}
</style>
