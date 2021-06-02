<script>
	import {screen as _screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import {toolName} from 'app/config';
	import theme from 'app/theme';

	const beisUrl = 'https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy';
	const nestaUrl = 'https://www.nesta.org.uk';
	const repoUrl = 'https://github.com/nestauk/beis-indicators';
</script>

<svelte:head>
	<title>BEIS indicators - Home</title>
	<meta
		content='{toolName}: homepage'
		name='description'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>BEIS indicators</h1>

		<h2>Intro</h2>

		<p>In this project, <a href={nestaUrl}>Nesta</a> have worked closely with <a href={beisUrl}>BEIS</a> to create an <a href={repoUrl}>open repository</a> of indicators capturing various dimensions of innovation and its drivers in regions across the UK.<p>
		<p>We have also built a tool to <a href='indicators'>visualise and explore</a> these indicators with the goal of informing policies to drive innovation and growth across all of the UK.<p>
		<p>All this work has been performed with support from <a href={beisUrl}>BEIS</a>.<p>

		<h2>The framework</h2>

		<p>Our indicators are arranged in four broad categories.<p>

		<h3>Public R&D</h3>
		<p>Measuring the quantity and excellence of R&D activity taking place in higher education institutions in a region.<p>

		<h3>Knowledge exchange</h3>
		<p>Measuring the connectivity between higher education institutions in a region and the wider economy.<p>

		<h3>Private R&D</h3>
		<p>Measuring the level of R&D activity and innovative outputs in the private sector in a region.<p>

		<h3>Place potential</h3>
		<p>Measuring wider infrastructures and framework conditions in a region that might drive - or hinder - its innovative performance.</p>

		<div class='cta'>
			<LinkButton
				href='/methodology'
				text='Read more about the methodology'
				theme={{backgroundColor: theme.colorMain}}
			/>
			<LinkButton
				href='/indicators'
				text='Explore the indicators'
				theme={{backgroundColor: theme.colorMain}}
			/>
		</div>
	</section>
</main>

<style>
	main {
		background-color: var(--color-background);
		display: flex;
		font-size: 1.05rem;
		font-weight: 200;
		height: 100%;
		justify-content: space-around;
		width: 100%;
	}

	section {
		background-color: white;
		box-shadow: var(--box-shadow-y);
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}

	h1 {
		font-family: 'Open Sans Semibold', sans-serif;
	}
	h2 {
		font-family: 'Open Sans Regular', sans-serif;
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
	}
	h3 {
		font-family: 'Open Sans Regular', sans-serif;
		margin-top: 1.5rem;
	}

	p {
		margin-bottom: 1.5rem;
	}

	a {
		border-bottom: 1px solid var(--color-link);
		color: var(--color-link);
		font-weight: bold;
		padding: 0.1rem;
		text-decoration: none;
	}

	.cta {
		align-content: center;
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		margin: 4rem 0 3rem 0;
		row-gap: 1em;
	}

	.large .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
