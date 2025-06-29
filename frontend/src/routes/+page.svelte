<script>
    let files = [];
    let format;
    let format_image;
    let dpi;
    async function submit() {
        const formData = new FormData();
        for (const file of files) formData.append("files", file);
        formData.append("format", format);
        formData.append("format_image", format_image);

        const res = await fetch("http://localhost:8000/api", {
            method: "POST",
            body: formData,
        });
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        window.open(url);
    }
    function handleFiles(e) {
        files = Array.from(e.target.files);
    }
</script>

<div class="centered-div">
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

    <button on:click={submit}>Compile</button>
</div>
