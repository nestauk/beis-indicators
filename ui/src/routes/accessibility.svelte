<script>
	import {onMount} from 'svelte';
	import * as _ from 'lamb';
	import {isNotNil} from '@svizzle/utils';
	import Bowser from 'bowser';
	import {_screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';

	import ChevronLeft from '@svizzle/ui/src/icons/feather/ChevronLeft.svelte';
	import ChevronRight from '@svizzle/ui/src/icons/feather/ChevronRight.svelte';
	import Icon from '@svizzle/ui/src/icons/Icon.svelte';
	import Link from '@svizzle/ui/src/Link.svelte';
	import LinkButton from '@svizzle/ui/src/LinkButton.svelte';
	import LoadingView from '@svizzle/ui/src/LoadingView.svelte';

	import {zipUrl} from 'app/utils/assets';
	import {
		getTest,
		getTestResultsFilename,
		groupTests,
		testResultsBaseURL,
		summarizeResults
	} from 'app/utils/tests';
	import {failingA11yAudit, lighthouseUrls, toolName} from 'app/config';
	import theme from 'app/theme';

	const lighthouseIssueUrl = 'https://github.com/GoogleChrome/lighthouse/issues/12039';
	const lighthouseUrl = 'https://developers.google.com/web/tools/lighthouse';
	const openDyslexicUrl = 'https://opendyslexic.org/';
	const osxMouseURL = 'https://support.apple.com/guide/mac-help/change-cursor-preferences-for-accessibility-mchl5bb12e1e/mac';
	const pa11yUrl = 'https://pa11y.org/'
	const screenReadersUrl = 'https://en.wikipedia.org/wiki/List_of_screen_readers';
	const wcag21Url = 'https://www.w3.org/TR/WCAG21/';
	const windowsMouseURL = 'https://support.microsoft.com/en-us/windows/change-mouse-settings-e81356a4-0e74-fe38-7d01-9d79fbf8712b';

	const reportNames = _.keys(lighthouseUrls)
	const updateCurrentReport = id => currentreport = id;

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};

	let currentreport = reportNames[0];
	let environment;
	let lighthouseFrame;
	let loadingResults = false;
	let testResults = {
		tested: false,
		passed: false
	};

	async function loadResults (environment) {
		const fileName = getTestResultsFilename(environment);
		if (fileName) {
			const response = await fetch(`${testResultsBaseURL}/${fileName}`);
			const allTests = await response.json();
			const indexedResults = groupTests(allTests);
			const test = getTest(indexedResults, environment)
			testResults = summarizeResults(test);
		}
	}

	function resizeIFrameToFitContent ( iFrame ) {
		loadingResults = false
		iFrame.height = iFrame.contentWindow.document.body.scrollHeight;
	}

	onMount(() => {
		environment = Bowser.parse(window.navigator.userAgent);
		loadResults(environment);
	})

	$: currentreport, loadingResults = true;
	$: currentValueIndex = _.findIndex(
		reportNames,
		_.is(currentreport)
	);
	$: prevValue = reportNames[currentValueIndex - 1];
	$: nextValue = reportNames[currentValueIndex + 1];
	$: hasPrevValue = isNotNil(prevValue);
	$: hasNextValue = isNotNil(nextValue);
	$: clickedPrev =
		() => hasPrevValue && updateCurrentReport(prevValue);
	$: clickedNext =
		() => hasNextValue && updateCurrentReport(nextValue);
	$: reportUrl = `/audits/lighthouse/${currentreport}.html`;
</script>

