<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import IndicatorsMedium
		from 'app/components/content/guides/IndicatorsMedium.svelte';
	import IndicatorsSmall
		from 'app/components/content/guides/IndicatorsSmall.svelte';

	import {toolName} from 'app/config';
</script>

<svelte:head>
	<title>Indicators guide - {toolName}</title>
	<meta
		content='{toolName}: how to explore the indicators'
		name='description'
	/>
</svelte:head>

{#if $_screen?.sizes.medium}
	<IndicatorsMedium />
{:else}
	<IndicatorsSmall />
{/if}
