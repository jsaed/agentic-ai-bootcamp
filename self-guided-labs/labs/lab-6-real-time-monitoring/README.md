# 👀 Monitor Agents in Real Time

## 🔎 Overview

This lab guide introduces you to real-time monitoring capabilities in watsonx Orchestrate. You'll learn how to track agent performance, analyze conversation patterns, and monitor key metrics like success rates, user feedback, and content safety indicators. Real-time monitoring is crucial for maintaining agent quality in production and identifying issues before they impact users.



## 💻 Hands-on Instructions

watsonx Orchestrate allows you to fully monitor AI Agents, whether in development or production. In the previous labs, you have created multiple agents. Go to your Master Car Buying agent and perform the following actions.

1. On yout Agent Builder screen and click on the **Deploy** button above the chat window:

<img src="images/deploy-agent.png" alt="Description of image" width="600">

2. Now, in the Pre-deployment screen, you can review your agent settings and parameters. There's no need to make any changes. Now click on **Deploy**.

<img src="images/pre-deployment-summary.png" alt="Description of image" width="100%">

> [!NOTE]
Once your agent has been deployed, it can be accessed via a number of channels. watsonx Orchestrate can also help you embed your agents into a website, or make them avaiable via **Slack**, **WhatsApp**, and a number of other channels. Since the focus of this lab is monitoring, we'll skip this for now but the user is encouraged to try out the **Channels** section in the Agent Builder.

3. Now your agent is live and you will see a green **Live** icon above the chat window:

<img src="images/live-agent.png" alt="Description of image" width="400">
   
4. Now chat with the agent. Ask a number of questions and look at the answers. You can thumbs up or thumbs down each answer to provide feedback on the quality of the responses.
     
6. Now go to the Hamburger menu and click on **Analyze**

<img src="images/hamburger.png" alt="hamburger" width="300">
   
7. This will take you to the main **Agent Analytics Screen**. This one shows you an overview of all your agents.

<img src="images/analytics.png" alt="Analytics" width="100%">
   
8. Click on your own agent on the right side and you'll be able to see macro metrics such as:

- Total number of conversations
- Total input and output token counts
- Number of unique users that have interacted with the agent
- Average conversation duration
- Average message latency

<img src="images/agent-analytics2.png" alt="Agent Analytics" width="100%">
   
8. But you can also inspect granularly each conversation and each message in the chats. Click on **Conversations**.

> [!NOTE]
If you'd like to populate more conversations, you can go back to your chat window and ask questions to the agent. You can click on the Restart 🔄 button above in the chat window to force a new conversation to be created.

<img src="images/conversations.png" alt="Conversation" width="100%">
   
9. Finally on the **Evaluation** tab you can check for:

- Hallucinations
- Toxicity
- Helpfulness

These features are still in preview mode and additional labs will be developed soon.

<img src="images/agent-analytics2.png" alt="Agent Analytics" width="100%">

---

<div align="center">

**[← Previous: 5. Automatic Evaluation](../lab-5-automatic-evaluation/README.md) &nbsp;&nbsp;|&nbsp;&nbsp; [🏠 Home](../../README.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: 7. Dashboard and Agent Analytics →](../lab-7-dashboard-analytics/README.md)**

</div>