<svelte:head>
	<title>EURITO - Accessibility</title>
	<meta
		name='description'
		content='All about accessibility in {toolName}, including a guide on how to enable the accessibility dialog, accessibility audit and other quality audits, plus some pointers to setup various accessibility tools on your system'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>Accessibility</h1>

		<p>
			Ensuring greater access to technologies by meeting the needs of
			people with disabilities lays the foundation for inclusive work
			cultures that empower individuals and teams to thrive.
		</p>
		<p>
			Therefore, {toolName} is committed to making its best effort towards
			continually improving the accessibility of all the information
			provided in this website.
		</p>
		<h2>Support</h2>
		<p>
			We follow the recommendations of the
			<Link
				href={wcag21Url}
				isBold={true}
				theme={linkTheme}
				type='external'
			>
				WCAG 2.1 guidelines
			</Link>.
			Also:
		</p>
		<ul>
			<li>
				<p>
					Ensure that the choices of color provide sufficient
					contrast for comfortable reading.
				</p>
			</li>
			<li>
				<p>
					Offer a selection of typefaces for improved legibility,
					including one widely believed to improve comprehension among
					people with
					<Link
						href={openDyslexicUrl}
						isBold={true}
						theme={linkTheme}
						type='external'
					>
						Dyslexia
					</Link>.
				</p>
			</li>
			<li>
				<p>
					Wherever it's possible, enhance the semantic meta
					information of each page to improve the reach of tools such
					as screen readers.
				</p>
			</li>
			<li>
				<p>
					We regularly measure our site using a variety of methods,
					such as third-party automated and manual audits across a
					range of different browsers and devices. You can review some
					of those results in the "Quality audits" section below.
				</p>
			</li>
		</ul>
		<h2>WCAG compliance rating</h2>
		<p>
			According to automated testing using the
			<Link
				href={pa11yUrl}
				isBold={true}
				type='external'
			>
				Pa11y accessibility testing tool
			</Link>,
			no accessibility issues were detected and this website is reported
			to have a WCAG 2.0 AAA compliance level. This website also passes
			the accessibility audits checked by
			<Link
				href={lighthouseUrl}
				isBold={true}
				type='external'
			>
				Google's Lighthouse tool
			</Link>.
		</p>
		<h2>Limitations</h2>
		<p>
			Although we continually revise the website for proper support, we
			recognize that some pages may present occasional accessibility
			problems. Also, just as technology improves and standards evolve,
			our work is also never done and we continually strive to achieve the
			highest levels of compliance with the requirements and
			recommendations.
		</p>
		<p>
			Meeting all of the WCAG criteria requires evaluating some of
			them manually. Due to time constraints we might not have been able 
			to test all of the recommendations listed in the section "Additional
			items to manually check" in the "Accessibility" part of each audit
			below, in the "Quality audits" section of this page. In particular
			at this time ARIA and keyboard navigation are only partially
			supported.
		</p>
		<p>
			While we aim to make the information provided as accessible as
			possible, this website presents data mostly as interactive charts
			which at the moment do not also render a text alternative, so those
			aren't accessible by screen readers. However, the data is available
			for
			<Link
				download
				href={zipUrl}
				isBold={true}
				theme={linkTheme}
			>
				download in CSV format
			</Link>.
		</p>
		<h2>Feedback</h2>
		<p>
			If you see any errors or have other suggestions on how we
			can further improve the accessibility of our site,
			please contact us at
			<Link
				href="mailto:dataanalytics@nesta.org.uk"
				isBold={true}
				theme={linkTheme}
			>
				dataanalytics@nesta.org.uk
			</Link>.
		</p>

		<h2>Resources</h2>
		<h3>Using a screen reader</h3>
		<p>
			If you need a screen reader and have not installed one already, you
			may choose one from this
			<Link
				href={screenReadersUrl}
				isBold={true}
				theme={linkTheme}
				type='external'
			>
				comprehensive list of screen readers
			</Link>.
		</p>
		<h3>How to customize the mouse pointer</h3>
		<p>
			You can customize a computer mouse pointer in several ways. For
			example, you can slow down the speed of the mouse pointer for easier
			handling. You can also change its appearance so that it contrasts
			more with the screen content.
		</p>

		<div class='cta'>
			<LinkButton
				href={windowsMouseURL}
				text='Windows'
				theme={{backgroundColor: theme.colorLink}}
				type='external'
			/>
			<LinkButton
				href={osxMouseURL}
				text='OS X'
				theme={{backgroundColor: theme.colorLink}}
				type='external'
			/>
		</div>

		<h2>Detected Browsing Environment</h2>
		<dl>
			<dt>Platform</dt>
			<dd>{environment?.platform?.type}</dd>
			<dt>Operating System</dt>
			<dd>
				{environment?.os?.name}
				{#if environment?.os?.versionName}
					- {environment.os.versionName}
				{/if}
			</dd>
			<dt>Browser</dt>
			<dd>
				{environment?.browser.name}
				{#if environment?.browser?.version}
					- {environment.browser.version}
				{/if}
			</dd>
			<dt>Engine</dt>
			<dd>
				{environment?.engine.name}
				{#if environment?.engine?.version}
					- {environment.engine.version}
				{/if}
			</dd>
		</dl>

		{#if testResults?.tested}
			<p>
				{#if testResults.passed}
					This browsing environment has been tested and is supported.
				{:else}
					This browsing environment has been tested but some tests
					have failed and it may not be fully supported.
				{/if}
			</p>
		{:else}
			<p>
				This browsing environment hasn't been tested and user experience
				may vary.
				{#if environment?.os?.name === 'Linux'}
					Browserstack does not offer testing under Linux operating
					systems
				{/if}
			</p>
		{/if}

		<h2>Quality audits</h2>
		<menu class='tabs'>
			{#if $_screen?.sizes?.medium}
				<ul>
					{#each reportNames as id}
						<li>
							<input
								{id}
								type='radio'
								bind:group={currentreport}
								value={id}
							>
							<label for={id} class='clickable'>
								{id}
							</label>
						</li>
					{/each}
					{#if loadingResults}
						<li class='meta'>
							<div class='spinner'>
								<LoadingView
									size={24}
									stroke={theme.colorMain}
									strokeWidth={1}
								/>
							</div>
						</li>
					{/if}
				</ul>
			{:else}
				<div class='tab-selector'>
					<label for=''>
						{currentreport}
						{#if loadingResults}
							<div class='spinner'>
								<LoadingView
									size={24}
									stroke={theme.colorMain}
									strokeWidth={1}
								/>
							</div>
						{/if}
					</label>

					<button
						class:clickable={hasPrevValue}
						disabled={!hasPrevValue}
						on:click={clickedPrev}
					>
						<Icon glyph={ChevronLeft} />
					</button>
					<button
						class:clickable={hasNextValue}
						disabled={!hasNextValue}
						on:click={clickedNext}
					>
						<Icon glyph={ChevronRight} />
					</button>
				</div>
			{/if}
		</menu>
		{#if failingA11yAudit.includes(currentreport)}
			<figure>
				Unfortunately the accessibility audit for this page fails
				because of an
				<Link
					href={lighthouseIssueUrl}
					isBold={true}
					theme={linkTheme}
					type='external'
				>
					issue
				</Link> in Google Lighthouse.
			</figure>
		{/if}
		<iframe
			bind:this={lighthouseFrame}
			frameborder='0'
			marginheight='0'
			marginwidth='0'
			src={reportUrl}
			title='Accessibility validation results'
			on:load={e => resizeIFrameToFitContent(lighthouseFrame)}
		>
			Loading...
		</iframe>
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

	figure {
		background: var(--color-warning-background);
		border: thin solid var(--color-warning-border);
		color: var(--color-warning-text);
		padding: 0.5em 1em;
	}

	iframe {
		width: 100%;
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
	dl {
		display: grid;
		grid-template-rows: repeat(4, auto);
		grid-template-columns: repeat(2, minmax(min-content, max-content));
	}
	dt {
		padding: 0.5em 1em;
		border-top: thin solid white;
		color: white;
		background: var(--color-main);
		text-align: right;
	}
	dt:first-child {
		border-top: none;
	}
	dd {
		border: thin solid var(--color-main);
		padding: 0.5em 1em;
	}
	dd:not(:last-child) {
		border-bottom: none;
	}
	.tabs ul {
		border-bottom: thin solid var(--color-main);
		display: flex;
		flex-direction: row;
		list-style-type: none;
		margin: 0;
	}
	.tabs input {
		display: none;
	}
	.tabs input[type="radio"] + label, .tabs div label, .tabs li .spinner {
		display: block;
		padding: 0.5em 1em;
	}
	.tabs li:first-child {
		border-left: thin solid var(--color-main);
	}
	.tabs li {
		border-top: thin solid var(--color-main);
		border-right: thin solid var(--color-main);
	}
	.tabs li.meta {
		align-items: center;
		border: none;
		display: flex;
	}
	.tabs input[type="radio"]:checked + label {
		background: var(--color-main);
		color: white;
	}

	.tabs .tab-selector {
		border: thin solid var(--color-main);
		display: grid;
		grid-template-columns: 1fr min-content min-content;
	}
	.tabs button {
		background: white;
		border: none;
		border-left: thin solid var(--color-main);
		height: 2.5rem;
		width: 2.5rem;
	}
	.spinner {
		display: inline-block !important;
		margin-left: 1em;
		height: 1rem;
		width: 1rem;
	}

	.cta {
		display: flex;
		justify-content: space-around;
		margin: 4rem 0 3rem 0;
		flex-direction: column;
		row-gap: 1em;
	}
	.medium .cta {
		flex-direction: row;
		row-gap: 0;
	}
</style>
