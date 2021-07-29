<script>
	import {toolName} from 'app/config';

	const userTestingUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSekqhPhm4VNDdQNmpbE0EjTQj8zruLw8mIyqJH5hV9z-Dytbw/viewform?embedded=true';
</script>

<svelte:head>
	<title>{toolName}: Feedback</title>
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
	>Loading...</iframe>
</main>

<style>
	main, iframe {
		height: 100%;
		width: 100%;
	}
</style>
