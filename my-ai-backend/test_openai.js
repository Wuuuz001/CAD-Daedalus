// test_openai.js
import { OpenAI } from 'openai';
import dotenv from 'dotenv';

// 加载 .env 文件中的环境变量
dotenv.config();

console.log("... 准备测试 OpenAI 连接 ...");
console.log(`将要使用的模型: ${process.env.AI_MODEL_NAME}`);

// 检查 API Key 是否被加载
if (!process.env.OPENAI_API_KEY) {
    console.error("❌ 错误：在 .env 文件中未找到 OPENAI_API_KEY。");
    process.exit(1); // 退出程序
}

// 创建 OpenAI 客户端
const openai = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
    // 【注意】当使用 Gemini 等第三方代理时，这里需要 baseURL
    // 当使用 OpenAI 官方时，这里必须为空
    baseURL: process.env.OPENAI_API_BASE_URL || null, 
});

async function main() {
    try {
        console.log("🚀 正在发送一个简单的请求到 AI 服务...");
        const completion = await openai.chat.completions.create({
            messages: [{ role: "system", content: "You are a helpful assistant." }, { role: "user", content: "Hello world" }],
            model: process.env.AI_MODEL_NAME || "gpt-3.5-turbo", // 确保有模型名称
        });
        console.log("✅ 成功！已收到 AI 的回复:");
        console.log(completion.choices[0]);

    } catch (error) {
        console.error("❌ 请求失败! 错误详情:");
        console.error(error);
    }
}

main();