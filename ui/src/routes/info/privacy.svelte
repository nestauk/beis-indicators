<script>
	import Link from '@svizzle/ui/src/Link.svelte';
	import theme from 'app/theme';

	const linkTheme = {
		color: theme.colorLink,
		iconStroke: theme.colorLink
	};
</script>

<section>
	<h2>Cookies and data privacy policy</h2>
	<p>
		Cookies are files saved on your phone, tablet or computer when you visit
		a website.
	</p>
	<p>
		We only use essential cookies on this website:
	</p>
	
	<ul>
		<li>the tool itself does not collect any personal data.</li>
		<li>
			the feedback form is using 
			<Link
				href='https://www.google.com/forms/about/'
				theme={linkTheme}
			>
				Google Forms
			</Link>
			, which installs cookies in your browser.
		</li>
	</ul>

	<p>
		By submitting data with Google Forms you accept the
		<Link
			href='https://policies.google.com/terms'
			theme={linkTheme}
		>
			Terms of Service
		</Link>
		and the 
		<Link
			href='https://policies.google.com/privacy'
			theme={linkTheme}
		>
			Data Privacy Policy of Google Inc
		</Link>.
	</p>
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
