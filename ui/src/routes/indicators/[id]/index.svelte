<script context="module">
  export async function preload({ params: id, query }) {
    return id;
  }
</script>

<script>
  import * as _ from 'lamb';
  import {lookup} from 'app/data/groups';
  import {availableYearsStore, lookupStore} from 'app/stores';
  import {inclusiveRange} from 'app/utils';

  export let id;

  $: $availableYearsStore = inclusiveRange($lookupStore[id].year_range)
  $: makeRoutes = _.pipe([
    inclusiveRange,
    _.mapWith(year => [year, `/indicators/${id}/${year}`])
  ]);
  $: routes = makeRoutes(lookup[id].year_range);

  $: console.log('indicators/[id]/index.svelte: id =', id)
</script>

<ul>
  {#each routes as [year, href]}
  <li>
    <a
      rel='prefetch'
      {href}
    >
      <p>{year}</p>
    </a>
  </li>
  {/each}
</ul>
