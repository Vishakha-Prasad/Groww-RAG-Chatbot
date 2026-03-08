# Deployment Guide: Vercel

Follow these steps to deploy your Groww RAG Chatbot to [Vercel](https://vercel.com/).

## Prerequisites
1. A [GitHub](https://github.com/) account with the repository pushed.
2. A [Vercel](https://vercel.com/) account.

## Step 1: Create a New Project on Vercel
1. Log in to [Vercel](https://vercel.com/).
2. Click **+ New Project**.
3. Select **Import** next to your repository: `Groww-RAG-Chatbot`.
4. Click **Deploy**.

## Step 2: Configure Environment Variables
1. In your Vercel project dashboard, go to the **Settings** tab.
2. Click **Environment Variables**.
3. Add the following variables:
   - `GROQ_API_KEY`: (Your Groq API Key)
   - `GROQ_MODEL`: `llama-3.3-70b-versatile` (or your preferred model)
4. Click **Save**.

## Step 3: Deployment Strategy
Vercel automatically builds and deploys your project when you push to the `main` branch. 
> [!IMPORTANT]
> Because Vercel uses a serverless environment, there are some important considerations:
> 1. **No Background Scheduler**: The Phase 6 scheduler (`scheduler.py`) will **not** run on Vercel. Vercel functions are short-lived and cannot run as long-running daemons.
> 2. **Index Persistence**: The `index.pkl` file is bundled with your deployment. If you update the index locally and push, it will be updated on Vercel. However, any runtime updates to the index (e.g., if you were to trigger a crawl on Vercel) will be lost when the function instance is recycled.
> 3. **Logging**: Structured logs (`chat_events.jsonl`) will NOT persist on Vercel's ephemeral disk. Use Vercel's built-in **Logs** tab or a dedicated logging service (like Logtail or Axiom) for persistent observability.

## Step 4: Verify Deployment
1. Open the deployment URL provided by Vercel.
2. You should see the Chatbot UI.
3. Try a query: *"What is the expense ratio of HDFC Small Cap Fund?"*

---
## Recommended Deployment
For a production RAG system with scheduled refreshes and persistent logging, **Railway** (using `docker-compose.yml`) is the superior choice. Vercel is excellent for the front-end and the API, but less ideal for the background data refresh and file-based persistence components of this project.
