<svelte:options runes />

<script>
  import { onMount, tick } from "svelte";
  import { browser } from "$app/environment";

  // your existing state
  let advanced = $state(false);
  let files = $state([]);
  let format = $state("pdf");
  let format_image = $state("png");
  let dpi = $state(200);
  let compile_tool = $state("latexmk");
  let compile_path = $state("/");
  let macro = $state("latex");
  let loading = $state(false);
  let engine = $state("pdflatex");
  let text = $state("Compile");
  let raster_plasma = $state(false);
  let invert = $state(false);
  let compile_button;

  // RGBA picker state
  let bg_color = $state({ r: 255, g: 255, b: 255, a: 1 });
  let picker = $state();

  function handleColorChange(e) {
    bg_color = e.detail.value;
  }

  onMount(async () => {
    // SSR guard + dynamic import
    if (browser) {
      await import("vanilla-colorful/rgba-color-picker.js");
      await tick();
      if (picker) picker.color = bg_color;
    }
    // grab your compile button once
    compile_button = document.querySelector("button[name='compile_button']");
  });

  function handleFiles(e) {
    files = Array.from(e.target.files);
  }

  async function submit() {
    compile_button.classList.remove("error");
    loading = true;
    compile_button.disabled = true;
    if (!files.length) {
      text = "Please select files to compile.";
      loading = false;
      compile_button.disabled = false;
      return;
    }
    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));
    formData.append("format", format);
    formData.append("format_image", format_image);
    formData.append("dpi", dpi);
    formData.append("compile_tool", compile_tool);
    formData.append("compile_folder", compile_path);
    console.log("compile_path:", compile_path);
    formData.append("macro", macro);
    formData.append("engine", engine);
    formData.append("bg_color", JSON.stringify(bg_color));
    formData.append("raster_plasma", raster_plasma);
    formData.append("invert", invert);

    const res = await fetch("/api", { method: "POST", body: formData });
    loading = false;
    compile_button.disabled = false;
    const contentType = res.headers.get("Content-Type");

    if (contentType && contentType.includes("application/json")) {
      const data = await res.json();
      if (!res.ok) {
        console.error("Error:", data);
        text = "Error: " + (data.error || "Unknown error");
        compile_button.classList.add("error");
        return;
      }
      // If you get here and it's JSON + OK, you're probably not using this path anyway.
    } else {
      // Not JSON — probably a file
      const blob = await res.blob();
      const disposition = res.headers.get("Content-Disposition");
      let filename = "download";
      if (disposition) {
        const match = disposition.match(/filename="?([^"]+)"?/);
        if (match) filename = match[1];
      }

      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    }
  }
</script>

<!-- Markup -->
<label class="advanced">
  {#if !advanced}
    <span style="background-color: var(--element-bg);"></span>
  {:else}
    <span style="background-color: var(--primary-color);">
      <img src="/check.svg" alt="Checked" />
    </span>
  {/if}
  <input type="checkbox" style="display:none" bind:checked={advanced} /> Advanced
</label>

<div class="centered-div">
  <img src="/txcpapi.svg" class="txcpapi" alt="TXCPAPI" />

  <label class="custom-file-label"
    >Select Files
    <input
      id="fileUpload"
      type="file"
      multiple
      style="display:none"
      on:change={handleFiles}
    />
  </label>

  {#if files.length}
    <ul class="box">
      {#each files as f}
        <li>{f.name}</li>
      {/each}
    </ul>
  {/if}

  <select bind:value={format}>
    <option value="pdf">PDF</option>
    {#if advanced}
      <option value="html">HTML</option>
      <option value="md">Markdown</option>
      <option value="txt">Text</option>
    {/if}
    <option value="raster">Raster</option>
  </select>

  {#if format === "raster"}
    <select bind:value={format_image}>
      <option value="png">PNG</option>
      <option value="jpg">JPG</option>
      {#if advanced}
        <option value="webp">WebP</option>
        <option value="gif">GIF</option>
      {/if}
    </select>

    {#if advanced}
      <input
        type="number"
        bind:value={dpi}
        placeholder="DPI"
        min="20"
        max="600"
      />

      {#if browser}
        <rgba-color-picker
          class="bg-picker"
          bind:this={picker}
          color={bg_color}
          on:color-changed={handleColorChange}
        />
      {/if}
      <label class="checkbox">
        {#if !raster_plasma}
          <span style="background-color: var(--element-bg);">
            <img src="/empty_checkbox.svg" alt="Unchecked" />
          </span>
        {:else}
          <span style="background-color: var(--primary-color);">
            <img src="/check.svg" alt="Checked" />
          </span>
        {/if}
        <input
          type="checkbox"
          style="display:none"
          bind:checked={raster_plasma}
        /> Noise
      </label>
      <label class="checkbox">
        {#if !invert}
          <span style="background-color: var(--element-bg);">
            <img src="/empty_checkbox.svg" alt="Unchecked" />
          </span>
        {:else}
          <span style="background-color: var(--primary-color);">
            <img src="/check.svg" alt="Checked" />
          </span>
        {/if}
        <input
          type="checkbox"
          style="display:none"
          bind:checked={invert}
        /> Invert
      </label>
    {/if}
  {/if}

  <select bind:value={macro}>
    <option value="latex">LaTeX</option>
    <option value="context">ConTeXt</option>
  </select>

  {#if macro === "latex"}
    <select bind:value={engine}>
      <option value="pdflatex">PDFLaTeX</option>
      <option value="lualatex">LuaLaTeX</option>
      <option value="xelatex">XeLaTeX</option>
    </select>
  {/if}

  {#if advanced}
    <input type="text" placeholder="Compile path" bind:value={compile_path}/>
  {/if}

  <button name="compile_button" on:click={submit}>
    {#if loading}
      <img src="/loading.svg" alt="Loading..." />
    {:else}
      {text}
    {/if}
  </button>
</div>
