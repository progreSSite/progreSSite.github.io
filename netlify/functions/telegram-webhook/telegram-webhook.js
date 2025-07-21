// /netlify/functions/telegram-webhook/telegram-webhook.js
const { Telegraf } = require('telegraf');
const axios = require('axios');

const bot = new Telegraf(process.env.TELEGRAM_BOT_TOKEN);

// Обработчик callback запросов кнопок одобрения/отклонения с учетом нового формата callback_data
bot.action(/^(approve|reject)_comment_([a-zA-Z0-9]{1,20})_[a-f0-9]{8}$/, async (ctx) => {
  try {
    const [_, action, newsId] = ctx.match;
    const messageText = ctx.update.callback_query.message.text;

    const authorMatch = messageText.match(/👤 Автор: (.+)/);
    const textMatch = messageText.match(/✉️ Текст: (.+)/);

    if (!authorMatch || !textMatch) {
      await ctx.answerCbQuery('Не удалось обработать комментарий');
      return;
    }

    const author = authorMatch[1];
    const text = textMatch[1];

    // Используем newsId из callback_data как имя файла
    const safeFileName = newsId; // уже ограничено и безопасно
    const filePath = `_data/comments/${safeFileName}.json`;
    const url = `https://api.github.com/repos/${process.env.REPO_OWNER}/${process.env.REPO_NAME}/contents/${filePath}`;

    let existingContent = [];
    let sha = null;

    try {
      const response = await axios.get(url, {
        headers: {
          'Authorization': `token ${process.env.GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      });
      existingContent = JSON.parse(Buffer.from(response.data.content, 'base64').toString());
      sha = response.data.sha;
    } catch (error) {
      if (error.response?.status !== 404) throw error;
      existingContent = [];
    }

    const newComment = {
      author,
      text,
      status: action === 'approve' ? 'approved' : 'rejected',
      date: new Date().toISOString()
    };

    const updatedContent = [...existingContent, newComment];

    await axios.put(url, {
      message: `${action === 'approve' ? 'Approved' : 'Rejected'} comment`,
      content: Buffer.from(JSON.stringify(updatedContent, null, 2)).toString('base64'),
      sha,
      branch: 'main'
    }, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });

    await ctx.answerCbQuery(`Комментарий ${action === 'approve' ? 'одобрен' : 'отклонен'}`);
    await ctx.deleteMessage();

  } catch (error) {
    console.error('Ошибка модерации:', error);
    await ctx.answerCbQuery('Произошла ошибка. Попробуйте позже.');
  }
});

exports.handler = async (event) => {
  try {
    await bot.handleUpdate(JSON.parse(event.body));
    return { statusCode: 200, body: '' };
  } catch (error) {
    console.error('Webhook handler error:', error);
    return { statusCode: 500, body: 'Internal Server Error' };
  }
};