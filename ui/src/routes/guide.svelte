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

		<h3>Timeline</h3>
		<p>Here you find a list of all the years where there's data available for at least one indicator.<p>
		<p>In this page, the timeline is not interactive.<p>

		<h3>Sidebar</h3>
		<p>Here you find a list of indicators, grouped in various thematic sections.<p>
		<p>Clicking on a title will navigate to the trend view for that indicator.<p>

		<h2>Indicator trends</h2>

		<h3>Timeline</h3>
		<p>The Timeline shows one white dot for each available year. It is now interactive in that by clicking on a dot lets you navigate to the indicator yearly view for that year.<p>
		<p>In this page, the timeline is not interactive.<p>

		<h3>Sidebar</h3>
		<p>The sidebar has the same function described above: you can use it to navigate to the trends page of the available indicators.<p></p>

		<h3>Trends</h3>
		<p>Here you find a set of trend lines, one for each selected NUTS2 regions.</p>
		<p>Hovering trends, highlights the trend and the data point nearest to the pointer.</p>
		<p>Please use the switch on the top-right corner to choose between showing trends with absolute or ranked values.</p>

		<h3>Regional selection</h3>
		<p>It is possible to select NUTS1 regions to inherently select its contained NUTS2 region. This is particularly useful because NUTS1 regions don't vary over the years whereas NUTS2 regions do.</p>
		<p>By default all NUTS2 regions are selected. The "globe" button toggles the menu where you can select the NUTS1 regions.</p>
		<p>The selected NUTS2 regions can be highlighted or filtered.</p>
		<p>Highlighting is useful to focus the attention on the trends for the desired regions while still being able to see them all.</p>
		<p>Filtering is useful to isolate trends for the desired regions: when filtering, the color scale on the left gets updated only considering the values of the active trends.</p>

		<h3>indicator info and download</h3>
		<p>Clicking in the "i" icon at the right of the page title shows an info panel reporting the indicator metadata (data provenance, date of processing, etc).</p>
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
