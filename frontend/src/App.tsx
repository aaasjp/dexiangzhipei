import React, { useState } from 'react';
import { 
  Container, 
  Grid, 
  TextField, 
  Button, 
  Box,
  Typography,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton
} from '@mui/material';
import axios from 'axios';
import CloseIcon from '@mui/icons-material/Close';
import SaveIcon from '@mui/icons-material/Save';

interface SceneData {
  sceneName: string;
  sceneGoal: string;
  aiRole: string;
  myRole: string;
  openingLine: string;
  instructions: string;
  dialogTurns: number;
  reasoning?: string;
}

function App() {
  const [userInput, setUserInput] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [sceneData, setSceneData] = useState<SceneData>({
    sceneName: '',
    sceneGoal: '',
    aiRole: '',
    myRole: '',
    openingLine: '',
    instructions: '',
    dialogTurns: 10
  });

  const [openDialog, setOpenDialog] = useState(false);
  const [reasoningContent, setReasoningContent] = useState('');
  const [courseContent, setCourseContent] = useState('');
  const [adjustInstruction, setAdjustInstruction] = useState('如果你对生成的课程不满意，请输入修改建议');

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const selectedFile = event.target.files[0];
      const fileType = selectedFile.type;
      if (fileType.includes('pdf') || fileType.includes('image')) {
        setFile(selectedFile);
      } else {
        alert('只支持 PDF 和图片文件');
      }
    }
  };

  const handleOptimize = async () => {
    try {
      const formData = new FormData();
      formData.append('scene_description', userInput);
      if (file) {
        formData.append('file', file);
      }

      const response = await axios.post('http://127.0.0.1:5000/optimize_course_scense', formData);
      
      // 假设后端返回的数据格式与 SceneData 接口匹配
      setSceneData(response.data);
    } catch (error) {
      console.error('优化请求失败:', error);
      alert('优化请求失败');
    }
  };

  const handleCreateCourse = async () => {
    try {
      setReasoningContent(''); // 清空推理内容
      setCourseContent(''); // 清空课程内容
      setOpenDialog(true); // 打开对话框
      
      const formData = new FormData();
      formData.append('scene_description', userInput);
      formData.append('sceneName', sceneData.sceneName);
      formData.append('sceneGoal', sceneData.sceneGoal);
      formData.append('aiRole', sceneData.aiRole);
      formData.append('myRole', sceneData.myRole);
      formData.append('openingLine', sceneData.openingLine);
      formData.append('instructions', sceneData.instructions);
      formData.append('diag_turns', sceneData.dialogTurns.toString());
      if (file) {
        formData.append('file', file);
      }

      const response = await fetch('http://127.0.0.1:5000/ai_create_course', {
        method: 'POST',
        body: formData,
      });

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'reasoning') {
                setReasoningContent(prev => prev + data.text);
              } else {
                setCourseContent(prev => prev + data.text);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('创建课程失败:', error);
      alert('创建课程失败');
      setOpenDialog(false);
    }
  };

  const handleAdjustCourse = async () => {
    try {
      setReasoningContent('');
      setCourseContent('');
      
      const formData = new FormData();
      formData.append('scene_description', userInput);
      formData.append('sceneName', sceneData.sceneName);
      formData.append('sceneGoal', sceneData.sceneGoal);
      formData.append('aiRole', sceneData.aiRole);
      formData.append('myRole', sceneData.myRole);
      formData.append('openingLine', sceneData.openingLine);
      formData.append('instructions', sceneData.instructions);
      formData.append('diag_turns', sceneData.dialogTurns.toString());
      formData.append('adjust_instruction', adjustInstruction);
      formData.append('course_content', courseContent);

      const response = await fetch('http://127.0.0.1:5000/adjust_ai_create_course', {
        method: 'POST',
        body: formData,
      });

      const reader = response.body?.getReader();
      if (!reader) return;

      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const text = decoder.decode(value);
        const lines = text.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.type === 'reasoning') {
                setReasoningContent(prev => prev + data.text);
              } else {
                setCourseContent(prev => prev + data.text);
              }
            } catch (e) {
              console.error('Error parsing SSE data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('调整课程失败:', error);
      alert('调整课程失败');
    }
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
  };

  const handleSaveCourse = async (content: string) => {
    try {
      const response = await axios.post('http://127.0.0.1:5000/save_course', {
        course_content: content
      });
      if (response.status === 200) {
        alert('课程保存成功！');
      }
    } catch (error) {
      console.error('保存课程失败:', error);
      alert('保存课程失败');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Grid container spacing={4}>
        {/* 左侧部分 */}
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            multiline
            rows={4}
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="请输入文本"
            variant="outlined"
            sx={{ mb: 2 }}
          />
          <Box display="flex" gap={2} sx={{ mb: 2 }}>
            <Button
              variant="contained"
              component="label"
            >
              上传附件
              <input
                type="file"
                hidden
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileChange}
              />
            </Button>
            <Button
              variant="contained"
              onClick={handleOptimize}
            >
              场景优化
            </Button>
          </Box>
          <TextField
            fullWidth
            multiline
            rows={8}
            value={sceneData.reasoning || ''}
            label="AI推理过程"
            variant="outlined"
            InputProps={{
              readOnly: true,
            }}
            sx={{ mb: 2 }}
          />
        </Grid>

        {/* 右侧部分 */}
        <Grid item xs={12} md={6}>
          <Box display="flex" flexDirection="column" gap={2}>
            <TextField
              label="场景名称"
              value={sceneData.sceneName}
              onChange={(e) => setSceneData({...sceneData, sceneName: e.target.value})}
              fullWidth
            />
            <TextField
              label="场景目标"
              value={sceneData.sceneGoal}
              onChange={(e) => setSceneData({...sceneData, sceneGoal: e.target.value})}
              fullWidth
            />
            <TextField
              label="AI角色"
              value={sceneData.aiRole}
              onChange={(e) => setSceneData({...sceneData, aiRole: e.target.value})}
              fullWidth
            />
            <TextField
              label="我的角色"
              value={sceneData.myRole}
              onChange={(e) => setSceneData({...sceneData, myRole: e.target.value})}
              fullWidth
            />
            <TextField
              label="开场白"
              value={sceneData.openingLine}
              onChange={(e) => setSceneData({...sceneData, openingLine: e.target.value})}
              fullWidth
            />
            <TextField
              label="要求指令"
              value={sceneData.instructions}
              onChange={(e) => setSceneData({...sceneData, instructions: e.target.value})}
              fullWidth
            />
            <TextField
              label="对话轮数"
              type="number"
              value={sceneData.dialogTurns}
              onChange={(e) => setSceneData({...sceneData, dialogTurns: Math.max(1, parseInt(e.target.value) || 10)})}
              inputProps={{ min: 1 }}
              fullWidth
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleCreateCourse}
              sx={{ mt: 2 }}
            >
              AI建课
            </Button>
          </Box>
        </Grid>
      </Grid>

      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            height: '80vh', // 设置对话框高度
            display: 'flex',
            flexDirection: 'column'
          }
        }}
      >
        <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">课程内容</Typography>
          <IconButton
            aria-label="close"
            onClick={handleCloseDialog}
            sx={{ color: 'grey.500' }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers sx={{ flex: 1, overflow: 'auto' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* 推理内容部分 */}
            <Box
              sx={{
                flex: 1,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '1rem',
                lineHeight: 1.5,
                mb: 2,
                p: 2,
                bgcolor: '#f5f5f5',
                borderRadius: 1,
                overflow: 'auto'
              }}
            >
              <Typography variant="subtitle1" gutterBottom>
                推理过程：
              </Typography>
              {reasoningContent || '正在生成推理过程...'}
            </Box>
            
            {/* 课程内容部分 */}
            <Box
              sx={{
                flex: 1,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '1rem',
                lineHeight: 1.5,
                p: 2,
                bgcolor: '#f5f5f5',
                borderRadius: 1,
                overflow: 'auto'
              }}
            >
              <Typography variant="subtitle1" gutterBottom>
                课程内容：
              </Typography>
              {courseContent || '正在生成课程内容...'}
            </Box>
          </Box>
          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              multiline
              rows={2}
              value={adjustInstruction}
              onChange={(e) => setAdjustInstruction(e.target.value)}
              placeholder="如果你对生成的课程不满意，请输入修改建议"
              variant="outlined"
            />
            <Button
              variant="contained"
              onClick={handleAdjustCourse}
              sx={{ minWidth: '120px' }}
            >
              优化建课
            </Button>
            <Button
              variant="contained"
              color="secondary"
              onClick={() => handleSaveCourse(courseContent)}
              startIcon={<SaveIcon />}
              sx={{ minWidth: '120px' }}
            >
              保存课程
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>关闭</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}

export default App;
