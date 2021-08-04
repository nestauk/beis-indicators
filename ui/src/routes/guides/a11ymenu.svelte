<script>
	import {_screen}
		from '@svizzle/ui/src/gauges/screen/ScreenGauge.svelte';
	import {toolName} from 'app/config';
</script>

<svelte:head>
	<title>Accessibility menu guide - {toolName}</title>
	<meta
		content='{toolName}: Accessibility menu guide'
		name='description'
	>
</svelte:head>

<section>
	<h2>What the accessibility menu does</h2>

	<p>
		You can use the menu to change two groups of features.
	</p>

	<h3>Text features</h3>

	<p>You can change:</p>

	<ul>
		<li>
			the font (in particular we provide a font specific to help
			people with Dyslexia),
		</li>
		<li>the font size,</li>
		<li>
			the line height (distance between lines of text in a paragraph),
		</li>
		<li>the letter spacing (distance between letters in a word),</li>
		<li>the word spacing (distance between words).</li>
	</ul>

	<h3>Color features</h3>

	<p>You can:</p>

	<ul>
		<li>invert all the colors in the app,</li>
		<li>
			select a color vision deficiency: this will remap all the colors
			in the app to compensate for a diminished ability to see certain
			colors,
		</li>
		<li>
			edit the hue of all the colors in the app,
		</li>
		<li>
			edit the saturation of all the colors in the app (by editing
			their level of grey),
		</li>
		<li>edit the brightness of all the colors in the app,</li>
		<li>edit the contrast of all the colors in the app.</li>
	</ul>

	<h2>How to use the menu</h2>

	<h3>How to toggle the menu on/off</h3>

	<p>
		To show or hide the menu, you need to click the accessibility
		icon in the top-right corner of the app.
	</p>

	<h3>Where to find the menu</h3>

	{#if $_screen?.sizes.medium}
		<p>
			The menu should appear at the center of the screen
			sligthly toward the bottom.
		</p>
	{:else}
		<p>
			The menu should appear below the navigation header, near the
			thumb.
		</p>
	{/if}

	<h3>How to navigate the menu</h3>

	<p>The menu is composed of three sections:</p>

	<ul>
		<li>
			the main area, in the center, shows the controls to manipulate a
			certain feature,
		</li>
		<li>
			on the right, you have two buttons to navigate to the previous
			or next feature,
		</li>
		<li>
			on the left, you have two buttons to reset all the features of a
			particular group (text or color).
		</li>
	</ul>

	<h3>Editing features</h3>

	<h4>List of values</h4>

	<p>
		When you have a list of options, you might get presented with a
		series of radio buttons. For small screens, the list of radio
		buttons will be just two buttons:
	</p>

	<ul>
		<li>for numeric values, these will be a plus and a minus button</li>
		<li>
			otherwise, these will be two left/right arrows that navigate to
			the previous/next option, respectively.
		</li>
	</ul>

	<p>For example, you can choose multiple font sizes.</p>

	<h4>Pair of values</h4>

	<p>
		When you have only two opposite options you get presented with a
		switch.
	</p>

	<p>For example, you can invert all colors of the app, or not.</p>

	<h4>Range of values</h4>

	<p>
		When the feature you are editing is defined by a numerical range,
		you can select any value in between the range extent using a slider.
	</p>

	<p>
		For example, you can change the saturation gradually, from no change
		to grey.
	</p>
</section>

<style>
	section {
		background-color: white;
		max-width: 900px;
		overflow-y: auto;
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
	h4 {
		color: var(--color-main);
		font-style: italic;
	}

	p {
		margin: 0.75rem 0;
	}

	ul {
		padding: 0.5rem 0 0.5rem 2rem;
	}
</style>
