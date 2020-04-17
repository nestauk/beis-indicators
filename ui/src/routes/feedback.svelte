<script>
	const userTestingUrl = 'https://docs.google.com/a/nesta.org.uk/forms/d/1O4jcWQmZOtfubJV9CBdfSBozpuEC5beGc-cmWoFzn0s/edit?usp=drive_web';
</script>

<svelte:head>
	<title>BEIS indicators - Feedback</title>
</svelte:head>

<main>
	<iframe
		src={userTestingUrl}
	/>
</main>

<style>
	main, iframe {
		height: 100%;
		width: 100%;
	}
</style>
