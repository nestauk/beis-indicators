<script context="module">
	import {basename} from 'app/utils';

	export async function preload() {
		return this.redirect(302, `/data/${basename}.zip`);
	}
</script>
