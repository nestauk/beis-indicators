<script context="module">
  export async function preload({ params: id, query }) {
    return id;
  }
</script>

<script>
  import * as _ from 'lamb';
  import {inclusiveRange} from '@svizzle/utils';

  import {lookup} from 'app/data/groups';
  import {availableYearsStore, resetSelectedYear} from 'app/stores';

  export let id;

  $: id && resetSelectedYear();
  $: $availableYearsStore = inclusiveRange(lookup[id].year_range)
  $: makeRoutes = _.pipe([
    inclusiveRange,
    _.mapWith(year => [year, `/indicators/${id}/${year}`])
  ]);
  $: routes = makeRoutes(lookup[id].year_range);
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
