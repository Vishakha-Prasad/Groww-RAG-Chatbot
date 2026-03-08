# Deployment Guide: Railway

Follow these steps to deploy your Groww RAG Chatbot to [Railway](https://railway.app/).

## Prerequisites
1. A [GitHub](https://github.com/) account with the repository pushed.
2. A [Railway](https://railway.app/) account.

## Step 1: Create a New Project on Railway
1. Log in to [Railway](https://railway.app/).
2. Click **+ New Project**.
3. Select **Deploy from GitHub repo**.
4. Choose your repository: `Groww-RAG-Chatbot`.
5. Click **Deploy Now**.

## Step 2: Configure Environment Variables
Railway will attempt to build the project, but it will fail initially because the API keys are missing.
1. In your Railway project dashboard, click on the **chatbot** service.
2. Go to the **Variables** tab.
3. Add the following variables:
   - `GROQ_API_KEY`: (Your Groq API Key)
   - `GROQ_MODEL`: `llama-3.3-70b-versatile` (or your preferred model)
   - `PORT`: `8000`

## Step 3: Configure Persistent Storage (Volumes)
Since the chatbot uses local files for the knowledge base (`index.pkl`) and logs, you should use a Railway Volume if you want data to persist across redeploys.
1. Go to the **Settings** tab of your service.
2. Scroll down to **Volumes**.
3. Click **Add Volume**.
4. Set the Mount Path to `/app/phase-2-knowledge-base` (or specifically for the index).
   > [!NOTE]
   > For simple usage, Railway will keep files in the temporary container disk, but they will be lost if the service restarts. For production, consider using a Volume.

## Step 4: Expose the Service
1. In the **Settings** tab, find the **Networking** section.
2. Click **Generate Domain**. This will give you a public URL (e.g., `groww-rag-chatbot-production.up.railway.app`).

## Step 5: Custom Domain Setup (Optional)
If you have your own domain (e.g., `chatbot.yourdomain.com`), follow these steps:
1. In the **Settings** tab, find the **Networking** section.
2. Click **+ Custom Domain**.
3. Enter your domain name and click **Add**.
4. Railway will provide a **DNS Target** (usually your Railway app's default URL).
5. Go to your domain registrar (GoDaddy, Namecheap, Google Domains, etc.).
6. Add a **CNAME record**:
   - **Host/Name**: `chatbot` (or `@` for root)
   - **Value/Target**: (The DNS Target provided by Railway)
7. Wait for DNS propagation (can take from a few minutes to 24 hours). Railway will automatically provision an SSL certificate once the domain is linked.

## Step 6: Verify Deployment
1. Open the generated domain or your custom domain in your browser.
2. You should see the Chatbot UI.
3. Try a query: *"What is the expense ratio of HDFC Small Cap Fund?"*

## Running the Refresh Worker (Optional)
If you want the background scheduler to run on Railway:
1. Click **+ New** in your project dashboard.
2. Select **GitHub Repo** -> `Groww-RAG-Chatbot` again.
3. In the **Settings** for this new service, rename it to `refresh-worker`.
4. Go to **Deploy** -> **Start Command** and set it to:
   `python phase-6-scheduler-refresh/scheduler.py --daemon --interval 24`
5. Share the same **Volumes** as the chatbot service to ensure the index is updated in the same place.

---
**Tips:**
- Check the **Deployments** tab for build logs if searching for errors.
- Use the **Railway CLI** (`railway up`) for even faster local-to-cloud deployments.
