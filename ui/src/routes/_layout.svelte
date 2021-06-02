<script>
	import ScreenGauge, {screen as _screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';

	import Banner from 'app/components/Banner.svelte';
	import Nav from 'app/components/Nav.svelte';
	import {isDev} from 'app/config';
	import {_isBannerActive, disableBanner} from 'app/stores/banner';

	export let segment;

	let contentHeight;
</script>

<ScreenGauge devMode={isDev} />

<section class={$_screen?.classes}>
	<header>
		<Nav
			{_screen}
			{contentHeight}
			{segment}
		/>
	</header>
	<main bind:offsetHeight={contentHeight}>
		<slot></slot>
	</main>
</section>

{#if $_isBannerActive}
	<Banner
		{_screen}
		on:click={disableBanner}
	/>
{/if}

<style>
	section {
		display: grid;
		grid-template-areas:
			'content'
			'nav';
		grid-template-rows: 1fr min-content;
		height: 100%;
		overflow: hidden;
	}
	section.medium {
		grid-template-areas:
			'nav'
			'content';
		grid-template-rows: min-content 1fr;
	}
	header {
		border-top: 1px solid var(--color-main-lighter);
		grid-area: nav;
		height: var(--dim-header-height);
		padding: 0 var(--dim-padding);
		width: 100%;
	}
	.medium header {
		border-bottom: 1px solid var(--color-main-lighter);
		border-top: none;
	}
	main {
		grid-area: content;
		height: 100%;
		overflow: hidden;
		position: relative;
		width: 100%;
	}
</style>
