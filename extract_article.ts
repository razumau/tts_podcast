const { Readability } = require('@mozilla/readability');
const { JSDOM } = require('jsdom');
const fs = require('fs');

const url = process.argv[2];
const ARTICLE_FILE = process.argv[3] || 'extracted_article.txt';
const ARTICLE_TITLE_FILE = process.argv[4] || 'extracted_article_title.txt';

if (!url) {
    console.error('Provide a URL or local file path as an argument');
    process.exit(1);
}

async function extractContent(url: string) {
    const article_fd = fs.openSync(ARTICLE_FILE, 'w');
    const title_fd = fs.openSync(ARTICLE_TITLE_FILE, 'w');
    try {
        let dom: any;
        if (url.startsWith('http')) {
            // Not JSDOM.fromURL: jsdom 27+ fetches through undici's Dispatcher, which Bun's built-in undici lacks
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status} for ${url}`);
            }
            // Pass bytes rather than text so that jsdom detects the encoding, like fromURL did
            dom = new JSDOM(Buffer.from(await response.arrayBuffer()), {
                url: response.url,
                contentType: response.headers.get('content-type') ?? 'text/html',
            });
        } else {
            const fileContent = fs.readFileSync(url, 'utf8');
            dom = new JSDOM(fileContent);
        }
        const reader = new Readability(dom.window.document);
        const article = reader.parse();
        fs.writeFileSync(article_fd, article.textContent, 'utf8');
        fs.writeFileSync(title_fd, article.title, 'utf8');
    } catch (error: unknown) {
        if (error instanceof Error) {
            console.error('Error:', error.message);
        } else {
            console.error('An unknown error occurred');
        }
        process.exit(1);
    } finally {
        fs.closeSync(article_fd);
        fs.closeSync(title_fd);
    }
}

extractContent(url);
