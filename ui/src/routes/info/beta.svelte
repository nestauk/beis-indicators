<script>
	import Beta from 'app/components/content/info/Beta.svelte';
	import {toolName} from 'app/config';
</script>

<svelte:head>
	<title>Beta release - {toolName}</title>
	<meta
		content='{toolName}: Beta release'
		name='description'
	>
</svelte:head>

<Beta />
