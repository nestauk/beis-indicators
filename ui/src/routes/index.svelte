<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import Link from '@svizzle/ui/src/Link.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import {toolName} from 'app/config';
	import theme from 'app/theme';

	const beisUrl = 'https://www.gov.uk/government/organisations/department-for-business-energy-and-industrial-strategy';
	const nestaUrl = 'https://www.nesta.org.uk';
	const repoUrl = 'https://github.com/nestauk/beis-indicators';

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};
</script>

<svelte:head>
	<title>{toolName}: Home</title>
	<meta
		content='{toolName}: homepage'
		name='description'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>BEIS/Nesta Research & Development spatial data tool</h1>

		<h2>Intro</h2>

		<p>
			In this project,
			<Link
				href={beisUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>BEIS</Link>
			and
			<Link
				href={nestaUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>Nesta</Link>
			have co-developed a research and development (R&D) spatial data tool,
			that allows users to access, visualise and compare indicators that show
			the scale of R&D systems at a subregional level.
			The tool is an
			<Link
				href={repoUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>open data repository</Link>,
			giving access to R&D related indicators broken down by place and time,
			with associated easy-to-use visualisation options
			(such as line charts and choropleths).
		</p>
		<p>
			The indicators are wide-ranging and capture various dimensions of R&D
			ecosystems including public R&D, knowledge exchange and university
			commercialisation, private R&D and places attracting R&D firms and workers.
			With this tool users can access,
			<Link
				href='indicators'
				isBold={true}
				isUnderlined={true}
				theme={linkTheme}
			>
				visualise and explore
			</Link>
			the indicators, using it as a foundation for further analysis - with the
			goal of informing policies to drive R&D, innovation and growth across
			all of the UK.
		</p>
		<p>
			All this work has been performed with support from BEIS.
		</p>

		<h2>The framework</h2>
		<p>Our indicators are arranged in four broad categories.</p>

		<h3>Public R&D</h3>
		<p>
			Measuring the quantity and excellence of R&D activity taking place
			in higher education institutions in a region.
		</p>

		<h3>Knowledge exchange and university commercialisation</h3>
		<p>
			Measuring the connectivity between higher education institutions in a
			region and the wider economy.
		</p>

		<h3>Private R&D</h3>
		<p>
			Measuring the level of R&D activity and innovative outputs in the private
			sector in a region.
		</p>

		<h3>Places attracting R&D firms and workers</h3>
		<p>
			Measuring wider infrastructures and framework conditions in a region
			that might drive - or hinder - its innovative performance.
		</p>

		<div class='cta'>
			<LinkButton
				href='/methodology'
				text='Read more about the methodology'
				theme={{backgroundColor: theme.colorLink}}
			/>
			<LinkButton
				href='/indicators'
				text='Explore the indicators'
				theme={{backgroundColor: theme.colorLink}}
			/>
		</div>
	</section>
</main>

<style>
	main {
		background-color: var(--color-background);
		display: flex;
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
		font-weight: bold;
	}
	h2 {
		font-weight: normal;
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
	}
	h3 {
		font-weight: normal;
		margin-top: 1.5rem;
	}

	p {
		margin-bottom: 1.5rem;
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
