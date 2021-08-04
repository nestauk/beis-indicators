<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import AppMedium
		from 'app/components/content/guides/AppMedium.svelte';
	import AppSmall
		from 'app/components/content/guides/AppSmall.svelte';

	import {toolName} from 'app/config';
</script>

<svelte:head>
	<title>App guide - {toolName}</title>
	<meta
		content='{toolName}: how to use the app'
		name='description'
	>
</svelte:head>

{#if $_screen?.sizes.medium}
	<AppMedium />
{:else}
	<AppSmall />
{/if}
