# Reference samples

Real files to look at when a figure needs a precedent.
Never read a scene whole into context: open it on excalidraw.com, or read only what you need with a short script (element count, texts, colors).
None of these is a template: templates are in `examples/`, already sized for the 666px column with site tokens.

## `owner/`: the owner's business-diagram samples

19 PlantUML sources the owner wrote and converted with excaliplant, plus the guide `excalidraw-master-guide.md` (Vietnamese) that lists sources, lessons and errors met.
Templates 21 to 25 are redrawn from samples 01, 08, 09, 13 and 14.

| Read when | Files |
|---|---|
| Sequence with branches, auth flows, saga | `01-checkout-sequence` `04-login-sequence` `07-cache-aside-sequence` `10-oauth2-pkce-sequence` `12-saga-orchestration-sequence` |
| Activity or swimlane | `02-order-activity` `05-password-reset-activity` `09-leave-approval-swimlane` |
| State and composite state | `03-order-state` `06-pull-request-state` `13-payment-composite-state` |
| ER | `08-ecommerce-er` |
| Deployment and system design | `11-microservices-deployment` `14-url-shortener-system` `15-notification-system` `16-news-feed-system` `17-chat-system` `18-cqrs-event-sourcing` `19-analytics-pipeline` |

The `.puml` files hold the facts of each flow in a few lines: a good input for step 2 of the workflow.
The rendered samples are 1,400 units wide, so do not copy their layout.

## `prakash-sa/`: 43 system-design scenes

From github.com/Prakash-sa/system-design-ultimatum, CC BY 4.0 (`LICENSE.md`).
Reusing or adapting a scene in published work needs the credit "Prakash Saini, system-design-ultimatum, CC BY 4.0".

| Topic | Files |
|---|---|
| Building blocks | `load-balancer` `redis` `kafka` `rate-limiter` `communication-patterns` `database-strategies` `distributed-transactions` `data-structure` |
| Classic designs | `tiny-url` `web-crawler` `price-tracker` `price-checking-system` `sso` `auth-system` |
| Social and messaging | `chat-system-messaging` `whatsapp` `newsfeed` `facebook-newsfeed` `twitter-tweets-timelines` `ticketmaster` `tinder` `donation-drive` `facebook-live-comments` |
| Search and location | `search-auto-complete` `facebook-post-search` `proximity-service` `nearby-friends` `google-maps` `uber` `local-delivery-service` |
| Data and streaming | `ad-click-aggregator` `top-k-leaderboard` `top-k-youtube-videos` `log-ingestion-service` `batch-inference-system` `leetcode-online-coding-competition` |
| Storage and media | `file-storage-dropbox-google-drive` `google-photos` `youtube-video-hosting-streaming` |
| Other | `distributed-job-scheduler-airflow-temporal-celery` `chatgpt` `rag-chatbot` `system-design-all` |

What these scenes teach (already distilled into the rules): numbered arrows with a step list beside the figure, standing and lying cylinders, note cards, one color per section.
What not to copy: the median scene is about 2,800 units wide (most between 1,700 and 4,000) and would shrink to unreadable text in the site column.
