<script context="module">
	import {basename} from 'app/utils/assets';

	export async function preload() {
		return this.redirect(302, `/data/${basename}.zip`);
	}
</script>
