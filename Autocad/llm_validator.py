# llm_validator_openai.py  (请使用这个完整版本替换你的文件内容)

import os
import json
from openai import OpenAI


class LLMValidator:
    """
    使用兼容OpenAI API的LLM（可通过代理访问Gemini等）进行代码审查。
    """

    def __init__(self, api_key: str, base_url: str, model_name: str):
        """
        初始化LLM验证器。

        :param api_key: 你的API密钥。
        :param base_url: 你的API代理地址。
        :param model_name: 要使用的模型名称。
        """
        if not api_key:
            raise ValueError("API Key不能为空。")
        if not base_url:
            raise ValueError("API Base URL不能为空。")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model_name = model_name
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.overall_rating = "UNKNOWN"

    def _construct_prompt(self, lisp_code: str, json_data: dict) -> str:
        """【中文版】构建用于审查的详细Prompt。"""

        json_str = json.dumps(json_data, indent=2, ensure_ascii=False)  # ensure_ascii=False 保证JSON中的中文正常显示

        prompt = f"""
        # 角色设定
        你是一位资深的AutoCAD LISP专家程序员，也是一位一丝不苟的质量保证工程师。
        你的任务是分析根据JSON规范生成的LISP代码，检查其正确性、逻辑错误以及是否符合工程常识。
        **你的所有回答都必须使用简体中文。**

        # 任务上下文
        ## 1. 原始设计图纸 (JSON格式)
        这是定义图纸的原始JSON输入：
        ```json
        {json_str}
        ```

        ## 2. 生成的LISP代码
        这是根据上述JSON生成的LISP代码：
        ```lisp
        {lisp_code}
        ```

        # 审查指令
        请严格按照以下清单进行检查，并用中文提供你的分析：

        1.  **语法检查:** LISP的语法是否基本正确？（例如：括号是否匹配，引号是否闭合等）。
        2.  **逻辑与参数验证:** LISP代码是否准确地实现了JSON中的参数？
            - 检查关键尺寸（如半径、高度、长度等）是否与JSON中的值一致。
            - 验证图层、插入点和其他选项是否与JSON规范匹配。
        3.  **工程常识检查:** 从工程角度看，这个图纸的设计是否合理？
            - 是否存在不可能的几何形状（例如：孔比零件本身还大）？
            - 装配体的零件是否能正确配合（例如：螺钉直径与螺母孔径是否匹配）？
            - 标注（尺寸、基准等）的放置是否符合逻辑，是否指向了相关的特征？
        4.  **最佳实践与潜在问题:** 代码中是否存在某些部分，虽然语法正确，但可能在AutoCAD中导致问题或违反了编程最佳实践？（例如：使用了过时的命令，绘图方法效率低下等）。

        # 输出格式要求
        你的回复**必须**是一个结构化的JSON对象。根对象应包含三个键: "overall_rating", "analysis", "raw_thought_process"。
        - "overall_rating": 一个字符串, 必须是 "通过", "通过但有警告", 或 "失败" 中的一个。
        - "analysis": 一个对象，包含三个字符串列表: "errors", "warnings", "suggestions"。
          - "errors" (错误): 用于描述那些会导致脚本失败或画出完全错误图形的严重问题。
          - "warnings" (警告): 用于描述那些可能导致结果不正确或违反工程常识的问题。
          - "suggestions" (建议): 用于提出可以改进代码风格或实践的建议。
        - "raw_thought_process" (原始思考过程): 一个字符串，包含你进行分析时的逐步思考过程。

        **请确保你的整个输出是一个单一、完整、且严格合法的JSON对象。**
        """
        return prompt
    def validate(self, lisp_code: str, json_data: dict) -> bool:
        """使用LLM API执行验证。"""
        # --- 这里是完整的函数体 ---
        print("\n--- [LLM 验证器开始 (通过OpenAI兼容代理)] ---")
        print(f"正在使用模型 '{self.model_name}' 进行分析，请稍候...")

        prompt = self._construct_prompt(lisp_code, json_data)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2
            )

            response_content = response.choices[0].message.content

            if "```json" in response_content:
                response_content = response_content.split("```json\n", 1)[1].split("```")[0]

            analysis_result = json.loads(response_content)

            self.overall_rating = analysis_result.get("overall_rating", "UNKNOWN")
            analysis = analysis_result.get("analysis", {})
            self.errors = analysis.get("errors", [])
            self.warnings = analysis.get("warnings", [])
            self.suggestions = analysis.get("suggestions", [])

            print("--- [LLM 验证器结束] ---")
            self.print_report()

            return self.overall_rating != "FAIL"

        except Exception as e:
            print(f"--- [LLM 验证器错误] ---")
            print(f"调用LLM API时发生错误: {e}")
            self.overall_rating = "VALIDATION_ERROR"
            return False

    def print_report(self):
        """打印LLM生成的验证报告。"""
        # --- 这里是完整的函数体 ---
        print(f"\nLLM 分析报告 (模型: {self.model_name}):")
        print("=" * 40)
        print(f"总体评级: {self.overall_rating}")
        print("=" * 40)

        if not self.errors and not self.warnings and not self.suggestions:
            print("✅ LLM分析通过，未发现任何问题。")
            return

        if self.errors:
            print("\n--- 🔴 错误 (Errors) ---")
            for item in self.errors:
                print(f"- {item}")

        if self.warnings:
            print("\n--- 🟡 警告 (Warnings) ---")
            for item in self.warnings:
                print(f"- {item}")

        if self.suggestions:
            print("\n--- 💡 建议 (Suggestions) ---")
            for item in self.suggestions:
                print(f"- {item}")

        print("=" * 40)