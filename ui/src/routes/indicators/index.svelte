<script>
	import Index from '@svizzle/time_region_value/src/routes/index.svelte';

	import {toolName} from 'app/config';
	import {_groups, _yearRange} from 'app/stores/data';
</script>

<svelte:head>
	<title>BEIS indicators - Timelines</title>
	<meta
		content='{toolName}: the temporal distribution of all the indicators in this tool'
		name='description'
	>
</svelte:head>

<Index
	{_groups}
	{_yearRange}
	hrefBase='indicators'
/>
