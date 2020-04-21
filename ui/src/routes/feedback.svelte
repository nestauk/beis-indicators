<script>
	const userTestingUrl = 'https://docs.google.com/forms/d/e/1FAIpQLSekqhPhm4VNDdQNmpbE0EjTQj8zruLw8mIyqJH5hV9z-Dytbw/viewform?embedded=true';
</script>

<svelte:head>
	<title>BEIS indicators - Feedback</title>
</svelte:head>

<main>
	<iframe
		title='User testing survey'
		src={userTestingUrl}
		frameborder='0'
		marginheight='0'
		marginwidth='0'
	>Loading...</iframe>
</main>

<style>
	main, iframe {
		height: 100%;
		width: 100%;
	}
</style>
