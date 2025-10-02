import { OpenAI } from 'openai';
import { cylinderSchema } from '../../schemas/cylinder_schema'; // 导入我们刚刚创建的schema

// 初始化OpenAI客户端，从环境变量中读取API密钥，确保安全
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export default async function handler(req, res) {
  // 只接受POST请求
  if (req.method !== 'POST') {
    return res.status(405).json({ message: '方法不允许' });
  }

  try {
    // 从请求体中获取Base64编码的图片和上一次的分析结果（用于迭代）
    const { image, previousAnalysis } = req.body;

    // --- 核心Prompt（给AI的指令） ---
    // 这是项目最关键的部分。我们给AI设定角色、任务，并提供精确的格式要求。
    let userPrompt = `
      你是一个专业的AI助手，擅长解读机械工程图纸。
      你的任务是分析提供的圆柱体零件的图像，并提取所有指定的参数。
      你的回答必须是一个严格遵守下面提供的JSON Schema的、单一且有效的JSON对象。
      对于任何你无法从图像中高置信度确定的值，你必须使用 null。不要猜测或编造数据。
      请特别注意图纸上的形位公差(GD&T)、表面粗糙度符号和基准。

      必须遵守的JSON Schema如下:
      ${JSON.stringify(cylinderSchema, null, 2)}
    `;

    // 如果有上一次的分析结果（用户迭代），则加入到Prompt中
    if (previousAnalysis) {
      userPrompt += `
      
      这是一次迭代分析。用户提供了他们修改过的数据或上一次的分析结果。
      请使用这些信息来修正你的分析，重点关注填充那些之前为null或不正确的字段。
      
      上一次的分析/用户的修正:
      ${JSON.stringify(previousAnalysis, null, 2)}
      `;
    }

    const response = await openai.chat.completions.create({
      model: "gpt-4o", // 使用最新、最强大的模型
      messages: [
        {
          role: "user",
          content: [
            { type: "text", text: userPrompt },
            {
              type: "image_url",
              image_url: {
                url: image, // 从前端传来的Base64图片数据
                detail: "high" // 使用高分辨率模式，以便读取图纸上的小字
              },
            },
          ],
        },
      ],
      max_tokens: 2048, // 限制最大token数，防止失控
      response_format: { type: "json_object" }, // 强制AI输出JSON格式，非常重要！
    });

    // 解析AI返回的JSON字符串
    const aiResponseJson = JSON.parse(response.choices[0].message.content);
    
    // 将解析后的JSON对象返回给前端
    res.status(200).json(aiResponseJson);

  } catch (error) {
    console.error('调用OpenAI时出错:', error);
    res.status(500).json({ message: '分析图像时出错', details: error.message });
  }
}