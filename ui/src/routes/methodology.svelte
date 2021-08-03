<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import Download from '@svizzle/ui/src/icons/feather/Download.svelte';
	import Link from '@svizzle/ui/src/Link.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import {toolName} from 'app/config';
	import {zipUrl} from 'app/utils/assets';
	import theme from 'app/theme';

	const crunchbaseUrl = 'https://www.crunchbase.com/';
	const DelgadoEtAlUrl = 'https://www.nber.org/papers/w20375.pdf';
	const eurostatUrl = 'https://ec.europa.eu/eurostat';
	const HausmanAndHidalgoUrl = 'https://www.pnas.org/content/106/26/10570';
	const hesaUrl = 'https://www.hesa.ac.uk';
	const lepUrl = 'https://geoportal.statistics.gov.uk/search?collection=Dataset&sort=name&tags=all(BDY_LEP)';
	const MateosGarciaUrl = 'https://osf.io/preprints/socarxiv/3cu67';
	const nutsUrl = 'https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/nuts';
	const onsUrl = 'https://ons.gov.uk';
	const ukriUrl = 'https://www.ukri.org/';

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};
</script>

<svelte:head>
	<title>{toolName}: Methodology</title>
	<meta
		content='{toolName}: methodology used to produce these indicators'
		name='description'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>Methodology</h1>

		<h2>Data sources</h2>
		<p>
			As much as possible we have used data from official sources such as
			<Link
				href={onsUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>ONS</Link>,
			<Link
				href={eurostatUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>Eurostat</Link>,
			<Link
				href={hesaUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>HESA</Link>,
			<Link
				href={ukriUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>UKRI</Link>.
		</p>
		<p>
			One reason to do this is to enable the reproducibility of our analysis,
			and to remove the reliance of the tool on proprietary sources.
		</p>
		<p>
			Having said this, in a small number of instances we have used proprietary
			data sources, such as
			<Link
				href={crunchbaseUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>Crunchbase</Link>
			for the analysis of venture capital investment.
		</p>

		<h2>Geographies</h2>
		<p>
			We use
			<Link
				href={nutsUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>NUTS2</Link>
			regions as our geographical unit of analysis. This has allowed us to
			collect data about regional R&D activity which is only available at
			that level.
			We note that where possible we have also calculated indicators at a
			higher level of granularity (NUTS3) as well as using policy-relevant
			<Link
				href={lepUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>LEP</Link> boundaries.
			These will be released when the tool is published later in 2020.
		</p>
		<p>
			In many cases we have reverse geocoded observations available at
			high level of geographical resolution (for example, the geographical
			coordinates of a higher education institution) using NUTS2 boundary
			files available from Eurostat. When doing this, we have assigned
			observations to regions in the NUTS2 version that was in use at the
			time when the data were collected / when the events captured in the
			data took place.
		</p>

		<h2>Data processing</h2>
		<p>
			In general, we have avoided complex data processing beyond what was
			required to aggregate data at our preferred level of geographical
			resolution. There are however a couple of exceptions to this:
		</p>

		<ul>
			<li>
				<p>
					We have calculated indices of economic complexity for UK
					regions used the algorithm developed by
					<Link
						href={HausmanAndHidalgoUrl}
						isBold={true}
						theme={linkTheme}
						type='external'
					>Hausman and Hidalgo (2009)</Link>.
				</p>
			</li>
			<li>
				<p>
					We have measured levels of employment in entertainment and
					cultural sectors using an industrial segmentation based on
					the methodology developed by
					<Link
						href={DelgadoEtAlUrl}
						isBold={true}
						theme={linkTheme}
						type='external'
					>Delgado et al (2015)</Link>.
				</p>
			</li>
			<li>
				<p>
					We have identified UKRI-funded research projects in STEM
					disciplines using a machine learning analysis of project
					descriptions presented in
					<Link
						href={MateosGarciaUrl}
						isBold={true}
						theme={linkTheme}
						type='external'
					>Mateos-Garcia (2017)</Link>.
				</p>
			</li>
		</ul>

		<p>
			We indicate those indicators based on experimental methodologies or
			data sources where relevant.
		</p>

		<div class='cta'>
			<LinkButton
				download
				glyph={Download}
				href={zipUrl}
				text='Download all indicators'
				theme={{backgroundColor: theme.colorLink}}
			/>
			<LinkButton
				href='/guides'
				text='Read the guides'
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

	p {
		margin-bottom: 1.5rem;
	}

	ul {
		list-style: initial;
		margin-left: 20px;
	}

	.cta {
		display: flex;
		justify-content: space-around;
		margin: 4rem 0 3rem 0;
		flex-direction: column;
		row-gap: 1em;
	}

	.large .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
