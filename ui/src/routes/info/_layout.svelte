<script>
	import * as _ from 'lamb';
	import {_screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';

	import ChevronLeft from '@svizzle/ui/src/icons/feather/ChevronLeft.svelte';
	import ChevronRight from '@svizzle/ui/src/icons/feather/ChevronRight.svelte';
	import Icon from '@svizzle/ui/src/icons/Icon.svelte';
	import Link from '@svizzle/ui/src/Link.svelte';

	import {isNotNil} from '@svizzle/utils';
	import {toolName} from 'app/config';
	import theme from 'app/theme';

	const links = {
		beta: 'Beta release',
		privacy: 'Privacy',
		disclaimer: 'Disclaimer',
		feedback: 'Feedback',
	}
	const segments = _.keys(links);

	export let segment;

	$: currentValueIndex = _.findIndex(
		segments,
		_.is(segment)
	);
	$: prevSegment = segments[currentValueIndex - 1];
	$: nextSegment = segments[currentValueIndex + 1];
	$: hasPrevSegment = isNotNil(prevSegment);
	$: hasNextSegment = isNotNil(nextSegment);
</script>

<svelte:head>
	<title>EURITO - Info</title>
	<meta
		name='description'
		content='All about accessibility in {toolName}, including a guide on how to enable the accessibility dialog, accessibility audit and other quality audits, plus some pointers to setup various accessibility tools on your system'
	>
</svelte:head>

<main class={$_screen?.classes}>
	<section>
		<h1>App information</h1>
		<menu class='tabs'>
			{#if $_screen?.sizes?.medium}
				<ul>
					{#each segments as id}
						<li
							class:selected={segment === id}
						>
							<Link
								href='/info/{id}'
								theme={{
									color: segment === id ? 'white' : theme.colorLink,
								}}
							>
								<span>
									{links[id]}
								</span>
							</Link>
						</li>
					{/each}
				</ul>
			{:else}
				<div class='tab-selector'>
					<label for=''>
						{links[segment]}
					</label>

					<div>
						<Link
							href={hasPrevSegment && `/info/${prevSegment}`}
							theme={{
								color: hasPrevSegment ? theme.colorLink : 'gray',
							}}
						>
							<Icon glyph={ChevronLeft} />
						</Link>
					</div>
					<div>
						<Link
							href={hasNextSegment && `/info/${nextSegment}`}
							theme={{
								color: hasNextSegment ? theme.colorLink : 'gray',
							}}
						>
							<Icon glyph={ChevronRight} />
						</Link>
					</div>
				</div>
			{/if}
		</menu>
		<slot />
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
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
		width: 100%;
	}

	h1 {
		font-weight: bold;
	}

	ul {
		list-style: initial;
		margin-left: 20px;
	}

	.tabs {
		user-select: none;
	}
	.tabs ul {
		display: flex;
		flex-direction: row;
		justify-content: center;
		list-style-type: none;
		margin: 3rem 0 1rem 0;
	}
	.tab-selector label{
		display: block;
		padding: 0.5em 1em;
	}
	.tab-selector div {
		padding: 0.5em 0.5em;
		border-left: thin solid var(--color-main);
	}
	.tabs li {
		border-bottom: thin solid var(--color-main);
		border-top: thin solid var(--color-main);
		border-right: thin solid var(--color-main);
	}
	.tabs li:first-child {
		border-left: thin solid var(--color-main);
	}
	.tabs li.selected {
		background: var(--color-main);
	}

	.tabs li span {
		display: block;
		padding: 0.5em 1em;
	}

	.tabs .tab-selector {
		border: thin solid var(--color-main);
		display: grid;
		grid-template-columns: 1fr min-content min-content;
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
</style>
