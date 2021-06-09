<script>
	import Layout from '@svizzle/time_region_value/src/routes/_layout.svelte';

	import {_groups} from 'app/stores/data';
	import theme from 'app/theme';

	export let segment;
</script>

<Layout
	{_groups}
	{segment}
	{theme}
	hrefBase='indicators'
>
	<slot></slot>
</Layout>
