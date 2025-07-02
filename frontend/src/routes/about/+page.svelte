<div style="display:block;margin-left:auto;margin-right:auto;width:40%">
    <img src="/txcpapi.svg" class="txcpapi" alt="TXCPAPI" />
    <div style="text-align: justify;">
        <p>
            <strong>TXCPAPI</strong> is an API that uses TeXLive (along with all its packages) to compile your TeX files. It is not stable. It never will be. But if it works, it works. You upload your TeX file, and you get a PDF or another format of your choice in return. You can also upload a .zip file, but keep in mind that commands will be executed in the root directory of your zip, so be cautious. If you encounter a bug, deal with it—it might be fixed later, but no guarantees. This service also uses Poppler, Pandoc, and ImageMagick to convert your compiled PDF into other formats. The API is built with FastAPI, and the frontend is developed using Svelte. <br />
            <em>This service is NOT affiliated with TeXLive, its packages, Poppler, Pandoc, ImageMagick, FastAPI, or Svelte.</em>
        </p>
    </div>
    <br />

    <h2>Terms of Service (ToS)</h2>
    <ol>
        <li>1. Do not abuse the service.</li>
        <li>2. There is no guarantee of uptime or data retention.</li>
        <li>3. Do not upload malicious or illegal content.</li>
        <li>4. Usage may be logged for debugging and abuse prevention.</li>
        <li>5. The service may be changed or discontinued at any time.</li>
        <li>6. Your files may be stored indefinitely.</li>
        <li>
            7. The owner of this service <strong>will not be held responsible for any legal consequences resulting from a user's actions or use of this service.</strong>
        </li>
    </ol>
    <br/>
    <h2>Open Source Tools Used and Their Licenses</h2>
    <table>
        <thead>
            <tr>
                <th>Tool</th>
                <th>License</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td><a href="https://github.com/sveltejs/svelte">Svelte</a></td>
                <td>MIT</td>
            </tr>
            <tr>
                <td><a href="https://github.com/tiangolo/fastapi">FastAPI</a></td>
                <td>MIT</td>
            </tr>
            <tr>
                <td><a href="https://github.com/encode/uvicorn">Uvicorn</a></td>
                <td>BSD 3-Clause</td>
            </tr>
            <tr>
                <td><a href="https://docs.python.org/3/license.html">Python</a></td>
                <td>PSF</td>
            </tr>
            <tr>
                <td><a href="https://www.tug.org/texlive/copying.html">TeX Live</a></td>
                <td>Collection of free software licenses (GPL, LPPL, etc.)</td>
            </tr>
            <tr>
                <td><a href="https://poppler.freedesktop.org/">Poppler</a></td>
                <td>GPL</td>
            </tr>
            <tr>
                <td><a href="https://github.com/jgm/pandoc/blob/main/COPYING">Pandoc</a></td>
                <td>GPL 2.0</td>
            </tr>
            <tr>
                <td><a href="https://github.com/ImageMagick/ImageMagick/blob/main/LICENSE">ImageMagick</a></td>
                <td>ImageMagick License</td>
            </tr>
        </tbody>
    </table>
</div>
