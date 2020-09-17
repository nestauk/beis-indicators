<script>
	import LinkButton from 'app/components/LinkButton.svelte';

	const beisUrl = 'https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy';
	const nestaUrl = 'https://www.nesta.org.uk';
	const repoUrl = 'https://github.com/nestauk/beis-indicators';
</script>

<svelte:head>
	<title>BEIS indicators - Home</title>
</svelte:head>

<main>
	<section>
		<h1>BEIS indicators</h1>

		<h2>Intro</h2>

		<p>In this project, <a href={nestaUrl}>Nesta</a> have worked closely with <a href={beisUrl}>BEIS</a> to create an <a href={repoUrl}>open repository</a> of indicators capturing various dimensions of innovation and its drivers in regions across the UK.<p>
		<p>We have also built a tool to <a href='indicators'>visualise and explore</a> these indicators with the goal of informing policies to drive innovation and growth across all of the UK.<p>
		<p>All this work has been performed with support from <a href={beisUrl}>BEIS</a>.<p>

		<h2>The framework</h2>

		<p>Our indicators are arranged in four broad categories.<p>

		<h3><span>Public R&D Capability</span></h3>
		<p>Measuring the quantity and excellence of R&D activity taking place in higher education institutions in a region.<p>

		<h3><span>Business R&D Capability</span></h3>
		<p>Measuring the level of R&D activity and innovative outputs in the private sector in a region.<p>

		<h3><span>Knowledge exchange</span></h3>
		<p>Measuring the connectivity between higher education institutions in a region and the wider economy.<p>

		<h3><span>Place potential</span></h3>
		<p>Measuring wider infrastructures and framework conditions in a region that might drive - or hinder - its innovative performance.<p>

		<LinkButton url='/methodology' text='Read more about our methodology' />
	</section>
</main>

<style>
	main {
		height: 100%;
		width: 100%;
		display: flex;
		justify-content: space-around;

		font-size: 1.05rem;
		font-weight: 200;
		background-color: var(--color-background);
	}

	p {
		margin-bottom: 1.5rem;
	}

	a {
		padding: 0.1rem;
		border-bottom: 1px solid var(--color-link);
		color: var(--color-link);
		text-decoration: none;
		font-weight: bold;
	}

	section {
		max-width: 800px;
		padding: 2rem;
		overflow-y: auto;
		background-color: white;
		box-shadow: 0px 8px 9px -4px lightgrey;
	}

	h3 span {
		font-weight: bold;
		color: var(--color-main);
	}
</style>
