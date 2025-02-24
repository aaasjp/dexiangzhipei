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
3. AI角色：描述AI扮演的客户角色，包括客户的身份和特征
4. 员工角色：描述客服人员应该扮演的角色，包括岗位和职责
5. 开场白：设计一个专业、得体的开场白
6. 要求指令：列出在对话过程中需要注意的关键点和要求

请以JSON格式返回，包含以下字段：
sceneName, sceneGoal, aiRole, myRole, openingLine, instructions"""

    # 组合用户输入
    combined_input = scene_description
    if file_content:
        combined_input = f"场景描述：{scene_description}\n\n相关资料：{file_content}"

    # 调用大模型
    response = chat_completion(
        combined_input,
        [],  # 空历史记录
        'deepseek-v3',
        system_prompt=system_prompt
    )
    print(f'llm response: {response}')
    try:
        # 解析大模型返回的JSON响应
        if isinstance(response, dict) and 'content' in response:
            result = json.loads(response['content'])
            return jsonify({
                'sceneName': result.get('sceneName', ''),
                'sceneGoal': result.get('sceneGoal', ''),
                'aiRole': result.get('aiRole', ''),
                'myRole': result.get('myRole', ''),
                'openingLine': result.get('openingLine', ''),
                'instructions': result.get('instructions', '')
            })
        else:
            return jsonify({'error': '无效的响应格式'}), 400
    except json.JSONDecodeError:
        return jsonify({'error': '响应解析失败'}), 400
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 400

if __name__ == '__main__':
    print("Starting Flask application...")  # 添加启动日志
    app.run(debug=True, host='0.0.0.0', port=5000) 