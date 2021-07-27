<script>
	import Link from '@svizzle/ui/src/Link.svelte';
	import theme from 'app/theme';

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};
</script>

<section>
	<h2>Beta release</h2>
	<p>
		Welcome to the BEIS/Nesta Research & Development spatial data tool.
		The tool is currently in a Beta release and this build will remain
		unmaintained over the course of the summer to enable feedback to be
		gathered from live users.
	</p>
	
	<p>
		Please use the feedback form provided 
		<Link
			href='/info/feedback'
			theme={linkTheme}
		>
			here
		</Link>
		in the Feedback tab, or alternatively email your feedback to
		<Link
			href='mailto:dataanalytics@nesta.org.uk'
			theme={linkTheme}
		>
			dataanalytics@nesta.org.uk.
		</Link>
	</p>

	<p>Thanks!</p>
</section>

<style>
	section {
		background-color: white;
		max-width: 900px;
		overflow-y: auto;
		padding: 2rem;
	}
	h2 {
		font-weight: normal;
		margin-bottom: 1.5rem;
		margin-top: 1.5rem;
	}
	p {
		margin: 0.75rem 0;
	}
	ul {
		padding: 0.5rem 0 0.5rem 2rem;
	}
</style>
