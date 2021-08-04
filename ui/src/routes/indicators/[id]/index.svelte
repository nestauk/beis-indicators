<script context='module'>
	import {lookup} from 'app/data/groups';
	import {parseCSV} from 'app/utils/domain';

	export function preload ({params: {id}}) {
		return this.fetch(lookup[id].url)
		.then(r => r.text())
		.then(parseCSV(id))
		.then(data => ({data, id}))
	}
</script>

<script>
	import * as _ from 'lamb';
	import IdIndex from '@svizzle/time_region_value/src/routes/[id]/index.svelte';

	/* local deps */

	import {toolName} from 'app/config';
	import types from 'app/data/types';
	import {_lookup} from 'app/stores/data';
	import {
		_availableYears,
		resetSelectedYear,
	} from 'app/stores/selection';

	/* props */

	export let data;
	export let id;

	/* local vars */

	let availableYears;
	let title;

	/* reactive vars */

	$: id && resetSelectedYear();
	$: ({availableYears, title} = $_lookup[id] || {});
	$: $_availableYears = availableYears;
</script>

<svelte:head>
	<title>{title} - {toolName}</title>
	<meta
		content='{toolName}: temporal trends for each available NUTS2 region for the indicator: {title}'
		name='description'
	>
</svelte:head>

<IdIndex
	{_lookup}
	{data}
	{id}
	{types}
/>
