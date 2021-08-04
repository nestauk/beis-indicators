<script>
	import {toolName, userTestingUrl} from 'app/config';
</script>

<svelte:head>
	<title>Feedback - {toolName}</title>
	<meta
		content='{toolName}: a survey where you can leave your feedback on this tool'
		name='description'
	>
</svelte:head>

<main>
	<iframe
		frameborder='0'
		marginheight='0'
		marginwidth='0'
		src={userTestingUrl}
		title='User testing survey'
	/>
</main>

<style>
	main, iframe {
		height: 100%;
		width: 100%;
	}
	main {
		position: relative;
	}
</style>
