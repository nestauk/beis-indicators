<script>
	import {_screen} from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import Link from '@svizzle/ui/src/Link.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';

	import {toolName} from 'app/config';
	import theme from 'app/theme';
	import {
		allNUTS2IndicatorsCsvName,
		availableDownloadIds,
		basename,
	} from 'app/utils/assets';
	import {version} from 'app/utils/version';

	const csvWikiURL = 'https://en.wikipedia.org/wiki/Comma-separated_values';
	const maxIndex = availableDownloadIds.length - 1;

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};
</script>

<svelte:head>
	<title>BEIS indicators - Guide</title>
	<meta
		content='{toolName}: usage guide for this tool'
		name='description'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>How to explore the indicators</h1>

		<!-- main -->
		<h2>Indicators page</h2>

		<h3>Temporal coverage</h3>
		<p>
			On the right you will find a representation of the temporal coverage
			for each available indicator.
		</p>
		<p>
			Each circle represents that data for an indicator is available for
			that year.
		</p>
		<p>
			Click on it to the navigate to that indicator for that specific
			year.
		</p>
		<p>
			The timeline below shows a list of all years where there is data
			available for at least one indicator.
		</p>

		<h3>Sidebar</h3>
		<p>
			Here you will find a list of indicators, grouped by theme sections.
			These are:
		</p>
		<ul>
			<li>Public R&D</li>
			<li>Knowledge exchange and university commercialisation</li>
			<li>Private R&D</li>
			<li>Places attracting R&D firms and workers</li>
		</ul>
		<p>
			Clicking on the name of an indicator will navigate to the trend view
			for that indicator.
		</p>

		<!-- trends -->
		<h2>Indicator trends</h2>

		<h3>Timeline</h3>
		<p>
			The Timeline shows one white dot for each year that the indicator is
			available. In this view, the timeline is interactive. Clicking on a
			dot navigates to a map showing the geographic distribution of the
			indicator for that year.
		</p>

		<h3>Trends</h3>
		<p>
			Here you will see a set of trend lines, with each line showing the
			indicator value for one NUTS2 region over time (where data is
			available).
		</p>
		<p>
			Hovering over a trend line highlights the trend and shows the value
			of the data point nearest to the pointer.
		</p>
		<p>
			You can use the toggle in the top-right corner to choose between
			showing actual values or the rank of each region.
		</p>

		<h3>Regional selection</h3>
		<p>
			The trend lines shown correspond to NUTS2 regions, however it is
			possible to select and filter regions based on the larger NUTS1
			regions, of which they are a part. This is particularly useful for
			clarity when focusing on specific regions and also because NUTS1
			regions don't vary over time whereas NUTS2 regions do.
		</p>
		<p>
			By default all NUTS2 regions are selected. The globe button toggles
			a menu where you can select which NUTS1 regions you want to show or
			filter out.
		</p>
		<p>
			The selected NUTS2 regions can be highlighted or filtered using the
			toggle next to the globe icon.
		</p>
		<p>
			Highlighting is useful to focus the attention on the trends for the
			desired regions while still being able to see them all.
		</p>
		<p>
			Filtering is useful to isolate trends for the desired regions. When
			filtering, the colour scale on the left is updated to reflect only
			the values of the active trends.
		</p>

		<h3>Indicator info and download</h3>
		<p>
			Clicking on the "i" icon at the right of the page title shows an
			info panel reporting the indicator metadata (data provenance, date
			of processing, etc).
		</p>
		<p>
			In that same panel there is a button to download a
			<Link
				href={csvWikiURL}
				isBold={true}
				theme={linkTheme}
				type='external'
			>CSV file</Link>
			of the current indicator.
		</p>
		<p>The panel can be dismissed by clicking on the page background.</p>

		<!-- map -->
		<h2>Geographic distribution</h2>
		<p>
			This page can be reached either by clicking on a dot in the
			Indicators page or by clicking on one of the dots of the timeline
			when looking at the trend for a particular indicator.
		</p>

		<h3>Map</h3>
		<p>
			On the left there is a choropleth showing the indicator values on a
			map of the UK for the NUTS2 regions in that year.
		</p>
		<p>
			Gray regions indicate that there is no data available for that
			region.
		</p>
		<p>
			The map shows cities with the most research intensive universities
			(those in "TRAC peer group A"). This group has been chosen due to
			its key relevance for BEIS regional policies.
		</p>

		<h3>Bar chart</h3>
		<p>
			On the right there is a bar chart showing the distribution of the
			indicator values for each NUTS2 region in descending order.
		</p>
		<p>
			The national average is also shown, represented by a vertical dashed
			line. This is calculated as the mean of all available values within
			the year shown.
		</p>

		<h3>Regional selection</h3>
		<p>
			As in the trends view, it is possible to highlight or filter the
			NUTS2 regions within a certain year by selecting a NUTS1 region and
			using the switch to change selection mode.
		</p>
		<p>
			When the 'Filter' option is selected, the map zooms in on the
			currently selected regions.
		</p>

		<h3>Indicator info and download</h3>
		<p>
			The "i" icon at the right of the page title has the same function
			described in the Trends section above.
		</p>

		<!-- download -->
		<h2>Downloading all indicators</h2>
		<p>
			You can download all data in the tool for your own use.
		</p>
		<p>
			Please click on the download icon at the top-right corner of the
			website header to download a zip file containing the CSV files of
			all of the indicators.
		</p>
		<p>
			That zip file also contains an extra CSV file (titled
			<code>{allNUTS2IndicatorsCsvName}</code>) containing all datapoints
			of all indicators in a single file.
		</p>

		<h3>Extras</h3>

		<p>
			Note that some indicators have been created for NUTS3 and LEP, but
			these are not provided in the tool, nor they are official and should
			be considered as non-official extras:
			{#each availableDownloadIds as availableId, index}
				<Link
					download
					href='/data/{basename}_{availableId}.csv'
					isBold={true}
					theme={linkTheme}
				>
					{availableId}
				</Link>
				{#if index < maxIndex},{/if}
			{/each}.
		</p>

		<!-- feedback -->
		<h2>Version, changelog and feedback</h2>

		<p>
			In the top-right corner, you will find the version number of the
			tool (currently <code>{version}</code>).
		</p>
		<p>
			Clicking on the version number will navigate to a list of all the
			notable changes introduced in each version of the tool.
		</p>
		<p>
			Should you find bugs or have ideas about how to enhance this tool,
			please don't hesitate to send your feedback: click on the "Feedback"
			link to navigate to a short survey and our contact details.
		</p>

		<div class='cta'>
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

	ul {
		padding: 0.5rem 0 0.5rem 2rem;
	}

	code {
		font-family: 'Courier new', monospace;
	}

	.cta {
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
