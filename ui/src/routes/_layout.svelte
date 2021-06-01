<script>
	import Icon from '@svizzle/ui/src/icons/Icon.svelte';
	import AlertTriangle from '@svizzle/ui/src/icons/feather/AlertTriangle.svelte';
	import XCircle from '@svizzle/ui/src/icons/feather/XCircle.svelte';

	import Nav from 'app/components/Nav.svelte';
	import {
		disableBanner,
		isBannerActiveStore,
	} from 'app/stores';

	export let segment;
</script>

<header>
	<Nav {segment}/>
</header>

<main>
	<slot></slot>
</main>

{#if $isBannerActiveStore}
	<div class='banner'>
		<header>
			<div class='title'>
				<Icon glyph={AlertTriangle} />
				<span>Disclaimer</span>
			</div>
			<div
				class='clickable'
				on:click={disableBanner}
			>
				<Icon glyph={XCircle} />
			</div>
		</header>
		<p>This is a beta tool that has not been publicly released, please request permission from BEIS/Nesta before sharing it any further.</p>
	</div>
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

	.banner {
		align-items: center;
		background-color: white;
		border: 1px solid red;
		box-shadow: var(--box-shadow-xy);
		display: flex;
		flex-direction: column;
		font-size: 1.5rem;
		justify-content: center;
		left: 25%;
		margin: auto;
		position: fixed;
		top: 25%;
		user-select: none;
		width: 50%;
	}
	.banner header {
		align-items: center;
		background-color: red;
		color: yellow;
		display: flex;
		padding: 1rem;
	}
	.banner header .title {
		flex: 1;
	}
	.banner p {
		padding: 1rem;
	}
</style>
