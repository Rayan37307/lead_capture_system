# Facebook Messenger Integration Guide

This guide provides a comprehensive overview of how to integrate Facebook Messenger into your application, focusing on setting up a bot with multi-tenant support and product search functionality.

## Table of Contents
1.  [Introduction](#1-introduction)
2.  [Prerequisites](#2-prerequisites)
3.  [Step-by-Step Integration](#3-step-by-step-integration)
    *   [3.1 Create a Facebook Page](#31-create-a-facebook-page)
    *   [3.2 Create a Facebook Developer Account](#32-create-a-facebook-developer-account)
    *   [3.3 Create a New Facebook App](#33-create-a-new-facebook-app)
    *   [3.4 Add Messenger Product to Your App](#34-add-messenger-product-to-your-app)
    *   [3.5 Set Up Webhooks](#35-set-up-webhooks)
    *   [3.6 Generate a Page Access Token](#36-generate-a-page-access-token)
    *   [3.7 Implement Your Webhook Endpoint (Backend)](#37-implement-your-webhook-endpoint-backend)
    *   [3.8 Subscribe Your App to the Page](#38-subscribe-your-app-to-the-page)
4.  [Multi-Tenant Configuration](#4-multi-tenant-configuration)
5.  [Product Search Integration](#5-product-search-integration)
6.  [Testing Your Integration](#6-testing-your-integration)
7.  [Going Live](#7-going-live)
8.  [Conclusion and Next Steps](#8-conclusion-and-next-steps)

---

## 1. Introduction

Facebook Messenger is a powerful platform for direct communication with your audience. Our integration allows you to build advanced chatbots with multi-tenant support and product search capabilities. This guide will walk you through the essential steps to connect your application with the Messenger platform.

## 2. Prerequisites

Before you begin, ensure you have the following:

*   A **Facebook Account**: Required to manage pages and developer apps.
*   A **Facebook Page**: Your bot will be linked to a specific Facebook Page.
*   A **Facebook Developer Account**: You'll need access to the Facebook Developer Dashboard.
*   A **Server/Hosting Environment**: To host your webhook endpoint (e.g., a simple web server with a public URL). Tools like `ngrok` can be useful for local development and testing.
*   **Basic Programming Knowledge**: Familiarity with a web framework (e.g., FastAPI, Flask, Node.js Express) will be helpful for implementing the webhook.
*   **Tenant ID**: You must have a valid tenant ID for your multi-tenant setup.

## 3. Step-by-Step Integration

### 3.1 Create a Facebook Page

If you don't already have one, create a new Facebook Page that your bot will represent. This is where users will interact with your bot.

1.  Go to [facebook.com/pages/create](https://www.facebook.com/pages/create).
2.  Follow the instructions to create your page.

### 3.2 Create a Facebook Developer Account

1.  Go to [developers.facebook.com](https://developers.facebook.com/).
2.  Click "Get Started" and follow the registration process to become a developer.

### 3.3 Create a New Facebook App

Your bot's functionality will live within a Facebook App.

1.  Go to the [Facebook Developer Dashboard](https://developers.facebook.com/apps/).
2.  Click "Create App".
3.  Choose the app type that best suits your needs. For a bot, "Business" is often appropriate.
4.  Provide an app display name and contact email.
5.  Link your Business Manager account if applicable, then click "Create App".

### 3.4 Add Messenger Product to Your App

1.  From your app's dashboard, scroll down to "Add a Product".
2.  Find "Messenger" and click "Set Up".

### 3.5 Set Up Webhooks

Webhooks are how Facebook tells your application when a user sends a message or interacts with your bot.

1.  In your app dashboard, navigate to "Messenger" -> "Settings".
2.  Scroll down to the "Webhooks" section and click "Add Callback URL".
3.  **Callback URL**: This is the public URL of your server endpoint that will receive updates from Facebook. During development, you can use `ngrok` to expose your local server to the internet (e.g., `https://your-ngrok-url.ngrok.io/api/v1/messenger/` for single webhook approach or `https://your-ngrok-url.ngrok.io/api/v1/messenger/{tenant_id}` for tenant-specific approach).
4.  **Verify Token**: This is a string you define. Facebook will send this token back to your endpoint during the verification process. Your endpoint needs to return this token to confirm it's legitimate. **Keep this token secret!**
5.  Click "Verify and Save".

### 3.6 Generate a Page Access Token

Your application needs a Page Access Token to send messages back to users through your Facebook Page.

1.  In your app dashboard, under "Messenger" -> "Settings", find the "Access Tokens" section.
2.  Select the Facebook Page you linked in Step 3.1 from the dropdown menu.
3.  Click "Generate Token".
4.  Copy this token. **Treat this token like a password and keep it secure.** You will use it in your backend code to authenticate API calls to Facebook.

### 3.7 Implement Your Webhook Endpoint (Backend)

Our system provides two approaches for Facebook Messenger integration with multi-tenant support and product search capabilities:

**Approach 1: Single Webhook with Tenant Mapping**
- Endpoint: `/api/v1/messenger/`
- Uses a single webhook URL for all tenants
- Automatically determines tenant based on Facebook Page ID
- Requires mapping Facebook Page IDs to tenant IDs

**Approach 2: Tenant-Specific Webhooks** 
- Endpoint: `/api/v1/messenger/{tenant_id}`
- Separate webhook URL for each tenant
- Explicit tenant ID in the URL path

Your server needs to handle two types of requests from Facebook:

1.  **Webhook Verification (GET request)**: When you set up the webhook, Facebook sends a `GET` request to your `Callback URL` with `hub.mode`, `hub.challenge`, and `hub.verify_token` parameters. Your endpoint must:
    *   Check if `hub.mode` is `subscribe`.
    *   Check if `hub.verify_token` matches your secret `Verify Token` from Step 3.5.
    *   If both are true, return the `hub.challenge` value.
2.  **Receiving Messages (POST request)**: Once verified, Facebook sends `POST` requests to your `Callback URL` with message payloads when users interact with your page. Our system handles:
    *   Parsing the incoming JSON payload.
    *   Extracting message details (sender ID, message text).
    *   Processing the message with AI and product search capabilities.
    *   Managing lead data with multi-tenant isolation.
    *   Sending responses back to users.

### 3.8 Subscribe Your App to the Page

Finally, you need to tell Facebook which events your app should subscribe to for your linked Page.

1.  In your app dashboard, under "Messenger" -> "Settings", scroll down to the "Webhooks" section.
2.  Click "Add Subscriptions" for the Page you linked.
3.  Select the events you want to receive. For a basic bot, `messages` and `messaging_postbacks` are common starting points.
4.  Click "Save".

## 4. Multi-Tenant Configuration

Our system implements strict multi-tenant architecture with two configuration options:

**Option 1: Single Webhook with Page-to-Tenant Mapping**
*   **Configuration**: One webhook URL serves all tenants
*   **Tenant Resolution**: System determines tenant based on Facebook Page ID
*   **Setup**: Map Facebook Page IDs to tenant IDs in the system
*   **URL**: `/api/v1/messenger/`

**Option 2: Tenant-Specific Webhooks**
*   **Configuration**: Separate webhook URL for each tenant
*   **Tenant Resolution**: Tenant ID specified in URL path
*   **Setup**: Configure separate webhook for each tenant
*   **URL**: `/api/v1/messenger/{tenant_id}`

**Common Features**:
*   **Tenant Isolation**: Each tenant has separate data storage and product catalogs.
*   **Database Files**: Each tenant has their own SQLite database file in `tenant_data/{tenant_id}.db`
*   **Product Catalogs**: Each tenant has their own product JSON file in `data_center/{tenant_id}.json`
*   **Data Privacy**: Tenants cannot access each other's data or product catalogs.

## 5. Product Search Integration

The bot includes advanced product search capabilities:

*   **Fuzzy Search**: Uses fuzzy string matching to find relevant products even with typos or partial matches.
*   **Natural Language Queries**: Users can search using phrases like "Show me CeraVe moisturizers" or "Find facial cleansers".
*   **Multi-Category Search**: Searches across product names, descriptions, categories, and brands.
*   **Rich Product Information**: Displays product names, prices, descriptions, and images in chat responses.
*   **Tenant-Specific Catalogs**: Each tenant can only search within their own product catalog.

## 6. Testing Your Integration

**For Option 1: Single Webhook with Page-to-Tenant Mapping**
1.  **Set up `ngrok` (if developing locally)**: Run `ngrok http 8000` (or your chosen port) to get a public URL for your local server. Update your Facebook webhook callback URL with this `ngrok` URL: `https://your-ngrok-url.ngrok.io/api/v1/messenger/`.
2.  **Configure Environment Variables**: Ensure your `.env` file contains the required Facebook Messenger settings:
   ```
   FB_PAGE_ACCESS_TOKEN=your_page_access_token
   FB_APP_SECRET=your_app_secret
   FB_WEBHOOK_VERIFY_TOKEN=your_verify_token
   ```
3.  **Configure Page-to-Tenant Mapping**: Update the `get_tenant_for_page()` function in `messenger.py` to map your Facebook Page ID to your tenant ID.
4.  **Send a message**: As a user (who has a role in your Facebook App or is a test user for your app), go to your Facebook Page and send a message.
5.  **Check your server logs**: You should see your server receiving the webhook event and processing the message with AI and product search.
6.  **Test Product Search**: Try sending product search queries like "Show me moisturizers" or "Find CeraVe products".
7.  **Check Messenger**: You should receive the bot's intelligent response with relevant product information.

**For Option 2: Tenant-Specific Webhooks**
1.  **Set up `ngrok` (if developing locally)**: Run `ngrok http 8000` (or your chosen port) to get a public URL for your local server. Update your Facebook webhook callback URL with this `ngrok` URL, including your tenant ID: `https://your-ngrok-url.ngrok.io/api/v1/messenger/YOUR_TENANT_ID`.
2.  **Configure Environment Variables**: Ensure your `.env` file contains the required Facebook Messenger settings:
   ```
   FB_PAGE_ACCESS_TOKEN=your_page_access_token
   FB_APP_SECRET=your_app_secret
   FB_WEBHOOK_VERIFY_TOKEN=your_verify_token
   ```
3.  **Send a message**: As a user (who has a role in your Facebook App or is a test user for your app), go to your Facebook Page and send a message.
4.  **Check your server logs**: You should see your server receiving the webhook event and processing the message with AI and product search.
5.  **Test Product Search**: Try sending product search queries like "Show me moisturizers" or "Find CeraVe products".
6.  **Check Messenger**: You should receive the bot's intelligent response with relevant product information.

## 7. Going Live

Before your bot can interact with anyone other than developers and test users, your app needs to undergo App Review by Facebook. You'll need to submit your app for review for the `pages_messaging` permission (and any other permissions your bot uses) and provide a clear explanation and demo of its functionality.

## 8. Conclusion and Next Steps

You've successfully integrated a Facebook Messenger bot with multi-tenant support and product search capabilities! From here, you can expand its capabilities by:

*   **Custom AI Prompts**: Customize the AI system prompts to match your brand voice.
*   **Rich Media**: Send images, videos, quick replies, and structured messages (templates).
*   **User Profiles**: Fetch user profile information (name, profile picture) to personalize interactions.
*   **Analytics**: Monitor conversation metrics and lead generation performance.
*   **Workflow Automation**: Set up custom workflows for different lead intents (HOT, WARM, COLD).
*   **Google Sheets Integration**: Enable automatic lead synchronization to Google Sheets.

This integration opens up a world of possibilities for engaging with your audience directly on Messenger with advanced product search and multi-tenant capabilities.