# Web Scraping Commands

The web scraping commands help you extract content from websites, particularly focusing on Markdown content.

## Available Commands

### Markdown Scraping

```bash
# Scrape Markdown content from a URL
craftsmanship scrape url https://example.com/docs

# Scrape entire documentation site
craftsmanship scrape site https://example.com/docs

# Save scraped content to local files
craftsmanship scrape url https://example.com/docs --output ./local-docs
```

## Scraping Options

The scrape commands support various options for controlling the scraping process:

| Option           | Description                                    |
|------------------|------------------------------------------------|
| `--depth`        | Maximum recursion depth for following links    |
| `--rate-limit`   | Rate limiting to avoid overwhelming sites      |
| `--concurrency`  | Number of concurrent requests                  |
| `--format`       | Output format (markdown, html, text)           |
| `--selector`     | CSS selector for targeting specific content    |
| `--timeout`      | Request timeout value                          |

## Content Processing

Processing scraped content:

```bash
# Extract specific sections
craftsmanship scrape url https://example.com/docs --selector ".main-content"

# Process content into specific format
craftsmanship scrape url https://example.com/docs --process format

# Extract and organize content
craftsmanship scrape site https://example.com/docs --organize by-section
```

## Authentication Support

Scraping content that requires authentication:

```bash
# Scrape with basic authentication
craftsmanship scrape url https://example.com/docs --auth basic --username user --password pass

# Use cookie-based authentication
craftsmanship scrape url https://example.com/docs --auth cookie --cookie-file ./cookies.json
```

## Monitoring and Reporting

Monitoring scraping progress:

```bash
# Scrape with detailed progress reporting
craftsmanship scrape site https://example.com/docs --verbose

# Generate scraping report
craftsmanship scrape site https://example.com/docs --report ./scrape-report.json
```

## Usage Examples

```bash
# Scrape documentation with depth limit
craftsmanship scrape site https://example.com/docs --depth 3 --output ./docs

# Extract specific content with rate limiting
craftsmanship scrape url https://example.com/api-docs --selector ".endpoint" --rate-limit 1
```