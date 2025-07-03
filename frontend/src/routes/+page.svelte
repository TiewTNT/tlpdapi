<svelte:options runes />

<script>
  import { onMount, tick } from 'svelte';
  import { browser } from '$app/environment';

  // your existing state
  let advanced = $state(false);
  let files = $state([]);
  let format = $state("pdf");
  let format_image = $state("png");
  let dpi = $state(200);
  let compile_tool = $state("latexmk");
  let macro = $state("latex");
  let loading = $state(false);
  let engine = $state("pdflatex");
  let text = $state("Compile");
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
      await import('vanilla-colorful/rgba-color-picker.js');
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
    formData.append("macro", macro);
    formData.append("engine", engine);
    formData.append("bg_color", JSON.stringify(bg_color));

    const res = await fetch("/api", { method: "POST", body: formData });
    loading = false;
    compile_button.disabled = false;
    if (!res.ok) {
      const errText = await res.text();
      console.error("Server error:", errText);
      text = "Error";
      compile_button.classList.add("error");
      return;
    }
    const disposition = res.headers.get("Content-Disposition");
    let filename = "file";
    if (disposition) filename = disposition.split("filename=")[1].slice(1, -1);
    text = "Compile";
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const aEl = document.createElement("a");
    aEl.href = url;
    aEl.download = filename;
    document.body.appendChild(aEl);
    aEl.click();
    aEl.remove();
    URL.revokeObjectURL(url);
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

  <label class="custom-file-label" for="fileUpload">Select Files</label>
  <input
    id="fileUpload"
    type="file"
    multiple
    style="display:none"
    on:change={handleFiles}
  />

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

  <button name="compile_button" on:click={submit}>
    {#if loading}
      <img src="/loading.svg" alt="Loading..." />
    {:else}
      {text}
    {/if}
  </button>
</div>
