<script>
	import Index from '@svizzle/time_region_value/src/routes/index.svelte';

	import {toolName} from 'app/config';
	import {_groups, _yearRange} from 'app/stores/data';
	import {goTo} from 'app/utils/sapper';
</script>

<svelte:head>
	<title>BEIS indicators - Timelines</title>
	<meta
		content='{toolName}: the temporal distribution of all the indicators in this tool'
		name='description'
	>
</svelte:head>

<Index
	{goTo}
	groupsStore={_groups}
	yearRangeStore={_yearRange}
	hrefBase='indicators'
/>
