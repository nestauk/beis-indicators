<script>
	import LoadingView from '@svizzle/ui/src/LoadingView.svelte';
	import {toolName, userTestingUrl} from 'app/config';

	let showSpinner = true;

	const hideSpinner = () => {
		showSpinner = false;
	};
</script>

<svelte:head>
	<title>EURITO - Feedback</title>
	<meta
		content='{toolName}: a survey where you can leave your feedback on this tool'
		name='description'
	>
</svelte:head>

<main>
	{#if showSpinner}
		<LoadingView />
	{/if}

	<iframe
		frameborder='0'
		marginheight='0'
		marginwidth='0'
		src={userTestingUrl}
		title='User testing survey'
		on:load={hideSpinner}
	/>
</main>

<style>
	main, iframe {
		height: 100%;
		width: 100%;
	}
</style>
