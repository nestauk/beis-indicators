<script>
	import Privacy from 'app/components/content/info/Privacy.svelte';
	import {toolName} from 'app/config';
</script>

<svelte:head>
	<title>Privacy - {toolName}</title>
	<meta
		content='{toolName}: Privacy statement'
		name='description'
	>
</svelte:head>

<Privacy />
