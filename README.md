# Awesome Discogs [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> [Discogs](https://www.discogs.com) is a crowdsourced database of music releases and a marketplace for physical media.

## Contents

- [Official Resources](#official-resources)
- [API Clients](#api-clients)
  - [.NET](#net)
  - [Go](#go)
  - [JavaScript](#javascript)
  - [PHP](#php)
  - [Python](#python)
  - [Rust](#rust)
  - [Swift](#swift)
- [Data Dump Tools](#data-dump-tools)
- [Command-Line Tools](#command-line-tools)
- [Collection Management](#collection-management)
- [Selling and Marketplace](#selling-and-marketplace)
- [Browser Extensions and Userscripts](#browser-extensions-and-userscripts)
- [Music Tagging](#music-tagging)
- [AI and MCP Servers](#ai-and-mcp-servers)
- [Analytics and Visualization](#analytics-and-visualization)

## Official Resources

- [API Documentation](https://www.discogs.com/developers) - REST API for the database, marketplace, collections, and wantlists.
- [API Forum](https://www.discogs.com/forum/topic/1082) - Official forum for API questions and announcements.
- [API Terms of Use](https://support.discogs.com/hc/en-us/articles/360009334593-API-Terms-of-Use) - Rules every application using the API must follow.
- [Data Dumps](https://data.discogs.com/) - Monthly XML exports of artists, labels, masters, and releases.
- [Discogs App](https://www.discogs.com/about/features/app/) - iOS and Android app with a barcode scanner, collection value, and wantlist (closed source).

## API Clients

### .NET

- [DiscogsApiClient](https://github.com/damidhagor/DiscogsApiClient) - Client for .NET 8 and later covering the database, collection, and wantlist, with OAuth or a personal token.
- [DiscogsConnect](https://github.com/christophdebaene/DiscogsConnect) - Client covering the database, collection, and wantlist with a personal token, without OAuth (source available).
- [ParkSquare.Discogs](https://www.parksq.co.uk/dotnet-core/discogs-csharp) - Read-only client for database search, masters, versions, and releases, with automatic paging (closed source).

### Go

- [go-discogs](https://github.com/adamvanw/go-discogs) - Maintained fork of irlndts/go-discogs, covering the database, search, collection, and marketplace with a personal token.
- [go-discogs-client](https://github.com/mrcl29/go-discogs-client) - Client covering the database, marketplace, inventory, collection, wantlist, and lists, with OAuth and automatic rate limiting.

### JavaScript

- [Discogs SDK](https://github.com/Cr8-audio/discogs-sdk) - Client limited to OAuth, collection, search, and identity that also runs on Cloudflare Workers (source available).
- [discogs-client](https://github.com/lionralfs/discogs-client) - Client for Node.js and browsers covering the full API, with OAuth.

### PHP

- [Discogs API Bundle for Symfony](https://github.com/calliostro/discogs-bundle) - Symfony bundle that provides php-discogs-api through dependency injection and autowiring.
- [discogs-api](https://github.com/JolitaGrazyte/discogs-api) - Guzzle 7 client that also runs on PHP 7.4, with a companion Laravel facade package.
- [php-discogs-api](https://github.com/calliostro/php-discogs-api) - Client for PHP 8.1 and later covering the database, marketplace, collection, and wantlist, with OAuth.

### Python

- [discogs-sdk](https://github.com/jmfontaine/discogs-sdk) - Client covering every documented endpoint, with chainable calls and response caching.
- [python3-discogs-client](https://github.com/joalla/discogs_client) - Most used client, the community continuation of the official one that Discogs deprecated in 2020, with OAuth.

### Rust

- [discogs-rs](https://github.com/yezizp2012/discogs-rs) - Async client covering the database, marketplace, inventory, and user endpoints, with OAuth.

### Swift

- [Discogs Service](https://github.com/rock-n-code/discogs-service) - Client for Swift 5.10 and later, with hosted reference documentation.
- [DiscogsKit](https://github.com/The-Amber-Team/DiscogsKit) - Client for Swift 6 on iOS 17, macOS 14, and later, with typed endpoints and OAuth through Authentication Services.

## Data Dump Tools

- [Discogs Data Processor CLI](https://github.com/ofurkancoban/DiscogsCLI) - Downloads the dumps, extracts them, and converts them to CSV (source available).
- [discogs-xml2db](https://github.com/philipmat/discogs-xml2db) - Converts the dumps to CSV and imports them into MySQL, PostgreSQL, or SQLite.
- [discogskit](https://github.com/jmfontaine/discogskit) - Converts the dumps to Parquet or JSONL, or loads them into SQLite or PostgreSQL.
- [Discogsography](https://github.com/SimplicityGuy/discogsography) - Loads the dumps into Neo4j and PostgreSQL to explore releases as a graph (source available).

## Command-Line Tools

- [discogs-cli](https://github.com/jesseward/discogs-cli) - Searches and shows artists, labels, and releases in a terminal.
- [Music Sync Toolbox](https://github.com/bolinocroustibat/music-sync-toolbox) - Syncs Spotify, YouTube Music, and local music files, with Discogs as the source of truth (source available).

## Collection Management

- [DISCODES](https://www.discodes.app/) - Web app that turns a collection or inventory CSV export into printable QR code labels (closed source).
- [Discographic](https://github.com/SimonBlancoE/discographic) - Self-hosted app to browse a collection, see its value and stats, and bulk-edit it, with edits synced back to Discogs.
- [Discographic for Discogs](https://apps.apple.com/us/app/discographic-for-discogs/id979196369) - iOS app to manage a collection, wantlist, and inventory offline, with Last.fm scrobbling (closed source).
- [Discogs Notification On New Items](https://github.com/KirianCaumes/Discogs-Notification-On-New-Items) - Script that sends email or Discord notifications of new items by chosen artists, by scraping the site's internal GraphQL API.
- [Discogs QR Code Generator](https://github.com/bollewolle/pydiscogsqrcodegenerator) - Web app that prints QR code stickers for the releases in a collection.
- [Discogs Sync](https://github.com/iamjoshk/discogs_sync) - Home Assistant integration with sensors for collection size, value, wantlist, and a random record.
- [discogs-spotify](https://github.com/martiriera/discogs-spotify) - Web app that turns a collection, wantlist, or list into a Spotify playlist (source available).
- [Discrobble](https://apps.apple.com/us/app/discrobble-vinyl-scrobbler/id6761305573) - iOS app that scrobbles records from a collection to Last.fm (paid, closed source).
- [My Vinyl+](https://apps.apple.com/us/app/my-vinyl-scanner-for-discogs/id1547173908) - iOS app that syncs a collection and wantlist, scans barcodes, and shows collection value (closed source).
- [NowSpinning](https://apps.apple.com/us/app/nowspinning-vinyl-collection/id6748545131) - iOS app that recognizes the record playing, logs the spin against the collection, and shows listening stats (closed source).
- [Record Scanner](https://apps.apple.com/us/app/record-scanner-vinyl-cd/id1507752204) - iOS app that identifies records from the cover, barcode, or catalog number and adds them to a collection (closed source).
- [VinylBox](https://vinylbox.app/) - iOS app to manage a collection and wantlist, scan barcodes, and list records on the marketplace (closed source).

## Selling and Marketplace

- [Discoger](https://github.com/beudbeud/discoger) - Telegram bot that alerts on new listings for followed releases and the wantlist, by scraping marketplace pages.
- [Discogs Alert](https://github.com/michaelhball/discogs_alert) - Near real-time alerts for wantlist items that go on sale, filtered by price, seller rating, condition, and country, by scraping marketplace pages.
- [Discogs Marketplace API NodeJS](https://github.com/KirianCaumes/Discogs-Marketplace-API-NodeJS) - Node.js library that searches marketplace listings by scraping the shop from a headless browser.
- [Discogs to WooCommerce](https://github.com/AlexanderHoll/discogs-to-woocommerce) - WordPress plugin that imports a seller inventory into WooCommerce and keeps stock in sync (source available).
- [Discogs Wantlist Marketplace Monitor](https://github.com/jch254/discogs-market-monitor) - Self-hostable AWS service that emails new wantlist listings from chosen countries, by scraping marketplace pages.
- [Disconnect](https://constacloud.com/disconnect/) - Syncs inventory, listings, and orders between Discogs and Shopify, WooCommerce, eBay, Amazon, and point-of-sale systems (paid, closed source).
- [Vinylscanner](https://vinylscanner.com/) - Recognizes records from a webcam or phone camera and lists them on Discogs with price suggestions (paid, closed source).

## Browser Extensions and Userscripts

- [Discogs - Sort by Total Price in Marketplace](https://greasyfork.org/en/scripts/461485-discogs-sort-by-total-price-in-marketplace) - Userscript that sorts marketplace listings by price plus shipping.
- [Discogs Edit Helper](https://greasyfork.org/en/scripts/562100-discogs-edit-helper) - Userscript that fills release edit forms from web stores and plain-text tracklists.
- [Discogs Enhancer](https://github.com/salcido/discogs-enhancer) - Chrome and Firefox extension that adds seller blocking, dark themes, price comparisons, and marketplace filters (source available).
- [Discogs Submitter](https://github.com/denis-g/userscript-discogs-submitter) - Userscript that turns release pages from Bandcamp, Qobuz, Beatport, and other stores into Discogs drafts.
- [MusicBrainz: Import from Discogs CSV](https://greasyfork.org/en/scripts/556207-musicbrainz-import-from-discogs-csv) - Userscript that adds the releases of a collection export to a MusicBrainz collection.

## Music Tagging

- [beets Discogs plugin](https://beets.readthedocs.io/en/stable/plugins/discogs.html) - Adds Discogs as a metadata source to the beets autotagger.
- [Discogger Tagger](https://github.com/ghDaYuYu/foo_discogger) - foobar2000 component that tags files with data from a chosen Discogs release (source available).
- [Jellyfin Discogs Plugin](https://github.com/jellyfin/jellyfin-plugin-discogs) - Adds Discogs as a metadata provider to Jellyfin.

## AI and MCP Servers

- [agent-discogs](https://github.com/jmfontaine/agent-discogs) - CLI for AI agents that keeps output short and API calls few.
- [Discogs MCP](https://github.com/rianvdm/discogs-mcp) - Self-deployed MCP server with OAuth to search a collection, get stats and recommendations, and edit the wantlist.
- [Discogs MCP Server](https://github.com/cswkim/discogs-mcp-server) - MCP server for database search, collections, wantlists, and the marketplace.

## Analytics and Visualization

- [Compare Discogs Collections](https://github.com/KirianCaumes/Compare-Discogs-Collections) - Web app that compares a collection or wantlist with another user's.
- [discogs-visualizer](https://github.com/kolorfilm/discogs-visualizer) - Web app that charts a seller's marketplace sales (source available).

## Related Lists

## Contributing

Contributions are welcome. Read the [contribution guidelines](CONTRIBUTING.md) first.

## Footnotes

Entries marked `(paid)` require payment for their main features. Entries marked `(source available)` publish their source code without an open source license. Entries marked `(closed source)` have no public source code. Unmarked tools are open source.
