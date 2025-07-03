<script>
	import "../app.css";
	import { page } from "$app/stores";
	import { derived } from "svelte/store";

	const currentPath = derived(page, ($page) => $page.url.pathname);

	const navItems = [
		{ href: "/", label: "Home" },
		{ href: "/about", label: "About" },
	];
</script>

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
	href="https://fonts.googleapis.com/css2?family=Noto+Sans:ital,wght@0,100..900;1,100..900&display=swap"
	rel="stylesheet"
/>

<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link
	href="https://fonts.googleapis.com/css2?family=Noto+Serif+Display:ital,wght@0,100..900;1,100..900&display=swap"
	rel="stylesheet"
/>

<div class="min-h-screen pb-20 overflow-auto">
  <slot />
</div>

<nav>
  {#each navItems as item}
    <a
      href="{item.href}"
      class:selected={$page.url.pathname === item.href}
    >
      {item.label}
    </a>
  {/each}
</nav>

