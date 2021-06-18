<script>
	import ScreenGauge, {_screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import {onMount} from 'svelte';

	import Banner from 'app/components/Banner.svelte';
	import ColorCorrection from 'app/components/ColorCorrection.svelte';
	import Nav from 'app/components/Nav.svelte';
	import AccessibilityMenu from 'app/components/AccessibilityMenu.svelte';
	import {_isBannerActive, disableBanner} from 'app/stores/banner';
	import {
		_a11yColorStyles,
		_a11yTextStyles,
		_isA11yDirty,
		applyStyles,
	} from 'app/stores/a11ySettings';

	export let segment;

	let contentHeight;
	let headerHeight;
	let a11yHeight;
	let rootStyle;
	let showA11yMenu;

	onMount(() => {
		const root = document.documentElement;
		rootStyle = root.style;
	})

	$: rootStyle && applyStyles(rootStyle, $_a11yTextStyles);
	$: rootStyle && applyStyles(rootStyle, $_a11yColorStyles);
	$: menuHeight = headerHeight + (showA11yMenu ? a11yHeight : 0);
</script>

<ScreenGauge />
<ColorCorrection />

<section
	class={$_screen?.classes}
	style='--menu-height: {menuHeight}px;'
>
	<header bind:offsetHeight={headerHeight}>
		<Nav
			{_screen}
			{contentHeight}
			{segment}
			bind:showA11yMenu
			isA11yDirty={$_isA11yDirty}
		/>
	</header>
	<main bind:offsetHeight={contentHeight}>
		<slot></slot>
	</main>
	{#if showA11yMenu}
		<div class='accessibility' bind:offsetHeight={a11yHeight}>
			<AccessibilityMenu {_screen} />
		</div>
	{/if}
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
			'nav'
			'accessibility';
		grid-template-rows: calc(100% - var(--menu-height)) min-content min-content;
		height: 100%;
		overflow: hidden;
	}
	section.medium {
		grid-template-areas:
			'nav'
			'content'
			'accessibility';
		grid-template-rows: min-content 1fr min-content;
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
	.accessibility {
		grid-area: accessibility;
	}
</style>
