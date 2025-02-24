from flask import Flask, request, Response, jsonify
from utils.llm import chat_completion, chat_completion_stream
import json
from flask_cors import CORS  # 添加CORS支持
import fitz  # PyMuPDF
from PIL import Image
import io
import pytesseract  # For image text extraction

app = Flask(__name__)
CORS(app)  # 启用CORS

# 添加一个测试路由
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Server is running!"})

@app.route('/optimize_course_scense', methods=['POST'])
def optimize_course_scense():
    # 获取场景描述
    scene_description = request.form.get('scene_description', '')
    
    # 处理文件上传
    file = request.files.get('file')
    file_content = ""
    
    if file:
        # 获取文件名和扩展名
        filename = file.filename
        file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
        
        # 处理PDF文件
        if file_extension == 'pdf':
            try:
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    file_content += page.get_text()
                pdf_document.close()
            except Exception as e:
                return jsonify({'error': f'PDF processing error: {str(e)}'}), 400
                
        # 处理图片文件
        elif file_extension in ['png', 'jpg', 'jpeg']:
            try:
                image = Image.open(io.BytesIO(file.read()))
                file_content = pytesseract.image_to_string(image)
            except Exception as e:
                return jsonify({'error': f'Image processing error: {str(e)}'}), 400
        else:
            return jsonify({'error': 'Unsupported file format'}), 400

    # 构建提示词
    system_prompt = """你是一个专业的员工培训专家，擅长设计客户服务场景。
请基于用户提供的场景描述，生成一个完整的员工培训场景方案。
你需要输出以下内容，每个内容都要简洁明确：
1. 场景名称：用简短的词语概括这个场景
2. 场景目标：描述这个培训场景要达到的具体目标
3. AI角色：描述AI扮演的客户角色（简短一些）
4. 员工角色：描述客服人员应该扮演的角色（简短一些）
5. 开场白：设计一个专业、得体的开场白
6. 要求指令：列出在对话过程中需要注意的关键点和要求（不超过5条）

请以JSON格式返回，包含以下字段：
sceneName(string类型), sceneGoal(string类型), aiRole(string类型), myRole(string类型), openingLine(string类型), instructions(list类型 )"""

    # 组合用户输入
    combined_input = scene_description
    if file_content:
        combined_input = f"场景描述：{scene_description}\n\n相关资料：{file_content}"

    # 调用大模型
    response = chat_completion(
        combined_input,
        [],  # 空历史记录
        'deepseek-r1',
        system_prompt=system_prompt
    )
    print(f'------llm response: {response}')
    try:
        # 解析大模型返回的JSON响应
        if isinstance(response, dict):
            result = {}
            content = response.get('content', '').strip('```json\n').strip('```')
            reasoning = response.get('reasoning', '')  # 获取推理过程
            
            try:
                result = json.loads(content)
                # 使用json.dumps进行格式化打印，设置缩进为2，确保中文正确显示
                print("\n=== 解析后的场景数据 ===")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print("========================\n")
            except json.JSONDecodeError:
                return jsonify({'error': '响应解析失败'}), 400

            instructions = result.get('instructions', [])
            instructions_str="\n".join([f" {i + 1}. {instruction}" for i, instruction in enumerate(instructions)])    
            return jsonify({
                'sceneName': result.get('sceneName', ''),
                'sceneGoal': result.get('sceneGoal', ''),
                'aiRole': result.get('aiRole', ''),
                'myRole': result.get('myRole', ''), 
                'openingLine': result.get('openingLine', ''),
                'instructions': instructions_str,
                'reasoning': reasoning  # 添加推理过程到返回值
            })
        else:
            return jsonify({'error': '无效的响应格式'}), 400
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 400

@app.route('/ai_create_course', methods=['POST'])
def ai_create_course():
    try:
        # 获取所有参数
        scene_description = request.form.get('scene_description', '')
        scene_name = request.form.get('sceneName', '')
        scene_goal = request.form.get('sceneGoal', '')
        ai_role = request.form.get('aiRole', '')
        my_role = request.form.get('myRole', '')
        opening_line = request.form.get('openingLine', '')
        instructions = request.form.get('instructions', '')
        
        # 处理文件上传
        file = request.files.get('file')
        file_content = ""
        
        if file:
            filename = file.filename
            file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
            
            if file_extension == 'pdf':
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                for page_num in range(pdf_document.page_count):
                    page = pdf_document[page_num]
                    file_content += page.get_text()
                pdf_document.close()
            elif file_extension in ['png', 'jpg', 'jpeg']:
                image = Image.open(io.BytesIO(file.read()))
                file_content = pytesseract.image_to_string(image)
            else:
                return Response('Unsupported file format', status=400)

        # 构建用户提示词
        system_prompt = f"""你是一个专业的培训对话生成专家。请基于以下信息生成一个10轮的培训对话：

场景描述：{scene_description}
场景名称：{scene_name}
场景目标：{scene_goal}
AI角色：{ai_role}
员工角色：{my_role}
开场白：{opening_line}
指令要求：{instructions}

参考资料：{file_content if file_content else '无'}

请生成10轮对话，要求：
1. 对话要符合场景描述和目标
2. AI扮演{ai_role}角色
3. 员工扮演{my_role}角色
4. 第一句话必须是员工说的开场白
5. 整个对话必须严格遵守指令要求
6. 对话要自然流畅，符合真实场景
7. 必须是员工和客户的轮流对话，不要员工或者AI连续说两轮的情况
8. 推理过程不要太啰嗦

请输出对话内容，每一轮都要标明是谁在说话,生成的对话格式如下:
{my_role}: 第一句话
{ai_role}: 第二句话
{my_role}: 第三句话
{ai_role}: 第四句话
...
"""

        # 使用流式响应
        def generate():
            for is_reasoning, content in chat_completion_stream(
                "",  # 用户输入为空，因为所有信息都在system_prompt中
                [],  # 空历史记录
                'deepseek-r1',
                system_prompt=system_prompt
            ):
                # 构建包含类型和内容的JSON响应
                response_data = {
                    'type': 'reasoning' if is_reasoning else 'content',
                    'text': content
                }
                yield f"data: {json.dumps(response_data)}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return Response(f'Error: {str(e)}', status=500)

if __name__ == '__main__':
    print("Starting Flask application...")  # 添加启动日志
    app.run(debug=True, host='0.0.0.0', port=5000) 