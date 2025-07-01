<script>
    import { onMount } from "svelte";
    let files = [];
    let format;
    let format_image;
    let dpi = 200;
    let compile_tool = "latexmk";
    let macro = "latex";
    let loading = false;
    let engine;
    let text = "Compile";
    let compile_button;
    onMount(() => {
        compile_button = document.getElementsByName("compile_button")[0];
    });
    async function submit() {
        compile_button.classList.remove("error");
        loading = true;
        compile_button.disabled = true;
        if (files.length === 0) {
            text = "Please select files to compile.";
            loading = false;
            return;
        }
        const formData = new FormData();
        for (const file of files) formData.append("files", file);
        formData.append("format", format);
        formData.append("format_image", format_image);
        formData.append("dpi", dpi);
        formData.append("compile_tool", compile_tool);
        formData.append("macro", macro);
        formData.append("engine", engine)

        const res = await fetch("http://127.0.0.1:8000/api", {
            method: "POST",
            body: formData,
        });
        loading = false;
        compile_button.disabled = false;

        if (!res.ok) {
            const errText = await res.text(); // <-- important!
            console.error("Server error:", errText);
            text = "Error";
            compile_button.classList.add("error");
            return;
        } else {
            text = "Compile";
            const blob = await res.blob();
            const url = URL.createObjectURL(blob);
            window.open(url);
        }
    }
    function handleFiles(e) {
        files = Array.from(e.target.files);
    }
</script>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Display:ital,wght@0,100..900;1,100..900&family=Noto+Serif:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">

<div class="centered-div">
    <h1>TXCPAPI</h1>
    <label class="custom-file-label" for="fileUpload">Select Files</label>
    <input
        id="fileUpload"
        style="display: none;"
        type="file"
        multiple
        on:change={handleFiles}
    />

    {#if files.length}
        <ul class="box">
            {#each files as file}
                <li>{file.name}</li>
            {/each}
        </ul>
    {/if}
    <select bind:value={format}>
        <option value="pdf">PDF</option>
        <option value="html">HTML</option>
        <option value="md">Markdown</option>
        <option value="txt">Text</option>
        <option value="raster">Raster</option>
    </select>

    {#if format === "raster"}
    <select bind:value={format_image}>
        <option value="png">PNG</option>
        <option value="jpg">JPG</option>
        <option value="webp">WebP</option>
    </select>

    <input
        type="number"
        bind:value={dpi}
        placeholder="DPI"
        min="5"
        max="600"
        step="1"
    />
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

    

    <!-- <select bind:value={compile_tool}>
        <option value="latexmk">LaTeXmk</option>
        <option value="manual">Manual</option>
    </select> Tools specification on frontend not supported -->


    <button name="compile_button" on:click={submit}>
        {#if loading}<img
                src="/loading.svg"
                alt="Loading..."
            />{:else}{text}{/if}
    </button>
</div>
