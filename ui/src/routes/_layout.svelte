<script>
	import Banner from 'app/components/Banner.svelte';
	import Nav from 'app/components/Nav.svelte';
	import {_isBannerActive, disableBanner} from 'app/stores/banner';

	export let segment;
</script>

<header>
	<Nav {segment}/>
</header>

<main>
	<slot></slot>
</main>

{#if $_isBannerActive}
	<Banner on:click={disableBanner} />
{/if}

<style>
	header {
		border-bottom: 1px solid var(--color-main-lighter);
		height: var(--dim-header-height);
		padding: 0 var(--dim-padding);
		width: 100%;
	}

	main {
		height: var(--dim-main-height);
		width: 100%;
	}
</style>
