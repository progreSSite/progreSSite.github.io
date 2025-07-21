exports.handler = async (event) => {
  // Разрешаем CORS для preflight-запросов (OPTIONS)
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
      },
      body: ''
    };
  }

  // Основной обработчик POST-запросов
  if (event.httpMethod === 'POST') {
    try {
      const { urls, keyword } = JSON.parse(event.body);
      
      const analysis = await Promise.all(urls.map(async (url) => {
        try {
          const startTime = Date.now();
          const res = await fetch(url);
          const html = await res.text();
          const loadTime = Date.now() - startTime;

          // Анализ URL
          const urlObj = new URL(url.includes('://') ? url : `https://${url}`);
          const urlAnalysis = {
            length: urlObj.href.length,
            isDynamic: urlObj.search.length > 0,
            hasKeyword: keyword ? urlObj.href.toLowerCase().includes(keyword.toLowerCase()) : false
          };

          // Анализ контента
          const cleanHtml = html
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi, '')
            .replace(/<[^>]+>/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();

          const contentAnalysis = {
            length: cleanHtml.length,
            textToCodeRatio: (cleanHtml.length / html.length * 100).toFixed(2)
          };

          // Извлечение title, description, h1, h2
          const title = html.match(/<title>(.*?)<\/title>/i)?.[1] || 'Не найден';
          const descriptionMatch = html.match(/<meta\s+name="description"\s+content="(.*?)"/i);
          const description = descriptionMatch ? descriptionMatch[1] : 'Не найден';
          const h1 = html.match(/<h1.*?>(.*?)<\/h1>/i)?.[1] || 'Отсутствует';
          const h2Tags = [...html.matchAll(/<h2.*?>(.*?)<\/h2>/gi)].map(match => match[1]);
          
          // Извлечение alt текстов изображений
          const altTexts = [...html.matchAll(/<img[^>]+alt="([^"]*)"/gi)].map(match => match[1]);

          // Подсчет вхождений ключевой фразы
          let keywordStats = { exactCount: 0, partialCount: 0 };
          if (keyword && keyword.trim() !== '') {
            const keywordLower = keyword.toLowerCase();
            const textLower = cleanHtml.toLowerCase();
            const regexExact = new RegExp(`(^|\\s)${keywordLower}(\\s|$)`, 'gi');
            keywordStats.exactCount = (cleanHtml.match(regexExact) || []).length;
            keywordStats.partialCount = textLower.split(keywordLower).length - 1;
          }

          return {
            url,
            status: res.status,
            title,
            description,
            h1,
            h2: h2Tags,
            alts: altTexts,
            loadTime,
            urlAnalysis,
            contentAnalysis,
            keywordStats,
            error: null
          };
        } catch (error) {
          return { 
            url, 
            error: 'Не удалось загрузить страницу',
            status: 500,
            title: null,
            description: null,
            h1: null,
            h2: null,
            alts: null,
            loadTime: null,
            urlAnalysis: null,
            contentAnalysis: null,
            keywordStats: null
          };
        }
      }));

      return {
        statusCode: 200,
        body: JSON.stringify(analysis),
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      };
    } catch (error) {
      return { 
        statusCode: 500, 
        body: JSON.stringify({ error: 'Ошибка сервера', details: error.message }) 
      };
    }
  }

  return {
    statusCode: 405,
    body: JSON.stringify({ error: 'Метод не поддерживается' })
  };
};