<script>
	import LinkButton from 'app/components/LinkButton.svelte';
	import ExternalLink from 'app/components/ExternalLink.svelte';
	import {version} from 'app/utils';

	const csvWikiURL = 'https://en.wikipedia.org/wiki/Comma-separated_values';
</script>

<svelte:head>
	<title>BEIS indicators - Methodology</title>
</svelte:head>

<main>
	<section>
		<h1>How to explore the indicators</h1>

		<h2>Indicators page</h2>

		<h3>Time coverage</h3>
		<p>On the right you will find a representation of the temporal coverage for each available indicator.<p>
		<p>Each circle represents that data for an indicator is available for that year.<p>
		<p>Click on it to the navigate to that indicator for that specific year.<p>
		<p>The timeline below shows a list of all years where there is data available for at least one indicator.<p>

		<h3>Sidebar</h3>
		<p>Here you will find a list of indicators, grouped by theme sections. These are:<p>
		<li>Public R&D capability</li>
		<li>Business R&D capacity</li>
		<li>Knowledge exchange</li>
		<li>Place potential</li>
		<p>Clicking on the name of an indicator will navigate to the trend view for that indicator.<p>

		<h2>Indicator trends</h2>

		<h3>Timeline</h3>
		<p>The Timeline shows one white dot for each year that the indicator is available. In this view, the timeline is interactive. Clicking on a dot navigates to a map showing the geographic distribution of the indicator for that year.<p>

		<h3>Trends</h3>
		<p>Here you will see a set of trend lines, with each line showing the indicator value for one NUTS2 region over time (where data is available).</p>
		<p>Hovering over a trend line highlights the trend and shows the value of the data point nearest to the pointer.</p>
		<p>You can use the toggle in the top-right corner to choose between showing actual values or the rank of each region.</p>

		<h3>Regional selection</h3>
		<p>The trend lines shown correspond to NUTS2 regions, however it is possible to select and filter regions based on the larger NUTS1 regions, of which they are a part. This is particularly useful for clarity when focusing on specific regions and also because NUTS1 regions don't vary over time whereas NUTS2 regions do.</p>
		<p>By default all NUTS2 regions are selected. The globe button toggles a menu where you can select which NUTS1 regions you want to show or filter out.</p>
		<p>The selected NUTS2 regions can be highlighted or filtered using the toggle next to the globe icon.</p>
		<p>Highlighting is useful to focus the attention on the trends for the desired regions while still being able to see them all.</p>
		<p>Filtering is useful to isolate trends for the desired regions. When filtering, the colour scale on the left is updated to reflect only the values of the active trends.</p>

		<h3>Indicator info and download</h3>
		<p>Clicking on the "i" icon at the right of the page title shows an info panel reporting the indicator metadata (data provenance, date of processing, etc).</p>
		<p>In that same panel there is a button to download the <a href={csvWikiURL}>CSV file</a> of the current indicator.</p>
		<p>The panel cak be dismissed by clicking iot the page background.</p>

		<h2>Indicator yearly data</h2>

		<p>This page cak be reached either by clicking on a dot in the index page or by clicking on one of the dots of the timeline in the trend of a certain indicator.<p></p>

		<h3>Sidebar</h3>
		<p>The sidebar has the same function described above: you can use it to navigate indicators trend page.<p></p>

		<h3>Map</h3>
		<p>On the left there is a choropleth showing the indicator values on the map of UK NUTS2 regions.</p>
		<p>Gray regions indicate that there is no data available for that region.</p>
		<p>The map shows cities with the most research intensive universities (called "Trac peer group A"), as used previously on maps within BEIS because they are key to BEIS regional policies.</p>

		<h3>Barchart</h3>
		<p>On the rightleft there is a barchart showing the disrtibution of the indicator values in various NUTS2 regions, sorted by value in descendent order.</p>

		<h3>Regional selection</h3>
		<p>As for the trends view, it ir porrible toi highlight or filter the NUTS2 regions for a certain year by selecting a NUTS1 region and using the switch to change selection mode.</p>
		<p>When filtering the map zooms on the currently selected regions.</p>

		<h3>Indicator info and download</h3>
		<p>The "i" icon at the right of the page title has the very same function described above.</p>

		<h2>Downloading all the indicators at once</h2>
		<p>Please click on "download" icon on the top-right of the website header to download a zip file containing the CSV files of all all the indicators.</p>
		<p>That zip file also contains an extra CSV file (titled <code>beis_indicators_{version}.csv</code>) containing all datapoints of all indicators in a single place.</p>

		<LinkButton url='/indicators' text='Explore the indicators' />
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

	section {
		max-width: 800px;
		padding: 2rem;
		overflow-y: auto;
		background-color: white;
		box-shadow: var(--box-shadow-y);
	}

	h1 {
		font-family: 'Open Sans Semibold', sans-serif;
	}
	h2 {
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
		font-family: 'Open Sans Regular', sans-serif;
	}
	h3 {
		margin-top: 1.5rem;
		font-family: 'Open Sans Regular', sans-serif;
	}
	p {
		line-height: 2rem;
	}

	a {
		text-decoration: none;
		font-weight: bold;
	}

	p a {
		padding: 0.1rem;
		border-bottom: 1px solid var(--color-link);
		color: var(--color-link);
		text-decoration: none;
		font-weight: bold;
	}

	code {
		font-weight: bold;
		font-family: 'Courier new', monospace;
	}
</style>
